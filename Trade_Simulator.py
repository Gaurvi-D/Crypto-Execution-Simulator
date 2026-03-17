import sys
import asyncio
import json
import websockets
import time
import threading
import pyqtgraph as pg
import numpy as np
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QApplication, QTextEdit
from PyQt5.QtCore import pyqtSignal, QObject
from sklearn.linear_model import LogisticRegression

# Signal handler for thread-safe GUI updates
class SignalHandler(QObject):
    update_output = pyqtSignal(dict)

signal_handler = SignalHandler()

class TradeSimulatorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crypto Trade Simulator")
        self.setGeometry(100, 100, 700, 400)

        self.price_history = []
        self.chart = pg.PlotWidget()
        self.chart.setTitle("Live Price Chart")
        self.chart.setLabel("left", "Price")
        self.chart.setLabel("bottom", "Time")

        # Input panel
        self.asset_label = QLabel("Asset (e.g. btcusdt):")
        self.asset_input = QLineEdit("btcusdt")

        self.qty_label = QLabel("Order Quantity (USD):")
        self.qty_input = QLineEdit("100")

        self.fee_label = QLabel("Fee Percent (e.g. 0.1):")
        self.fee_input = QLineEdit("0.1")

        self.vol_label = QLabel("Volatility (est.):")
        self.vol_input = QLineEdit("0.02")

        self.run_button = QPushButton("Run Simulation")
        self.run_button.clicked.connect(self.start_simulation)

        # Output panel
        self.output = QTextEdit()
        self.output.setReadOnly(True)

        # Layouts
        input_layout = QVBoxLayout()
        input_layout.addWidget(self.asset_label)
        input_layout.addWidget(self.asset_input)
        input_layout.addWidget(self.qty_label)
        input_layout.addWidget(self.qty_input)
        input_layout.addWidget(self.fee_label)
        input_layout.addWidget(self.fee_input)
        input_layout.addWidget(self.vol_label)
        input_layout.addWidget(self.vol_input)
        input_layout.addWidget(self.run_button)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.output)
        right_layout.addWidget(self.chart)

        main_layout = QHBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)
        signal_handler.update_output.connect(self.update_output)

    def start_simulation(self):
        asset = self.asset_input.text()
        qty = float(self.qty_input.text())
        fee = float(self.fee_input.text())
        vol = float(self.vol_input.text())
        threading.Thread(target=lambda: asyncio.run(websocket_listener(asset, qty, fee, vol)), daemon=True).start()

    def update_output(self, metrics):
        text = "\n".join([f"{k}: {v:.6f}" if isinstance(v, float) else f"{k}: {v}" for k, v in metrics.items()])
        self.output.setText(text)
        price = metrics.get("Microprice", None)
        if price:
            self.price_history.append(price)

            if len(self.price_history) > 100:
                self.price_history.pop(0)

            self.chart.clear()
            self.chart.plot(self.price_history)

# Metrics calculation per tick
def calculate_metrics(orderbook, qty_usd, fee_percent, volatility):
    start_time = time.time()
    asks = orderbook.get("asks", [])
    bids = orderbook.get("bids", [])

    if not asks or not bids:
        return

    ask_prices = np.array([float(price) for price, _ in asks[:10]])
    ask_vols = np.array([float(size) for _, size in asks[:10]])
    total_qty = qty_usd / ask_prices[0]  # Quantity in coins

    # Simulate order book execution (order book walk)
    remaining_qty = total_qty
    cost = 0

    for price, size in asks:
        price = float(price)
        size = float(size)

        trade_qty = min(size, remaining_qty)

        cost += trade_qty * price
        remaining_qty -= trade_qty

        if remaining_qty <= 0:
            break

    if remaining_qty > 0:
        return  # not enough liquidity

    avg_execution_price = cost / total_qty
    est_slip = avg_execution_price - ask_prices[0]

    # --- Market Microstructure Metrics ---

    best_ask = ask_prices[0]
    best_bid = float(bids[0][0])

    # Bid-Ask Spread
    spread = best_ask - best_bid

    # Order book depth (top 10 levels)
    bid_depth = sum(float(size) for _, size in bids[:10])
    ask_depth = sum(float(size) for _, size in asks[:10])

    # Liquidity imbalance
    imbalance = (bid_depth - ask_depth) / (bid_depth + ask_depth)

    # Microprice (liquidity weighted mid price)
    microprice = (best_bid * ask_depth + best_ask * bid_depth) / (bid_depth + ask_depth)

    # Fees
    fee_cost = qty_usd * (fee_percent / 100)

    # Market Impact
    market_impact = volatility * total_qty * 0.01

    # Net Cost
    net_cost = est_slip + fee_cost + market_impact

    # Maker/Taker probability
    logistic = LogisticRegression().fit(np.array([[0], [1]]), [0, 1])
    prob = logistic.predict_proba([[spread]])[0][1]

    # Latency
    latency = time.time() - start_time

    signal_handler.update_output.emit({
        "Slippage": est_slip,
        "Spread": spread,
        "Liquidity Imbalance": imbalance,
        "Microprice": microprice,
        "Fee Cost": fee_cost,
        "Market Impact": market_impact,
        "Net Cost": net_cost,
        "Maker/Taker Probability": prob,
        "Internal Latency (s)": latency
    })

async def websocket_listener(asset, qty, fee, vol):
    url = f"wss://stream.binance.com:9443/ws/{asset.lower()}@depth"

    while True:
        try:
            async with websockets.connect(url) as ws:
                print("Connected to Binance WebSocket")

                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)

                    orderbook = {
                        "asks": data.get("a", []),
                        "bids": data.get("b", [])
                    }

                    calculate_metrics(orderbook, qty, fee, vol)

        except Exception as e:
            print("Connection error:", e)
            print("Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

# Launch app
if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = TradeSimulatorGUI()
    gui.show()
    sys.exit(app.exec_())
