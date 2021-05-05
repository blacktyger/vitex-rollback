from vitex_api import get_wallet_transactions, get_exchange_orders
from flask import Flask, render_template, request, jsonify
import pandas as pd
import datetime

# ---------------------------------#
# DIRTY VERSION WITH MESS IN FILES #
# ---------------------------------#

app = Flask(__name__)


@app.template_filter()
def numberFormat(value):
    return format(int(value), ',d')


@app.route('/')
def home():
    return render_template('vitex_tool.html')


@app.route('/get_account_info_btc', methods=['POST'])
def get_account_info():
    response = {'wallet': False, 'exchange': False}
    address = request.form['address']
    print('-----------------------------------------------')
    print(str(datetime.datetime.now()))
    print(address)
    if not address.startswith('vite') or len(address) != 55:
        return jsonify(response)

    # We are looking only for transactions filled after block 861141^,
    # this is 1615530744s in UNIX TIMESTAMP^, Fri Mar 12 2021 06:32:24 GMT+0
    #
    # ^ 'THE' block: https://explorer.epic.tech/blockdetail/861141
    # ^ UNIX TIMESTAMP: https://www.unixtimestamp.com/
    year_ago = 1584705600
    end_date = 1616355904  # 21 March 2021
    event_timestamp = 1615530744  # 12 March 2021
    trading_pair = "EPIC-001_BTC-000"

    # Here we gonna use our functions from vitex_api.py
    # to download and save data from API in form of CSV files
    transactions = []
    # transactions = get_wallet_transactions(viteAddress=address)
    # print(transactions)
    orders = get_exchange_orders(viteAddress=address, limit=10000,
                                 filterTime=[event_timestamp, end_date],
                                 side=None, symbol=trading_pair, status=None)

    # ---------------------------------------#
    # Define filters and process wallet data #
    # ---------------------------------------#
    if len(transactions) > 0:
        wallet_df = transactions

        sent = wallet_df.transactionType == "Sent"
        received = wallet_df.transactionType == "Recieved"
        time = wallet_df.datetime < event_timestamp
        end_time = wallet_df.datetime < end_date

        # Calculate balance before event date
        e_total_sent = round(sum(wallet_df[sent & time].decimalAmount), 2)
        e_total_received = round(sum(wallet_df[received & time].decimalAmount), 2)
        wallet_history_balance = round(e_total_received + e_total_sent, 2)

        # Calculate balance for 21 March
        total_sent = round(sum(wallet_df[sent & end_time].decimalAmount), 2)
        total_received = round(sum(wallet_df[received & end_time].decimalAmount), 2)
        wallet_today_balance = round(total_received + total_sent, 2)

        # Balance difference between event day and 21 March
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
        df = pd.DataFrame(orders)

        # -----------------------------------------#
        # Define filters and process exchange data #
        # -----------------------------------------#
        bought = df.side == "Buy"
        sold = df.side == "Sell"

        total_buy = round(sum(df[bought].quantity), 2)
        total_sold = round(sum(df[sold].quantity), 2)

        buy_value = round(sum(df[bought].amount), 2)
        sold_value = round(sum(df[sold].amount), 2)

        buy_value_usd = round(sum(df[bought].usd_value), 2)
        sold_value_usd = round(sum(df[sold].usd_value), 2)

        balance = round(total_buy - total_sold, 2)
        balance_usd = round(buy_value_usd - sold_value_usd, 2)

        # --------------------------#
        # Some interesting numbers  #
        # --------------------------#
        total_hack_epics = 2_800_000

        # What part of it is user
        participation = round(balance / total_hack_epics * 100, 3)

        table = []
        for order in orders:
            if order['side'] == 'Buy':
                color = 'success'
                sign1 = "+"
                sign2 = "-"
            elif order['side'] == 'Sell':
                color = 'warning'
                sign1 = "-"
                sign2 = "+"

            table.append(
                f"<tr><td>{order['createTime']}</td>"
                f"<td class='text-{color}'>{order['side']}</td>"
                f"<td>{sign1}{order['quantity']}</td>"
                f"<td>{sign2}{order['amount']}</td>"
                f"<td class='pull-right'>{sign2}{order['usd_value']}$</td</tr>"
                )

        table.append(
            f"<tr><td>TOTALS: </td><td></td>"
            f"<td>{int(sum(df.quantity))}</td>"
            f"<td>{round(sum(df.amount), 6)}</td>"
            f"<td>{int(sum(df.usd_value))}$</td>"
            )

        table = "".join(table)

        response['exchange'] = {
            'total_buy': total_buy,
            'total_sold': total_sold,
            'buy_value': buy_value,
            'sold_value': sold_value,
            'buy_value_usd': buy_value_usd,
            'sold_value_usd': sold_value_usd,
            'balance': balance,
            'balance_usd': balance_usd,
            'participation': participation,
            'orders_table': table,
            'total_orders': df.shape[0]
            }
    print('-----------------------------------------------')
    return jsonify(response)


if __name__ == "__main__":
    app.run(port=5555)
