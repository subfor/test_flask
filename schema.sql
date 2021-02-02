DROP TABLE IF EXISTS exchange;

CREATE TABLE exchange (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        currency_to TEXT NOT NULL,
                        exchange_rate REAL NOT NULL,
                        amount REAL NOT NULL,
                        result REAL NOT NULL
);