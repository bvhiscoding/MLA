"""Convert the frozen report to Word/PDF; run from the repository root.

Requires python-docx, PyMuPDF, pywin32 and desktop Microsoft Word.
QA images go to the system temporary directory, never into the repository.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape

import fitz
import pythoncom
import win32com.client
from docx import Document
from docx.enum.section import WD_SECTION_START
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Pt
from docx.text.paragraph import Paragraph

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output'
STEM = 'Group06_CLC02_Final_Report'
DOCX = OUT / (STEM + '.docx')
PDF = OUT / (STEM + '.pdf')
# Build profile. Defaults reproduce the full (thesis) report; `--paper` builds the short main paper.
CFG = {'source': 'FINAL_REPORT.md', 'figures': 26, 'chapters': 9, 'contents': 3, 'notes': 1, 'paper': False,
       'checks_name': 'build_checks.json'}
CAPTION_LABEL = r'(?:Figure|Table) (?:[A-G]\.)?\d+(?:\.\d+)?\.'
TNR = 'Times New Roman'
TABLE_FONTS = [fitz.Font(fontfile='C:/Windows/Fonts/times.ttf'),
               fitz.Font(fontfile='C:/Windows/Fonts/timesbd.ttf')]
CODE_FONT = fitz.Font(fontfile='C:/Windows/Fonts/consola.ttf')
EXPECTED_HEADINGS = {
    'Context representations': '4.3.3',
    'Data verification': '3.5',
    'Essay length, holistic score and class mix': '3.7.4',
    'Ten high-confidence Ineffective failures': '7.3',
    'Model–rater agreement': '8.3',
    'Limitations': '8.5',
}


def el(tag, **attrs):
    node = OxmlElement(tag)
    for key, value in attrs.items():
        node.set(qn('w:' + key), str(value))
    return node


def font(obj, size, name=TNR, bold=False, italic=False):
    obj.font.name = name
    obj.font.size = Pt(size)
    obj.font.bold = bold
    obj.font.italic = italic
    obj.font.color.rgb = __import__('docx').shared.RGBColor(0, 0, 0)
    obj.font.underline = False
    rp = obj.element.get_or_add_rPr()
    rf = rp.find(qn('w:rFonts'))
    for slot in ('ascii', 'hAnsi', 'eastAsia', 'cs'):
        rf.set(qn('w:' + slot), name)
    for slot in ('asciiTheme', 'hAnsiTheme', 'eastAsiaTheme', 'cstheme'):
        rf.attrib.pop(qn('w:' + slot), None)
    rp.append(el('w:szCs', val=int(size * 2)))
    rp.append(el('w:bCs', val=int(bold)))


def inline(p, text, size=13, bold=False, code_size=11):
    # The report uses backticks for paths/code and very little emphasis.
    pattern = r'(`[^`]+`|\*\*[^*]+\*\*|(?<!\w)\*[^*\n]+\*(?!\w)|\[[^\]]+\]\(https?://[^)]+\))'
    for token in re.split(pattern, text):
        if not token:
            continue
        code = token.startswith('`') and token.endswith('`')
        italic = token.startswith('*') and not token.startswith('**')
        if code:
            token = token[1:-1]
        elif token.startswith('**'):
            token = token[2:-2]  # Source emphasis must not introduce body bold.
        elif italic:
            token = token[1:-1]
        link = re.fullmatch(r'\[([^\]]+)\]\((https?://[^)]+)\)', token)
        if link:
            token = link[1]
        run = p.add_run(token)
        font(run, code_size if code else size, 'Consolas' if code else TNR, bold and not code, italic)


def field(p, instruction):
    r = p.add_run()
    font(r, 12)
    r._r.append(el('w:fldChar', fldCharType='begin'))
    ins = OxmlElement('w:instrText')
    ins.set(qn('xml:space'), 'preserve')
    ins.text = instruction
    r._r.append(ins)
    r._r.append(el('w:fldChar', fldCharType='separate'))
    r._r.append(el('w:fldChar', fldCharType='end'))


def page_setup(sec, landscape=False, page_format=None):
    sec.page_width, sec.page_height = (Cm(29.7), Cm(21)) if landscape else (Cm(21), Cm(29.7))
    sec.orientation = 1 if landscape else 0
    sec.top_margin = sec.bottom_margin = Cm(2.5)
    sec.left_margin, sec.right_margin = Cm(3), Cm(2)
    sec.header_distance = sec.footer_distance = Cm(1.25)
    # A section copied by python-docx must not restart page numbering.
    for old in list(sec._sectPr.findall(qn('w:pgNumType'))):
        sec._sectPr.remove(old)
    if page_format:
        sec._sectPr.append(el('w:pgNumType', fmt=page_format, start=1))


def footer(sec):
    sec.footer.is_linked_to_previous = False
    p = sec.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = 0
    p.paragraph_format.space_after = 0
    field(p, ' PAGE ')
    for r in p.runs:
        font(r, 12)


def configure(doc):
    styles = doc.styles
    for style in list(styles):
        if style.type in (1, 2):
            font(style, 13)
        for border in style.element.xpath('./w:pPr/w:pBdr'):
            border.getparent().remove(border)
    normal = styles['Normal']
    pf = normal.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf.line_spacing = 1.3
    pf.space_before, pf.space_after = Pt(0), Pt(6)
    pf.first_line_indent = Cm(1)
    pf.widow_control = True
    sizes = [(1, 14, 14, 6), (2, 13, 10, 4), (3, 13, 8, 4)] if CFG['paper'] else [(1, 16, 0, 18), (2, 14, 12, 6), (3, 13, 10, 4)]
    for level, size, before, after in sizes:
        s = styles[f'Heading {level}']
        font(s, size, bold=True, italic=level == 3)
        p = s.paragraph_format
        p.first_line_indent = 0
        p.space_before, p.space_after = Pt(before), Pt(after)
        p.keep_with_next = True
        p.keep_together = True
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if level == 1 and not CFG['paper'] else WD_ALIGN_PARAGRAPH.LEFT
        p.page_break_before = level == 1 and not CFG['paper']
    styles['Heading 1'].font.all_caps = not CFG['paper']
    for name, base in [('Unnumbered H1', 'Heading 1'), ('Appendix H1', 'Heading 1'),
                       ('Appendix H2', 'Heading 2'), ('Appendix H3', 'Heading 3'),
                       ('Front Heading', 'Heading 1')]:
        s = styles.add_style(name, 1)
        s.base_style = styles[base]
        h1, h2 = (14, 13) if CFG['paper'] else (16, 14)
        font(s, h1 if 'H1' in name or name == 'Front Heading' else h2 if name.endswith('H2') else 13,
             bold=True, italic=name.endswith('H3'))
        s.font.all_caps = False
        s.element.get_or_add_pPr().append(el('w:outlineLvl', val=9 if name == 'Front Heading' else int(base[-1]) - 1))
    for name in ('Figure Caption', 'Table Caption'):
        s = styles.add_style(name, 1)
        s.base_style = normal
        font(s, 12)
        p = s.paragraph_format
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.first_line_indent = 0
        p.space_before, p.space_after = Pt(6), Pt(3)
        p.keep_together = True
        p.keep_with_next = name == 'Table Caption'
    for name, size, bold in [('Title Page Header', 14, True), ('Table Note', 11, False)]:
        s = styles.add_style(name, 1)
        s.base_style = normal
        font(s, size, bold=bold)
        s.paragraph_format.first_line_indent = 0
        s.paragraph_format.space_before = Pt(3) if name == 'Table Note' else 0
        s.paragraph_format.space_after = 0
        s.paragraph_format.keep_together = True
    for level in range(1, 4):
        name = f'TOC {level}'
        s = styles[name] if name in styles else styles.add_style(name, 1)
        font(s, 13)
        s.paragraph_format.first_line_indent = 0
        s.paragraph_format.space_after = Pt(3)
        s.paragraph_format.line_spacing = 1.3
    font(styles['Hyperlink'], 13) if 'Hyperlink' in styles else None
    page_setup(doc.sections[0])
    numbering = doc.part.numbering_part.element
    abstract = el('w:abstractNum', abstractNumId=50)
    abstract.append(el('w:multiLevelType', val='multilevel'))
    for level in range(9):
        text = ('%1' if CFG['paper'] else 'CHAPTER %1.') if level == 0 else '.'.join(f'%{n+1}' for n in range(level+1))
        lv = el('w:lvl', ilvl=level)
        lv.extend([el('w:start', val=1), el('w:numFmt', val='decimal')])
        # Word's default restarts subordinate levels when their parent advances.
        # Word emits an Arial glyph for an automatic space suffix; a literal
        # space in the number format uses the numbering run's explicit font.
        lv.extend([el('w:suff', val='nothing'), el('w:lvlText', val=text + ' '),
                   el('w:lvlJc', val='left')])
        rp = el('w:rPr')
        rp.append(el('w:rFonts', ascii=TNR, hAnsi=TNR, eastAsia=TNR, cs=TNR))
        rp.append(el('w:b'))
        if level == 2:
            rp.append(el('w:i'))
        lv.append(rp)
        abstract.append(lv)
    first_num = numbering.find(qn('w:num'))
    numbering.insert(list(numbering).index(first_num), abstract)
    num = el('w:num', numId=50)
    num.append(el('w:abstractNumId', val=50))
    numbering.append(num)
    for lv in numbering.iter(qn('w:lvl')):
        rp = lv.find(qn('w:rPr'))
        if rp is None:
            rp = el('w:rPr')
            lv.append(rp)
        old = rp.find(qn('w:rFonts'))
        if old is not None:
            rp.remove(old)
        rp.insert(0, el('w:rFonts', ascii=TNR, hAnsi=TNR, eastAsia=TNR, cs=TNR))
    defaults = styles.element.find(qn('w:docDefaults')).find(qn('w:rPrDefault')).find(qn('w:rPr'))
    old = defaults.find(qn('w:rFonts'))
    if old is not None:
        defaults.remove(old)
    defaults.insert(0, el('w:rFonts', ascii=TNR, hAnsi=TNR, eastAsia=TNR, cs=TNR))


def caption(doc, text, kind):
    p = doc.add_paragraph(style=f'{kind} Caption')
    m = re.match('(' + CAPTION_LABEL + ')(.*)', text)
    assert m, text
    r = p.add_run(m[1])
    font(r, 12, bold=True)
    inline(p, m[2], 12)
    return p


def table_cells(line):
    return [v.strip().replace(r'\|', '|') for v in re.split(r'(?<!\\)\|', line.strip().strip('|'))]


def column_requirements(rows, size, body_weights=False):
    minimums, weights = [], []
    for col in zip(*rows):
        longest, weight = 0, 0
        for ri, value in enumerate(col):
            plain = re.sub(r'`[^`]+`', '', value)
            words = [v for v in re.split(r'[\s/\-–—]+|(?<=↔)', plain) if v]
            longest = max(longest, *(TABLE_FONTS[ri == 0].text_length(w, fontsize=size) for w in words)) if words else longest
            if '`' in value:
                longest = max(longest, 44)  # Code identifiers may wrap; reserve a readable chunk.
            if ri or not body_weights:
                weight += TABLE_FONTS[ri == 0].text_length(value.replace('`', ''), fontsize=size)
        minimums.append((longest + 10) / 28.3464567)
        weights.append(max(1, weight))
    return minimums, weights


def path_widths(rows, size):
    minimums = []
    for col in zip(*rows):
        required = 0
        for value in col:
            for code in re.findall(r'`([^`]+)`', value):
                for path in re.findall(r'[^,\s]+', code):
                    if re.search(r'[/\\]|\.[a-zA-Z]\w*\b', path):
                        width = CODE_FONT.text_length(path, fontsize=size - 1) / 2.5
                        component = max(CODE_FONT.text_length(v, fontsize=size - 1)
                                        for v in re.split(r'[/\\]', path)) / 2
                        required = max(required, (max(width, component) + 10) / 28.3464567)
        minimums.append(required)
    return minimums


def table_layout(lines, label):
    rows = [table_cells(line) for line in lines]
    align = rows.pop(1)
    assert all(len(row) == len(rows[0]) for row in rows), 'Ragged source table'
    size = 10.5 if len(rows[0]) >= 6 else 11
    minimums, weights = column_requirements(rows, size, body_weights=label == 'Table 7.1')
    if label == 'Table 7.1':
        # Keep a slash with a number, and two F1 values on one line.
        for ci, count in [(1, 2), (2, 2), (6, 3)]:
            prefix = max(TABLE_FONTS[0].text_length(' '.join(row[ci].split()[:count]), fontsize=size)
                         for row in rows[1:])
            minimums[ci] = max(minimums[ci], (prefix + 10) / 28.3464567)
    # A4 portrait only (no landscape sections): shrink the font step by step until the table fits 16 cm.
    for step in (10.5, 10, 9.5, 9, 8.5):
        if sum(minimums) <= 16 or step >= size:
            if sum(minimums) <= 16:
                break
            continue
        size = step
        minimums, weights = column_requirements(rows, size, body_weights=label == 'Table 7.1')
    landscape = False
    total = 16
    if sum(minimums) > total:  # still too wide: let long tokens (paths) wrap inside cells
        minimums = [m * total / sum(minimums) * 0.96 for m in minimums]
    remaining = total - sum(minimums)
    widths = [minimum + remaining * w / sum(weights) for minimum, w in zip(minimums, weights)]
    return {'label': label, 'rows': rows, 'align': align, 'size': size,
            'landscape': landscape, 'widths_cm': widths, 'minimums_cm': minimums}


def make_table(doc, layout):
    rows, align = layout['rows'], layout['align']
    landscape, size = layout['landscape'], layout['size']
    n = len(rows[0])
    total = 24.7 if landscape else 16
    widths = layout['widths_cm']
    t = doc.add_table(rows=0, cols=n)
    t.autofit = False
    pr = t._tbl.tblPr
    pr.append(el('w:jc', val='center'))
    pr.append(el('w:tblLayout', type='fixed'))
    pr.find(qn('w:tblW')).set(qn('w:w'), str(round(Cm(total).twips)))
    pr.find(qn('w:tblW')).set(qn('w:type'), 'dxa')
    borders = el('w:tblBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        borders.append(el('w:' + edge, val='single', sz=4, color='000000'))
    pr.append(borders)
    margins = el('w:tblCellMar')
    for edge, width in [('top', 40), ('bottom', 40), ('left', 65), ('right', 65)]:
        margins.append(el('w:' + edge, w=width, type='dxa'))
    pr.append(margins)
    for col, width in zip(t.columns, widths):
        col.width = Cm(width)
    for ri, values in enumerate(rows):
        row = t.add_row()
        row._tr.get_or_add_trPr().append(el('w:cantSplit'))
        if ri == 0:
            row._tr.get_or_add_trPr().append(el('w:tblHeader'))
        for ci, (cell, value) in enumerate(zip(row.cells, values)):
            cell.width = Cm(widths[ci])
            cell.vertical_alignment = 1
            if ri == 0:
                cell._tc.get_or_add_tcPr().append(el('w:shd', fill='D9D9D9'))
            p = cell.paragraphs[0]
            f = p.paragraph_format
            f.first_line_indent = 0
            f.line_spacing = 1
            f.space_before, f.space_after = 0, Pt(2)
            f.keep_with_next = ri == 0
            a = align[ci]
            p.alignment = (WD_ALIGN_PARAGRAPH.CENTER if a.startswith(':') and a.endswith(':')
                           else WD_ALIGN_PARAGRAPH.RIGHT if a.endswith(':') else WD_ALIGN_PARAGRAPH.LEFT)
            inline(p, value, size, bold=ri == 0, code_size=size - 1)
            # Inline code in cells remains regular, including in headers.
            for r in p.runs:
                if r.font.name == 'Consolas':
                    r.bold = False
                    r._r.get_or_add_rPr().append(el('w:bCs', val=0))
    return t


def table_gap(doc):
    p = doc.add_paragraph()
    f = p.paragraph_format
    f.first_line_indent = 0
    f.space_before = f.space_after = 0
    f.line_spacing = Pt(8)
    font(p.add_run(), 1)


def equation(doc, source):
    expected = r'\mathcal{L} = -\frac{1}{N}\sum_{i=1}^{N} w_{y_i}\,\log p_\theta(y_i \mid x_i), \qquad w_k = \frac{N}{3\,N_k},'
    assert source.strip() == expected, 'Equation changed: adapt the OMML conversion explicitly'
    def r(text, upright=False):
        return '<m:r>' + ('<m:rPr><m:sty m:val="p"/></m:rPr>' if upright else '') + '<w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/><w:sz w:val="26"/></w:rPr><m:t xml:space="preserve">' + escape(text) + '</m:t></m:r>'
    def sub(base, lower):
        return '<m:sSub><m:e>' + base + '</m:e><m:sub>' + lower + '</m:sub></m:sSub>'
    def frac(a, b):
        return '<m:f><m:num>' + a + '</m:num><m:den>' + b + '</m:den></m:f>'
    yi = sub(r('y'), r('i'))
    xi = sub(r('x'), r('i'))
    summation = '<m:nary><m:naryPr><m:chr m:val="∑"/><m:limLoc m:val="undOvr"/></m:naryPr><m:sub>' + r('i=1') + '</m:sub><m:sup>' + r('N') + '</m:sup><m:e>' + sub(r('w'), yi) + r(' log ', upright=True) + sub(r('p'), r('θ')) + r('(') + yi + r(' | ') + xi + r('),') + '</m:e></m:nary>'
    script_l = '<m:r><m:rPr><m:scr m:val="script"/></m:rPr><m:t>L</m:t></m:r>'
    xml = '<m:oMathPara ' + nsdecls('m', 'w') + '><m:oMathParaPr><m:jc m:val="center"/></m:oMathParaPr><m:oMath>' + script_l + r(' = −') + frac(r('1'), r('N')) + summation + r('    ') + sub(r('w'), r('k')) + r(' = ') + frac(r('N'), r('3 ') + sub(r('N'), r('k'))) + r(',') + '</m:oMath></m:oMathPara>'
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = 0
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p._p.append(parse_xml(xml))


def build(source):
    doc = Document()
    configure(doc)
    source = source.replace('\r\n', '\n')
    source = re.sub(r'\A---\n.*?\n---\n', '', source, flags=re.S)
    source = re.sub(r'<!--.*?-->', '', source, flags=re.S)
    lines = source.splitlines()
    i, chapter, appendix, after_heading = 0, 0, False, False
    figures, tables, expected_blocks, table_layouts, left_code_paragraphs = [], [], [], [], []
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith(':::'):
            kind = line[3:].strip()
            j = i + 1
            while j < len(lines) and lines[j].strip() != ':::':
                j += 1
            content = lines[i + 1:j]
            if kind == 'titlepage':
                for raw in content:
                    header = raw in ['HANOI UNIVERSITY', 'FACULTY OF INFORMATION TECHNOLOGY', 'FINAL PROJECT REPORT']
                    p = doc.add_paragraph(style='Title' if raw.startswith('PREDICTING ') else 'Title Page Header' if header else 'Normal')
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    pf = p.paragraph_format
                    pf.first_line_indent = 0
                    pf.line_spacing = 1.15
                    pf.space_after = Pt(5)
                    title = raw.startswith('PREDICTING ')
                    size = (19 if title else 14 if raw in ['HANOI UNIVERSITY', 'FACULTY OF INFORMATION TECHNOLOGY', 'FINAL PROJECT REPORT'] or raw.startswith('Classical and transformer') else 13)
                    if raw == 'HANOI UNIVERSITY':
                        pf.space_before = Pt(18)
                    if raw.startswith('Hanoi,'):
                        pf.space_before = Pt(110 if CFG['paper'] else 155)
                    r = p.add_run(raw)
                    font(r, size, bold=title or header, italic=raw.startswith('Classical and transformer'))
                    expected_blocks.append(raw)
            elif kind in ('toc', 'lof', 'lot'):
                doc.add_paragraph(' '.join(content).strip(), 'Front Heading')
                p = doc.add_paragraph()
                p.paragraph_format.first_line_indent = 0
                instruction = ' TOC \\o "1-3" \\h \\z \\u ' if kind == 'toc' else f' TOC \\h \\z \\t "{"Figure" if kind == "lof" else "Table"} Caption,1" '
                field(p, instruction)
            elif kind != 'pagebreak':
                raise ValueError('Unknown source block: ' + kind)
            # All source breaks precede a new-page heading; avoid duplicate blank pages.
            i = j + 1
            continue
        hm = re.match(r'^(#{1,3}) (.*)', line)
        if hm:
            level, text = len(hm[1]), hm[2]
            unnumbered = '{.unnumbered}' in text
            is_appendix = '{.appendix}' in text
            text = re.sub(r'\s*\{\.(?:unnumbered|appendix)\}', '', text)
            if level == 1:
                appendix = is_appendix
                if appendix and text.startswith('Appendix A.'):
                    sec = doc.add_section(WD_SECTION_START.NEW_PAGE)
                    page_setup(sec)
                if text == 'Abstract':
                    sec = doc.add_section(WD_SECTION_START.NEW_PAGE)
                    page_setup(sec, page_format='decimal' if CFG['paper'] else 'lowerRoman')
                    footer(sec)
                if not unnumbered and not appendix:
                    chapter += 1
                    if chapter == 1 and not CFG['paper']:
                        sec = doc.add_section(WD_SECTION_START.NEW_PAGE)
                        page_setup(sec, page_format='decimal')
                        footer(sec)
                style = 'Appendix H1' if appendix else 'Unnumbered H1' if unnumbered else 'Heading 1'
            else:
                style = f'Appendix H{level}' if appendix else f'Heading {level}'
            p = doc.add_paragraph(style=style)
            h1, h2 = (14, 13) if CFG['paper'] else (16, 14)
            inline(p, text, h1 if level == 1 else h2 if level == 2 else 13, bold=True)
            if level == 3:
                for r in p.runs:
                    r.italic = True
            if not appendix and not unnumbered:
                np = el('w:numPr')
                np.extend([el('w:ilvl', val=level - 1), el('w:numId', val=50)])
                p._p.get_or_add_pPr().append(np)
            if text == 'Abstract' or chapter == 1 and text == 'Introduction' or text.startswith('Appendix A.'):
                p.paragraph_format.page_break_before = False
            expected_blocks.append(text)
            after_heading = True
            i += 1
            continue
        if line.startswith('```'):
            j = i + 1
            while not lines[j].startswith('```'):
                j += 1
            p = doc.add_paragraph()
            f = p.paragraph_format
            f.first_line_indent = 0
            f.line_spacing = 1
            f.space_before = f.space_after = Pt(6)
            f.alignment = WD_ALIGN_PARAGRAPH.LEFT
            f.keep_together = True
            pr = p._p.get_or_add_pPr()
            pr.append(el('w:shd', fill='F2F2F2'))
            border = el('w:pBdr')
            border.append(el('w:left', val='single', sz=4, color='A6A6A6', space=6))
            pr.append(border)
            code = '\n'.join(lines[i + 1:j])
            font(p.add_run(code), 10.5, 'Consolas')
            expected_blocks.append(code)
            i = j + 1
            continue
        if line.startswith('$$'):
            eq = line[2:]
            while '$$' not in eq:
                i += 1
                eq += '\n' + lines[i]
            equation(doc, eq.split('$$')[0])
            after_heading = True  # The following paragraph continues the equation's sentence.
            i += 1
            continue
        fm = re.fullmatch(r'!\[(.*?)\]\((.*?)\)', line)
        if fm:
            path = ROOT / fm[2]
            im = fitz.Pixmap(str(path))
            width = min(16, 18 * im.width / im.height)
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.first_line_indent = 0
            p.paragraph_format.keep_with_next = True
            p.paragraph_format.space_after = 0
            p.paragraph_format.line_spacing = 1
            p.add_run().add_picture(str(path), width=Cm(width))
            p._p.xpath('.//wp:docPr')[0].set('descr', fm[1])
            caption(doc, fm[1], 'Figure')
            figures.append(fm[1])
            expected_blocks.append(fm[1])
            after_heading = False
            i += 1
            continue
        # A caption is distinguished from a prose reference by its following table.
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        is_caption = line.startswith('Table') and re.match('^' + CAPTION_LABEL + ' ', line) and j < len(lines) and lines[j].startswith('|')
        if is_caption or line.startswith('|'):
            start = j if is_caption else i
            end = start
            while end < len(lines) and lines[end].startswith('|'):
                end += 1
            label = re.match(CAPTION_LABEL, line)[0].rstrip('.') if is_caption else 'Abbreviations'
            layout = table_layout(lines[start:end], label)
            table_layouts.append(layout)
            landscape = layout['landscape']
            if landscape and doc.sections[-1].page_width < doc.sections[-1].page_height:
                sec = doc.add_section(WD_SECTION_START.NEW_PAGE)
                page_setup(sec, landscape=True)
            if is_caption:
                caption(doc, line, 'Table')
                tables.append(line)
                expected_blocks.append(line)
            t = make_table(doc, layout)
            expected_blocks.extend('\t'.join(table_cells(v)) for k, v in enumerate(lines[start:end]) if k != 1)
            j = end
            while j < len(lines) and not lines[j].strip():
                j += 1
            while j < len(lines) and lines[j].startswith('¹'):
                note = lines[j].strip()
                p = doc.add_paragraph(style='Table Note')
                inline(p, note, 11)
                expected_blocks.append(note)
                for cell in t.rows[-1].cells:
                    cell.paragraphs[-1].paragraph_format.keep_with_next = True
                j += 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                end = j
            table_gap(doc)
            if landscape:
                sec = doc.add_section(WD_SECTION_START.NEW_PAGE)
                page_setup(sec)
            after_heading = False
            i = end
            continue
        # Paragraphs in this source are separated by blank lines; preserve soft wraps.
        parts = [line]
        if not re.match(r'^(?:- |\d+\. )', line):
            while i + 1 < len(lines) and lines[i + 1].strip() and not re.match(r'^(?:#|:::|\||!\[|```|\$\$|- |\d+\. )', lines[i + 1]):
                i += 1
                parts.append(lines[i].strip())
        text = ' '.join(parts)
        p = doc.add_paragraph()
        lm = re.match(r'^(- |\d+\. )(.*)', text)
        if lm:
            p.paragraph_format.left_indent = Cm(.75)
            p.paragraph_format.first_line_indent = Cm(-.75)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.tab_stops.add_tab_stop(Cm(.75))
            text = ('•' if lm[1] == '- ' else lm[1].strip()) + '\t' + lm[2]
        elif after_heading:
            p.paragraph_format.first_line_indent = 0
        if any(len(code) > 20 for code in re.findall(r'`([^`]+)`', text)):
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            left_code_paragraphs.append(text.replace('`', ''))
        inline(p, text)
        expected_blocks.append(text)
        after_heading = False
        i += 1
    assert chapter == CFG['chapters'] and len(figures) == CFG['figures'], (chapter, len(figures))
    doc.core_properties.title = 'Predicting the Effectiveness of Argumentative Discourse Units in Student Essays'
    doc.core_properties.author = 'Group 06 · CLC02'
    doc.settings.element.append(el('w:updateFields', val='true'))
    doc.settings.element.append(el('w:embedTrueTypeFonts'))
    doc.save(DOCX)
    return {'figures': figures, 'table_captions': tables, 'expected_blocks': expected_blocks,
            'table_layouts': table_layouts, 'left_code_paragraphs': left_code_paragraphs}


def word_export():
    pythoncom.CoInitialize()
    word = doc = None
    try:
        word = win32com.client.DispatchEx('Word.Application')
        word.Visible = False
        word.DisplayAlerts = 0
        doc = word.Documents.Open(str(DOCX), ConfirmConversions=False, ReadOnly=False, AddToRecentFiles=False)
        doc.EmbedTrueTypeFonts = True
        doc.SaveSubsetFonts = True
        doc.DoNotEmbedSystemFonts = False
        for _ in range(2):
            doc.Repaginate()
            doc.Fields.Update()
            for toc in doc.TablesOfContents:
                toc.Update()
                # Word copies direct caption emphasis into LOF/LOT field results.
                f = toc.Range.Font
                f.Name = TNR
                f.Size = 13
                f.Bold = 0
                f.Italic = 0
                f.Underline = 0
                f.Color = 0
                toc.Range.ParagraphFormat.FirstLineIndent = 0
                toc.Range.ParagraphFormat.Alignment = 0
                toc.Range.ParagraphFormat.SpaceAfter = 3
            for sec in doc.Sections:
                sec.Footers(1).Range.Fields.Update()
            doc.Repaginate()
        for toc in doc.TablesOfContents:
            toc.UpdatePageNumbers()
        doc.Save()
        headings = []
        for p in doc.Paragraphs:
            if p.OutlineLevel <= 3:
                headings.append({'text': p.Range.Text.strip('\r\x07'),
                                 'number': p.Range.ListFormat.ListString.strip(),
                                 'page': p.Range.Information(3)})
        contents = [{'text': t.Range.Text, 'entries': t.Range.Paragraphs.Count} for t in doc.TablesOfContents]
        figure_pages = []
        for shape in doc.InlineShapes:
            image_page = shape.Range.Information(3)
            cap = shape.Range.Paragraphs(1).Next().Range
            cap.End -= 1
            figure_pages.append([image_page, cap.Information(3)])
        header_pages = [[t.Rows(1).Range.Information(3), t.Rows(2).Range.Information(3)]
                        for t in doc.Tables if t.Rows.Count > 1]
        table_pages = [[t.Rows(1).Range.Information(3), t.Range.Information(3)] for t in doc.Tables]
        doc.ExportAsFixedFormat(str(PDF), 17, OpenAfterExport=False, OptimizeFor=0,
                                Range=0, Item=0, IncludeDocProps=True, KeepIRM=True,
                                CreateBookmarks=1, DocStructureTags=True,
                                BitmapMissingFonts=True, UseISO19005_1=True)
        return {'headings': headings, 'contents_fields': contents,
                'figure_caption_pages': figure_pages, 'table_header_first_row_pages': header_pages,
                'table_pages': table_pages}
    finally:
        try:
            if doc is not None:
                doc.Close(SaveChanges=False)
        finally:
            try:
                if word is not None:
                    word.Quit()
            finally:
                pythoncom.CoUninitialize()


def split_words(source, rendered):
    """Compare source word boundaries with actual PDF line boundaries."""
    plain = source.replace('`', '')
    expected = re.sub(r'\s', '', plain)
    chars = [(c, line) for line, text in enumerate(rendered.splitlines())
             for c in text if not c.isspace()]
    actual = ''.join(c for c, _ in chars)
    if actual != expected:
        return [], {'expected': plain, 'actual': rendered}
    errors, pos = [], 0
    for index, part in enumerate(source.split('`')):
        if index % 2 == 0:
            for match in re.finditer(r'\w+(?:[’\']\w+)*', part):
                start = pos + len(re.sub(r'\s', '', part[:match.start()]))
                length = len(match[0])
                if len({line for _, line in chars[start:start + length]}) > 1:
                    errors.append(match[0])
        pos += len(re.sub(r'\s', '', part))
    return errors, None


def path_line_counts(source, rendered):
    lines = [line for line, text in enumerate(rendered.splitlines()) for c in text if not c.isspace()]
    result, pos = [], 0
    for index, part in enumerate(source.split('`')):
        if index % 2:
            for token in re.finditer(r'[^,\s]+', part):
                if not re.search(r'[/\\]|\.[a-zA-Z]\w*\b', token[0]):
                    continue
                start = pos + len(re.sub(r'\s', '', part[:token.start()]))
                result.append({'path': token[0], 'lines': len(set(lines[start:start + len(token[0])]))})
        pos += len(re.sub(r'\s', '', part))
    return result


def pdf_table_checks(pdf, layouts, table_pages):
    # Check only Word's table pages, and match complete rows to their source.
    # A text mismatch is a failure, never an excuse to skip a cell.
    def key(text):
        return re.sub(r'\s', '', text.replace('`', ''))
    headers = {tuple(key(v) for v in t['rows'][0]): i for i, t in enumerate(layouts)}
    assert len(headers) == len(layouts), 'Ambiguous table headers in source'
    seen, errors, mismatches = set(), [], []
    path_breaks, path_maximums, body_line_maximums = [], {}, {}
    checked_cells = 0
    indices = sorted({p - 1 for start, end in table_pages for p in range(start, end + 1)})
    for pi in indices:
        page = pdf[pi]
        glyphs = [(c['c'], c['bbox'], span['origin'][1])
                  for b in page.get_text('rawdict')['blocks'] if b['type'] == 0
                  for line in b['lines'] for span in line['spans'] for c in span['chars']]
        def cell_text(box):
            x0, y0, x1, y1 = box
            baselines = []
            for char, bounds, baseline in glyphs:
                cx, cy = (bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2
                if not (x0 <= cx < x1 and y0 <= cy < y1):
                    continue
                group = next((v for v in baselines if abs(v[0] - baseline) < 1), None)
                if group is None:
                    group = [baseline, []]
                    baselines.append(group)
                group[1].append((bounds[0], char))
            # Underscores have a lower glyph box but share the text baseline.
            return '\n'.join(''.join(c for _, c in sorted(chars))
                             for _, chars in sorted(baselines))
        detected = page.find_tables(clip=fitz.Rect(80, 65, page.rect.width - 50, page.rect.height - 65),
                                    strategy='lines_strict', snap_tolerance=5, join_tolerance=5)
        for table in detected.tables:
            values = [[cell_text(box) if box else '' for box in row.cells] for row in table.rows]
            if not values:
                continue
            ti = headers.get(tuple(key(v or '') for v in values[0]))
            if ti is None:
                continue  # Figure grids are not report tables.
            layout = layouts[ti]
            rows = {tuple(key(v) for v in row): ri for ri, row in enumerate(layout['rows'])}
            for row, geometry in zip(values, table.rows):
                ri = rows.get(tuple(key(v or '') for v in row))
                if ri is None:
                    mismatches.append({'table': layout['label'], 'page': pi + 1, 'row': row})
                    continue
                seen.add((ti, ri))
                for ci, box in enumerate(geometry.cells):
                    if box is None:
                        mismatches.append({'table': layout['label'], 'page': pi + 1, 'empty_geometry': ci})
                        continue
                    rendered = row[ci]
                    if ri:
                        maxima = body_line_maximums.setdefault(layout['label'], [0] * len(row))
                        maxima[ci] = max(maxima[ci], len([v for v in rendered.splitlines() if v.strip()]))
                    words, mismatch = split_words(layout['rows'][ri][ci], rendered)
                    checked_cells += 1
                    if words:
                        errors.append({'table': layout['label'], 'page': pi + 1, 'row': ri,
                                       'column': ci, 'words': words, 'rendered': rendered})
                    if mismatch:
                        mismatches.append({'table': layout['label'], 'page': pi + 1,
                                           'row': ri, 'column': ci, **mismatch})
                    else:
                        for path in path_line_counts(layout['rows'][ri][ci], rendered):
                            path_maximums[layout['label']] = max(path_maximums.get(layout['label'], 0), path['lines'])
                            if path['lines'] > 3:
                                path_breaks.append({'table': layout['label'], 'page': pi + 1,
                                                    'row': ri, 'column': ci, **path})
    missing = [{'table': t['label'], 'row': ri} for ti, t in enumerate(layouts)
               for ri in range(len(t['rows'])) if (ti, ri) not in seen]
    return {'mid_word_breaks': errors, 'table_pdf_text_mismatches': mismatches,
            'table_pdf_unverified_rows': missing, 'table_pdf_checked_cells': checked_cells,
            'code_paths_over_three_lines': path_breaks, 'code_path_max_lines_by_table': path_maximums,
            'table_body_max_lines_by_column': body_line_maximums}


def validate(manifest, word_info, source_hash):
    doc = Document(DOCX)
    pdf = fitz.open(PDF)
    temp = Path(tempfile.mkdtemp(prefix='MLA-report-QA-'))
    print(f'Rendering {len(pdf)} pages at 80 dpi to {temp}', flush=True)
    pages = []
    bounds = []
    for i, page in enumerate(pdf):
        page.get_pixmap(dpi=80).save(temp / f'page-{i + 1:03}.png')
        pages.append(page.get_text())
        for block in page.get_text('rawdict')['blocks']:
            if block['type'] != 0:
                continue
            for line in block['lines']:
                for span in line['spans']:
                    chars = [c for c in span['chars'] if c['c'].strip()]
                    if not chars:
                        continue
                    x0, y0 = min(c['bbox'][0] for c in chars), min(c['bbox'][1] for c in chars)
                    x1, y1 = max(c['bbox'][2] for c in chars), max(c['bbox'][3] for c in chars)
                    # Footers are outside the body rectangle by design.
                    if y0 < page.rect.height - 65 and (x0 < 84 or x1 > page.rect.width - 55.5):
                        bounds.append({'page': i + 1, 'text': ''.join(c['c'] for c in span['chars']), 'bbox': [x0, y0, x1, y1]})
    all_paras = [Paragraph(node, doc._body) for node in doc.element.body.xpath('.//w:p')]
    text = '\n'.join(p.text for p in all_paras)
    raw_markdown = {s: text.count(s) for s in ['**', ':::', '$$', '{.unnumbered}', '{.appendix}', '![', '|---']}
    bold_errors, font_errors = [], []
    default_rp = doc.styles.element.find(qn('w:docDefaults')).find(qn('w:rPrDefault')).find(qn('w:rPr'))
    def effective(r, p, attr):
        value = getattr(r.font, attr)
        if value is not None:
            return value
        for start in (r.style, p.style):
            s = start
            while s is not None:
                value = getattr(s.font, attr)
                if value is not None:
                    return value
                s = s.base_style
        if attr == 'name':
            return default_rp.find(qn('w:rFonts')).get(qn('w:ascii'))
        if attr == 'size':
            return Pt(int(default_rp.find(qn('w:sz')).get(qn('w:val'))) / 2)
        return False if attr in ('bold', 'italic') else None

    # Word removes redundant direct formatting on save; resolve style inheritance.
    for p in all_paras:
        style = p.style.name
        in_table = bool(p._p.xpath('ancestor::w:tc'))
        is_header = bool(p._p.xpath('ancestor::w:tr/w:trPr/w:tblHeader'))
        heading = 'Heading' in style or re.match(r'(Unnumbered|Appendix) H[123]', style)
        label = re.match(CAPTION_LABEL, p.text) if style.endswith('Caption') else None
        offset = 0
        for r in p.runs:
            if not r.text:
                continue
            allowed = heading or is_header or style in ('Title', 'Title Page Header') or (label and offset + len(r.text) <= label.end())
            offset += len(r.text)
            name, size = effective(r, p, 'name'), effective(r, p, 'size')
            if effective(r, p, 'bold') and not allowed:
                bold_errors.append(r.text)
            if name not in (TNR, 'Consolas'):
                font_errors.append([style, r.text[:50], name])
            if style == 'Normal' and not in_table and name == TNR and size != Pt(13):
                # Only the centred title-page lines have intentional size exceptions.
                if p.alignment != WD_ALIGN_PARAGRAPH.CENTER:
                    font_errors.append([style, r.text[:50], str(size)])
            rf = r._r.xpath('./w:rPr/w:rFonts')
            for slot in ('ascii', 'hAnsi', 'eastAsia', 'cs'):
                values = []
                if rf:
                    values.append(rf[0].get(qn('w:' + slot)))
                s = p.style
                while s is not None:
                    nodes = s.element.xpath('./w:rPr/w:rFonts')
                    if nodes:
                        values.append(nodes[0].get(qn('w:' + slot)))
                    s = s.base_style
                values.append(default_rp.find(qn('w:rFonts')).get(qn('w:' + slot)))
                value = next((v for v in values if v is not None), None)
                if value != name:
                    font_errors.append(['font slot ' + slot, r.text[:50], value, name])
    body = doc.element.body
    table_positions = []
    for t in doc.tables:
        prev = t._tbl.getprevious()
        txt = ''.join(prev.itertext()) if prev is not None else ''
        # Only the abbreviations table is intentionally uncaptioned.
        table_positions.append(bool(prev is not None and prev.tag == qn('w:p') and prev.xpath('./w:pPr/w:pStyle[@w:val="TableCaption"]')))
    shape_checks = []
    for shape in doc.inline_shapes:
        p = shape._inline.xpath('ancestor::w:p')[0]
        nxt = p.getnext()
        shape_checks.append(bool(nxt is not None and nxt.xpath('./w:pPr/w:pStyle[@w:val="FigureCaption"]')))
    width_errors = []
    landscape_count = 0
    for t in doc.tables:
        following = t._tbl.getnext()
        while following is not None and not (following.tag == qn('w:sectPr') or following.xpath('./w:pPr/w:sectPr')):
            following = following.getnext()
        sec = following if following.tag == qn('w:sectPr') else following.xpath('./w:pPr/w:sectPr')[0]
        w = int(sec.find(qn('w:pgSz')).get(qn('w:w')))
        mar = sec.find(qn('w:pgMar'))
        available = w - int(mar.get(qn('w:left'))) - int(mar.get(qn('w:right')))
        actual = sum(int(c.get(qn('w:w'))) for c in t._tbl.tblGrid)
        if actual > available + 3:
            width_errors.append([actual, available])
    for sec in doc.sections:
        landscape_count += int(sec.page_width > sec.page_height)
    expected_numbers = {}
    for prefix, expected in ({} if CFG['paper'] else EXPECTED_HEADINGS).items():
        found = [h for h in word_info['headings'] if h['text'].startswith(prefix)]
        expected_numbers[prefix] = {'expected': expected, 'actual': found[0]['number'] if len(found) == 1 else found,
                                    'pass': len(found) == 1 and found[0]['number'] == expected}
    needles = ['Table of Contents', 'List of Figures', 'List of Tables', 'Table 5.2.', 'Table 6.5.',
               'Table 6.7.', 'Table 6.10.', 'Table 7.4.', 'Table F.2.', 'Architecture and loss',
               'B.3 Commands', 'Figure 3.1.', 'Figure 6.4.']
    locations = {s: [i + 1 for i, text in enumerate(pages) if s in text] for s in needles}
    source_images = re.findall(r'^!\[.*?\]\((.*?)\)', (ROOT / CFG['source']).read_text(encoding='utf-8'), re.M)
    image_bytes_match = []
    for shape, path in zip(doc.inline_shapes, source_images):
        rel = shape._inline.xpath('.//a:blip')[0].get(qn('r:embed'))
        image_bytes_match.append(doc.part.related_parts[rel].blob == (ROOT / path).read_bytes())
    pdf_fonts = {item[0] for page in pdf for item in page.get_fonts()}
    table_pdf = pdf_table_checks(pdf, manifest['table_layouts'], word_info['table_pages'])
    table_notes = [p for p in doc.paragraphs if p.style.name == 'Table Note']
    note_checks = []
    note_page_checks = []
    for p in table_notes:
        previous = p._p.getprevious()
        note_checks.append(previous is not None and previous.tag == qn('w:tbl')
                           and p.paragraph_format.first_line_indent in (None, 0)
                           and all(effective(r, p, 'size') == Pt(11) for r in p.runs if r.text))
        ti = len(p._p.xpath('preceding-sibling::w:tbl')) - 1
        needle = re.sub(r'\s', '', p.text[:60])
        found = [i + 1 for i, value in enumerate(pages) if needle in re.sub(r'\s', '', value)]
        note_page_checks.append(found == [word_info['table_pages'][ti][1]])
    gap_checks = []
    for t in doc.tables:
        nxt = t._tbl.getnext()
        while nxt is not None and nxt.xpath('./w:pPr/w:pStyle[@w:val="TableNote"]'):
            nxt = nxt.getnext()
        gap_checks.append(nxt is not None and bool(nxt.xpath('./w:pPr/w:spacing[@w:line="160"]')))
    # Content assertion compares every parsed paragraph/cell with the saved OOXML.
    def plain(s):
        return re.sub(r'\s+', ' ', s.replace('`', '')).strip()
    saved_text = plain(text)
    missing = [v for v in manifest['expected_blocks'] if plain(v) and plain(v) not in saved_text]
    left_code_errors = [value for value in manifest['left_code_paragraphs']
                        if not any(plain(p.text) == plain(value) and p.alignment == WD_ALIGN_PARAGRAPH.LEFT
                                   for p in doc.paragraphs)]
    equation_paragraph = next(p for p in doc.paragraphs if p._p.xpath('./m:oMathPara'))
    continuation = Paragraph(equation_paragraph._p.getnext(), doc._body)
    # Table cells are separate paragraphs, so tabs in expected rows become spaces.
    result = {
        'pdf_pages': len(pdf), 'qa_png_folder': str(temp),
        'source_sha256': source_hash,
        'raw_markdown': raw_markdown,
        'figures': len(doc.inline_shapes), 'figure_captions': len([p for p in doc.paragraphs if p.style.name == 'Figure Caption']),
        'table_captions': len(manifest['table_captions']), 'tables_including_abbreviations': len(doc.tables),
        'caption_positions_pass': all(table_positions[1:]) and all(shape_checks),
        'figure_caption_same_page_pass': all(a == b for a, b in word_info['figure_caption_pages']),
        'no_orphan_table_headers_pass': all(a == b for a, b in word_info['table_header_first_row_pages']),
        'native_equations': len(body.xpath('.//m:oMath')),
        'equation_log_upright': bool(body.xpath('.//m:r[m:t=" log "]/m:rPr/m:sty[@m:val="p"]')),
        'equation_continuation_no_indent': continuation.paragraph_format.first_line_indent == 0,
        'long_code_paragraphs_left_aligned': len(manifest['left_code_paragraphs']),
        'long_code_alignment_errors': left_code_errors,
        'bold_errors': bold_errors, 'font_errors': font_errors,
        'table_width_errors': width_errors,
        'image_widths_pass': all(s.width <= Cm(16) + 2 for s in doc.inline_shapes),
        'original_image_bytes_preserved': len(image_bytes_match) == CFG['figures'] and all(image_bytes_match),
        'repeated_table_headers_pass': all(t.rows[0]._tr.xpath('./w:trPr/w:tblHeader') for t in doc.tables),
        'no_split_rows_pass': all(r._tr.xpath('./w:trPr/w:cantSplit') for t in doc.tables for r in t.rows),
        'landscape_sections': landscape_count,
        'landscape_tables': [t['label'] for t in manifest['table_layouts'] if t['landscape']],
        'table_layouts': manifest['table_layouts'],
        'table_notes_pass': len(table_notes) == CFG['notes'] and all(note_checks) and all(note_page_checks),
        'table_spacing_pass': all(gap_checks),
        'arial_fonts': sorted({item[3] for page in pdf for item in page.get_fonts() if 'arial' in item[3].lower()}),
        **table_pdf,
        'heading_cross_references': expected_numbers,
        'contents_field_count': len(word_info['contents_fields']),
        'contents_entries': [v['entries'] for v in word_info['contents_fields']],
        'contents_have_page_numbers': [bool(re.search(r'\t(?:\d+|[ivxlcdm]+)\r', v['text'])) for v in word_info['contents_fields']],
        'bookmark_error': 'Error! Bookmark not defined' in text + '\n'.join(pages),
        'pdf_bookmarks': len(pdf.get_toc()),
        'pdf_fonts_embedded': all(bool(pdf.extract_font(xref)[3]) for xref in pdf_fonts),
        'blank_pdf_pages': [i + 1 for i, text in enumerate(pages) if len(text.strip()) < 10],
        'content_blocks_missing': missing,
        'text_outside_horizontal_margins': bounds,
        'sample_page_locations': locations,
        'word': word_info,
    }
    result['main_text_pages'] = main_text_pages(word_info)
    (OUT / CFG['checks_name']).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    summary = {k: v for k, v in result.items() if k not in ('word', 'table_layouts', 'text_outside_horizontal_margins', 'content_blocks_missing')}
    summary['content_blocks_missing_count'] = len(missing)
    summary['text_outside_horizontal_margins_count'] = len(bounds)
    for key in ('font_errors', 'bold_errors', 'mid_word_breaks', 'table_pdf_text_mismatches', 'table_pdf_unverified_rows', 'code_paths_over_three_lines'):
        summary[key + '_count'] = len(summary[key])
        summary[key] = summary[key][:8]
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    return result


def main_text_pages(word_info):
    """Pages from the Abstract (paper) or Chapter 1 (thesis) up to, not including, the References page."""
    heads = word_info['headings']
    start = next((h['page'] for h in heads if h['text'] == ('Abstract' if CFG['paper'] else 'Introduction')), None)
    end = next((h['page'] for h in heads if h['text'] == 'References'), None)
    return {'from_page': start, 'references_page': end,
            'pages_before_references': (end - start) if start and end else None}


def configure_run():
    import argparse
    global STEM, DOCX, PDF
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--paper', action='store_true', help='build the short main paper from paper/PAPER.md')
    if ap.parse_args().paper:
        CFG.update({'source': 'paper/PAPER.md', 'figures': 2, 'chapters': 7, 'contents': 0, 'notes': 1,
                    'paper': True, 'checks_name': 'build_checks_paper.json'})
        STEM = 'Group06_CLC02_Final_Paper'
        DOCX, PDF = OUT / (STEM + '.docx'), OUT / (STEM + '.pdf')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    configure_run()
    assert split_words('Counterclaim', 'Countercl\naim')[0] == ['Counterclaim']
    assert split_words('`long_identifier`', 'long_iden\ntifier') == ([], None)
    assert split_words('Training file', 'Training\nfile') == ([], None)
    assert path_line_counts('`outputs/a.csv`', 'out\nputs/\na.\ncsv')[0]['lines'] == 4
    OUT.mkdir(exist_ok=True)
    path = ROOT / CFG['source']
    data = path.read_bytes()
    source_hash = hashlib.sha256(data).hexdigest()
    print('Building DOCX from unchanged Markdown', flush=True)
    manifest = build(data.decode('utf-8-sig'))
    print('Updating Word fields twice and exporting PDF', flush=True)
    word_info = word_export()
    result = validate(manifest, word_info, source_hash)
    assert path.read_bytes() == data, 'Source changed during build'
    assert result['figures'] == result['figure_captions'] == CFG['figures']
    assert not any(result['raw_markdown'].values()), 'Unconverted Markdown'
    assert result['caption_positions_pass'] and result['image_widths_pass']
    assert result['figure_caption_same_page_pass'] and result['no_orphan_table_headers_pass']
    assert not result['bold_errors'] and not result['font_errors']
    assert not result['table_width_errors'] and not result['content_blocks_missing']
    assert all(v['pass'] for v in result['heading_cross_references'].values())
    assert result['contents_field_count'] == CFG['contents'] and all(result['contents_have_page_numbers'])
    assert not result['bookmark_error']
    assert result['original_image_bytes_preserved'] and result['pdf_fonts_embedded']
    assert not result['text_outside_horizontal_margins'] and not result['blank_pdf_pages']
    assert result['table_notes_pass'] and not result['arial_fonts']
    assert result['table_spacing_pass'] and result['equation_log_upright']
    assert not result['mid_word_breaks'] and not result['table_pdf_text_mismatches']
    assert not result['table_pdf_unverified_rows']
    assert not result['code_paths_over_three_lines'] and not result['long_code_alignment_errors']
    assert result['equation_continuation_no_indent']
    print('Main-text pages:', result['main_text_pages'], flush=True)
    print('Structural checks passed. Review the rendered PNGs before delivery.', flush=True)


if __name__ == '__main__':
    main()
