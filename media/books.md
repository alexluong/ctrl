# Books (calibre / ebooks)

Ebook library served by two **calibre-web** instances that share one calibre library:

| Who | URL | Container | /config |
| --- | --- | --- | --- |
| Alex | `http://<host>:8074` | `calibre-web-alex` | `${DATA_PATH}/calibre-web-alex` |
| Hannah | `http://<host>:8073` | `calibre-web-hannah` | `${DATA_PATH}/calibre-web-hannah` |

- **Library (shared):** `/Volumes/Blue4/arr/media/books/library` → mounted `/library` in both
  containers. calibre's `metadata.db` lives at the library root; per-author folders hold the
  book files (epub/kepub/azw3/pdf) + `.opf` metadata + cover `.jpg`.
- **Incoming/unsorted:** `/Volumes/Blue4/arr/media/books/downloads/`.
- Audiobooks are separate — audiobookshelf (`:13378`), not calibre. See `README.md`.

## Golden rule

**Never move files into the library by hand.** calibre tracks everything in `metadata.db`;
hand-filing desyncs it (orphaned entries, broken covers). Always go through `calibredb`, which
the `books.py` pipeline wraps.

## The `calibredb` tool

`calibredb` is **not** in the calibre-web image. We run it from the cached full-calibre image
as a one-shot container (also provides `fetch-ebook-metadata`, `ebook-convert`, …):

```sh
docker --context colima-arr run --rm \
  -v /Volumes/Blue4/arr/media/books:/books \
  --entrypoint /usr/bin/calibredb lscr.io/linuxserver/calibre:latest \
  --library-path /books/library list --limit 5
```

Note: even read-only `list` needs the mount **read-write** (calibredb writes a case-sensitivity
probe file into the library dir); a `:ro` mount fails with `Read-only file system`.

## The pipeline: `catalog/scripts/books.py`

Analogous to `catalog.py` but for ebooks. Runs on the host; shells out to the calibre container.

```sh
./catalog/scripts/books.py status                 # library summary + health (ghosts/dupes/odd authors)
./catalog/scripts/books.py scan                    # list downloads/ ebooks, flag already-imported vs new
./catalog/scripts/books.py import [--dry-run]      # add NEW ebooks (dedup + online enrich + author-normalize)
./catalog/scripts/books.py normalize [--dry-run]   # apply author-alias fixes library-wide
./catalog/scripts/books.py archive [--dry-run]     # move already-imported files -> downloads/_imported/
```

What it does:
- **Dedup** — ebooks in `downloads/` are usually the leftover source files calibre already
  copied in, so `import`/`scan` match each file against the library (ISBN, then normalized
  title + first-author) and **skip anything already present**. Re-running is safe.
- **Anna's Archive filenames** parse cleanly: `Title -- Author -- [Series #N,] Year -- Publisher
  -- [ISBN] -- hash -- Anna's Archive.ext`. AA replaces `:` with `_` and prepends the series
  name onto the title — the matcher accounts for both (treats `_` as `:`, uses substring match).
- **Enrichment** — `import` fetches metadata by ISBN (or title+author) via `fetch-ebook-metadata`
  and applies it (description, tags, series, publisher). Covers come from the embedded epub
  cover that `calibredb add` extracts; online metadata fills the rest.
- **Author normalization** — `Last, First` → `First Last`, plus explicit aliases in
  `AUTHOR_ALIASES` (e.g. `Chainani, Soman` → `Soman Chainani`). Keeps series from splitting
  across two author folders and keeps sort order sane.

### Writes stop calibre-web first

`metadata.db` is on the virtiofs drive, so **concurrent writers cause `database is locked`**
(same failure class as the Jellyfin DB — see `jellyfin.md` gotcha #8). `import` and `normalize`
therefore **stop both calibre-web instances during writes and restart them after**. If you run
raw `calibredb` writes yourself, do the same:
`docker --context colima-arr stop calibre-web-alex calibre-web-hannah` → write → `start`.

## Out of scope (for now): manga / comics

`downloads/` also holds **cbz manga** (Detective Conan / Case Closed — same series, two names —
and ASOUE loose page images). These are intentionally **not** handled by `books.py`. They also
pollute the calibre library as 4 **"Unknown"**-author entries (ids 6/8/9/10). A dedicated comic
server (Komga/Kavita) is the better home; TBD — expand this section when we tackle it.

## History

- **2026-07-15 cleanup:** removed 3 junk entries (two empty "ghost" ASOUE records with no
  files; one duplicate Agatha Christie "Seven Dials Mystery"), unified the School for Good and
  Evil series under "Soman Chainani" (book #2 was filed under "Chainani, Soman"), and normalized
  "Miller, Madeline" → "Madeline Miller". Archived 21 already-imported source files from
  `downloads/` to `downloads/_imported/`. Library: 50 → 47 books. Deletions go to the library's
  `.caltrash` (recoverable).
