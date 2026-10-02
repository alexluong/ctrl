# TASK-2: two clock problems on kernel 7.0.14 (found 2026-10-02)

Both appeared with the first boot of kernel 7.0.14-20-pve (Proxmox 9.2.21); the three boots on 6.14.8-2-pve were clean. BIOS: T26 02.02.00 (2021-11-03).

## 1. Timer fallback: TSC marked unstable, kernel runs on HPET (the one that matters)

- dmesg at 3.7s: `clocksource: timekeeping watchdog on CPU6: Marking clocksource 'tsc' as unstable because the skew is too large` (tsc skewed -3.5ms over a 507ms HPET interval), then `TSC found unstable after boot, most likely due to broken BIOS. Use 'tsc=unstable'`, then `Switched to clocksource hpet`.
- `current_clocksource` = `hpet`; available: `hpet acpi_pm` (TSC removed from the list). CPU flags still say `constant_tsc nonstop_tsc`.
- Cost measured on the host: reading the clock takes ~1400 ns per call (Python loop, 2M calls). With TSC it is typically well under 100 ns. Time reads are everywhere in databases, Kafka, Node and Docker, and VMs depend on the host's TSC for their own fast clock, so this slows the workloads the box was bought for.
- Seen on one boot only so far; not yet known whether it repeats on every 7.0 boot.
- Suspects: the 2021 BIOS (AMD fixed firmware-TPM stalls in 2022 firmware, and stalls like that make the watchdog misjudge the TSC), or a stricter watchdog in the newer kernel.

## 2. No hardware-clock device (`/dev/rtc0` missing)

- 6.14: `rtc_cmos 00:02: registered as rtc0` (attached through the PNP layer).
- 7.0: the clock chip shows up as platform device `PNP0B00:00` (I/O 0x70-0x71 claimed), no driver attached, nothing logged. `/sys/bus/pnp/devices` is empty; `hwclock` fails; `timedatectl` shows `RTC time: n/a`.
- Cause: a February 2026 kernel rework by the ACPI maintainer that moved the CMOS clock from PNP devices to platform devices ("ACPI: x86/rtc-cmos: Use platform device for driver binding", commit 2a78e4210444, plus "ACPI: PNP: Drop CMOS RTC PNP device support"). It is known to have broken attachment on some machines (`rtc_cmos PNP0B00:00: error -ENXIO: IRQ index 0 not found`), with a follow-up fix. This box fails silently, so it may be a variant; this BIOS lists no interrupt for the clock chip, which the old code worked around.
- Effect: time is still right (read at boot, kept by chrony). The hardware clock is no longer written back; no wake alarms. Low impact.

## Options

1. Boot the installed 6.14.11-9-pve kernel and pin it (`proxmox-boot-tool kernel pin 6.14.11-9-pve`): expect both problems gone; older kernel line.
2. Install and pin `proxmox-kernel-6.17` (6.17.13-21): newer than 6.14, predates the February 2026 rework.
3. BIOS update (at the box, HP network update), then retest 7.0.
4. Stay on 7.0 with `tsc=reliable` on the kernel command line (turns the watchdog off); does nothing for problem 2.

## Sources

- https://lkml.iu.edu/2602.2/08357.html ([PATCH v1 4/8] ACPI: x86/rtc-cmos: Use platform device for driver binding)
- https://lkml.iu.edu/2602.2/08344.html ([PATCH v1 5/8] ACPI: PNP: Drop CMOS RTC PNP device support)
- https://lkml.iu.edu/2602.2/08354.html ([PATCH v1 6/8] x86: rtc: Drop PNP device check)
- https://lkml.iu.edu/hypermail/linux/kernel/2603.0/05152.html (regression report and fix confirmation)
