from flask import Flask, render_template
import requests


currency = {"eur_to_usd", "eur_to_gbp", "eur_to_php"}

app = Flask(__name__, template_folder='template')

def check_amount(amaunt_str: str):
    try:
        float(amaunt_str)
        return True
    except ValueError:
        return False




class Currency:
    def __init__(self, cur_to_exchange="USD", amount=0):
        self._cur_to_exchange = cur_to_exchange
        self._amount = amount

    def __str__(self):
        b = self._get_cur_rate()
        return f"{self._cur_to_exchange},{b},{self._amount},{round(b * float(self._amount), 4)} \n"

    def _get_cur_rate(self):
        url = "https://api.exchangeratesapi.io/latest"
        response = requests.get(url)
        rate = response.json()
        return rate["rates"][self._cur_to_exchange]

    def write_to_history(self):
        with open("history.txt", "a") as txt_file:
            txt_file.write(self.__str__())
        return None


@app.route('/')
def index():
    return 'Hello, World!'


@app.route('/<route_id>/<amount>')
def get_route(route_id, amount):
    if route_id not in currency or not check_amount(amount):
        return "error"
    else:
        cur_to_exchanche = Currency(route_id[7:].upper(), amount)
        cur_to_exchanche.write_to_history()
    return str(cur_to_exchanche)


@app.route('/history')
def read_history():
    with open("history.txt", 'r') as file:
        lines = file.readlines()
    return render_template('history_templ.html', exchange_history=lines)


if __name__ == '__main__':
    app.run(debug=True)
