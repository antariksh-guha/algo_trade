# NSE Stock Lists for Algo Trading Dashboard

This project uses two important NSE stock lists:

---

## 1. NIFTY 100 Constituents List (`nifty_100.csv`)

**Purpose:**  
This file contains the official list of NIFTY 100 index constituents (top 100 liquid stocks).

**Use:**  
Used in the app for scanning top stocks with reliable price data and for the stock selection dropdown.

**Where to download:**  
You can download the NIFTY 100 constituents list from the NSE official Market Watch page:

- [NSE Market Watch - Equity/Stock](https://www.nseindia.com/market-data/live-equity-market#)

**How to get the NIFTY 100 list:**

1. Open the **Indices** section.
2. Select the **NIFTY 100** index.
3. Export or download the constituent list as CSV or copy-paste the table into a CSV file.
4. Save this file as `nifty_100.csv` in your app folder.

---

## 2. Full NSE Equity List (`nse_stock_list.csv`)

**Purpose:**  
Complete list of all NSE equities available for trading, used for comprehensive symbol lookups and extended stock selection.

**Use:**  
Used to populate detailed dropdown selector with all NSE stocks.

**Where to download:**  
You can download the full NSE equities list CSV from the NSE official archive:

- [EQUITY_L.csv – NSE official archive](https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv)
- Direct download link: https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv

Save this file as `nse_stock_list.csv` in your app folder.

---

## Recommended Update Frequency

- **Weekly update** is recommended for both files to ensure you get the latest listings, additions, exclusions, and corporate actions.
- You may automate downloads via scripts running weekly on your local machine and commit updates to your app repository, or update files manually.
- Regular updates help maintain accuracy for trading decisions.

---

## Summary

| File                 | Purpose                   | Source URL                                                                                   | Update Frequency |
|----------------------|---------------------------|----------------------------------------------------------------------------------------------|------------------|
| `nifty_100.csv`      | NIFTY 100 constituents    | [https://www.nseindia.com/market-data/live-equity-market#](https://www.nseindia.com/market-data/live-equity-market#) | Weekly           |
| `nse_stock_list.csv` | Full list of NSE equities | [https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv](https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv) | Weekly           |

---

**Current Date:** Tuesday, July 22, 2025, 3:04 PM IST

---

If you need help automating the download and CSV updating process, or integrating these files into your app, feel free to reach out!

