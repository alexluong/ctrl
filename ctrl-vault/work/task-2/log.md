# TASK-2 log: every change made to the G8, the router and the MBP

Newest last. One entry per change: what, why, how to undo. Read-only checks go in `discovery.md`; decisions in `plan.md` and `docs/home-systems.md`.

## 2026-09-30

- **BIOS (Alex, at the box):** After Power Loss = Power On (Advanced → Boot Options). SVM was already on.
- **Root password (Alex, at the box):** changed with `passwd` from the shop's.
- **Memtest86+:** pass 1, 0 errors.
- **Moved to the router**, wired. Reachable at `192.168.1.21` (shop's static config, unchanged).

## 2026-10-02

- **G8 `authorized_keys` (Alex):** added the MBP's `id_ed25519` public key with `ssh-copy-id`. Undo: delete that line from `/etc/pve/priv/authorized_keys`.
- **MBP agent (Alex):** `ssh-add --apple-use-keychain ~/.ssh/id_ed25519` (passphrase saved in Keychain) so Claude can use the key. Undo: `ssh-add -d ~/.ssh/id_ed25519`.
- **MBP `known_hosts`:** host key for `192.168.1.21` accepted on first connect.
- Discovery run (read-only): `discovery.md`.
