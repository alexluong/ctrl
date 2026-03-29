#!/usr/bin/env python3
"""
Media catalog management.

Usage:
    ./catalog.py scan torrents [--source blue4|red4] [--dry-run]
    ./catalog.py scan downloads [--source blue4|red4] [--dry-run]
    ./catalog.py import [--dry-run]
    ./catalog.py link [--type movies|movies4k|tv|tv4k|all] [--dry-run]
    ./catalog.py status
    ./catalog.py prune [--dry-run]
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Set

# =============================================================================
# Config
# =============================================================================

# Torrent file locations
TORRENT_BASES = {
    "blue4": Path.home() / "Documents/pt/blue4",
    "red4": Path.home() / "Documents/pt/red4",
}

# Download locations
DOWNLOADS = {
    "blue4": Path("/Volumes/Blue4/arr/downloads"),
    "red4": Path("/Volumes/Red4/arr/downloads"),
}

# Library locations
LIBRARIES = {
    "blue4": {
        "movies": Path("/Volumes/Blue4/arr/media/movies"),
        "movies4k": Path("/Volumes/Blue4/arr/media/movies4k"),
        "tv": Path("/Volumes/Blue4/arr/media/tv"),
        "tv4k": Path("/Volumes/Blue4/arr/media/tv4k"),
    },
    "red4": {
        "movies": Path("/Volumes/Red4/arr/media/movies"),
        "movies4k": Path("/Volumes/Red4/arr/media/movies4k"),
        "tv": Path("/Volumes/Red4/arr/media/tv"),
        "tv4k": Path("/Volumes/Red4/arr/media/tv4k"),
    },
}

CATALOG_DIR = Path(__file__).parent.parent
DOWNLOADS_JSON = CATALOG_DIR / "downloads.json"
CATALOG_JSON = CATALOG_DIR / "catalog.json"

# Patterns that indicate TV show
TV_PATTERNS = [
    r"\.S\d{2}\.",
    r"\.S\d{2}E\d{2}",
    r"\sS\d{2}\s",
    r"\sS\d{2}\(",
    r"Season\s*\d+",
    r"S\d{2}-S\d{2}",
]

# Known non-media to skip
SKIP_LIST = ["Case Closed"]

# ANSI colors
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
BLUE = "\033[0;34m"
RED = "\033[0;31m"
NC = "\033[0m"

# =============================================================================
# Parsing Functions
# =============================================================================

def detect_resolution(name: str) -> str:
    """Detect resolution from filename."""
    name_lower = name.lower()

    if "2160p" in name_lower:
        return "2160p"

    if "uhd" in name_lower and "bluray" not in name_lower:
        return "2160p"

    if "4k" in name_lower:
        if "ds4k" in name_lower or "rm4k" in name_lower:
            return "1080p"
        if "hdr" in name_lower:
            return "2160p"
        return "2160p"

    if "1080p" in name_lower:
        return "1080p"
    if "720p" in name_lower:
        return "720p"

    return "unknown"


def detect_source(name: str) -> str:
    """Detect source from filename."""
    name_lower = name.lower()

    if "bluray" in name_lower or "bdrip" in name_lower:
        return "BluRay"
    if "web-dl" in name_lower or "webdl" in name_lower:
        return "WEB-DL"
    if "webrip" in name_lower:
        return "WEBRip"
    if "hdtv" in name_lower:
        return "HDTV"
    if "amzn" in name_lower:
        return "AMZN"
    if "nf" in name_lower:
        return "NF"
    if "dsnp" in name_lower:
        return "DSNP"

    return "unknown"


def detect_group(name: str) -> str:
    """Detect release group from filename."""
    # Remove extension
    name = re.sub(r"\.(mkv|mp4|avi|torrent)$", "", name, flags=re.IGNORECASE)

    # Pattern: -GROUP at end, or -GROUP followed by bracketed tags
    # Examples: Movie-SPARKS, Movie-d3g, Movie-INFERNO[rartv]
    match = re.search(r"-([A-Za-z0-9]+)(?:\[.*\])?$", name)
    if match:
        group = match.group(1)
        # Filter out common false positives (codecs, etc.)
        false_positives = ["x264", "x265", "h264", "h265", "hevc", "avc", "10bit"]
        if group.lower() not in false_positives:
            return group

    return "unknown"


def detect_video(name: str) -> str:
    """Detect video codec from filename."""
    name_lower = name.lower()

    if "av1" in name_lower:
        return "AV1"
    if "x265" in name_lower or "h265" in name_lower or "h.265" in name_lower or "hevc" in name_lower:
        return "x265"
    if "x264" in name_lower or "h264" in name_lower or "h.264" in name_lower or "avc" in name_lower:
        return "x264"
    if "vp9" in name_lower:
        return "VP9"
    if "xvid" in name_lower:
        return "XviD"

    return ""


def detect_audio(name: str) -> str:
    """Detect audio codec from filename."""
    name_lower = name.lower()

    if "atmos" in name_lower:
        return "Atmos"
    if "truehd" in name_lower:
        return "TrueHD"
    if "dts-hd" in name_lower or "dtshd" in name_lower:
        return "DTS-HD"
    if "dts" in name_lower:
        return "DTS"
    if "ddp" in name_lower or "dd+" in name_lower or "eac3" in name_lower:
        return "DD+"
    if "dd5" in name_lower or "dd7" in name_lower or "ac3" in name_lower:
        return "DD"
    if "opus" in name_lower:
        return "Opus"
    if "flac" in name_lower:
        return "FLAC"
    if "aac" in name_lower:
        return "AAC"

    return ""


def detect_hdr(name: str) -> str:
    """Detect HDR format from filename."""
    name_lower = name.lower()

    # Check for Dolby Vision first (can be combined with HDR10)
    if "dv" in name_lower or "dolby vision" in name_lower or "dolbyvision" in name_lower:
        if "hdr10" in name_lower or "hdr 10" in name_lower:
            return "DV HDR10"
        return "DV"
    if "hdr10+" in name_lower or "hdr10plus" in name_lower:
        return "HDR10+"
    if "hdr10" in name_lower or "hdr 10" in name_lower:
        return "HDR10"
    if "hdr" in name_lower:
        return "HDR"
    if "sdr" in name_lower:
        return "SDR"

    return ""


def is_tv_show(name: str) -> bool:
    """Check if filename looks like a TV show."""
    for pattern in TV_PATTERNS:
        if re.search(pattern, name, re.IGNORECASE):
            return True
    return False


def should_skip(name: str) -> bool:
    """Check if item should be skipped."""
    for skip in SKIP_LIST:
        if name.startswith(skip):
            return True
    return False


def parse_movie(name: str) -> Optional[Dict[str, Any]]:
    """Parse movie title and year from filename."""
    name_clean = re.sub(r"\.(mkv|mp4|avi|torrent)$", "", name, flags=re.IGNORECASE)

    # Pattern 1: Title (2020)
    match = re.search(r"^(.+?)\s*\((\d{4})\)", name_clean)
    if match:
        title = match.group(1)
        year = int(match.group(2))
        title = re.sub(r"\[.*?\]", "", title).strip()
        return {"title": title, "year": year}

    # Pattern 2: Title.2020.stuff
    match = re.search(r"^(.+?)\.(\d{4})\.", name_clean)
    if match:
        title = match.group(1).replace(".", " ").strip()
        year = int(match.group(2))
        if 1900 <= year <= 2030:
            return {"title": title, "year": year}

    return None


def parse_tv_show(name: str) -> Optional[Dict[str, Any]]:
    """Parse TV show title and seasons from filename."""
    name_clean = re.sub(r"\.torrent$", "", name, flags=re.IGNORECASE)

    # Multi-season: Show.Name.S01-S08
    match = re.search(r"^(.+?)\.S(\d{2})-S(\d{2})", name_clean, re.IGNORECASE)
    if match:
        title = match.group(1).replace(".", " ").strip()
        start, end = int(match.group(2)), int(match.group(3))
        return {"title": title, "seasons": list(range(start, end + 1))}

    # Single season: Show.Name.S01
    match = re.search(r"^(.+?)\.S(\d{2})", name_clean, re.IGNORECASE)
    if match:
        title = match.group(1).replace(".", " ").strip()
        title = re.sub(r"\s*\(\d{4}\)\s*", " ", title).strip()
        return {"title": title, "seasons": [int(match.group(2))]}

    # With spaces: Show Name (2020) S01
    match = re.search(r"^(.+?)\s+S(\d{2})\s", name_clean, re.IGNORECASE)
    if match:
        title = match.group(1).strip()
        title = re.sub(r"\s*\(\d{4}\)\s*", " ", title).strip()
        return {"title": title, "seasons": [int(match.group(2))]}

    # Season folder: Show Name Season 1
    match = re.search(r"^(.+?)\s*Season\s*(\d+)", name_clean, re.IGNORECASE)
    if match:
        title = match.group(1).strip()
        return {"title": title, "seasons": [int(match.group(2))]}

    return None


# =============================================================================
# Downloads Functions (torrent -> download mapping)
# =============================================================================

def load_downloads() -> Dict[str, Any]:
    """Load downloads.json."""
    if DOWNLOADS_JSON.exists():
        with open(DOWNLOADS_JSON) as f:
            return json.load(f)
    return {"items": []}


def save_downloads(downloads: Dict[str, Any]):
    """Save downloads.json."""
    downloads["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(DOWNLOADS_JSON, "w") as f:
        json.dump(downloads, f, indent=2)


def get_existing_torrents(downloads: Dict[str, Any]) -> Set[str]:
    """Get set of torrent paths already tracked."""
    return {item["torrent"] for item in downloads.get("items", []) if item.get("torrent")}


def get_existing_downloads(downloads: Dict[str, Any]) -> Set[str]:
    """Get set of download paths already tracked."""
    return {item["download"] for item in downloads.get("items", []) if item.get("download")}


# =============================================================================
# Catalog Functions (media library)
# =============================================================================

def load_catalog() -> Dict[str, Any]:
    """Load catalog.json."""
    if CATALOG_JSON.exists():
        with open(CATALOG_JSON) as f:
            return json.load(f)
    return {"items": []}


def save_catalog(catalog: Dict[str, Any]):
    """Save catalog.json."""
    catalog["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(CATALOG_JSON, "w") as f:
        json.dump(catalog, f, indent=2)


# =============================================================================
# File Functions
# =============================================================================

def find_video_file(path: Path) -> Optional[Path]:
    """Find the main video file (largest, non-sample)."""
    if path.is_file():
        return path

    if not path.is_dir():
        return None

    videos = []
    for ext in ["*.mkv", "*.mp4", "*.avi"]:
        videos.extend(path.glob(ext))
        videos.extend(path.glob(f"*/{ext}"))

    videos = [v for v in videos if not any(x in v.name.lower() for x in ["sample", "preview"])]

    if not videos:
        return None

    return max(videos, key=lambda f: f.stat().st_size)


def find_episodes(path: Path) -> List[Path]:
    """Find all episode files in a directory."""
    if not path.is_dir():
        return []

    episodes = []
    for ext in ["mkv", "mp4", "avi"]:
        episodes.extend(path.glob(f"*.{ext}"))
        episodes.extend(path.glob(f"*/*.{ext}"))

    episodes = [e for e in episodes if e.stat().st_size > 50_000_000]

    return sorted(episodes)


def parse_episode_code(filename: str) -> Optional[tuple]:
    """Extract S##E## from filename."""
    match = re.search(r"S(\d{2})E(\d{2})", filename, re.IGNORECASE)
    if match:
        return (match.group(1), match.group(2))
    return None


def normalize_name(name: str) -> str:
    """Normalize name for matching (lowercase, no special chars)."""
    name = re.sub(r"\.(mkv|mp4|avi|torrent)$", "", name, flags=re.IGNORECASE)
    name = name.lower()
    name = re.sub(r"[^a-z0-9]", "", name)
    return name


# =============================================================================
# Command: scan torrents
# =============================================================================

def cmd_scan_torrents(args):
    """Scan torrent directories for new .torrent files."""

    # Select source
    if args.source:
        sources = {args.source: TORRENT_BASES[args.source]}
    else:
        sources = {k: v for k, v in TORRENT_BASES.items() if v.exists()}

    if not sources:
        print("No torrent sources available.")
        return 1

    print()
    print("=" * 50)
    print("Scan Torrents")
    print("=" * 50)

    downloads = load_downloads()
    if "items" not in downloads:
        downloads["items"] = []
    existing = get_existing_torrents(downloads)
    print(f"Existing torrents: {len(existing)}")

    new_count = 0

    for source_name, base_path in sources.items():
        if not base_path.exists():
            print(f"\n{YELLOW}Skipping {source_name}: {base_path} not found{NC}")
            continue

        print(f"\nScanning: {base_path}")

        # Scan all .torrent files recursively
        for torrent_file in base_path.rglob("*.torrent"):
            rel_path = f"{source_name}/{torrent_file.relative_to(base_path)}"

            if rel_path in existing:
                continue

            # Simple entry: just torrent and download
            entry = {
                "torrent": rel_path,
                "download": None,
            }

            downloads["items"].append(entry)
            new_count += 1

    print(f"\nNew torrents: {new_count}")

    if new_count == 0:
        print("No new torrents.")
        return 0

    if args.dry_run:
        print(f"\n[DRY RUN] Would save {len(downloads['items'])} entries")
        return 0

    save_downloads(downloads)
    print(f"\n{GREEN}Saved:{NC} {DOWNLOADS_JSON}")
    print(f"Total: {len(downloads['items'])} entries")

    return 0


# =============================================================================
# Command: scan downloads
# =============================================================================

def cmd_scan_downloads(args):
    """Scan downloads and match to torrents."""

    # Select source
    if args.source:
        sources = {args.source: DOWNLOADS[args.source]}
    else:
        sources = {k: v for k, v in DOWNLOADS.items() if v.exists()}

    if not sources:
        print("No download sources available.")
        return 1

    print()
    print("=" * 50)
    print("Scan Downloads")
    print("=" * 50)

    downloads = load_downloads()
    if "items" not in downloads:
        downloads["items"] = []

    # Build lookup of items by normalized torrent name
    torrent_lookup = {}
    for item in downloads["items"]:
        if item.get("torrent"):
            torrent_name = Path(item["torrent"]).stem
            norm = normalize_name(torrent_name)
            torrent_lookup[norm] = item

    existing_downloads = get_existing_downloads(downloads)
    matched = 0
    unmatched = []

    for source_name, dl_path in sources.items():
        if not dl_path.exists():
            print(f"\n{YELLOW}Skipping {source_name}: {dl_path} not found{NC}")
            continue

        print(f"\nScanning: {dl_path}")

        for item in sorted(dl_path.iterdir()):
            name = item.name
            if name.startswith(".") or should_skip(name):
                continue

            dl_key = f"{source_name}/{name}"
            if dl_key in existing_downloads:
                continue

            # Try to match to existing torrent
            norm = normalize_name(name)
            if norm in torrent_lookup:
                entry = torrent_lookup[norm]
                if entry["download"] is None:
                    entry["download"] = dl_key
                    matched += 1
            else:
                unmatched.append(dl_key)

    print(f"\nMatched: {matched}")
    if unmatched:
        print(f"Unmatched downloads: {len(unmatched)}")
        for u in unmatched[:5]:
            print(f"  {u}")
        if len(unmatched) > 5:
            print(f"  ... and {len(unmatched) - 5} more")

    if args.dry_run:
        print(f"\n[DRY RUN] Would save {len(downloads['items'])} entries")
        return 0

    save_downloads(downloads)
    print(f"\n{GREEN}Saved:{NC} {DOWNLOADS_JSON}")

    return 0


# =============================================================================
# Command: import (parse metadata -> catalog.json with status: pending)
# =============================================================================

def cmd_import(args):
    """Import downloads to catalog (parse metadata, add to catalog.json)."""

    downloads = load_downloads()
    catalog = load_catalog()
    if "items" not in catalog:
        catalog["items"] = []

    # Get already cataloged downloads
    cataloged_downloads = {i["download"] for i in catalog["items"] if i.get("download")}

    # Get pending downloads (have download path, not yet in catalog)
    new_items = []
    parse_errors = []
    for item in downloads.get("items", []):
        dl = item.get("download")
        if dl and dl not in cataloged_downloads:
            # Parse metadata from download name
            name = dl.split("/", 1)[1] if "/" in dl else dl
            resolution = detect_resolution(name)
            source = detect_source(name)
            group = detect_group(name)
            video = detect_video(name)
            audio = detect_audio(name)
            hdr = detect_hdr(name)

            if is_tv_show(name):
                parsed = parse_tv_show(name)
                if parsed:
                    new_items.append({
                        "download": dl,
                        "type": "tv",
                        "title": parsed["title"],
                        "seasons": parsed["seasons"],
                        "resolution": resolution,
                        "source": source,
                        "group": group,
                        "video": video,
                        "audio": audio,
                        "hdr": hdr,
                        "status": "pending",
                    })
                else:
                    parse_errors.append(dl)
            else:
                parsed = parse_movie(name)
                if parsed:
                    new_items.append({
                        "download": dl,
                        "type": "movie",
                        "title": parsed["title"],
                        "year": parsed["year"],
                        "resolution": resolution,
                        "source": source,
                        "group": group,
                        "video": video,
                        "audio": audio,
                        "hdr": hdr,
                        "status": "pending",
                    })
                else:
                    parse_errors.append(dl)

    if not new_items and not parse_errors:
        print("Nothing new to import.")
        return 0

    # Group by type for display
    by_type = {
        "movies": [i for i in new_items if i["type"] == "movie" and i["resolution"] != "2160p"],
        "movies4k": [i for i in new_items if i["type"] == "movie" and i["resolution"] == "2160p"],
        "tv": [i for i in new_items if i["type"] == "tv" and i["resolution"] != "2160p"],
        "tv4k": [i for i in new_items if i["type"] == "tv" and i["resolution"] == "2160p"],
    }

    print()
    print("=" * 50)
    print("Import to Catalog")
    print("=" * 50)
    if args.dry_run:
        print(f"{YELLOW}DRY RUN{NC}")
    print("=" * 50)

    for import_type in ["movies", "movies4k", "tv", "tv4k"]:
        items = by_type[import_type]
        if not items:
            continue

        print(f"\n{import_type}: {len(items)} items")
        for item in items:
            if item["type"] == "movie":
                print(f"  {GREEN}+{NC} {item['title']} ({item['year']})")
            else:
                print(f"  {GREEN}+{NC} {item['title']} S{item['seasons']}")

    if parse_errors:
        print(f"\n{RED}Parse errors: {len(parse_errors)}{NC}")
        for err in parse_errors[:5]:
            print(f"  {RED}✗{NC} {err}")
        if len(parse_errors) > 5:
            print(f"  ... and {len(parse_errors) - 5} more")

    print()
    print("=" * 50)
    print(f"New entries: {GREEN}{len(new_items)}{NC}")
    if parse_errors:
        print(f"Errors: {RED}{len(parse_errors)}{NC}")

    if args.dry_run:
        print(f"\n[DRY RUN] Would add {len(new_items)} entries to catalog")
        return 0

    if new_items:
        catalog["items"].extend(new_items)
        save_catalog(catalog)
        print(f"\n{GREEN}Saved:{NC} {CATALOG_JSON}")
        print(f"Total: {len(catalog['items'])} entries")

    return 0


# =============================================================================
# Command: link (create hardlinks for pending items)
# =============================================================================

def cmd_link(args):
    """Create hardlinks for pending catalog items."""

    catalog = load_catalog()
    if "items" not in catalog:
        catalog["items"] = []

    # Get pending items
    pending_items = [i for i in catalog["items"] if i.get("status") == "pending"]

    if not pending_items:
        print("Nothing pending to link.")
        return 0

    # Group by type
    pending = {
        "movies": [i for i in pending_items if i["type"] == "movie" and i["resolution"] != "2160p"],
        "movies4k": [i for i in pending_items if i["type"] == "movie" and i["resolution"] == "2160p"],
        "tv": [i for i in pending_items if i["type"] == "tv" and i["resolution"] != "2160p"],
        "tv4k": [i for i in pending_items if i["type"] == "tv" and i["resolution"] == "2160p"],
    }

    # Select type
    if args.type:
        if args.type == "all":
            types_to_link = ["movies", "movies4k", "tv", "tv4k"]
        else:
            types_to_link = [args.type]
    else:
        options = []
        for t in ["movies", "movies4k", "tv", "tv4k"]:
            if pending[t]:
                options.append((t, f"{t} ({len(pending[t])} pending)"))

        if not options:
            print("Nothing pending to link.")
            return 0

        options.append(("all", f"all ({sum(len(pending[t]) for t in pending)} pending)"))

        choice = interactive_select("What to link?", options)
        if not choice:
            return 0
        types_to_link = ["movies", "movies4k", "tv", "tv4k"] if choice == "all" else [choice]

    print()
    print("=" * 50)
    print("Link to Library")
    print("=" * 50)
    if args.dry_run:
        print(f"{YELLOW}DRY RUN{NC}")
    print("=" * 50)

    linked_count = 0
    errors = []

    for link_type in types_to_link:
        items_to_link = pending[link_type]
        if not items_to_link:
            continue

        print(f"\n{link_type}: {len(items_to_link)} items")

        for item in items_to_link:
            # Determine source from download path
            dl_path = item["download"]
            source_name = dl_path.split("/")[0]
            dl_name = "/".join(dl_path.split("/")[1:])

            source = DOWNLOADS.get(source_name)
            libs = LIBRARIES.get(source_name)
            if not source or not libs:
                errors.append(f"Unknown source: {source_name}")
                continue

            src_path = source / dl_name
            lib_path = libs[link_type]
            lib_path.mkdir(parents=True, exist_ok=True)

            if item["type"] == "movie":
                result, library_path = link_movie(item, src_path, lib_path, source_name, args.dry_run)
            else:
                result, library_path = link_tv(item, src_path, lib_path, source_name, args.dry_run)

            if result:
                linked_count += 1
                if not args.dry_run:
                    # Update catalog entry
                    item["library"] = library_path
                    item["status"] = "linked"
            else:
                errors.append(item["download"])

    print()
    print("=" * 50)
    print(f"Linked: {GREEN}{linked_count}{NC}")
    if errors:
        print(f"Errors: {RED}{len(errors)}{NC}")

    if not args.dry_run and linked_count > 0:
        save_catalog(catalog)
        print(f"\n{GREEN}Saved:{NC} {CATALOG_JSON}")

    return 0


def link_movie(item: Dict, src_path: Path, lib_path: Path, source_name: str, dry_run: bool) -> tuple:
    """Link a single movie. Returns (success, library_path)."""
    title = item["title"]
    year = item["year"]
    folder_name = f"{title} ({year})"
    dest_folder = lib_path / folder_name
    library_path = f"{source_name}/{lib_path.name}/{folder_name}"

    if dest_folder.exists():
        print(f"  {BLUE}○{NC} Exists: {folder_name}")
        return True, library_path

    video = find_video_file(src_path)
    if not video:
        print(f"  {RED}✗{NC} No video: {src_path.name}")
        return False, None

    dest_file = dest_folder / f"{title} ({year}){video.suffix}"

    if dry_run:
        print(f"  {BLUE}[DRY]{NC} {folder_name}")
        return True, library_path

    try:
        dest_folder.mkdir(parents=True, exist_ok=True)
        os.link(video, dest_file)
        print(f"  {GREEN}✓{NC} {folder_name}")
        return True, library_path
    except OSError as e:
        print(f"  {RED}✗{NC} {folder_name}: {e}")
        if dest_folder.exists() and not any(dest_folder.iterdir()):
            dest_folder.rmdir()
        return False, None


def get_base_show_name(title: str) -> str:
    """Extract base show name by stripping 'Season X' suffix."""
    # Remove "Season X" or "Season XX" suffix
    base = re.sub(r"\s+Season\s+\d+$", "", title, flags=re.IGNORECASE)
    return base.strip()


def link_tv(item: Dict, src_path: Path, lib_path: Path, source_name: str, dry_run: bool) -> tuple:
    """Link a TV show. Returns (success, library_path)."""
    title = item["title"]
    # Use base show name for folder (strip "Season X" suffix)
    show_name = get_base_show_name(title)
    show_folder = lib_path / show_name
    library_path = f"{source_name}/{lib_path.name}/{show_name}"

    episodes = find_episodes(src_path)
    if not episodes:
        print(f"  {RED}✗{NC} No episodes: {src_path.name}")
        return False, None

    if dry_run:
        print(f"  {BLUE}[DRY]{NC} {title} ({len(episodes)} eps)")
        return True, library_path

    linked = 0
    for ep in episodes:
        parsed = parse_episode_code(ep.name)
        if not parsed:
            continue

        season, episode = parsed
        season_folder = show_folder / f"Season {season}"
        season_folder.mkdir(parents=True, exist_ok=True)

        quality = "WEB-2160p" if item["resolution"] == "2160p" else "WEB-1080p"
        dest_name = f"{title} - S{season}E{episode} {quality}{ep.suffix}"
        dest_file = season_folder / dest_name

        if dest_file.exists():
            continue

        try:
            os.link(ep, dest_file)
            linked += 1
        except OSError:
            pass

    if linked > 0:
        print(f"  {GREEN}✓{NC} {title} ({linked} eps)")
        return True, library_path

    print(f"  {BLUE}○{NC} {title} (already linked)")
    return True, library_path


# =============================================================================
# Command: status
# =============================================================================

def cmd_status(args):
    """Show status of downloads and catalog."""

    downloads = load_downloads()
    catalog = load_catalog()

    dl_items = downloads.get("items", [])
    cat_items = catalog.get("items", [])

    # Get cataloged downloads for comparison
    cataloged_downloads = {i["download"] for i in cat_items if i.get("download")}

    print()
    print("=" * 50)
    print("Status")
    print("=" * 50)

    # Downloads
    total_torrents = len(dl_items)
    with_download = len([i for i in dl_items if i.get("download")])
    not_cataloged = len([i for i in dl_items if i.get("download") and i["download"] not in cataloged_downloads])

    print(f"\n{BLUE}Downloads:{NC} {DOWNLOADS_JSON.name}")
    print(f"  Torrents:      {total_torrents}")
    print(f"  With download: {with_download}")
    print(f"  Not cataloged: {YELLOW}{not_cataloged}{NC}")

    # Catalog
    pending = [i for i in cat_items if i.get("status") == "pending"]
    linked = [i for i in cat_items if i.get("status") == "linked"]

    print(f"\n{BLUE}Catalog:{NC} {CATALOG_JSON.name}")
    print(f"  Total:   {len(cat_items)}")
    print(f"  Pending: {YELLOW}{len(pending)}{NC}")
    print(f"  Linked:  {GREEN}{len(linked)}{NC}")

    if cat_items:
        movies = [i for i in cat_items if i["type"] == "movie"]
        tv = [i for i in cat_items if i["type"] == "tv"]
        movies_4k = [i for i in movies if i["resolution"] == "2160p"]
        tv_4k = [i for i in tv if i["resolution"] == "2160p"]

        print(f"\n  Movies: {len(movies)} ({len(movies_4k)} 4K)")
        print(f"  TV:     {len(tv)} ({len(tv_4k)} 4K)")

    print("=" * 50)
    return 0


# =============================================================================
# Command: prune
# =============================================================================

def cmd_prune(args):
    """Remove entries for deleted torrents/downloads."""

    downloads = load_downloads()
    items = downloads.get("items", [])

    print()
    print("=" * 50)
    print("Prune Downloads")
    print("=" * 50)

    removed = 0
    cleared_downloads = 0
    kept = []

    for item in items:
        keep = True

        # Check torrent exists
        if item.get("torrent"):
            source_name = item["torrent"].split("/")[0]
            rel_path = "/".join(item["torrent"].split("/")[1:])
            base = TORRENT_BASES.get(source_name)
            if base and not (base / rel_path).exists():
                keep = False

        # Check download exists
        if keep and item.get("download"):
            source_name = item["download"].split("/")[0]
            rel_path = "/".join(item["download"].split("/")[1:])
            dl_path = DOWNLOADS.get(source_name)
            if dl_path and not (dl_path / rel_path).exists():
                item["download"] = None
                cleared_downloads += 1

        if keep:
            kept.append(item)
        else:
            removed += 1

    print(f"Removed torrents: {removed}")
    print(f"Cleared downloads: {cleared_downloads}")

    if args.dry_run:
        print(f"\n[DRY RUN] Would keep {len(kept)} entries")
        return 0

    if removed > 0 or cleared_downloads > 0:
        downloads["items"] = kept
        save_downloads(downloads)
        print(f"\n{GREEN}Saved:{NC} {DOWNLOADS_JSON}")

    return 0


# =============================================================================
# Helpers
# =============================================================================

def interactive_select(prompt: str, options: List[tuple]) -> Optional[str]:
    """Interactive selection menu."""
    print(f"\n{prompt}")
    for i, (key, label) in enumerate(options, 1):
        print(f"  [{i}] {label}")
    print(f"  [0] Cancel")

    try:
        choice = input("\nChoice: ").strip()
        if choice == "0" or not choice:
            return None
        idx = int(choice) - 1
        if 0 <= idx < len(options):
            return options[idx][0]
    except (ValueError, IndexError):
        pass

    print("Invalid choice")
    return None


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Media catalog management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # scan
    p_scan = subparsers.add_parser("scan", help="Scan for new items")
    scan_sub = p_scan.add_subparsers(dest="scan_type")

    p_scan_torrents = scan_sub.add_parser("torrents", help="Scan torrent files")
    p_scan_torrents.add_argument("--source", choices=list(TORRENT_BASES.keys()))
    p_scan_torrents.add_argument("--dry-run", action="store_true")

    p_scan_downloads = scan_sub.add_parser("downloads", help="Scan downloads")
    p_scan_downloads.add_argument("--source", choices=list(DOWNLOADS.keys()))
    p_scan_downloads.add_argument("--dry-run", action="store_true")

    # import
    p_import = subparsers.add_parser("import", help="Import to catalog")
    p_import.add_argument("--dry-run", action="store_true")

    # link
    p_link = subparsers.add_parser("link", help="Link to library")
    p_link.add_argument("--type", choices=["movies", "movies4k", "tv", "tv4k", "all"])
    p_link.add_argument("--dry-run", action="store_true")

    # status
    subparsers.add_parser("status", help="Show status")

    # prune
    p_prune = subparsers.add_parser("prune", help="Remove deleted entries")
    p_prune.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "scan":
        if args.scan_type == "torrents":
            return cmd_scan_torrents(args)
        elif args.scan_type == "downloads":
            return cmd_scan_downloads(args)
        else:
            print("Usage: ./catalog.py scan [torrents|downloads]")
            return 1
    elif args.command == "import":
        return cmd_import(args)
    elif args.command == "link":
        return cmd_link(args)
    elif args.command == "status":
        return cmd_status(args)
    elif args.command == "prune":
        return cmd_prune(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
