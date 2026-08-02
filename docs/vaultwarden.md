# Vaultwarden

Self-hosted password manager. `vault.collie.studio` → collielab VM (Vultr), Docker,
behind Caddy + Cloudflare. Compose lives in the `collielab` repo at
`services/vaultwarden/`; this doc is the decisions and operating model, not the config.

## Layout (settled 2026-08-02)

Two accounts, two orgs. Both accounts are on the same self-hosted instance.

| | Holds | Notes |
|---|---|---|
| `alex@alexluong.com` | ~300 items, 8 folders | main Chrome profile |
| `alex.luong@enable.tech` | 32 items | **dedicated Chrome profile** |
| org `Collie Studio` | 8 items | owned by personal; the LLC |
| org `Shared` | GitHub etc. | personal + ENABLE both members |

WishTender and Hookdeck (former jobs) are **archived**, not deleted — hidden from
search and autofill, still retrievable.

### Why accounts vs orgs vs folders

Four independent axes; picking the wrong one is the usual mistake:

- **Account** — scopes *what a client sees*. The only mechanism that limits the
  extension's item list. This is the entire justification for a separate ENABLE
  account: the work Chrome profile shows ~36 items instead of ~341, and
  `accounts.google.com` autofills 1 candidate instead of 6.
- **Org** — controls *who can access*. Use when a second person might need in, or
  when an entity should own the items. Collie Studio is an org (not an account) so a
  bookkeeper can later get one collection without touching anything else.
- **Folder** — *how you browse*. Private, per-user, one folder per item.
- **Archive** — *whether it shows up*. Private, per-user, reversible.

The ENABLE login identity itself is worth ~nothing — we self-host, nobody verifies
that email, and it grants no access. The scoping is the whole value.

**No tags.** Bitwarden has never shipped them (open request since 2018), so an item
lives in exactly one folder. Folders nest with `/` in the name.

**Don't add a third account.** Each one is another master password, and with no SMTP
there is **no reset** — losing it means losing that vault.

## Folders (personal vault)

Cut by *context you're in*, not service type — you always know the context, and
contexts stay stable while services churn.

| Folder | ~n | |
|---|---|---|
| `Dev` | 96 | cloud, data, infra, monitoring, APIs, tooling, AI |
| `Life` | 58 | media, social, shopping, travel |
| `Finance` | 43 | banking, trading, crypto |
| `Accounts & Home` | 24 | identity anchors, SSN/GPG, router, gov |
| `Projects` | 21 | own side projects, grouped per project |
| `Vietnam` | 15 | `.vn` services, VNeID, e-tax, Zalo |
| `Real Estate` | 14 | incl. Collie MI Properties entity docs |
| `Career & Learning` | 8 | job hunting, courses |

`Dev` is a third of the vault — acceptable because it's searched, not browsed.
Split to `Dev` + `Dev/Infra` if it ever chafes.

## Adding new items

**Save it, don't file it.** Filing at save time is where these systems die.

1. Never pick a folder when saving. Unfoldered *is* the inbox ("No folder" is a
   real filter).
2. The **Chrome profile decides the account** — nothing to remember.
3. Shared-in-both credential? Still just save it; it gets moved to the `Shared` org
   at triage.

### Triage (Claude, monthly-ish or when unfiled > ~20)

Alex exports unencrypted JSON → Claude classifies unfiled items, proposes moves,
applies via `bw` CLI → export deleted. Each pass also flags: work creds that landed
in personal, items belonging in an org, dead accounts to archive, new password reuse.

Plaintext exports never enter this repo and are deleted after use.

## Operations

- **Upgrade regularly.** The 2026-08-02 outage was version skew: server sat at
  1.35.4 (Feb image) while the auto-updating Chrome extension moved on. Login
  worked, the vault never populated, and the server logged nothing but 200s.
  Clients ≥ 2026.7.0 need Vaultwarden ≥ 1.37.
- **Item archiving needs ≥ 1.36.** Stored in a separate `archives` table, not a
  column on `ciphers`, and **not present in exports** — so an export can't tell you
  what's archived.
- **Self-registration is closed** (`SIGNUPS_ALLOWED=false`). New users come from the
  `/admin` panel; invitations bypass it. Note `/api/config` still reports
  `disableUserRegistration: false` regardless — that field is not wired up, so test
  behaviour, don't trust the flag.
- **No SMTP.** Consequences: no email verification, **no password reset**, and org
  invites **auto-accept**. But accepted ≠ confirmed — an owner must hit
  **Confirm** or the member never receives the org key and silently sees nothing.
- `ADMIN_TOKEN` lives in `services/vaultwarden/.env` (gitignored, chmod 600) because
  that repo has a public remote.
- **Caddy real-IP**: `header_up X-Real-IP {http.request.header.Cf-Connecting-Ip}` —
  braces required. Without them Caddy sends the literal string, every request logs as
  the Docker bridge IP, and failed-login throttling keys on one bucket.
- Backups: `~/backups/vw-data-*.tar.gz` on the VM (full data dir incl. attachments
  and `rsa_key.pem`). Take one before any DB-level change.

### What Claude can and can't do server-side

The vault is end-to-end encrypted; the server holds ciphertext and no key.

- **Can** (metadata only): archive/unarchive, delete items, assign items to
  *existing* folders, delete folders, purge trash, manage accounts/invites, upgrade,
  read counts and dates.
- **Can't** (needs the key): read any item's name/username/password, create items,
  create a folder (the *name* is encrypted), move items into an org (re-encryption).

So cataloguing requires an export, and anything creating ciphertext runs through the
`bw` CLI locally (`mise use -g bitwarden`) — never through Claude.

One leak worth knowing: `/data/icon_cache` stores favicons as **plaintext
domain-named files**, so anyone with server or backup access can enumerate every
service with an account, without decrypting anything. Accepted; `DISABLE_ICON_DOWNLOAD=true`
plus clearing the dir would close it.

## Accepted, not fixed

- Password reuse exists across some items; triage flags it, Alex prioritises.
- Trash isn't auto-purged (`TRASH_AUTO_DELETE_DAYS` unset) — soft-deleted items
  accumulate. Harmless, left alone.
- Favicon cache leak above.
