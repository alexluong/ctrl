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

## Getting new books (sourcing)

Two sources; both end the same way (file lands in `downloads/` → `books.py import`):

1. **Anna's Archive** — how the *existing* library was built (direct download, not torrents).
   Search annas-archive.org, download the epub, drop it in `books/downloads/`. Simplest for
   ebooks; the filename format parses cleanly (see the pipeline notes below).
2. **MyAnonaMouse (MAM)** — private tracker; better for **audiobooks** and curated ebook releases,
   and the source for whole-**series packs** (one torrent = the complete series). Flow: search
   MAM → download the `.torrent` **in the browser** → drop it in `~/Documents/pt/red4/mam/` →
   add to qBittorrent (behind the VPN) → it downloads to `downloads/` and seeds.
   - The MAM **search API** works from the box (see `README.md` → MAM), so Claude can *find* books
     and their torrent IDs. But **the `.torrent` download must be done in the browser** — the
     seedbox session can't fetch torrent files. (Prowlarr's MAM indexer is the automated
     alternative, if we ever set it up.)
   - **Ban-safety:** keep torrents **seeding** for ratio, and don't let the client crash-loop or
     the VPN flap — rapid re-announces trigger MAM "duplicate peer" bans (`README.md`).
   - Prefer packs that include **epub** (calibre's native format); azw3/mobi-only needs conversion.

**Only deliberately-chosen books get cataloged.** The MAM download pile is mostly ratio/seeding
torrents — `books.py` is never pointed at the torrent `downloads/` dirs; it only ingests
`books/downloads/`, and only what you actually want in the library.

## The goal & the standing workflow (on-demand)

**Goal:** keep the calibre **catalog** (`metadata.db`) *current and clean*. The catalog is the
asset; the per-user calibre-web `app.db` state (shelves, reading progress) is disposable and not
something we go out of our way to preserve. "Clean" means: no duplicate or ghost (file-less)
entries, no author filed two ways, series intact, and no untitled "Unknown" junk.

**How new books get in — on-demand (not scheduled).** When ebooks land in `downloads/`:

```sh
cd media
./catalog/scripts/books.py status        # 1. baseline: current counts + health
./catalog/scripts/books.py scan           # 2. see what's NEW vs already-imported
./catalog/scripts/books.py import          # 3. add the new ones (dedup + enrich + normalize)
./catalog/scripts/books.py archive         # 4. move imported source files to _imported/
./catalog/scripts/books.py status         # 5. confirm health is still clean
```

Every `import`/`normalize` runs **with a human/Claude looking at the output** — that review *is*
the point (see decisions below). Re-running is always safe (idempotent dedup).

## Design decisions (so we don't re-litigate)

- **On-demand, not a blind schedule.** A cron that runs the script unattended has no judgment on
  the tricky ~10% (unparseable filenames, maybe-duplicates, junk metadata) — the same weakness
  as a generic auto-importer. Since "clean" is the priority and books arrive infrequently, we run
  it *with eyes on it*. (If we ever want hands-off, the right form is Claude-on-a-timer that
  reviews + reports, not a dumb cron.)
- **Curated pipeline over calibre-web-automated (CWA).** CWA gives a drop-and-forget watch folder
  (keeps the library *current*) but its ingest is trusting — it re-adds duplicates and files
  authors as "Last, First". That erodes *clean*, which is exactly what we care about. `books.py`
  does the dedup + normalization CWA doesn't. Revisit CWA only if the priority shifts to
  convenience over cleanliness.
- **calibredb via one-shot full-calibre container**, not the `universal-calibre` mod on
  calibre-web — keeps the always-on readers lightweight; the tooling is only spun up when needed.

## Backlog — improve when needed

This doc + `books.py` are meant to grow. Known next steps:

- **Manga / comics (cbz).** `downloads/` holds Detective Conan / Case Closed (same series, two
  names) + ASOUE loose page images, and they pollute the catalog as 4 **"Unknown"**-author
  entries (ids 6/8/9/10). Out of scope for `books.py`. Plan: stand up a dedicated comic server
  (Komga/Kavita) and move them there, then remove the Unknown entries from calibre.
- **Extend `AUTHOR_ALIASES`** in `books.py` as new split/odd author names show up.
- **Other sources.** The filename parser is tuned for Anna's Archive; add parsers if books start
  arriving from other sources with different naming.
- **Covers.** Currently rely on the embedded epub cover + online metadata. If a book lands with no
  cover, add an explicit cover-fetch step (`fetch-ebook-metadata -c`).

## History

- **2026-07-15 cleanup:** removed 3 junk entries (two empty "ghost" ASOUE records with no
  files; one duplicate Agatha Christie "Seven Dials Mystery"), unified the School for Good and
  Evil series under "Soman Chainani" (book #2 was filed under "Chainani, Soman"), and normalized
  "Miller, Madeline" → "Madeline Miller". Archived 21 already-imported source files from
  `downloads/` to `downloads/_imported/`. Library: 50 → 47 books. Deletions go to the library's
  `.caltrash` (recoverable).
