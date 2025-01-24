from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework import status

from .models import Client
from .tasks import proccess_file_async


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

        filters_client = {}
        filters_order = {}

        if order_id:
            filters_client['orders__id'] = order_id
            filters_order['id'] = order_id

        try:
            if start_date:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
                filters_client['orders__created_at__gte'] = start_date_obj
                filters_order['created_at__gte'] = start_date_obj

            if end_date:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
                filters_client['orders__created_at__lte'] = end_date_obj
                filters_order['created_at__lte'] = end_date_obj
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        clients = Client.objects.filter(**filters_client)

        data = [
            {
                "user_id": client.id,
                "name": client.name,
                "orders": [
                    {
                        "order_id": order.id,
                        "total": order.get_order_value(),
                        "date": order.created_at,
                        "products": [
                            {
                                "product_id": product_order.product_id,
                                "value": product_order.value
                            }
                            for product_order in order.product_orders.all()
                        ]
                    }
                    for order in client.orders.filter(**filters_order)
                ]
            }
            for client in clients
        ]

        return Response(data, status=status.HTTP_200_OK)
