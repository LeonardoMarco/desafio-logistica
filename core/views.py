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
