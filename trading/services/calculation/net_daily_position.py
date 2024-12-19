from datetime import datetime
from django.db.models import Sum, Q

from trading.models import DailyNetPosition, Trade


class NetDailyPositionService:
    @staticmethod
    def calculate_daily_net_position(day: datetime.date) -> dict:
        print("ENTERED")
        result = (
            Trade.objects
            .filter(date=day)
            .values('company_symbol')
            .annotate(
                total_buy=Sum('quantity', filter=Q(direction = 'buy')),
                total_sell=Sum('quantity', filter=Q(direction = 'sell'))
            )
            .order_by('company_symbol')
        )

        for item in result:
            DailyNetPosition.objects.get_or_create(
                date=day,
                company_symbol=item['company_symbol'],
                daily_net_position=(item['total_buy'] or 0) - (item['total_sell'] or 0)
            )

        return result