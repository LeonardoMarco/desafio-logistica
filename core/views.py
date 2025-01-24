from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework import status
from django.core.cache import cache

from .tasks import proccess_file_async
from .utils import set_orders_cache


class FileProcessor(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        uploaded_file = request.FILES.get('file', None)

        if uploaded_file and not uploaded_file.name.endswith('.txt'):
            return Response({'error': 'No valid .txt file provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            proccess_file_async.delay(uploaded_file)

            return Response(
                {
                    'message': 'File processed successfully',
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GetOrders(APIView):
    def get(self, request):
        order_id = request.query_params.get('order_id', None)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        try:
            if start_date:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')

            if end_date:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')

            orders_data = cache.get('orders_data')

            if not orders_data:
                set_orders_cache()
                orders_data = cache.get('orders_data')

            result = []
            for user in orders_data:
                filtered_orders = []
                for order in user.get('orders', []):

                    if start_date and order['date'] < start_date_obj.date():
                        continue
                    if end_date and order['date'] > end_date_obj.date():
                        continue
                    if order_id and order['order_id'] != int(order_id):
                        continue

                    filtered_orders.append(order)

                if filtered_orders:
                    result.append({
                        'user_id': user['user_id'],
                        'name': user['name'],
                        'orders': filtered_orders
                    })

            if len(result) == 0:
                return Response({'message': 'not found Order'}, status=status.HTTP_404_NOT_FOUND)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
