# thread-notes

Each work item is one Markdown note with fixed fields: status, owner, due date, where things stand, and the live source to check. An index lists them all, a viewer shows them, and a checker flags notes that are stale or missing fields.

![Demo](docs/demo.gif)

## Quick start

```
python demo.py
```

Runs on a temp copy of the sample notes. Tests: `python -m unittest discover -s tests`. On your own folder: `python -m threadnotes check|index|view path/to/notes`.

## Requirements

Python 3.8+. No dependencies.

## How it works

- A note is a `.md` file with frontmatter (`title`, `status`, `owner`, `due`, `checked`, `source`) and a body that says where things stand.
- `check` reports missing fields, unknown statuses, overdue dates, and notes whose live source has not been checked for more than `THREADS_STALE_DAYS` (default 14). Done notes are never overdue. It exits non-zero on any problem, so it fits CI or a hook.
- `index` writes `INDEX.md`, a table sorted by status then due date.
- `view` writes a static, dark `viewer.html` with each note as a card and its problems highlighted. Text is HTML-escaped.
- The sample notes use invented data; two are deliberately broken so the checker has something to find.

## License

MIT. See [LICENSE](LICENSE).

Built with Claude Code. More: https://made-by-asking.pages.dev/showcase/thread-notes/
