from rest_framework import serializers
from trading.models import Price, Trade

class ExcelUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        if not value.name.endswith(('.xls', '.xlsx')):
            raise serializers.ValidationError("Only Excel files are allowed.")
        return value

class DateInputSerializer(serializers.Serializer):
    date = serializers.DateField(required=True, format='%Y-%m-%d')
    

class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = ['company_symbol', 'date', 'close', 'high', 'low', 'open', 'volume', 'dividents', 'stock_split']


class TradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = '__all__'
