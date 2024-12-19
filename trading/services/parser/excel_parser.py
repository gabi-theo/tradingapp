from datetime import datetime, timedelta
import pandas as pd

from trading.models import TradeError, Trade
from trading.services.calculation.costs import CostsService
from trading.services.calculation.net_daily_position import NetDailyPositionService
from trading.services.yahoo_finance.yahoo_api import YahooFinanceService

class ExcelParserService:
    @staticmethod
    def parse_and_store_input_excel(excel_file: pd.DataFrame):
        if ExcelParserService.validate_columns(excel_file=excel_file):
            for _, row in excel_file.iterrows():
                storing_result =  ExcelParserService.store_row_to_db(row=row)
                ExcelParserService.validate_storing_result(storing_result=storing_result)
            print("All trades have been successfully imported.")
            dates = list(Trade.objects.values_list('date', flat=True).distinct().order_by('date'))
            dates.insert(0, dates[0] - timedelta(days=1))
            dates.append(dates[-1] + timedelta(days=1))
            full_date_range = [dates[0] + timedelta(days=i) for i in range((dates[-1] - dates[0]).days + 1)]
            all_dates = sorted(set(dates).union(full_date_range))
            for date in all_dates:
                YahooFinanceService.fetch_price_data_by_date(date)
                NetDailyPositionService.calculate_daily_net_position(date)
                CostsService.calculate_costs_for_day(date)
        else:
            TradeError.objects.create(error=f"Excel import error", level="excel_file")
            
    @staticmethod
    def validate_columns(excel_file: pd.DataFrame) -> bool:
        standard_columns = ["Date", "Ticker", "Quantity", "Price", "Direction"]
        return (excel_file.columns == standard_columns).all()

    @staticmethod
    def store_row_to_db(row: pd.Series) -> str:
        trade_date = datetime.strptime(str(row['Date']), '%Y-%m-%d %H:%M:%S').date()
        ticker = row['Ticker'].upper()
        quantity = int(row['Quantity'])
        price = float(row['Price'])
        direction = str(row['Direction']).lower()
        print(direction)
        try:
            trade, _ = Trade.objects.get_or_create(
                date=trade_date,
                company_symbol=ticker,
                quantity=quantity,
                price=price,
                direction=direction
            )
            return "ok"
        except Exception as e:
            return f"Storing error for ticker: {ticker} with date {trade_date}, direction {direction}, price {price} and quantity {quantity}. Reason: {e}"
        
    @staticmethod
    def validate_storing_result(storing_result: str):
        if storing_result != "ok":
            TradeError.objects.create(error=storing_result, level="excel_row")
