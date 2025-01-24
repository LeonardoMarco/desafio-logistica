from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework import status
from .utils import extract_data_from_line
from .models import Client, Order, Product, ProductOrder
from datetime import datetime
from django.db import IntegrityError


class FileProcessor(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get('file', None)

        if uploaded_file and not uploaded_file.name.endswith('.txt'):
            return Response({'error': 'No valid .txt file provided'}, status=status.HTTP_400_BAD_REQUEST)

        id_errors = []
        line_successfully = 0

        for line in uploaded_file:
            try:
                extracted_data = extract_data_from_line(line)

                client, _ = Client.objects.get_or_create(
                    id=extracted_data.user_id,
                    name=extracted_data.name.strip(),
                )

                order, _ = Order.objects.get_or_create(
                    id=extracted_data.order_id,
                    created_at=datetime.strptime(extracted_data.created_at.strip(), '%Y%m%d'),
                    client=client
                )

                product, _ = Product.objects.get_or_create(
                    id=extracted_data.product_id
                )

                _, _ = ProductOrder.objects.get_or_create(
                    order=order,
                    product=product,
                    value=extracted_data.product_value.strip()
                )

                line_successfully += 1
            except IntegrityError as e:
                id_errors.append({'user_id': extracted_data.user_id, 'error': str(e)})
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {
                'message': 'File processed successfully',
                'line_successfully': line_successfully,
                'id_errors': id_errors
            },
            status=status.HTTP_200_OK
        )


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
