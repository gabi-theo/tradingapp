from datetime import datetime, timedelta
import pandas as pd

from rest_framework.generics import ListAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from trading.models import Cost, DailyNetPosition, Price, Trade
from trading.serializers import DateInputSerializer, ExcelUploadSerializer, PriceSerializer, TradeSerializer
from trading.services.calculation.net_daily_position import NetDailyPositionService
from trading.services.calculation.pnl import PNLService
from trading.services.parser.excel_parser import ExcelParserService
from trading.services.yahoo_finance.yahoo_api import YahooFinanceService


class TradeListView(ListAPIView):
    queryset = Trade.objects.all()
    serializer_class = TradeSerializer


class ExcelUploadView(APIView):
    serializer_class = ExcelUploadSerializer
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        serializer = ExcelUploadSerializer(data=request.data)
        
        if serializer.is_valid():
            uploaded_file = serializer.validated_data['file']

            try: 
                df = pd.read_excel(uploaded_file, engine='openpyxl')
                df['Direction'] = df['Direction'].astype(str).replace('nan', '')
                df = df.dropna()
                if len(df) < 1:
                    return Response({
                        "error": f"Failed to process the excel file"
                    }, status=status.HTTP_400_BAD_REQUEST)
                ExcelParserService.parse_and_store_input_excel(excel_file=df)
                data = df.to_dict(orient='records')

                return Response({
                    "message": "File uploaded and processed successfully.",
                    "data": data
                }, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({
                    "error": f"Failed to process the file: {str(e)}"
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DailyNetPositionView(APIView):
    def get(self, request, *args, **kwargs):
        serializer = DateInputSerializer(data=request.query_params)
        if serializer.is_valid():
            target_date = serializer.validated_data['date']
            net_positions = DailyNetPosition.objects.filter(date=target_date)
            if not net_positions.exists():
                return Response({
                    "message": f"No net positions found for {target_date}."
                }, status=status.HTTP_404_NOT_FOUND)

            data = [
                {
                    "company_symbol": item.company_symbol,
                    "daily_net_position": item.daily_net_position
                }
                for item in net_positions
            ]

            return Response({
                "date": target_date,
                "net_positions": data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        serializer = DateInputSerializer(data=request.query_params)
        if serializer.is_valid():
            target_date = serializer.validated_data['date']

            try:
                NetDailyPositionService.calculate_daily_net_position(target_date)

                return Response({
                    "message": f"Daily net positions calculated and stored successfully for {target_date}."
                }, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({
                    "error": f"An error occurred: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class PriceDataView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            date = request.data.get('date')
            date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

        YahooFinanceService.fetch_price_data_by_date(date)

        return Response({"message": "Price data fetched and stored successfully"}, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        try:
            date = request.query_params.get('date')
            date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

        prices = Price.objects.filter(date=date)
        serializer = PriceSerializer(prices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class DailyPnLView(APIView):
    def get(self, request):
        symbol = request.query_params.get("symbol")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if not symbol or not start_date or not end_date:
            return Response(
                {"error": "Please provide 'symbol', 'start_date', and 'end_date' query parameters."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

            date_range = [
                start_date + timedelta(days=i)
                for i in range((end_date - start_date).days + 1)
            ]

            pnl_data = []
            for date in date_range:
                realized_pnl = PNLService.daily_realized_pnl_calculation_for_symbol_on_date(symbol, date)
                unrealized_pnl = PNLService.daily_unrealized_pnl_calculation_for_symbol_on_date(symbol, date)
                total_unrealized_pnl = PNLService.total_unrealized_pnl_calculation_for_symbol_on_date(symbol, date)

                pnl_data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "realized_pnl": realized_pnl,
                    "unrealized_pnl": unrealized_pnl,
                    "total_unrealized_pnl": total_unrealized_pnl
                })

            return Response(pnl_data, status=status.HTTP_200_OK)

        except ValueError:
            return Response(
                {"error": "Invalid date format. Use 'YYYY-MM-DD' for 'start_date' and 'end_date'."},
                status=status.HTTP_400_BAD_REQUEST
            )
            

class CurrentPositionView(APIView):
    def get(self, request):
        last_trading = Trade.objects.all().order_by("-date").first()
        positions = DailyNetPosition.objects.filter(date=last_trading.date, company_symbol=last_trading.company_symbol)
        prices = Price.objects.filter(date=last_trading.date, company_symbol=last_trading.company_symbol).order_by("-date").first()
        costs = Cost.objects.filter(date=last_trading.date, company_symbol=last_trading.company_symbol).order_by("-date").first()
        daily_net_position = positions.first().daily_net_position
        response_data = [{
            "date": last_trading.date,
            "symbol": last_trading.company_symbol,
            "direction": "LONG" if daily_net_position>0 else "SHORT",
            "close": prices.close if prices else 0,
            "current_position": costs.unit_quantity,
            "total_cost": costs.total_cost,
        }]
        return Response(response_data, status=status.HTTP_200_OK)
