import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import webbrowser
from src.bingx.services.market_data import MarketData
from src.bingx.services.analysis import Analyzer
from src.lib.requests_handler import RequestsHandler
from loguru import logger
from dotenv import load_dotenv
import os

load_dotenv()

BINGX_API_KEY = os.getenv("BINGX_API_KEY")
BINGX_API_SECRET = os.getenv("BINGX_API_SECRET")


class CryptoDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 加密貨幣走勢分析 - 桌面版")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1a1a1a")

        # 初始化市場數據服務
        self.requests_handler = RequestsHandler()
        self.market_data = MarketData(api_key=BINGX_API_KEY, api_secret=BINGX_API_SECRET)
        self.analyzer = Analyzer(self.market_data)

        # 數據變數
        self.current_symbol = tk.StringVar(value="BTC-USDT")
        self.current_interval = tk.StringVar(value="15m")
        self.symbols = []
        self.kline_data = None
        self.indicators_data = {}

        # 創建介面
        self.create_widgets()

        # 載入初始數據
        self.load_symbols()
        self.update_data()

        # 啟動定時更新
        self.start_auto_update()

    def create_widgets(self):
        """創建所有 UI 組件"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 標題
        title_label = ttk.Label(main_frame, text="🚀 加密貨幣走勢分析", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))

        # 控制面板
        self.create_control_panel(main_frame)

        # 內容區域
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 左側：圖表區域
        self.create_chart_area(content_frame)

        # 右側：指標面板
        self.create_indicators_panel(content_frame)

    def create_control_panel(self, parent):
        """創建控制面板"""
        control_frame = ttk.LabelFrame(parent, text="控制面板", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # 交易對選擇
        ttk.Label(control_frame, text="交易對:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.symbol_combo = ttk.Combobox(control_frame, textvariable=self.current_symbol, width=15, state="readonly")
        self.symbol_combo.grid(row=0, column=1, padx=5)
        self.symbol_combo.bind("<<ComboboxSelected>>", self.on_symbol_change)

        # 時間間隔選擇
        ttk.Label(control_frame, text="時間間隔:").grid(row=0, column=2, padx=5, sticky=tk.W)
        interval_combo = ttk.Combobox(
            control_frame, textvariable=self.current_interval, values=["1m", "5m", "15m", "1h", "4h", "1d"], width=10, state="readonly"
        )
        interval_combo.grid(row=0, column=3, padx=5)
        interval_combo.bind("<<ComboboxSelected>>", self.on_interval_change)

        # 更新按鈕
        update_btn = ttk.Button(control_frame, text="更新數據", command=self.update_data)
        update_btn.grid(row=0, column=4, padx=10)

        # TradingView 按鈕
        tv_btn = ttk.Button(control_frame, text="打開 TradingView", command=self.open_tradingview)
        tv_btn.grid(row=0, column=5, padx=5)

    def create_chart_area(self, parent):
        """創建圖表區域"""
        chart_frame = ttk.LabelFrame(parent, text="價格走勢圖", padding=5)
        chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # 創建 matplotlib 圖表
        self.fig = Figure(figsize=(10, 6), dpi=100, facecolor="#2a2a2a")
        self.ax = self.fig.add_subplot(111, facecolor="#2a2a2a")
        self.ax.tick_params(colors="white")

        # 嵌入到 tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 初始圖表
        self.plot_initial_chart()

    def create_indicators_panel(self, parent):
        """創建指標面板"""
        indicators_frame = ttk.LabelFrame(parent, text="自定義指標", padding=5)
        indicators_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))

        # 創建滾動區域
        canvas = tk.Canvas(indicators_frame, bg="#2a2a2a", highlightthickness=0)
        scrollbar = ttk.Scrollbar(indicators_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.indicators_frame = scrollable_frame

        # 警報區域
        alerts_frame = ttk.LabelFrame(parent, text="警報通知", padding=5)
        alerts_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))

        self.alerts_text = tk.Text(alerts_frame, height=4, bg="#1a1a1a", fg="white", font=("Arial", 9), wrap=tk.WORD)
        self.alerts_text.pack(fill=tk.BOTH, expand=True)

    def plot_initial_chart(self):
        """繪製初始圖表"""
        self.ax.clear()
        self.ax.set_title("載入中...", color="white", fontsize=14)
        self.ax.set_facecolor("#2a2a2a")
        self.canvas.draw()

    def plot_chart(self, data):
        """繪製價格圖表"""
        if data is None or len(data) == 0:
            return

        self.ax.clear()

        # 準備數據
        df = pd.DataFrame(data)
        df["time"] = pd.to_datetime(df["time"], unit="ms")

        # 繪製價格線
        self.ax.plot(df["time"], df["close"], color="#00d4aa", linewidth=2, label="收盤價")
        self.ax.plot(df["time"], df["open"], color="#ff6b6b", linewidth=1, alpha=0.7, label="開盤價")

        # 設置圖表樣式
        self.ax.set_title(f"{self.current_symbol.get()} - {self.current_interval.get()}", color="white", fontsize=14)
        self.ax.set_xlabel("時間", color="white")
        self.ax.set_ylabel("價格 (USDT)", color="white")
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)
        self.ax.tick_params(colors="white")

        # 旋轉 x 軸標籤
        plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45)

        self.fig.tight_layout()
        self.canvas.draw()

    def update_indicators_display(self, indicators):
        """更新指標顯示"""
        # 清除現有內容
        for widget in self.indicators_frame.winfo_children():
            widget.destroy()

        if not indicators:
            ttk.Label(self.indicators_frame, text="無數據", foreground="gray").pack(pady=10)
            return

        # 創建指標項目
        indicator_items = [
            ("當前價格", f"{indicators['current_price']:.4f}", "USDT"),
            ("價格變化", f"{indicators['price_change']*100:.2f}", "%"),
            ("48期移動平均", f"{indicators['ma_48']:.4f}", "USDT"),
            ("96期移動平均", f"{indicators['ma_96']:.4f}", "USDT"),
            ("平均波動率", f"{indicators['avg_fluc_pct']*100:.2f}", "%"),
            ("最大波動率", f"{indicators['max_fluc_pct']*100:.2f}", "%"),
            ("上影線比例", f"{indicators['upper_shadow_pct']*100:.2f}", "%"),
            ("下影線比例", f"{indicators['lower_shadow_pct']*100:.2f}", "%"),
            ("布林帶上軌", f"{indicators['upper_band']:.4f}", "USDT"),
            ("布林帶中軌", f"{indicators['middle_band']:.4f}", "USDT"),
            ("布林帶下軌", f"{indicators['lower_band']:.4f}", "USDT"),
            ("布林帶寬度", f"{indicators['band_width']:.4f}", "USDT"),
            ("成交量", f"{indicators['volume']:.2f}", ""),
        ]

        for label, value, unit in indicator_items:
            frame = ttk.Frame(self.indicators_frame)
            frame.pack(fill=tk.X, pady=2, padx=5)

            ttk.Label(frame, text=label, font=("Arial", 9, "bold")).pack(anchor=tk.W)

            # 根據數值設置顏色
            color = "#00ff88" if "變化" in label and float(value.replace("%", "")) >= 0 else "#ff4444"
            if "變化" not in label:
                color = "white"

            value_label = ttk.Label(frame, text=f"{value} {unit}", font=("Arial", 10), foreground=color)
            value_label.pack(anchor=tk.W)

    def load_symbols(self):
        """載入交易對列表"""

        def load_in_thread():
            try:
                symbols = list(self.market_data.get_all_fluctuations().keys())
                self.symbols = symbols[:50]  # 限制前50個

                # 在主線程中更新 UI
                self.root.after(0, self.update_symbol_combo)
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: messagebox.showerror("錯誤", f"載入交易對失敗: {error_msg}"))

        threading.Thread(target=load_in_thread, daemon=True).start()

    def update_symbol_combo(self):
        """更新交易對下拉選單"""
        self.symbol_combo["values"] = self.symbols
        if self.symbols and not self.current_symbol.get() in self.symbols:
            self.current_symbol.set(self.symbols[0])

    def update_data(self):
        """更新數據"""

        def update_in_thread():
            try:
                symbol = self.current_symbol.get()
                interval = self.current_interval.get()

                # 獲取 K線數據
                df = self.market_data.get_kline(symbol=symbol, interval=interval, limit=200)

                # 計算指標
                indicator_config = {"moving_average": [48, 96], "fluctuation_rate": 96, "shadow_pct": [], "boolinger_band": [48]}
                df = self.analyzer.extend_indicator(df, indicator=indicator_config)

                # 轉換為圖表格式
                kline_data = []
                for _, row in df.iterrows():
                    kline_data.append(
                        {
                            "time": int(row["time"]),
                            "open": float(row["open"]),
                            "high": float(row["high"]),
                            "low": float(row["low"]),
                            "close": float(row["close"]),
                            "volume": float(row["volume"]),
                        }
                    )

                # 提取最新指標
                latest = df.iloc[-1]
                indicators = {
                    "price_change": float(latest["price_change"]),
                    "avg_fluc_pct": float(latest["avg_fluc_pct"]),
                    "max_fluc_pct": float(latest["max_fluc_pct"]),
                    "upper_shadow_pct": float(latest["upper_shadow_pct"]),
                    "lower_shadow_pct": float(latest["lower_shadow_pct"]),
                    "ma_48": float(latest["48MA"]),
                    "ma_96": float(latest["96MA"]),
                    "upper_band": float(latest["upper_band"]),
                    "lower_band": float(latest["lower_band"]),
                    "middle_band": float(latest["middle_band"]),
                    "band_width": float(latest["band_width"]),
                    "current_price": float(latest["close"]),
                    "volume": float(latest["volume"]),
                }

                # 在主線程中更新 UI
                self.root.after(0, lambda: self.update_ui(kline_data, indicators))

            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: messagebox.showerror("錯誤", f"更新數據失敗: {error_msg}"))

        threading.Thread(target=update_in_thread, daemon=True).start()

    def update_ui(self, kline_data, indicators):
        """更新 UI 顯示"""
        self.kline_data = kline_data
        self.indicators_data = indicators

        # 更新圖表
        self.plot_chart(kline_data)

        # 更新指標
        self.update_indicators_display(indicators)

        # 更新警報
        self.update_alerts()

    def update_alerts(self):
        """更新警報顯示"""
        if not self.indicators_data:
            return

        alerts = []

        # 檢查各種警報條件
        price_change = self.indicators_data["price_change"]
        avg_fluc = self.indicators_data["avg_fluc_pct"]
        max_fluc = self.indicators_data["max_fluc_pct"]
        upper_shadow = self.indicators_data["upper_shadow_pct"]
        lower_shadow = self.indicators_data["lower_shadow_pct"]

        if abs(price_change) > avg_fluc * 2:
            alerts.append(f"⚠️ 價格快速變化: {price_change*100:.2f}%")

        if upper_shadow > 0.5:
            alerts.append(f"⚠️ 上影線過長: {upper_shadow*100:.2f}%")

        if lower_shadow > 0.5:
            alerts.append(f"⚠️ 下影線過長: {lower_shadow*100:.2f}%")

        # 更新警報文本
        self.alerts_text.delete(1.0, tk.END)
        if alerts:
            alert_text = f"{datetime.now().strftime('%H:%M:%S')}\n" + "\n".join(alerts)
            self.alerts_text.insert(1.0, alert_text)
        else:
            self.alerts_text.insert(1.0, "無警報")

    def on_symbol_change(self, event):
        """交易對改變事件"""
        self.update_data()

    def on_interval_change(self, event):
        """時間間隔改變事件"""
        self.update_data()

    def open_tradingview(self):
        """打開 TradingView"""
        symbol = self.current_symbol.get()
        interval = self.current_interval.get()
        url = f"https://www.tradingview.com/chart/?symbol=BINGX:{symbol}&interval={interval}"
        webbrowser.open(url)

    def start_auto_update(self):
        """啟動自動更新"""

        def auto_update():
            while True:
                time.sleep(30)  # 每30秒更新一次
                if self.kline_data is not None:  # 只有在有數據時才更新
                    self.update_data()

        threading.Thread(target=auto_update, daemon=True).start()


def main():
    root = tk.Tk()
    app = CryptoDesktopApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
