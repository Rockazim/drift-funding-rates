# Drift Funding Rate Averages

This repository contains a Python script that fetches funding rates and contract data from Drift's API endpoints, processes the data, and outputs average funding rates for perpetual markets into a text file.

## Overview

The program utilizes Drift's API to:
- **Fetch Contracts:**  
  - **Endpoint:** `GET /contracts`  
  - **Purpose:** Retrieve contract information for each market, which includes details such as funding rate and open interest.
  
- **Fetch Funding Rates:**  
  - **Endpoint:** `GET /fundingRates?marketName=<marketSymbol>`  
  - **Purpose:** Retrieve the last 3 days of funding rates for a given perpetual market (e.g., `SOL-PERP`).  
  - **Note:** The funding rate is returned as a string and must be divided by 1e9 to obtain the actual rate.

The script then:
1. **Filters Contracts:**  
   - Extracts only perpetual (PERP) markets while excluding prediction markets (using a basic check on the ticker and index price).

2. **Processes Funding Rates:**  
   - Filters funding rates to include only entries from the last 3 days (or a specified period).
   - Converts the raw funding rate (after dividing by 1e9) and the oracle price TWAP (after scaling by 1e6) into a percentage for display.
   
3. **Calculates Averages:**  
   - Computes average funding rates for each market and sorts the results from highest to lowest.
   
4. **Outputs Results:**  
   - Writes the market symbols and their average funding rates into a file named `driftrates.txt`.

## Requirements

- Python 3.x
- `requests` library

## Setup and Usage

1. **Clone the Repository:**

```bash
git clone https://github.com/Rockazim/drift-funding-rates.git
d drift-funding-rates
```
2. install the required library using pip:

  ```bash
  pip install requests
  ```
3. Run the Python script
```bash
python drift.py
```
