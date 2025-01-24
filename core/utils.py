from collections import namedtuple


ExtractedData = namedtuple('ExtractedData', ['user_id', 'name', 'order_id', 'product_id', 'product_value', 'created_at'])

def extract_data_from_line(line):
    line = line.decode('utf-8')

    user_id = line[:10]
    name = line[11:55].strip()
    order_id = line[55:65]
    product_id = line[65:75]
    product_value = line[75:87].strip()
    created_at = line[-9:].strip()

    return ExtractedData(user_id, name, order_id, product_id, product_value, created_at)
