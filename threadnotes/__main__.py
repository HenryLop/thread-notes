"""python -m threadnotes check|index|view [DIR]   (DIR defaults to ./threads)"""
import os
import sys

from threadnotes import core


def main(argv=None):
    argv = argv or sys.argv[1:]
    cmd = argv[0] if argv else "check"
    d = argv[1] if len(argv) > 1 else "threads"
    notes = core.load(d)
    if cmd == "check":
        bad = 0
        for n in notes:
            p = core.problems(n)
            print("%-28s %s" % (n["file"], "ok" if not p else "; ".join(p)))
            bad += bool(p)
        print("%d note(s), %d with problems" % (len(notes), bad))
        return 1 if bad else 0
    if cmd == "index":
        with open(os.path.join(d, "INDEX.md"), "w", encoding="utf-8") as fh:
            fh.write(core.index_md(notes))
        print("wrote %s" % os.path.join(d, "INDEX.md"))
        return 0
    if cmd == "view":
        out = os.path.join(d, "viewer.html")
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(core.viewer_html(notes))
        print("wrote %s" % out)
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
