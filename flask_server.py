from vitex_api import get_wallet_transactions, get_exchange_orders
from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('vitex_tool.html')


@app.route('/get_account_info', methods=['POST'])
def get_account_info():

    response = {'wallet': False, 'exchange': False}
    address = request.form['address']
    print(address)
    if not address.startswith('vite') or len(address) != 55:
        return jsonify(response)

    # We are looking only for transactions filled after block 861141^,
    # this is 1615530744s in UNIX TIMESTAMP^, Fri Mar 12 2021 06:32:24 GMT+0
    #
    # ^ 'THE' block: https://explorer.epic.tech/blockdetail/861141
    # ^ UNIX TIMESTAMP: https://www.unixtimestamp.com/

    time_frame = [1615530744, 1617631885]
    trading_pair = "EPIC-001_BTC-000"
    response = {'wallet': False, 'exchange': False}

    # Here we gonna use our functions from vitex_api.py
    # to download and save data from API in form of CSV files
    transactions = get_wallet_transactions(viteAddress=address)
    print(transactions)
    orders = get_exchange_orders(viteAddress=address, limit=5000, filterTime=time_frame,
                                 side=None, symbol=trading_pair, status=None)

    # ---------------------------------------#
    # Define filters and process wallet data #
    # ---------------------------------------#
    if len(transactions) > 0:
        wallet_df = transactions

        sent = wallet_df.transactionType == "Sent"
        received = wallet_df.transactionType == "Recieved"
        time = wallet_df.datetime < time_frame[0]

        # Calculate balance before event date
        e_total_sent = round(sum(wallet_df[sent & time].decimalAmount), 2)
        e_total_received = round(sum(wallet_df[received & time].decimalAmount), 2)
        wallet_history_balance = round(e_total_received + e_total_sent, 2)

        # Calculate balance for today
        total_sent = round(sum(wallet_df[sent].decimalAmount), 2)
        total_received = round(sum(wallet_df[received].decimalAmount), 2)
        wallet_today_balance = round(total_received + total_sent, 2)

        # Balance difference between event day and today
        wallet_difference = round(wallet_today_balance - wallet_history_balance, 2)

        response['wallet'] = {
            'total_sent': total_sent,
            'e_total_sent': e_total_sent,
            'total_received': total_received,
            'e_total_received': e_total_received,
            'wallet_difference': wallet_difference,
            'wallet_today_balance': wallet_today_balance,
            'wallet_history_balance': wallet_history_balance,
            }

    if len(orders) > 0:
        df = orders

        # -----------------------------------------#
        # Define filters and process exchange data #
        # -----------------------------------------#
        filled = df.status == 'Filled'
        bought = df.side == "Buy"
        sold = df.side == "Sell"

        total_buy = round(sum(df[filled & bought].quantity), 2)
        total_sold = round(sum(df[filled & sold].quantity), 2)

        buy_value = round(sum(df[filled & bought].amount), 2)
        sold_value = round(sum(df[filled & sold].amount), 4)

        balance = round(total_buy - total_sold, 2)

        # --------------------------#
        # Some interesting numbers  #
        # --------------------------#
        total_hack_epics = 2_800_000

        # What part of it is you
        participation = round(balance / total_hack_epics * 100, 3)

        response['exchange'] = {
            'total_buy': total_buy,
            'total_sold': total_sold,
            'buy_value': buy_value,
            'sold_value': sold_value,
            'balance': balance,
            'participation': participation
            }

    return jsonify(response)


if __name__ == "__main__":
    app.run()
