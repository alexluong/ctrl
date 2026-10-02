# Media Catalog

Structured catalog for the arr media library with torrent-first tracking.

## Quick Start

```bash
cd catalog/scripts

# 1. Scan torrent files
./catalog.py scan torrents

# 2. Scan downloads (match to torrents)
./catalog.py scan downloads

# 3. Import to catalog (parse metadata)
./catalog.py import

# 4. Link to library (create hardlinks)
./catalog.py link

# 5. Check status
./catalog.py status
```

## Files

| File | Purpose |
|------|---------|
| `downloads.json` | Torrent to download mapping |
| `catalog.json` | Media library with full metadata |

## Commands

### Scan Torrents

```bash
./catalog.py scan torrents               # scan all sources
./catalog.py scan torrents --source blue4  # scan Blue4 only
./catalog.py scan torrents --dry-run     # preview without saving
```

### Scan Downloads

```bash
./catalog.py scan downloads              # match downloads to torrents
./catalog.py scan downloads --source blue4
./catalog.py scan downloads --dry-run
```

### Import to Catalog

```bash
./catalog.py import              # parse metadata, add to catalog.json
./catalog.py import --dry-run    # preview without saving
```

### Link to Library

```bash
./catalog.py link                    # interactive type selection
./catalog.py link --type movies      # only 1080p movies
./catalog.py link --type movies4k    # only 4K movies
./catalog.py link --type tv          # only 1080p TV
./catalog.py link --type tv4k        # only 4K TV
./catalog.py link --type all         # everything
./catalog.py link --dry-run          # preview without linking
```

### Status

```bash
./catalog.py status                  # show pending/linked counts
```

### Prune

```bash
./catalog.py prune                   # remove entries for deleted torrents
./catalog.py prune --dry-run         # preview
```

## Workflow

1. **Add torrent** to `~/Documents/pt/blue4` or `~/Documents/pt/red4`

2. **Scan torrents** to add to downloads.json:
   ```bash
   ./catalog.py scan torrents
   ```

3. **Download** completes to `/Volumes/Blue4/arr/downloads`

4. **Scan downloads** to match:
   ```bash
   ./catalog.py scan downloads
   ```

5. **Import** to parse metadata and add to catalog:
   ```bash
   ./catalog.py import
   ```

6. **(Optional)** Review/fix catalog.json entries

7. **Link** to create hardlinks in library:
   ```bash
   ./catalog.py link
   ```

8. **Verify** with status:
   ```bash
   ./catalog.py status
   ```

## Storage Locations

### Torrent Files
- **Blue4**: `~/Documents/pt/blue4/`
- **Red4**: `~/Documents/pt/red4/`

### Blue4 (WD Blue 4TB)
- **Downloads**: `/Volumes/Blue4/arr/downloads/`
- **Library**: `/Volumes/Blue4/arr/media/`
  - `movies/` - 1080p movies
  - `movies4k/` - 4K movies
  - `tv/` - 1080p TV
  - `tv4k/` - 4K TV

### Red4 (WD Red 4TB)
- **Downloads**: `/Volumes/Red4/arr/downloads/`
- **Library**: `/Volumes/Red4/arr/media/`

## Resolution Detection

| Pattern | Resolution | Library |
|---------|-----------|---------|
| `2160p` | 4K | movies4k / tv4k |
| `4K` + `HDR` | 4K | movies4k / tv4k |
| `UHD` | 4K | movies4k / tv4k |
| `DS4K` | 1080p | movies / tv |
| `RM4K` | 1080p | movies / tv |
| `1080p` | 1080p | movies / tv |

## Encoding Detection

The import command detects encoding metadata from filenames:

| Field | Values |
|-------|--------|
| `video` | AV1, x265, x264, VP9, XviD |
| `audio` | Atmos, TrueHD, DTS-HD, DTS, DD+, DD, Opus, FLAC, AAC |
| `hdr` | DV HDR10, DV, HDR10+, HDR10, HDR, SDR |

## Hardlinks

Hardlinks allow the same file to exist in two locations (downloads + library) using zero extra disk space.

```
downloads/movie.mkv  ──┐
                       ├──► [actual data on disk]
media/movie.mkv      ──┘
```

- Delete from `/downloads` → `/media` still works
- Delete from `/media` → `/downloads` still works
- Delete both → data actually deleted

**Limitation**: Only works on same filesystem/volume.
