# Catalog Scripts Design

## Overview

Single `catalog.py` script manages media catalog: scan torrents, match downloads, import to library, track state.

## Data Model

**Flow**: Torrent → Download → Library

Two separate files:
- `downloads.json` - Torrent to download mapping (simple)
- `catalog.json` - Media library with full metadata

## Usage

```bash
./catalog.py scan torrents [--source blue4|red4] [--dry-run]
./catalog.py scan downloads [--source blue4|red4] [--dry-run]
./catalog.py import [--dry-run]
./catalog.py link [--type movies|movies4k|tv|tv4k|all] [--dry-run]
./catalog.py status
./catalog.py prune [--dry-run]
```

## Commands

### scan torrents

Scan torrent directories for new .torrent files, add to `downloads.json`.

- Only adds new torrents (existing entries preserved)
- Simple format: just torrent path and download path

### scan downloads

Match downloads to existing torrent entries.

- Finds downloads that match torrent filenames (normalized)
- Updates `download` field on matching entries

### import

Read `downloads.json`, parse metadata, add to `catalog.json` with status "pending".

- Parses title, year, resolution, source, group, video, audio, hdr from download name
- Adds entry to catalog.json with status "pending"
- Does NOT create hardlinks (use `link` for that)

### link

Read `catalog.json`, create hardlinks for pending items, update status to "linked".

- Routes by type + resolution:
  - movie + 1080p → movies/
  - movie + 2160p → movies4k/
  - tv + 1080p → tv/
  - tv + 2160p → tv4k/
- Creates hardlinks in library
- Updates entry status to "linked"

### status

Show status of both downloads.json and catalog.json.

### prune

Remove entries from `downloads.json` for torrents that no longer exist.

## Data Files

### downloads.json

Simple torrent → download mapping:

```json
{
  "items": [
    {
      "torrent": "blue4/dc/Movie.2020.1080p.BluRay.torrent",
      "download": "blue4/Movie.2020.1080p.BluRay/"
    },
    {
      "torrent": "blue4/dc/Show.S01.1080p.WEB.torrent",
      "download": null
    }
  ]
}
```

### catalog.json

Media library with full metadata:

```json
{
  "items": [
    {
      "title": "Movie Name",
      "year": 2020,
      "type": "movie",
      "resolution": "1080p",
      "source": "BluRay",
      "group": "KIMJI",
      "video": "AV1",
      "audio": "Opus",
      "hdr": "",
      "download": "blue4/Movie.2020.1080p.BluRay/",
      "library": "blue4/movies/Movie Name (2020)/",
      "status": "linked"
    },
    {
      "title": "Show Name",
      "seasons": [1, 2, 3],
      "type": "tv",
      "resolution": "2160p",
      "source": "WEB-DL",
      "group": "FLUX",
      "video": "x265",
      "audio": "DD+",
      "hdr": "DV HDR10",
      "download": "red4/Show.S01-S03.2160p.WEB/",
      "library": "red4/tv4k/Show Name/",
      "status": "linked"
    }
  ]
}
```

**Fields:**
| Field | Description |
|-------|-------------|
| `title` | Parsed title |
| `year` | Movie year |
| `seasons` | TV seasons (array) |
| `type` | `movie` or `tv` |
| `resolution` | `1080p`, `2160p`, etc. |
| `source` | `BluRay`, `WEB-DL`, `WEBRip`, etc. |
| `group` | Release group |
| `video` | `AV1`, `x265`, `x264`, etc. |
| `audio` | `Atmos`, `TrueHD`, `DD+`, `Opus`, etc. |
| `hdr` | `DV HDR10`, `HDR10`, `HDR`, `SDR`, etc. |
| `download` | Path in downloads folder |
| `library` | Path in media library (set after link) |
| `status` | `pending` or `linked` |

## Workflow

```
1. Add torrent to ~/Documents/pt/{blue4,red4}

2. ./catalog.py scan torrents
   → New entries added to downloads.json (download: null)

3. Download completes in /downloads

4. ./catalog.py scan downloads
   → Entries updated with download path

5. ./catalog.py import
   → Parses metadata from download name
   → Adds entry to catalog.json (status: pending)

6. (Optional) Review/fix catalog.json entries

7. ./catalog.py link
   → Creates hardlinks in library
   → Updates status to "linked"

8. ./catalog.py status
   → View pending/linked counts
```

## Resolution Detection

**Actual 4K (→ movies4k/tv4k):**
- `2160p` in filename
- `4K` + `HDR` in filename
- `UHD` (not just "UHD BluRay" source)

**Not 4K (→ movies/tv):**
- `DS4K` = downscaled from 4K = 1080p
- `RM4K` = remastered from 4K = 1080p
- `1080p`, `720p`, etc.

## Directory Structure

```
~/Documents/pt/
├── blue4/              # Torrent files for Blue4 downloads
└── red4/               # Torrent files for Red4 downloads

/Volumes/Blue4/arr/
├── downloads/          # Downloaded content
└── media/
    ├── movies/         # 1080p movies
    ├── movies4k/       # 4K movies
    ├── tv/             # 1080p TV
    └── tv4k/           # 4K TV

/Volumes/Red4/arr/
├── downloads/
└── media/

/catalog/
├── downloads.json      # Torrent → download mapping
├── catalog.json        # Media library
└── scripts/
    └── catalog.py      # Main script
```

## Editing catalog.json

**Always use scripts to modify catalog.json** - never edit manually.

```bash
# Use catalog.py commands for standard operations
./catalog.py import      # Add new entries
./catalog.py link        # Create hardlinks
./catalog.py prune       # Remove stale entries

# For custom edits, write a Python script:
python3 << 'EOF'
import json

with open('../catalog.json', 'r') as f:
    catalog = json.load(f)

# Make changes...
for item in catalog['items']:
    if item['title'] == 'Some Title':
        item['library'] = 'blue4/movies/New Path'

with open('../catalog.json', 'w') as f:
    json.dump(catalog, f, indent=2)
EOF
```

Why scripts over manual edits:
- JSON syntax errors break everything
- Easy to miss commas, quotes, brackets
- Scripts can validate before saving
- Reproducible changes

## Schema

### catalog.json

```json
{
  "items": [CatalogItem, ...]
}
```

### CatalogItem (Movie)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | yes | Display title |
| `year` | number | yes | Release year |
| `type` | `"movie"` | yes | Media type |
| `resolution` | string | yes | `1080p`, `2160p`, etc. |
| `source` | string | no | `BluRay`, `WEB-DL`, `WEBRip` |
| `group` | string | no | Release group |
| `video` | string | no | `AV1`, `x265`, `x264` |
| `audio` | string | no | `Atmos`, `TrueHD`, `DD+`, `Opus` |
| `hdr` | string | no | `DV HDR10`, `HDR10`, `HDR`, `SDR` |
| `download` | string | yes | Path in downloads (empty for external) |
| `library` | string | yes | Path in media library |
| `status` | string | yes | `pending`, `linked`, `external` |

### CatalogItem (TV)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | yes | Display title |
| `seasons` | number[] | yes | Array of season numbers |
| `type` | `"tv"` | yes | Media type |
| `resolution` | string | yes | `1080p`, `2160p`, etc. |
| `source` | string | no | `BluRay`, `WEB-DL`, `WEBRip` |
| `group` | string | no | Release group |
| `video` | string | no | `AV1`, `x265`, `x264` |
| `audio` | string | no | `Atmos`, `TrueHD`, `DD+`, `Opus` |
| `hdr` | string | no | `DV HDR10`, `HDR10`, `HDR`, `SDR` |
| `download` | string | yes | Path in downloads (empty for external) |
| `library` | string | yes | Path in media library |
| `status` | string | yes | `pending`, `linked`, `external` |

### Status Values

| Status | Description |
|--------|-------------|
| `pending` | Imported but not yet linked |
| `linked` | Hardlinked from downloads to library |
| `external` | Not from DC (no download path) |

## Naming Conventions

### Library Folder Names

- **Movies**: `Title (Year)` - e.g., `Blade Runner 2049 (2017)`
- **TV**: `Title` - e.g., `Breaking Bad`, `The Office (US)`
- Preserve special characters: colons, apostrophes, parentheses
- One folder per title (consolidate seasons for TV)

### Common Issues

**Multi-season TV shows**: Import may create separate entries per season. Consolidate into single entry with `seasons: [1, 2, 3, ...]`.

**Title mismatches**: Parser may not match user's preferred title. Library folder name is the source of truth.

**Duplicate resolutions**: Same title in both 1080p and 4K is valid - separate entries, separate library folders.

**External content**: Media not from DC should have `status: "external"` and empty `download` field.
