"""One-command demo: python demo.py  (works on a temp copy of threads/)"""
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from threadnotes.__main__ import main  # noqa: E402

d = os.path.join(tempfile.mkdtemp(prefix="threadnotes-demo-"), "threads")
shutil.copytree(os.path.join(ROOT, "threads"), d)

print("$ python -m threadnotes check")
main(["check", d])
print("\n$ python -m threadnotes index")
main(["index", d])
print()
print(open(os.path.join(d, "INDEX.md"), encoding="utf-8").read())
print("$ python -m threadnotes view")
main(["view", d])
