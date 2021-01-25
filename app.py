from flask import Flask, render_template
import requests
from os import path


currency = {"eur_to_usd", "eur_to_gbp"}

app = Flask(__name__, template_folder='template')


class Currency:
    def __init__(self, cur_to_exchange="USD", amount=0):
        self.cur_to_exchange = cur_to_exchange
        self.amount = amount

    def __str__(self):
        b = self.get_cur_rate()
        return f"{self.cur_to_exchange},{self.amount},{b * float(self.amount)} \n"

    def get_cur_rate(self):
        url = "https://api.exchangeratesapi.io/latest"
        r = requests.get(url)
        a = r.json()
        return a["rates"][self.cur_to_exchange]

    def write_to_history(self):
        with open(path.join(".", "history.txt"), "a") as txt_file:
            txt_file.write(self.__str__())
        return None


@app.route('/')
def index():
    return 'Hello, World!'


@app.route('/<route_id>/<amount>')
def get_route(route_id, amount):
    if route_id not in currency:
        return "error"
    else:
        a = Currency(route_id[7:].upper(), amount)
        a.write_to_history()

        print(a)
    return str(a)


@app.route('/history')
def read_history():
    with open(path.join("history.txt"), 'r') as file:
        lines = file.readlines()
    return render_template('history_templ.html', exchange_history=lines)


if __name__ == '__main__':
    app.run(debug=True)
