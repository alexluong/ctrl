---
name: report
description: Generate financial reports for the LLCs (P&L, per-property, by-period, tax summaries)
user_invocable: true
---

# Bookkeeping Report

Generate financial reports from the LLC ledger data.

## Instructions

1. Read `biz/BOOKKEEPING.md` for system documentation and data source reference
2. Read the relevant ledger(s):
   - RE: `re/bookkeeping/transactions.csv` (columns: date,property,description,amount,type,category,source,notes)
   - Studio: `biz/studio/bookkeeping/transactions.csv` (columns: date,description,amount,type,category,account,notes)
3. Parse the user's request to determine: which LLC, what period, what kind of report
4. Compute the report from CSV data using Bash (awk/python one-liners) or by reading and computing inline
5. Present results in a clear markdown table

## Common report types

- **P&L**: Revenue vs expenses by category for a period
- **Per-property**: Filter by property column (oakfield/haverhill) for RE
- **Tax summary**: Group by tax-relevant categories (rental income, repairs, depreciation, management fees, legal, utilities, property taxes, insurance)
- **Cash flow**: All transactions chronologically with running balance
- **Source reconciliation**: Compare totals by source (bank vs PM)

## Notes

- PM transactions (source=tradewinds_pm or grantmain_pm) represent money flowing through PM's trust account
- Bank transactions (source=mercury, wise, relay) represent LLC bank account flows
- Owner contributions appear in PM data (funded via bank) — don't double-count when combining sources
- For tax: rental income and property expenses come from PM data; LLC-level expenses (legal filings, tax advisors) come from bank data
- Feb-Aug 2025 PM data has gaps — note this in reports covering that period
