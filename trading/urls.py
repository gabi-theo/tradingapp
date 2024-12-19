from django.urls import path
from .views import CurrentPositionView, DailyNetPositionView, DailyPnLView, ExcelUploadView, PriceDataView, TradeListView

urlpatterns = [
    path('upload-excel/', ExcelUploadView.as_view(), name='upload-excel'),
    path('daily-net-position/', DailyNetPositionView.as_view(), name='daily-net-position'),
    path('price-data/', PriceDataView.as_view(), name='price_data_view'),
    path('trades/', TradeListView.as_view(), name='trade-list'),
    path('daily-pnl/', DailyPnLView.as_view(), name='daily-pnl'),
    path('current-position/', CurrentPositionView.as_view(), name='current-position'),
]
