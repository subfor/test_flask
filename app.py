import requests
import sqlite3
from flask import Flask, render_template, abort, g, request

currency = {"eur_to_usd", "eur_to_gbp", "eur_to_php"}

app = Flask(__name__, template_folder='template')
DATABASE = 'database.db'


class Currency:
    def __init__(self, cur_to_exchange, amount):
        self._cur_to_exchange = cur_to_exchange
        self._amount = amount
        self.result = self._get_cur_exchange()

    def _get_cur_rate(self):
        url = "https://api.exchangeratesapi.io/latest"
        response = requests.get(url)
        rate = response.json()
        return rate["rates"][self._cur_to_exchange]

    def _get_cur_exchange(self):
        return {"currency": self._cur_to_exchange,
                "rate": self._get_cur_rate(),
                "amount": self._amount,
                "result": round(self._get_cur_rate() * float(self._amount), 4)
                }


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        db = g._database = conn
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def write_to_db(cur_exchange: dict):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
            insert into exchange (currency_to, exchange_rate, amount, "result")
                values (?, ?, ?, ?)
        """, (cur_exchange["currency"], cur_exchange["rate"], cur_exchange["amount"], cur_exchange["result"]))

    conn.commit()


@app.route('/')
def index():
    return 'Currency Exchange'


@app.route('/<route_id>/<float:amount>')
@app.route('/<route_id>/<int:amount>')
def get_route(route_id, amount):
    if route_id not in currency:
        abort(404)
    else:
        cur_to_exchanche = Currency(route_id[7:].upper(), amount)
        write_to_db(cur_to_exchanche.result)
    return render_template('result.html', exchange_result=cur_to_exchanche.result)


@app.route('/history')
def read_history():
    result = ""
    connection = get_db()
    cursor = connection.cursor()
    resp = cursor.execute("""
                select exchange.currency_to, exchange.exchange_rate, exchange.amount, exchange.result
                from exchange
            """)
    resp = resp.fetchall()
    for row in resp:
        result += f"<li>{row['currency_to']}, {row['exchange_rate']} ," \
                  f" {row['amount']}, {row['result']}</li> \n"
    return result


@app.route('/history/currency/<cur>')
def get_history_by_currency(cur):
    if cur not in ("usd", "gbp", "php"):
        abort(404)
    else:
        result = ""
        connection = get_db()
        cursor = connection.cursor()
        resp = cursor.execute("""
                    select exchange.currency_to, exchange.exchange_rate, exchange.amount, exchange.result
                    from exchange
                    where exchange.currency_to like ?
                """, (cur.upper(),))
        resp = resp.fetchall()
        for row in resp:
            result += f"<li>{row['currency_to']}, {row['exchange_rate']} ," \
                      f" {row['amount']}, {row['result']}</li> \n"
    return result


@app.route('/history/amount_gte/<float:amount>')
@app.route('/history/amount_gte/<int:amount>')
def get_history_by_amount(amount):
    result = ""
    connection = get_db()
    cursor = connection.cursor()
    resp = cursor.execute("""
                    select exchange.currency_to, exchange.exchange_rate, exchange.amount, exchange.result
                    from exchange
                    where exchange.amount >= ?
                """, (amount,))
    resp = resp.fetchall()
    for row in resp:
        result += f"<li>{row['currency_to']}, {row['exchange_rate']} ," \
                  f" {row['amount']}, {row['result']}</li> \n"
    return result


@app.route('/history/statistic')
def get_statistic():
    result = ""
    connection = get_db()
    cursor = connection.cursor()
    resp = cursor.execute("""
                        select exchange.currency_to , 
                        count(exchange.currency_to) as count_exchange,
                        sum(exchange.result) as sum_result
                        from exchange
                        group by exchange.currency_to
                    """)
    resp = resp.fetchall()
    for row in resp:
        result += f'<li>{row["currency_to"]},{row["count_exchange"]}, {row["sum_result"]}\n'
    return result


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
