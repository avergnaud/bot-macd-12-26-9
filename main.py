from FtxClient import FtxClient
import time
import math
import os


def append_macd_values(data):
    multiplier12 = 2.0 / (12 + 1)
    multiplier26 = 2.0 / (26 + 1)
    data[0].update({ 'ema12': data[0]['close'] })
    data[0].update({ 'ema26': data[0]['close'] })
    for i in range(1, len(data)):
        data[i].update({ 'ema12': data[i-1]['ema12'] * (1-multiplier12) + data[i]['close'] * multiplier12 })
        data[i].update({ 'ema26': data[i-1]['ema26'] * (1-multiplier26) + data[i]['close'] * multiplier26 })
        data[i].update({ 'macd': data[i]['ema12'] - data[i]['ema26'] })
        if i < 9:
            # on ne peut pas calculer le signal
            continue
        sum = 0
        for j in range(i - 8, i + 1):
            sum += data[j]['macd']
        signal = sum / 9
        data[i].update({ 'signal': signal })


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
    symbol_stablecoin = "USDT"
    resolution = 86400
    limit = 1000
    my_truncate = 5

    data = client.get_historical_prices(market=pair_symbol, resolution=resolution,
                                        start_time=round(time.time() - resolution * limit),
                                        end_time=round(time.time()))
    append_macd_values(data)
    row = data[-1]
    balance_coin = get_balance(symbol_coin)
    balance_stablecoin = get_balance(symbol_stablecoin)
    print(f"{symbol_coin}={balance_coin}, {symbol_stablecoin}={balance_stablecoin}, macd={row['macd']}, signal={row['signal']}, close={row['close']}")
    if row['macd'] > row['signal'] and balance_stablecoin > 10:
        print("buy")
        amount_to_buy = balance_stablecoin / row["close"]
        # order_output = client.place_order(market=pair_symbol, side="buy", price=None, size=truncate(amount_to_buy, my_truncate), type='market')
        # print(order_output)
    elif row['macd'] < row['signal'] and balance_coin*row['close'] > 10:
        print("sell")
        amount_to_sell = balance_coin
        # order_output = client.place_order(market=pair_symbol, side="sell", price=None, size=truncate(amount_to_sell, myTruncate), type='market')
        # print(order_output)
    else:
        print("Nothing to do just wait")


if __name__ == "__main__":
    hello_pubsub(None, None)