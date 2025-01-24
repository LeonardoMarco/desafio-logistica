from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Order(models.Model):
    created_at = models.DateField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders')

    def __str__(self):
        return f"Order #{self.id} - Client: {self.client.nome}"

    def get_order_value(self):
        product_orders = self.product_orders.all()

        total_value = sum(order.value for order in product_orders)

        return total_value


class Product(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Product #{self.id}"


class ProductOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='product_orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_orders')
    value = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order #{self.order.id} - Product #{self.product.id} - Value: {self.value}"
