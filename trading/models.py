from django.db import models

# Create your models here.


class Trade(models.Model):
    DIRECTION = (
        ('buy', "BUY"),
        ('sell', "SELL"),
    )

    date = models.DateField(null=False, blank=False)
    company_symbol = models.CharField(max_length=10)
    quantity = models.IntegerField(default=0, null=False, blank=False)
    price = models.FloatField(default=0, null=False, blank=False)
    direction = models.CharField(max_length=50, choices=DIRECTION, blank=False, null=False)


class Ticker(models.Model):
    company_symbol = models.CharField(max_length=10)
    security_name = models.CharField(max_length=500)
    market_category = models.CharField(max_length=100)
    test_issue = models.CharField(max_length=10)
    financial_status = models.CharField(max_length=10)
    round_lot_size = models.CharField(max_length=10)
    etf = models.CharField(max_length=10)
    next_shares = models.CharField(max_length=10)

class StockPriceBase(models.Model):
    company_symbol = models.CharField(max_length=10)
    date = models.DateField()
    close = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    open = models.FloatField()
    volume = models.IntegerField()


class Stock(StockPriceBase):
    adj_close = models.FloatField()


class Price(StockPriceBase):
    dividents = models.FloatField()
    stock_split = models.FloatField()


class TradeError(models.Model):
    LEVEL = (
        ("excel_file", "Excel File"),
        ("excel_row", "Excel Row"),
        ("fyahoo_api_call", "FYahoo Api Call"),
        ("other", "Other"),
    )

    date = models.DateTimeField(auto_now_add=True)
    error = models.TextField(null=False, blank=False)
    level = models.CharField(max_length=20, choices=LEVEL,)

class DailyNetPosition(models.Model):
    date = models.DateField()
    company_symbol = models.CharField(max_length=10)
    daily_net_position = models.FloatField()


class Cost(models.Model):
    date = models.DateField()
    company_symbol = models.CharField(max_length=10)
    added_cost = models.FloatField()
    removed_cost = models.FloatField()
    total_cost = models.FloatField()
    unit_quantity = models.FloatField()
