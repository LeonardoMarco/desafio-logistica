from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework import status
from .utils import extract_data_from_line
from .models import Client, Order, Product, ProductOrder
from datetime import datetime


class FileProcessor(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get('file', None)

        if uploaded_file and uploaded_file.name.endswith('.txt'):
            try:
                for line in uploaded_file:
                    extracted_data = extract_data_from_line(line)

                    client, _ = Client.objects.get_or_create(
                        id=extracted_data.user_id,
                        name=extracted_data.name,
                    )

                    order, _ = Order.objects.get_or_create(
                        id=extracted_data.order_id,
                        created_at=datetime.strptime(extracted_data.created_at, '%Y%m%d'),
                        client=client
                    )

                    product, _ = Product.objects.get_or_create(
                        id=extracted_data.product_id
                    )

                    ProductOrder.objects.create(
                        order=order,
                        product=product,
                        value=extracted_data.product_value
                    )

                return Response({'message': 'File processed successfully'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'No valid .txt file provided'}, status=status.HTTP_400_BAD_REQUEST)
