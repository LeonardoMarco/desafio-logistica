from collections import namedtuple
from django.core.cache import cache
from .models import Client

ExtractedData = namedtuple('ExtractedData', ['user_id', 'name', 'order_id', 'product_id', 'product_value', 'created_at'])


def extract_data_from_line(line):
    line = line.decode('utf-8')

    user_id = line[:10]
    name = line[10:55]
    order_id = line[55:65]
    product_id = line[65:75]
    product_value = line[75:87]
    created_at = line[-9:]

    return ExtractedData(user_id, name, order_id, product_id, product_value, created_at)


def set_orders_cache():
    clients = Client.objects.all()

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
                for order in client.orders.all()
            ]
        }
        for client in clients
    ]

    if len(data) > 0:
        cache.set('orders_data', data, timeout=43200)
