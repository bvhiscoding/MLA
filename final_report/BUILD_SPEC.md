# Build specification: Word + PDF of the final report

Audience: the worker that converts `FINAL_REPORT.md` into a formal academic Word document and PDF.
Do not change the wording, numbers, tables or figures of the report. Only convert and format. If something in the source cannot be rendered faithfully, report it rather than rewriting it.

## Inputs and outputs

- Source: `final_report/FINAL_REPORT.md` (assembled from `final_report/report_src/*.md` by `python final_report/scripts/assemble_report.py`; edit the files in `report_src/`, never `FINAL_REPORT.md` directly).
- Images: `final_report/figures/*.png` (300 dpi), referenced with paths relative to `final_report/`.
- Outputs: `final_report/output/Group06_CLC02_Final_Report.docx` and `final_report/output/Group06_CLC02_Final_Report.pdf`.
- Put the build script in `final_report/scripts/build_docx_pdf.py` (and any reference template in `final_report/template/`) so the build can be rerun with one command.

## Source conventions to convert

| Markdown in the source | Word output |
|---|---|
| YAML block at the top | Metadata only; do not print it |
| `::: titlepage` … `:::` | A separate, centred title page (see below); no page number shown |
| `::: pagebreak` / `:::` | Page break |
| `::: toc` | Table of contents (Word TOC field, heading levels 1–3, with page numbers and dot leaders) |
| `::: lof` / `::: lot` | List of Figures / List of Tables (Word TOC fields built from the figure-caption and table-caption styles, e.g. `TOC \h \z \t "Figure Caption,1"`) |
| `# Heading {.unnumbered}` | Level-1 heading without a chapter number (Abstract, List of Abbreviations, References) |
| `# Heading {.appendix}` | Appendix heading, printed as written ("Appendix A. Run Table"), not numbered as a chapter |
| `# Heading` | Chapter: "CHAPTER 1" on one line and "INTRODUCTION" on the next, or "CHAPTER 1. INTRODUCTION"; starts on a new page |
| `## Heading`, `### Heading` | Numbered "1.1 …", "1.1.1 …" (automatic multilevel numbering tied to the chapter; appendix sub-headings as A.1, A.2 …) |
| A paragraph starting `Table X.Y.` immediately before a pipe table | Table caption, above the table |
| `![Figure X.Y. caption](figures/…png)` | Centred picture with the caption below it |
| Pipe tables | Word tables (see Tables) |
| `$$ … $$` | Display equation as a native Word equation (OMML), centred |
| `` `code` `` | Inline code (see Fonts) |
| Fenced code block | Shaded code block (Appendix B commands) |
| `[text in brackets]` placeholders (names, student IDs) | Keep exactly as written; the group fills them in |

Section numbers used in cross-references in the text ("Section 4.3.3", "Table 6.5", "Figure 7.2") were written for this numbering scheme: chapters 1–9 in order, sections numbered in order of appearance. Check that the automatic heading numbers match these references (for example, "Context representations" must come out as 4.3.3 and "Ten high-confidence Ineffective failures" as 7.3). Figure and table numbers are already written into the captions; keep them as text.

## Page setup

- A4 portrait. Margins: top 2.5 cm, bottom 2.5 cm, left 3.0 cm, right 2.0 cm. Header 1.25 cm, footer 1.25 cm.
- A4 portrait on every page; no landscape sections. Wide tables are set in 10–10.5 pt (down to 8.5 pt if needed) and must fit the 16 cm text width; if a table still does not fit, reduce columns in the source.
- Page numbers centred in the footer, Times New Roman 12 pt. Title page: no number. Front matter (Abstract to List of Abbreviations): lower-case Roman numerals (i, ii, …). From Chapter 1 to the end: Arabic numerals starting at 1.
- Optional running header from Chapter 1 on: "Group 06 · Discourse effectiveness on PERSUADE 2.0", Times New Roman 10 pt, right-aligned, thin bottom border.

## Fonts and paragraphs

- Everything in Times New Roman, including headings, tables, captions, footnotes and the TOC. Set it for the East Asian and complex-script slots as well, so Vietnamese diacritics in names render in Times New Roman.
- Body text: 13 pt, justified, line spacing 1.3 (multiple), 0 pt before, 6 pt after, first-line indent 1.0 cm. No first-line indent for the paragraph directly after a heading, in table cells, captions, list items or the title page.
- Lists: 13 pt, hanging indent, same line spacing, 3 pt after each item.
- Inline code and file paths: Consolas 11 pt, no shading, not bold. Code block: Consolas 10.5 pt, single spacing, light grey shading (F2F2F2), thin left border, 6 pt before and after.
- Equations: Cambria Math is acceptable inside the equation object only.

## Bold and emphasis (important)

The lecturer asked for a formal look with no arbitrary bold. Use bold only for:
1. headings (chapter, section, subsection titles);
2. the label part of a caption ("Table 3.4." / "Figure 6.2."), with the caption text itself in regular weight;
3. the header row of tables;
4. the report title on the title page.

Do not bold anything in body paragraphs, list items or table bodies, even if it looks like a key number. Do not add underline or colour to text. Italics only where the source uses `*…*` (it rarely does). Hyperlinks/DOIs in the reference list: black, not underlined.

## Headings

| Level | Format |
|---|---|
| Chapter (H1) | 16 pt, bold, all caps, centred, 0 pt before (new page), 18 pt after |
| Unnumbered H1 (Abstract, Abbreviations, References) and appendix H1 | 16 pt, bold, centred, new page |
| Section (H2) | 14 pt, bold, left, 12 pt before, 6 pt after, keep with next |
| Subsection (H3) | 13 pt, bold italic, left, 10 pt before, 4 pt after, keep with next |

## Tables

- Caption above the table: 12 pt, centred (or left-aligned for very wide tables), keep with next, 6 pt before, 3 pt after.
- Table text 11 pt (10–10.5 pt for wide tables), single line spacing, 2 pt cell padding top/bottom. Header row bold, light grey fill (D9D9D9 or E7E6E6), repeated on every page. Thin (0.5 pt) black horizontal rules; either a full thin grid or a three-line academic style (top rule, rule under the header, bottom rule) — pick one style and use it for every table.
- Numeric columns right-aligned or centred as in the Markdown alignment row; text columns left-aligned. Fit tables to the text width (autofit to window); do not let any table run off the page. Do not split a row across pages.
- Table F.2 and other long tables may break across pages; the header row must repeat.

## Figures

- Centre each image; width = text width (about 16 cm) for wide figures, less for narrow ones (diagrams that are tall, such as Figure 3.1, at most 75% of the page height). Never upscale beyond the text width; keep aspect ratio.
- Caption below the figure: 12 pt, centred, label bold, text regular; keep the image with its caption on the same page.

## Title page

Centred, Times New Roman. Suggested sizes: university and faculty 14 pt bold caps; course line 13 pt; "FINAL PROJECT REPORT" 14 pt bold; the title 18–20 pt bold caps; subtitle 14 pt italic; class, group, lecturer 13 pt; the member placeholder lines 13 pt; "Hanoi, November 2026" at the bottom, 13 pt. Use vertical spacing to fill the page; no logo is required (do not invent one).

## Front matter order

Title page → Abstract → Table of Contents → List of Figures → List of Tables → List of Abbreviations → Chapter 1 … Chapter 9 → References → Appendices A–G.

## PDF

- Update all fields (TOC, List of Figures, List of Tables, page numbers) before saving the .docx, then export the PDF with Microsoft Word (installed on this machine; e.g. `win32com.client` → `Document.ExportAsFixedFormat`, with bookmarks created from headings). Fields must be updated in the saved .docx too, so the TOC is not empty when opened.
- Embed fonts if possible.

## Checks before finishing (do all of them and report the results)

1. Render every PDF page to PNG at about 80 dpi (PyMuPDF is installed) and look at a sample of at least 15 pages covering: title page, TOC, List of Figures, a chapter opening, a page with a wide table (Tables 5.2, 6.5, 6.7, 6.10, 7.4, F.2), a page with a figure, the equation in Section 4.3.1, Appendix B code block, and the last page.
2. No raw Markdown remains anywhere in the document: search the docx text for `**`, `::: `, `$$`, `{.unnumbered}`, `{.appendix}`, `![`, `|---`.
3. Every one of the 27 figures appears exactly once, with its caption; every table caption is above its table.
4. TOC, List of Figures and List of Tables are populated with correct page numbers; no "Error! Bookmark not defined".
5. No table or figure exceeds the margins; no table header row is orphaned at a page bottom.
6. Body font is Times New Roman 13 pt throughout; no bold runs in body paragraphs (scan runs with python-docx and report any bold run outside headings, captions labels and table header rows).
7. Report the page count and the list of any issues that could not be fixed.
