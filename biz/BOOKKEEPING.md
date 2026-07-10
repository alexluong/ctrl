# Bookkeeping System

CSV ledgers in git. Claude manages all data entry, reconciliation, and reporting. Plain CSV — no external tooling dependencies.

## Architecture

- Single CSV ledger per LLC — all sources merged, `source` column for provenance
- Every cent tracked: acquisitions, operations, transfers, fees, interest — everything
- Raw bank/PM exports preserved in `raw/` subdirectories
- PM statement PDFs stay in iCloud at `~/Documents/REI/statements/`
- Balance sheet ledger (TODO) for assets/liabilities tracking

## LLCs

### Collie MI Properties LLC (RE)

Path: `re/bookkeeping/`

Sources & coverage:
| Source | Account | Coverage | In Ledger | Status |
|---|---|---|---|---|
| Wise | 88882279 | May 2024 – Dec 2025 | ✅ complete | active |
| Tradewinds PM | — | Jul – Dec 2024 | ✅ complete | terminated |
| Grant & Main PM | — | Dec 2024 – Feb 2026 | ✅ complete | active |
| Mercury | xx3810 | Jul 2025 – Mar 2026 | ✅ complete | closed |
| Relay | — | — | — | new, no data yet |

Ledger: `transactions.csv` — 465 rows, Jul 2024 – Mar 2026
Columns: `date,property,description,amount,type,category,source,notes`

Properties: `oakfield` (20259 Oakfield, Detroit 48235), `haverhill` (4300 Haverhill, Detroit 48224), `dixie` (15490 Dixie, Redford — closed 2026-05)

### Collie Studio LLC (software)

Path: `biz/studio/bookkeeping/`

Sources & coverage:
| Source | Account | Coverage | In Ledger | Status |
|---|---|---|---|---|
| Mercury | xx7792/xx8595 | 2022 – Apr 2026 | ✅ complete | closed |
| Wise | 53833530 | Mar 2023 – Dec 2025 | raw only | active |
| Relay | — | — | — | new, no data yet |

Ledger: `transactions.csv` — 387 rows, 2022 – Apr 2026
Columns: `date,description,amount,type,category,account,notes`

## Column Reference

- **date** — YYYY-MM-DD
- **property** — (RE only) oakfield, haverhill, or blank for LLC-level
- **description** — what happened
- **amount** — positive = inflow, negative = outflow
- **type** — `revenue`, `expense`, `owner_contribution`, `transfer`, `distribution`, `contractor_payment`
- **category** — specific category (rent, insurance, plumbing, management_fee, etc.)
- **source/account** — where the data came from (mercury, wise, relay, tradewinds_pm, grantmain_pm)
- **notes** — optional context

## Property-Source Mapping (RE)

Insurance paid from Wise:
- REInsurePro → haverhill
- Breckenridge, OSC INS SVCS → oakfield
- Foremost (Farmers) → dixie
- New provider (Apr 2026+) → TBD, covers oakfield + haverhill

Detroit Water from Wise → oakfield (haverhill water goes through PM)

## Double-Counting Prevention

Owner contributions flow: Personal → Wise → PM trust account (or direct vendor).
They appear in the ledger ONCE, at the point of operational impact:
- PM-side contributions: recorded as `owner_contribution` with source `tradewinds_pm` or `grantmain_pm`
- Wise-side direct expenses (insurance, water, tax, acquisition): recorded with source `wise`
- The Wise→PM transfers are NOT separately recorded as expenses (they'd duplicate the PM-side contribution)

Mercury→Wise transfers and Wise→Mercury transfers are recorded as `transfer` type.

## Adding New Data

1. Copy raw export to `raw/` (preserve original filename)
2. For PM PDFs: copy to iCloud `~/Documents/REI/statements/`, unzip, read Owner Packet
3. Parse into ledger format, assign property where applicable
4. Deduplicate against existing entries (date + amount + description + source)
5. Append and sort by date
6. Use `/import` skill for guided workflow

## Reconciliation

Run periodically:
- Cross-check Wise outflows to PM trust vs PM-side owner contributions (should match)
- Verify PM cash balances carry forward month-to-month
- Check Mercury/Wise/Relay bank balances against statements
- Use `/report` skill for P&L, per-property, or tax summaries

## TODO

- [ ] Balance sheet ledger (assets: properties at cost basis, bank balances; liabilities: loans; equity: contributions - distributions)
- [ ] Clean Studio Wise data into transactions.csv
- [ ] Mar 2026 Grant & Main PM statement (not yet available)
- [ ] 2024 tax report
- [ ] Relay account data (both LLCs) once transactions exist
- [ ] New insurance provider records (Apr 2026+)
