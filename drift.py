from datetime import datetime, timedelta, timezone
import requests

def fetch_raw_contracts():
    url = 'https://data.api.drift.trade/contracts'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def get_perpetual_markets():
    data = fetch_raw_contracts()
    if data and 'contracts' in data:
        # Filter for PERP markets and exclude prediction markets
        perp_markets = [
            market for market in data['contracts']
            if market.get('product_type') == 'PERP' and not is_prediction_market(market)
        ]
        return perp_markets
    return []

def is_prediction_market(market):
    ticker_id = market.get('ticker_id', '').upper()
    index_price = float(market.get('index_price', 0))
    if "WIN" in ticker_id or "BET" in ticker_id or "GP" in ticker_id:
        return True
    if index_price < 0.01:
        return True
    return False

def get_funding_rates(market_symbol):
    url = f'https://data.api.drift.trade/fundingRates'
    params = {'marketName': market_symbol}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get('fundingRates', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching funding rates for {market_symbol}: {e}")
        return []

def filter_recent_funding_rates(funding_rates, days=3, max_results=72):
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)
    recent_rates = [
        rate for rate in funding_rates
        if datetime.fromtimestamp(int(rate['ts']), timezone.utc) >= cutoff
    ]
    # Sort by timestamp and take the most recent `max_results` entries
    recent_rates = sorted(recent_rates, key=lambda r: int(r['ts']), reverse=True)[:max_results]
    return recent_rates

def process_funding_rate_data(funding_rates):
    BASE_PRECISION = 1e9
    QUOTE_PRECISION = 1e6
    processed_rates = []

    for rate in funding_rates:
        funding_rate = float(rate['fundingRate'])
        oracle_twap = float(rate['oraclePriceTwap'])
        scaled_funding_rate = funding_rate / BASE_PRECISION
        scaled_oracle_twap = oracle_twap / QUOTE_PRECISION
        ui_funding_rate = (scaled_funding_rate / scaled_oracle_twap) * 100

        processed_rates.append(ui_funding_rate)

    return processed_rates

# Calculate average funding rates for all perpetual markets
average_rates = []

perpetual_markets = get_perpetual_markets()
for market in perpetual_markets:
    market_symbol = market['ticker_id']
    funding_rates = get_funding_rates(market_symbol)

    # Filter for recent funding rates (last 3 days, max 72 results)
    recent_funding_rates = filter_recent_funding_rates(funding_rates)
    processed_rates = process_funding_rate_data(recent_funding_rates)

    if processed_rates:
        avg_rate = sum(processed_rates) / 3  # Divide by 3 days
        average_rates.append((market_symbol, avg_rate))

# Sort by average funding rate (highest to lowest)
sorted_rates = sorted(average_rates, key=lambda x: x[1], reverse=True)

# Write to 'driftrates.txt'
with open('driftrates.txt', 'w') as file:
    file.write("Market Symbol | Average Funding Rate (%)\n")
    file.write("---------------------------------------\n")
    for market_symbol, avg_rate in sorted_rates:
        file.write(f"{market_symbol} | {avg_rate:.6f}\n")

print("Funding rate averages written to 'driftrates.txt'.")
