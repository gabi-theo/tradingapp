from datetime import datetime

from trading.models import DailyNetPosition, Price


class MarketValueService:
    @staticmethod
    def calculate_market_value_for_symbol_on_date(symbol: str, date: datetime.date):
        market_close_price = Price.objects.filter(date=date, company_symbol=symbol.upper())
        if market_close_price.exists():
            market_close_price = market_close_price.first().close
        else:
            market_close_price = 0
        daily_net_position = DailyNetPosition.objects.filter(date=date, company_symbol=symbol.upper())
        if daily_net_position.exists():
            daily_net_position = daily_net_position.first().daily_net_position
        else:
            daily_net_position = 0
        return daily_net_position * market_close_price