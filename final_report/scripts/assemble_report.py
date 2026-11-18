"""Concatenate report_src/*.md into FINAL_REPORT.md and check figure/table numbering and image paths."""
import glob, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
FR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
parts = sorted(glob.glob(os.path.join(FR, "report_src", "*.md")))
text = "\n\n".join(open(p, encoding="utf-8").read().strip() for p in parts) + "\n"
open(os.path.join(FR, "FINAL_REPORT.md"), "w", encoding="utf-8").write(text)
ok = True
for img in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text):
    if not os.path.exists(os.path.join(FR, img)):
        print("MISSING IMAGE", img); ok = False
for kind, pat in (("Figure", r"!\[Figure (\d+)\.(\d+)\."), ("Table", r"^Table ([A-G0-9]+)\.(\d+)\.")):
    seen = {}
    for a, b in re.findall(pat, text, flags=re.M):
        seen.setdefault(a, []).append(int(b))
    for a, nums in seen.items():
        if nums != list(range(1, len(nums) + 1)):
            print(f"{kind} numbering in chapter {a}: {nums}"); ok = False
    print(kind, {a: len(v) for a, v in seen.items()})
print("words:", len(re.findall(r"\w+", text)), "| OK" if ok else "| PROBLEMS")
