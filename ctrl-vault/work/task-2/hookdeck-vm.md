# TASK-2: the hookdeck VM (built 2026-10-02)

VM 101 on g8, `hookdeck.lab.alexluong.com` = `192.168.1.101`, `ssh hookdeck` (user `alex`, passwordless sudo). 8 vCPU, 32GB RAM (fixed, no ballooning), 250GB thin disk, starts with the host. Debian 13 from the base template.
Scripts and runbook: `collielab/hosts/g8/README.md`. What the workspace needs and why: `hookdeck-vm-requirements.md`. T3: `docs/t3-code-remote.md`. Change log: `log.md`.

**The living doc for this VM is `docs/vms/hookdeck.md`** (tools, logins and their state, secret files, first run). This file keeps the build-day state and decisions.

## State when handed over

Ready, with no login and no secret on it:

- Base: Docker + compose, gh, git, mise, Node 22, Claude Code 2.1.287, T3 Code server 0.0.44 running as a user service on `127.0.0.1:3773`.
- Hookdeck tools: Doppler CLI, every tool pinned by the workspace `mise.toml` (node 22.22.0, go 1.26.1, gcloud, kubectl, terraform, awscli, railway, backlog.md, jq, gh), `gopls`, `golangci-lint`, Playwright's Chromium libraries, the stacks' public Docker images pre-pulled (`~/prepull-images.log`).
- Global Claude config: `~/.claude/settings.json` and `CLAUDE.md` copied from the dotfiles repo (plain copies; no secrets in them).
- An SSH key for GitHub generated on the VM (`~/.ssh/id_ed25519`, not yet registered anywhere).
- Proxmox snapshot `clean-setup` of this state (`qm rollback 101 clean-setup` on g8).

## First run (Alex)

1. `ssh hookdeck`
2. `claude` → log in.
3. `gh auth login` → GitHub.com, SSH, upload the existing key `~/.ssh/id_ed25519.pub`. The key needs access to the `hookdeck` and `amp-labs` orgs (authorize SSO if asked).
4. Workspace:
   ```sh
   git clone -b workspace git@github.com:alexluong/hookdeck-workspace.git ~/workspaces/hookdeck
   cd ~/workspaces/hookdeck && mise trust && mise install && mise trust ops/*/mise.toml && bin/wt init
   gcloud components install gke-gcloud-auth-plugin
   ```
5. Secrets, from the MBP (after step 4 so the folders exist; skip what the VM should not hold):
   ```sh
   cd ~/workspaces/hookdeck && rsync -avR --ignore-missing-args \
     .env ops/prd/.env ops/prd-rw/.env ops/stg/.env ops/prd/outpost/ .gcloud/ .kube/ \
     wt/core/main/local-dev/env/.env.dev wt/outpost/main/.env wt/outpost/main/.outpost.yaml \
     wt/outpost/main/spec-sdk-tests/.env wt/terraform-provider-hookdeck/main/.env.test wt/amp-server/main/.env \
     hookdeck:workspaces/hookdeck/
   ```
6. T3 app on the MBP: Settings → Connections → Add environment → SSH → `hookdeck`. Then Settings → Providers → that environment → enable Claude. Add the project `~/workspaces/hookdeck`.
7. As needed: `doppler login`, `railway login`, `hookdeck login`, `aws sso login --profile personal`, Notion MCP (`/mcp` in a session), the `hd_jumpbox` SSH hosts and key for `prd pg`, `~/.npmrc`.
8. Core stack, first time: in `wt/core/main`: `corepack enable && pnpm install`, then `pnpm start -n hookdeck-local` (snags: the `core-local-dev` skill).

## Decisions made while building (Claude, 2026-10-02)

| Decision | Why | To change |
|---|---|---|
| Scripts in `collielab` (`hosts/g8`, `hosts/workspace-vm`, `hosts/hookdeck`, `bin/new-vm`) | Alex: ctrl or collielab, not a new repo; `fleet.md` already put machine config there | n/a |
| Template built by booting the cloud image and running a shell script in it, then sealing | the same script updates an existing VM or any Debian machine; no extra tooling on the host | `hosts/g8/vm-template/` |
| Full clones, not linked | a VM survives the template being rebuilt or deleted; costs ~3GB each | `--full 0` in `new-vm.sh` |
| `cpu: host`, memory fixed (balloon off) | best performance on a single host; predictable memory for databases | `qm set 101 --balloon <MB>` |
| Passwordless sudo for `alex` in workspace VMs | agents cannot type a password; the VM is the isolation boundary | `/etc/sudoers.d/90-dev-user` |
| T3 server on loopback, reached over SSH | no unencrypted agent traffic on the home network | `T3_HOST=0.0.0.0` in `hosts/workspace-vm/setup.sh` |
| T3 pinned to 0.0.44 | must match the MBP app | `T3_VERSION` in `provision.sh`, `t3 update` in VMs |
| Docker container logs capped (3 × 50MB) | uncapped logs were part of the disk growth on the MBP | `/etc/docker/daemon.json` |
| `*.localhost` prefers IPv4 (`/etc/gai.conf`) | core's Caddy listens on 127.0.0.1:80 only; Debian answers `::1` first | remove the line |
| Global Claude settings copied as files | dotfiles repo needs a GitHub login to clone | clone dotfiles, symlink as on the Mac |
| No credentials copied from the MBP | Alex: logins and secrets are his | first-run steps above |

## Open points for Alex

1. **Where hookdeck sessions run from now on.** The board, memory and digest are committed from wherever sessions run; using both the MBP and the VM will conflict. Push the MBP's unpushed work first (`wt/core/task-23` was dirty on 2026-10-02).
2. **Opening the core dashboard from the MBP.** The stack's URLs are `http://<ns>.localhost` on the VM's own port 80. Options: `ssh -L 80:127.0.0.1:80 hookdeck` while the MBP's own stack is stopped (then the same URLs work on the Mac); the gateway (TASK-3); or `pnpm start --tailscale` once Tailscale exists.
3. **Which secrets live on an always-on agent machine.** `.env.test` holds prod API keys and gcloud `prd` can write. The guard hooks prevent accidents; they are not a boundary.
4. **Dev ports are open to the home network** (outpost and the PM2 services listen on all addresses). Fine at home; a firewall rule on the VM's network card in Proxmox can limit it to the MBP.
5. **Go pin** (1.26.1) is behind outpost and amp-server (1.27.1); works through Go's automatic toolchain download.
6. **No backups yet.** Snapshots live on the same disk. Backup target is the Mini (`plan.md` § Later).
7. **macOS paths inside the workspace** that will need a look on Linux: listed in `hookdeck-vm-requirements.md` § E.

## Useful

- Proxmox: `qm list`, `qm snapshot 101 <name>`, `qm rollback 101 <name>`, `qm shutdown 101`, `qm start 101` (on g8).
- T3 service on the VM: `t3 service status`, `systemctl --user restart t3code`, logs `~/.t3/userdata/logs/boot-service.log`.
- Disk: `docker system df`, `go clean -cache`, `bin/wt rm`; `sudo fstrim -av` gives freed space back to the host (also runs weekly).
- Bring the VM up to a newer base: `ssh hookdeck 'sudo bash -s' < hosts/g8/vm-template/provision.sh`, then `ssh hookdeck 'bash -s' < hosts/hookdeck/setup.sh` (both idempotent).
