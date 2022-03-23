from FtxClient import FtxClient
import time
import math
import os


def ema(data, periods):
    multiplier = 2.0 / (periods + 1)
    result = [ data[0] ]
    for i in range(1, len(data)):
        result.append(result[i-1] * (1-multiplier) + data[i] * multiplier)
    return result


def sma(data, periods):
    result = []
    for i in range(periods-1, len(data)):
        sum = 0
        for j in range(i-periods+1, i+1):
            sum += data[j]
        result.append(sum / periods)
    return result


def truncate(n, decimals=0):
    r = math.floor(float(n)*10**decimals)/10**decimals
    return str(r)


api_key = os.environ['API_KEY']
api_secret = os.environ['API_SECRET']
subaccount_name = os.environ['SUBACCOUNT_NAME']
client = FtxClient(api_key, api_secret, subaccount_name)


def get_balance(symbol):
    balance = 0
    try:
        for b in client.get_balances():
            if b['coin'] == symbol:
                balance = b['total']
    except:
        balance = 0
    return balance


def hello_pubsub(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    pair_symbol = "ETH/USDT"
    symbol_coin = "ETH"
    symbol_usd = "USDT"
    resolution = 86400
    limit = 1000
    myTruncate = 5

    data = client.get_historical_prices(market=pair_symbol, resolution=resolution,
                                        start_time=round(time.time() - resolution * limit), end_time=round(time.time()))
    close = [x['close'] for x in data]

    row = {"ema12": ema(close, 12)[-2], "ema26": ema(close, 26)[-2], "close": close[-2]}
    print(row)

    balance_coin = get_balance(symbol_coin)
    balance_usd = get_balance(symbol_usd)
    print(balance_coin)
    print(balance_usd)


if __name__ == "__main__":
    hello_pubsub(None, None)

TODO comparer avec :
    import pandas as pd
    import numpy as np

    def ema(values, period):
        values = np.array(values)
        return pd.ewma(values, span=period)[-1]

    values = [9, 5, 10, 16, 5]
    period = 5

    print ema(values, period)