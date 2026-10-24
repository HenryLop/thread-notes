"""One markdown note per work item, with fixed fields in frontmatter:

    ---
    title: Migrate the billing job
    status: open            # open | waiting | blocked | done
    owner: Ana
    due: 2026-11-15
    checked: 2026-10-20     # last time the live source was looked at
    source: https://tracker.example.com/ticket/123
    ---
    Where things stand: free text.
"""
import datetime as dt
import html
import os
import re

FIELDS = ["title", "status", "owner", "due", "checked", "source"]
STATUSES = ["open", "waiting", "blocked", "done"]
STALE_DAYS = int(os.environ.get("THREADS_STALE_DAYS", "14"))


def parse(path):
    text = _read(path)
    m = re.match(r"---\n(.*?)\n---\n?(.*)", text, re.S)
    meta, body = {}, text
    if m:
        body = m.group(2).strip()
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = re.sub(r"\s+#.*$", "", v).strip()
    meta["file"] = os.path.basename(path)
    meta["body"] = body
    return meta


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def load(d):
    return [parse(os.path.join(d, f)) for f in sorted(os.listdir(d)) if f.endswith(".md") and f.upper() != "INDEX.MD"]


def _date(s):
    try:
        return dt.date.fromisoformat(s)
    except (TypeError, ValueError):
        return None


def problems(note, today=None):
    today = today or dt.date.today()
    out = ["missing field: %s" % f for f in FIELDS if not note.get(f)]
    if note.get("status") and note["status"] not in STATUSES:
        out.append("unknown status '%s'" % note["status"])
    if note.get("due") and not _date(note["due"]):
        out.append("due is not a date")
    if note.get("status") != "done":
        due, chk = _date(note.get("due")), _date(note.get("checked"))
        if due and due < today:
            out.append("overdue since %s" % due)
        if chk and (today - chk).days > STALE_DAYS:
            out.append("stale: source not checked for %d days" % (today - chk).days)
    if not note.get("body"):
        out.append("no 'where things stand' text")
    return out


def index_md(notes):
    order = {s: i for i, s in enumerate(STATUSES)}
    rows = sorted(notes, key=lambda n: (order.get(n.get("status"), 9), n.get("due") or "9999"))
    lines = ["# Threads", "", "| Status | Title | Owner | Due | Note |", "| :--- | :--- | :--- | :--- | :--- |"]
    for n in rows:
        lines.append("| %s | %s | %s | %s | [%s](%s) |" % (n.get("status", "?"), n.get("title", n["file"]), n.get("owner", ""),
                                                         n.get("due", ""), n["file"], n["file"]))
    return "\n".join(lines) + "\n"


def viewer_html(notes, today=None):
    cards = []
    for n in notes:
        probs = problems(n, today)
        cards.append('<section class="%s"><h2>%s</h2><p class="meta">%s | owner %s | due %s</p><p>%s</p>%s'
                     '<p class="src">%s</p></section>' % (
                         html.escape(n.get("status", "?")), html.escape(n.get("title", n["file"])),
                         html.escape(n.get("status", "?")), html.escape(n.get("owner", "-")), html.escape(n.get("due", "-")),
                         html.escape(n["body"]).replace("\n", "<br>"),
                         "".join('<p class="warn">%s</p>' % html.escape(p) for p in probs), html.escape(n.get("source", ""))))
    css = ("body{font:15px system-ui;background:#111;color:#e8e8e8;margin:0;padding:1.5em}"
           "section{border:1px solid #333;padding:1em;margin:0 0 1em}.meta,.src{color:#999}"
           ".warn{color:#e0a030;margin:.2em 0}.done{opacity:.55}.blocked{border-color:#c44}h2{margin:0 0 .3em;font-size:1.1em}")
    return '<!doctype html><meta charset="utf-8"><title>Threads</title><style>%s</style><h1>Threads</h1>%s' % (css, "".join(cards))
