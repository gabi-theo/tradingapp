import yfinance as yf

from datetime import datetime, timedelta

from trading.models import Price, Trade, TradeError


class YahooFinanceService:
    @staticmethod
    def fetch_price_data_by_date(date: datetime.date):
        available_tickers = list(Trade.objects.values_list('company_symbol', flat=True).distinct())
        for ticker in available_tickers:
            try:
                ticker_data = yf.Ticker(ticker)
                price_history = ticker_data.history(start=date, end=date+timedelta(days=1), interval="1d")
                price, _ = Price.objects.get_or_create(
                    company_symbol=ticker.upper(),
                    date=date,
                    close=price_history["Close"][0],
                    high=price_history["High"][0],
                    low=price_history["Low"][0],
                    open=price_history["Open"][0],
                    volume=price_history["Volume"][0],
                    dividents=price_history["Dividends"][0],
                    stock_split=price_history["Stock Splits"][0],
                )
            except Exception as e:
                TradeError.objects.create(
                    error=f"Failed to add price from Yahoo Finance. Reason: {e}",
                    level="fyahoo_api_call",
                )
