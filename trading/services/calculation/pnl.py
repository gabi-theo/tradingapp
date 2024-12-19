

from datetime import datetime, timedelta
from trading.models import Cost, Price, Trade


class PNLService:
    @staticmethod
    def daily_realized_pnl_calculation_for_symbol_on_date(symbol: str, date: datetime.date) -> float:
        trade_object = Trade.objects.filter(company_symbol=symbol, date=date, direction="sell")
        if trade_object.exists():
            quantity = trade_object.first().quantity
            price = trade_object.first().price
        else:
            return 0.0
        cost_object = Cost.objects.filter(company_symbol=symbol, date=date)
        if cost_object.exists():
            unit_quantity = cost_object.first().unit_quantity
        else:
            unit_quantity = 0.0
        print("!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(quantity, price, unit_quantity)
        return quantity*(price-unit_quantity)

    @staticmethod
    def total_unrealized_pnl_calculation_for_symbol_on_date(symbol: str, date: datetime.date) -> float:
        price_object = Price.objects.filter(company_symbol=symbol, date=date)
        if price_object.exists():
            close_price = price_object.first().close
        else:
            close_price = 0.0
        cost_object = Cost.objects.filter(company_symbol=symbol, date=date)
        if cost_object.exists():
            unit_quantity = cost_object.first().unit_quantity
            total_cost = cost_object.first().total_cost
        else:
            unit_quantity = 0.0
            total_cost = 0.0
        return (close_price - unit_quantity) * total_cost
    
    @staticmethod
    def daily_unrealized_pnl_calculation_for_symbol_on_date(symbol: str, date: datetime.date) -> float:
        price_object = Price.objects.filter(company_symbol=symbol, date__lte=date, date__gte=(date-timedelta(days=1))).order_by("-date")
        todays_close_price = price_object.first().close if price_object.first() else 0.0
        yesterdays_close_price = price_object.last().close if price_object.last() else 0.0
        cost_object = Cost.objects.filter(company_symbol=symbol, date=date)
        if cost_object.exists():
            unit_quantity = cost_object.first().unit_quantity
        else:
            unit_quantity = 0.0
        return (todays_close_price - yesterdays_close_price) * unit_quantity
