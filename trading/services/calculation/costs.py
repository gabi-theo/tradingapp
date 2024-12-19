from datetime import datetime
from django.db.models import Sum, F, Case, When, Value, FloatField

from trading.models import Cost, DailyNetPosition, Trade


class CostsService:
    @staticmethod
    def calculate_costs_for_day(date: datetime.date):
        result = (
            Trade.objects.filter(date=date)
            .values('company_symbol')
            .annotate(
                added_cost=Sum(
                    Case(
                        When(direction='buy', then=F('quantity') * F('price')),
                        default=Value(0),
                        output_field=FloatField()
                    )
                ),
                removed_cost=Sum(
                    Case(
                        When(direction='sell', then=F('quantity') * F('price')),
                        default=Value(0),
                        output_field=FloatField()
                    )
                ),
                total_cost=(
                    Sum(
                        Case(
                            When(direction='buy', then=F('quantity') * F('price')),
                            default=Value(0),
                            output_field=FloatField()
                        )
                    ) -
                    Sum(
                        Case(
                            When(direction='sell', then=F('quantity') * F('price')),
                            default=Value(0),
                            output_field=FloatField()
                        )
                    )
                )
            )
        )
        for item in result:
            daily_net_position = DailyNetPosition.objects.filter(date=date, company_symbol=item['company_symbol'])
            Cost.objects.get_or_create(
                date=date,
                company_symbol=item['company_symbol'],
                added_cost=item.get('added_cost', 0.0),
                removed_cost=item.get('removed_cost', 0.0),
                total_cost=item.get('total_cost', 0.0),
                unit_quantity=(
                    item.get('total_cost', 0.0)/(
                        daily_net_position.first().daily_net_position if daily_net_position.exists() else 1
                        )
                    )
            )

        return result