import requests
import sqlite3
from flask import Flask, render_template, abort, g, request

currency = {"eur_to_usd", "eur_to_gbp", "eur_to_php"}

app = Flask(__name__, template_folder='template')
DATABASE = 'database.db'


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
    return None


class Currency:
    def __init__(self, cur_to_exchange, amount):
        self._cur_to_exchange = cur_to_exchange
        self._amount = amount
        self.result = self.get_cur_exchange()

    def _get_cur_rate(self):
        url = "https://api.exchangeratesapi.io/latest"
        response = requests.get(url)
        rate = response.json()
        return rate["rates"][self._cur_to_exchange]

    def get_cur_exchange(self):
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
        result_exch = cur_to_exchanche.get_cur_exchange()
        write_to_db(result_exch)
        print(result_exch)
    return render_template('result.html', exchange_result=result_exch)


@app.route('/history')
def read_history():
    with open("history.txt", 'r') as file:
        lines = file.readlines()
    return render_template('history_templ.html', exchange_history=lines)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
