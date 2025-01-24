from datetime import datetime

from celery import shared_task
from django.db import IntegrityError

from .utils import extract_data_from_line
from .models import Client, Order, Product, ProductOrder


@shared_task
def proccess_file_async(uploaded_file):
    errors = 0
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
            print(f'user_id: {extracted_data.user_id}, error: {str(e)}')
            errors += 1
        except Exception as e:
            print(f'error: {e}')
            return f'error: {e}'
    return f'File processed successfully. Success: {line_successfully}, errors: {errors}'
