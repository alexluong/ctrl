---
name: import
description: Import new bank statements or PM data into the LLC ledgers
user_invocable: true
---

# Bookkeeping Import

Import new financial data (bank exports, PM statements) into the LLC ledgers.

## Instructions

1. Read `biz/BOOKKEEPING.md` for format reference
2. Identify the source: Mercury CSV, Wise CSV, Relay CSV, or PM statement PDF
3. Identify the LLC: RE (Collie MI Properties) or Studio (Collie Studio)
4. Process the raw data:
   - Copy raw file to appropriate `raw/` directory
   - For CSVs: filter out Failed/Cancelled, convert dates to ISO, categorize
   - For PM PDFs: read the Owner Packet, extract transaction tables, categorize
5. Append cleaned transactions to the appropriate `transactions.csv`
6. Sort by date
7. Verify no duplicates (check date+amount+description combinations against existing entries)

## Format reference

RE ledger columns: `date,property,description,amount,type,category,source,notes`
Studio ledger columns: `date,description,amount,type,category,account,notes`

## Source mapping

| Raw source | RE source value | Studio account value |
|---|---|---|
| Mercury CSV | mercury | mercury-xx7792 or mercury-xx8595 |
| Wise CSV | wise | (use Wise account ID) |
| Relay CSV | relay | relay |
| Tradewinds PM PDF | tradewinds_pm | n/a |
| Grant & Main PM PDF | grantmain_pm | n/a |

## PM statement location

Grant & Main PDFs: `~/Documents/REI/statements/{month folder}/Owner Packet.pdf`
Copy new downloads there first, unzip if needed, then extract data.
