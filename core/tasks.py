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

            cliente_id = extracted_data.user_id.lstrip("0")
            order_id = extracted_data.order_id.lstrip("0")
            product_id = extracted_data.product_id.lstrip("0")

            if cliente_id and order_id and product_id:
                client, _ = Client.objects.get_or_create(
                    id=int(cliente_id),
                    name=extracted_data.name.strip(),
                )

                order, _ = Order.objects.get_or_create(
                    id=int(order_id),
                    created_at=datetime.strptime(extracted_data.created_at.strip(), '%Y%m%d'),
                    client=client
                )

                product, _ = Product.objects.get_or_create(
                    id=int(product_id)
                )

                _, _ = ProductOrder.objects.get_or_create(
                    order=order,
                    product=product,
                    value=extracted_data.product_value.strip()
                )

                print(f'INFO: Processed line. Client: {extracted_data.name.strip()}, Order: {extracted_data.order_id}')
                line_successfully += 1
            else:
                print(f'ERROR: Line order is not valid. Client: {extracted_data.name.strip()}, Order: {extracted_data.order_id}')
                errors += 1
        except IntegrityError as e:
            print(f'ERROR: user_id: {extracted_data.user_id}, error: {str(e)}')
            errors += 1
        except Exception as e:
            return f'error: {e}'
    return f'File processed successfully. Success: {line_successfully}, errors: {errors}'
