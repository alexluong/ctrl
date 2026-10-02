#!/usr/bin/env python3
"""
Ebook catalog management for the calibre library.

The calibre library lives at /Volumes/Blue4/arr/media/books/library and is
served by the two calibre-web instances (alex :8074, hannah :8073). This tool
drives calibre's own `calibredb` CLI (via a one-shot container from the cached
`lscr.io/linuxserver/calibre` image) so the library's metadata.db stays
consistent — never move files into the library by hand.

Usage:
    ./books.py status                    # library summary + health (dupes/ghosts/odd authors)
    ./books.py scan                      # list ebooks in downloads/, flag which are already imported
    ./books.py import [--dry-run]        # add NEW ebooks (skips dupes), enrich metadata, normalize authors
    ./books.py normalize [--dry-run]     # apply author-alias fixes across the whole library
    ./books.py archive [--dry-run]       # move already-imported download files into downloads/_imported/

Notes:
  - Ebooks in downloads/ are usually ALREADY in the library (they're the leftover
    source files calibre copied in on first import). `import` de-dupes against the
    library by normalized title + author, so re-running is safe.
  - `import` stops both calibre-web instances during writes (the library metadata.db
    is on the virtiofs drive; concurrent writers there cause "database is locked" —
    same class of issue as the Jellyfin DB). They're restarted afterwards.
  - Manga/comics (cbz, the "Unknown"-author Detective Conan/Case Closed dumps) are
    intentionally OUT of scope here; this tool handles epub/azw3/mobi/pdf ebooks.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# =============================================================================
# Config
# =============================================================================

BOOKS_ROOT = Path("/Volumes/Blue4/arr/media/books")
LIBRARY = BOOKS_ROOT / "library"
DOWNLOADS = BOOKS_ROOT / "downloads"
IMPORTED = DOWNLOADS / "_imported"

DOCKER_CONTEXT = "colima-arr"
CALIBRE_IMAGE = "lscr.io/linuxserver/calibre:latest"
# host BOOKS_ROOT is mounted at /books inside the container
CONTAINER_LIB = "/books/library"

CALIBRE_WEB = ["calibre-web-alex", "calibre-web-hannah"]

EBOOK_EXTS = {".epub", ".azw3", ".mobi", ".pdf", ".kepub"}

# Author-name normalization. Explicit aliases first; "Last, First" is handled
# generically by normalize_author().
AUTHOR_ALIASES = {
    "Chainani, Soman": "Soman Chainani",
    "Miller, Madeline": "Madeline Miller",
}

GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
BLUE = "\033[0;34m"
RED = "\033[0;31m"
NC = "\033[0m"


# =============================================================================
# calibredb / docker plumbing
# =============================================================================

def _env():
    e = dict(os.environ)
    e["DOCKER_CONTEXT"] = DOCKER_CONTEXT
    return e


def calibredb(args, capture=True, mount_ro=False):
    """Run a calibredb subcommand in a one-shot calibre container."""
    mount = f"{BOOKS_ROOT}:/books"
    cmd = [
        "docker", "run", "--rm",
        "-v", mount,
        "--entrypoint", "/usr/bin/calibredb",
        CALIBRE_IMAGE,
        "--library-path", CONTAINER_LIB,
    ] + args
    return subprocess.run(cmd, env=_env(), capture_output=capture, text=True)


def calibre_bash(script):
    """Run an arbitrary bash script inside the calibre container (has calibredb,
    fetch-ebook-metadata, ebook-* tools). BOOKS_ROOT mounted read-write at /books."""
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{BOOKS_ROOT}:/books",
        "--entrypoint", "/bin/bash",
        CALIBRE_IMAGE, "-c", script,
    ]
    return subprocess.run(cmd, env=_env(), capture_output=True, text=True)


def library_books():
    """Return the library as a list of dicts (id, authors, title, series, ...)."""
    r = calibredb([
        "list", "--fields", "id,authors,title,series,series_index,formats,isbn",
        "--limit", "100000", "--for-machine",
    ])
    if r.returncode != 0:
        sys.exit(f"{RED}calibredb list failed:{NC}\n{r.stderr}")
    return json.loads(r.stdout or "[]")


def calibre_web_running():
    r = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}"],
        env=_env(), capture_output=True, text=True,
    )
    names = set(r.stdout.split())
    return [c for c in CALIBRE_WEB if c in names]


def stop_calibre_web():
    running = calibre_web_running()
    if running:
        subprocess.run(["docker", "stop"] + running, env=_env(),
                       capture_output=True, text=True)
    return running


def start_calibre_web(names):
    if names:
        subprocess.run(["docker", "start"] + names, env=_env(),
                       capture_output=True, text=True)


# =============================================================================
# Parsing / matching
# =============================================================================

ISBN_RE = re.compile(r"\b(97[89]\d{10}|\d{9}[\dXx])\b")


def normalize_author(author):
    """'Last, First' -> 'First Last'; apply explicit aliases; collapse spaces."""
    if not author:
        return author
    author = AUTHOR_ALIASES.get(author.strip(), author.strip())
    if "," in author and author.count(",") == 1:
        last, first = [p.strip() for p in author.split(",", 1)]
        if first and last and " " not in last:
            author = f"{first} {last}"
    return re.sub(r"\s+", " ", author).strip()


def norm_title(title):
    """Full alphanumeric title key for dedup. Anna's Archive replaces ':' with
    '_' in filenames, so treat them the same. Drops parentheticals, series
    numbering, and leading articles, then strips to [a-z0-9]. Keeps the subtitle
    (needed because AA prefixes the series name onto the title)."""
    t = title.lower().replace("_", ":")
    t = re.sub(r"\([^)]*\)", " ", t)          # (enhanced edition)
    t = re.sub(r"#\s*\d+", " ", t)            # #2
    t = re.sub(r"\bbk[._ ]*\d+", " ", t)      # bk. 2
    t = re.sub(r"\bvol[.\s]*\d+", " ", t)     # vol 1
    t = re.sub(r"\b(the|a|an)\b", " ", t)
    t = re.sub(r"[^a-z0-9]+", "", t)
    return t


def author_key(author):
    """Last-name key of the FIRST listed author (fields may be 'A; B; C' or
    'A, B, C'); robust to the 'Last, First' form."""
    if not author:
        return ""
    first = re.split(r"[;]", author)[0]
    first = normalize_author(first).lower()
    first = re.sub(r"[^a-z0-9 ]+", " ", first)
    parts = first.split()
    return parts[-1] if parts else ""


def parse_annas_archive(filename):
    """Parse the 'Title -- Author -- ... -- ISBN -- hash -- Anna's Archive.ext'
    format. Falls back to stem-as-title for other filenames."""
    stem = Path(filename).stem
    isbn = None
    m = ISBN_RE.search(stem)
    if m:
        isbn = m.group(1)
    if " -- " in stem:
        fields = [f.strip() for f in stem.split(" -- ")]
        title = fields[0]
        author = normalize_author(fields[1]) if len(fields) > 1 else ""
        # strip a trailing "[Sortname]" calibre sometimes leaves in the author field
        author = re.sub(r"\s*\[[^\]]*\]\s*$", "", author)
    else:
        title, author = stem, ""
    return {"title": title, "author": author, "isbn": isbn}


def find_ebooks(root):
    return sorted(
        p for p in root.rglob("*")
        if p.is_file()
        and p.suffix.lower() in EBOOK_EXTS
        and IMPORTED not in p.parents
    )


def match_in_library(meta, lib_index):
    """Return the library book this download matches, or None. Order of tests:
      1. ISBN exact.
      2. same author + one title-key contains the other (>=6 chars) — handles
         Anna's Archive prepending the series name onto the stored subtitle.
      3. distinctive long title (>=18 chars) contained either way, author-agnostic
         — rescues records with mangled author fields."""
    if meta["isbn"]:
        hit = lib_index["isbn"].get(meta["isbn"].replace("-", "").upper())
        if hit:
            return hit
    dl_t = norm_title(meta["title"])
    dl_a = author_key(meta["author"])
    if len(dl_t) < 4:
        return None
    best, best_score = None, 0
    for b in lib_index["books"]:
        lb_t = b["_tkey"]
        if not lb_t:
            continue
        contained = (lb_t in dl_t or dl_t in lb_t)
        shorter = min(len(lb_t), len(dl_t))
        author_ok = bool(dl_a) and dl_a == b["_akey"]
        # require either an author match (>=6) or a distinctive long title (>=18)
        if not (contained and (shorter >= 18 or (shorter >= 6 and author_ok))):
            continue
        # score: prefer exact, then subtitle-suffix (AA = 'Series #N: Subtitle'),
        # then any substring; longer overlap and author match break ties.
        if dl_t == lb_t:
            score = 400
        elif dl_t.endswith(lb_t) or lb_t.endswith(dl_t):
            score = 300
        else:
            score = 200
        score += shorter + (50 if author_ok else 0)
        if score > best_score:
            best, best_score = b, score
    return best


def build_index(books):
    idx = {"isbn": {}, "books": books}
    for b in books:
        b["_tkey"] = norm_title(b.get("title", ""))
        b["_akey"] = author_key(b.get("authors", ""))
        isbn = (b.get("isbn") or "").replace("-", "").upper()
        if isbn:
            idx["isbn"][isbn] = b
    return idx


# =============================================================================
# Commands
# =============================================================================

def cmd_status(args):
    books = library_books()
    print(f"{BLUE}Library:{NC} {LIBRARY}  —  {GREEN}{len(books)} books{NC}\n")

    from collections import Counter
    authors = Counter(b.get("authors", "Unknown") for b in books)
    print(f"{BLUE}Authors ({len(authors)}):{NC}")
    for a, n in sorted(authors.items()):
        print(f"  {n:>3}  {a}")

    ghosts = [b for b in books if not b.get("formats")]
    lastfirst = [b for b in books
                 if "," in (b.get("authors") or "")
                 and b.get("authors") not in AUTHOR_ALIASES.values()]
    unknown = [b for b in books if (b.get("authors") or "") == "Unknown"]

    print(f"\n{BLUE}Health:{NC}")
    print(f"  ghost entries (no files): {RED if ghosts else GREEN}{len(ghosts)}{NC}"
          + (f"  -> ids {[b['id'] for b in ghosts]}" if ghosts else ""))
    print(f"  'Last, First' authors:    {YELLOW if lastfirst else GREEN}{len(lastfirst)}{NC}"
          + (f"  -> ids {[b['id'] for b in lastfirst]}" if lastfirst else ""))
    print(f"  'Unknown' author (manga): {YELLOW if unknown else GREEN}{len(unknown)}{NC}"
          + (f"  -> ids {[b['id'] for b in unknown]}" if unknown else ""))


def cmd_scan(args):
    books = library_books()
    idx = build_index(books)
    ebooks = find_ebooks(DOWNLOADS)
    if not ebooks:
        print(f"{YELLOW}No ebooks in {DOWNLOADS}{NC}")
        return
    new, dup = [], []
    for p in ebooks:
        meta = parse_annas_archive(p.name)
        hit = match_in_library(meta, idx)
        (dup if hit else new).append((p, meta, hit))
    print(f"{BLUE}Scanned {len(ebooks)} ebook file(s) in downloads/{NC}\n")
    print(f"{GREEN}NEW ({len(new)}) — not in library:{NC}")
    for p, meta, _ in new:
        isbn = f" isbn={meta['isbn']}" if meta["isbn"] else ""
        print(f"  + {meta['title']} — {meta['author']}{isbn}")
    print(f"\n{YELLOW}ALREADY IMPORTED ({len(dup)}):{NC}")
    for p, meta, hit in dup:
        print(f"  = {meta['title']} — {meta['author']}  ->  library id{hit['id']}")
    return new, dup


def cmd_import(args):
    books = library_books()
    idx = build_index(books)
    ebooks = find_ebooks(DOWNLOADS)
    new = []
    for p in ebooks:
        meta = parse_annas_archive(p.name)
        if not match_in_library(meta, idx):
            new.append((p, meta))
    if not new:
        print(f"{GREEN}Nothing new to import — all {len(ebooks)} download(s) already "
              f"in the library.{NC}")
        return
    print(f"{BLUE}{len(new)} new ebook(s) to import:{NC}")
    for p, meta in new:
        print(f"  + {meta['title']} — {meta['author']}")
    if args.dry_run:
        print(f"\n{YELLOW}[dry-run] no changes made.{NC}")
        return

    stopped = stop_calibre_web()
    print(f"\n{BLUE}stopped calibre-web ({', '.join(stopped) or 'none running'}) for writes{NC}")
    try:
        for p, meta in new:
            _import_one(p, meta)
    finally:
        start_calibre_web(stopped)
        print(f"{BLUE}restarted calibre-web.{NC}")


def _import_one(path, meta):
    """add -> enrich by ISBN/title -> normalize author. Runs inside one container."""
    rel = path.relative_to(BOOKS_ROOT).as_posix()
    isbn = meta["isbn"] or ""
    author = meta["author"] or ""
    title = meta["title"]
    # bash inside the calibre container; /books is the mount
    script = f'''
set -e
L="--library-path {CONTAINER_LIB}"
ADD=$(calibredb $L add "/books/{rel}" 2>&1)
ID=$(echo "$ADD" | grep -oE "ids: [0-9]+" | grep -oE "[0-9]+" | head -1)
[ -z "$ID" ] && ID=$(echo "$ADD" | grep -oE "book ids: [0-9]+" | grep -oE "[0-9]+" | head -1)
echo "added id=$ID"
OPF=/tmp/m.opf
if [ -n "{isbn}" ]; then
  fetch-ebook-metadata --isbn "{isbn}" --opf > $OPF 2>/dev/null || true
else
  fetch-ebook-metadata --title "{title}" --authors "{author}" --opf > $OPF 2>/dev/null || true
fi
if [ -s "$OPF" ]; then
  calibredb $L set_metadata "$ID" "$OPF" >/dev/null 2>&1 && echo "  enriched"
fi
'''
    r = calibre_bash(script)
    out = (r.stdout + r.stderr).strip()
    book_id = None
    m = re.search(r"added id=(\d+)", out)
    if m:
        book_id = m.group(1)
    enriched = "enriched" in out
    # normalize author on the freshly-added book
    if book_id and author:
        calibredb(["set_metadata", book_id, "--field",
                   f"authors:{normalize_author(author)}"])
    status = f"id{book_id}" if book_id else f"{RED}FAILED{NC}"
    tag = f" {GREEN}+enriched{NC}" if enriched else ""
    print(f"  {GREEN}✓{NC} {title} — {author}  [{status}]{tag}")


def cmd_normalize(args):
    books = library_books()
    fixes = []
    for b in books:
        cur = b.get("authors", "")
        new = normalize_author(cur)
        if new != cur:
            fixes.append((b["id"], cur, new))
    if not fixes:
        print(f"{GREEN}All author names already normalized.{NC}")
        return
    print(f"{BLUE}{len(fixes)} author fix(es):{NC}")
    for bid, cur, new in fixes:
        print(f"  id{bid}: {YELLOW}{cur}{NC} -> {GREEN}{new}{NC}")
    if args.dry_run:
        print(f"\n{YELLOW}[dry-run] no changes made.{NC}")
        return
    stopped = stop_calibre_web()
    try:
        for bid, _cur, new in fixes:
            calibredb(["set_metadata", str(bid), "--field", f"authors:{new}"])
    finally:
        start_calibre_web(stopped)
    print(f"{GREEN}Done.{NC}")


def cmd_archive(args):
    """Move download files that are already in the library into downloads/_imported/."""
    books = library_books()
    idx = build_index(books)
    ebooks = find_ebooks(DOWNLOADS)
    to_move = []
    for p in ebooks:
        meta = parse_annas_archive(p.name)
        if match_in_library(meta, idx):
            to_move.append(p)
    if not to_move:
        print(f"{GREEN}No already-imported files to archive.{NC}")
        return
    print(f"{BLUE}{len(to_move)} already-imported file(s) -> {IMPORTED}{NC}")
    for p in to_move:
        print(f"  {p.relative_to(DOWNLOADS)}")
    if args.dry_run:
        print(f"\n{YELLOW}[dry-run] no files moved.{NC}")
        return
    IMPORTED.mkdir(parents=True, exist_ok=True)
    for p in to_move:
        dest = IMPORTED / p.parent.relative_to(DOWNLOADS) if p.parent != DOWNLOADS else IMPORTED
        dest.mkdir(parents=True, exist_ok=True)
        p.rename(dest / p.name)
    print(f"{GREEN}Archived {len(to_move)} file(s).{NC}")


# =============================================================================
# CLI
# =============================================================================

def main():
    ap = argparse.ArgumentParser(description="Ebook catalog management (calibre).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status", help="library summary + health")
    sub.add_parser("scan", help="list downloads/ ebooks, flag already-imported")
    pi = sub.add_parser("import", help="add new ebooks (dedup + enrich + normalize)")
    pi.add_argument("--dry-run", action="store_true")
    pn = sub.add_parser("normalize", help="apply author-alias fixes library-wide")
    pn.add_argument("--dry-run", action="store_true")
    pa = sub.add_parser("archive", help="move already-imported files to _imported/")
    pa.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    {
        "status": cmd_status,
        "scan": cmd_scan,
        "import": cmd_import,
        "normalize": cmd_normalize,
        "archive": cmd_archive,
    }[args.cmd](args)


if __name__ == "__main__":
    main()
