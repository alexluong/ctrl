# TASK-5: Mac Mini cleanup: scan and step list

Scan run 2026-10-02 from the MBP over `ssh mini`, read-only. Nothing changed on the Mini.
Rule for this task (Alex, 2026-10-02): Claude proposes, Alex approves each step before it runs. Media stack problems (`gluetun`, `seedboxapi`) are out of scope.

## State

- Disk: 228GB internal, 147GB used, 60GB free.
- Memory: 16GB; the media VM holds 7.9GB; everything else is small (Setapp agent 204MB, Chrome ~250MB, iTerm, Jump Desktop, iStat). 57% free. Apps are not what loads this machine; `spotlightknowledged` was at 97% CPU during the scan.
- Up 7 days. No cron, no tmux, no brew services. A Claude session is running on it.

## Hookdeck on the Mini

| What | Where | Size | Note |
|---|---|---|---|
| Colima profile `hookdeck` (stopped) | `~/.colima/hookdeck`, `_lima/colima-hookdeck`, `_lima/_disks/colima-hookdeck` | ~52GB | 6 CPU / 6GB / 50GB disk; holds Docker volumes from local dev |
| `hookdeck-workspace` | `~/git/hub/alexluong/hookdeck-workspace` | 4.7GB | **3 unpushed commits on `main`, 3 changed files**; last commit 2026-01-22 |
| `outpost` | `~/git/hub/hookdeck/outpost` | 720MB | **branch `model-delivery-event` 23 commits ahead of its remote, 29 stashes, 4 changed files**; last commit 2026-01-22 |
| `hookdeck-cli` | `~/git/hub/hookdeck/hookdeck-cli` | 11MB | 1 changed file |
| `core`, `outpost-2`, `website` | `~/git/hub/hookdeck/` | 1.3GB | clean, nothing unpushed |
| `dev-playground` | `~/git/hub/hookdeck/dev-playground` | 11MB | not a git repo: only copy |
| zshrc line | `~/.zshrc:33-34` | | sources `hookdeck-workspace/core/local-dev/completions.zsh`; breaks the shell start once the folder is gone |
| gcloud login | `~/.config/gcloud` | | `alex.luong@hookdeck.com`, configs `outpost-production`, `outpost-staging` |
| Azure login | `~/.azure` | | token cache present |
| Doppler | `~/.doppler` | | fallback secrets cache |
| Jumpbox key | `~/.ssh/jumpbox_ed25519`, `~/.ssh/config.d/jumpbox` | | config still has the placeholder `JUMPBOX_IP_HERE` |
| Editor/agent history | `~/.cursor/projects/*hookdeck*`, `~/.claude/projects/*hookdeck*` | | |
| Caches from that work | `~/Library/Caches/Yarn` 9.6GB, `go-build` 3.3GB, `~/.npm` 1.1GB, `~/.asdf` 5.5GB | ~19GB | |
| Tools only that work used | brew: `azure-cli`, `gcloud-cli`, `helm`, `minikube`, `mkcert`, `goreleaser`, `asdf`; apps: Postman, Bruno, Redis Insight; `~/.pm2` | | |

## Other repos

| Repo | State |
|---|---|
| `alexluong/arr` | 22 unpushed commits, 6 changed files, 2 stashes; replaced by `ctrl/media`, not yet compared |
| `alexluong/ctrl` | on `docs/mac-mini` (merged); local `main` shows 45 commits ahead: check before touching |
| `alexluong/dotfiles` | 4 changed files, 1 stash |
| `alexluong/ralph` | clean |
| `gh` on the Mini | login expired |

## Apps (`/Applications`)

Needed by what the Mini does: Plex Media Server, Tailscale, Jump Desktop Connect (remote screen), calibre (book library tools), iTerm.

Candidates to remove:

| Group | Apps |
|---|---|
| Work/dev | Slack, Postman, Bruno, Redis Insight, Figma, Notion, Fork, Visual Studio Code, Cursor leftovers (`~/.cursor` 1GB, app already gone), Toggl Track |
| Desktop comfort | Magnet, Karabiner-Elements, Second Clock, SnippetsLab, Pixea, Numbers, Setapp (+ iStat Menus, Paste, CleanMyMac agent that come with it) |
| Peripherals/gaming | Logitech G HUB, Logi Options+, Parsec |
| Passwords | 1Password and Bitwarden (both installed) |
| VPN | Private Internet Access app + its root daemon (the stack uses PIA inside `gluetun`, not this app) |
| Other | hakuneko (brew cask + app data), Google Chrome (3.1GB data + 2.7GB cache) |

Background items today: Setapp (4 agents), iStat Menus (2 agents + 2 root daemons), Google updater (3), Logitech G HUB (agent + updater daemon), CleanMyMac agent (root), Jump Desktop (agent + service), PIA daemon (root).

Apple side, signed in and syncing on a server: Messages (6.8GB), Photos (2.2GB + 4.4GB in `~/Pictures`), iCloud Drive (2.6GB), widgets (Weather, Stocks, News), Spotlight indexing.

## Docker (media VM)

15.3GB of images, 11.4GB not used by any container; one leftover container `relaxed_archimedes`.

## Space that would come back (estimate)

| Step | GB |
|---|---|
| Colima `hookdeck` profile | 52 |
| Hookdeck repos | 7 |
| Yarn / go-build / npm caches, `~/.asdf` | 19 |
| Chrome data + cache (if removed) | 6 |
| Messages + Photos (if signed out) | 13 |
| Unused Docker images (inside the 30GB VM disk, not the Mac's free space) | 11 |

About 80-95GB on the internal disk: 60GB free → roughly 140-155GB.

## Proposed order (each step waits for Alex)

1. Save or drop the unpushed hookdeck work (outpost branch + 29 stashes, `hookdeck-workspace` 3 commits, `dev-playground`).
2. Remove the zshrc line, then delete hookdeck repos and the Colima profile.
3. Log out and remove hookdeck credentials (gcloud, Azure, Doppler, jumpbox key).
4. Remove the dev tools and caches that only that work used.
5. Apps and background items, per the keep list.
6. Apple services (Messages, Photos, iCloud Drive, widgets, Spotlight on the external drives).
7. Docker image prune in the media VM.
8. Repos: compare `arr` with `ctrl/media`, move the ctrl clone to `main`, sort `dotfiles`.
9. Record free space, update `mac-mini.md` and `fleet.md`.

Removing apps that have root daemons (PIA, iStat, Logitech, CleanMyMac) needs sudo: Alex runs a script, as with `root-setup.sh`.

## Decisions

Alex, 2026-10-02:

- **Hookdeck work on the Mini: delete it, no need to save** the unpushed commits and stashes ("it's been a long time, no problem"). Still waits for his go on the actual delete.
- **Apps: keep the list, don't act yet.** Leanings: 1Password remove (definite), Bitwarden probably remove, Parsec remove, PIA app maybe, Setapp/iStat discuss later.
- The Mini is used at the screen only now and then, mainly to turn on Jump Desktop Connect. **Wanted: Jump Desktop Connect starts by itself at login.**
- Apple services (Messages, Photos, iCloud Drive): maybe, not yet.
- Claude on the Mini: keep for now.
- Open question he raised: what the Mini is for besides media (see `docs/fleet.md` § The Mini).

## Measurements for the "what is the Mini for" question (2026-10-02)

- Mini: M4 10 cores, 16GB. Container memory: qBittorrent 4.7GB, Jellyfin 457MB, calibre-web 189MB + 154MB, audiobookshelf 45MB, the rest under 60MB each. Moving books and audiobooks to g8 frees about 0.4GB on the Mini.
- g8: Ryzen 7 5700G (8 cores / 16 threads), 62GB RAM with 47GB free, 810GB free VM storage. `hookdeck-ws` has 32GB assigned.
- Jellyfin runs in a Linux container on the Mini, so it cannot use the M4's video hardware; Plex (native app) can.
- Books and audiobooks, all on Blue4: `media/books` 20GB, `media/audiobooks` 2GB, app config under `data/` about 12MB. Fits g8 easily (800GB free). Catch: new books arrive through qBittorrent on the Mini and are hardlinked into the library on the same drive; with the library on g8 each new book needs a copy step to g8.

## Jump Desktop Connect not starting at login (checked 2026-10-02, read-only)

Alex's experience: he has to turn it on by hand. What the Mini shows: the root service (`/Library/LaunchDaemons/com.p5sys.jump.connect.service.plist`) starts at boot and is kept alive. The per-user part (`/Library/LaunchAgents/com.p5sys.jump.connect.agent.plist`) has `RunAtLoad = 0`: it only starts when the service sends it a signal, not at login. Last boot and login were 2026-09-25; the user part was started 2026-10-02 17:09, so it did not come up by itself. Candidate fix (not applied): add the app to Login Items, or its own "start at login" setting; then test with a reboot.

## Ideas for using the Mini's CPU (2026-10-02, brainstorm, nothing decided)

- **Local CI** (Alex's idea): GitHub Actions self-hosted runner on the Mini for personal repos. VMs push a branch and the runner picks the job up from GitHub, so no VM holds a key to the Mini (keeps the fleet rule). Linux jobs in a small separate Colima VM (about 4 CPU / 4GB); Xcode jobs need a runner on macOS itself. Private repos only. Not for Hookdeck org repos without the company's say.
- Jellyfin as a native app (hardware transcoding), re-encode the library to HEVC, Whisper subtitles, Mac-only builds, backup target for g8.
