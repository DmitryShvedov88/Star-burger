from rest_framework.serializers import ModelSerializer, ListField

from foodcartapp.models import Order, OrderProduct


class OrderProductSerializer(ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = [
            'product', 'quantity'
        ]


class OrderSerializer(ModelSerializer):
    products = ListField(
        child=OrderProductSerializer(),
        write_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id', 'firstname', 'lastname',
            'phonenumber', 'address', 'products'
        ]

    def create(self, validated_data):
        order = Order.objects.create(
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            phonenumber=validated_data['phonenumber'],
            address=validated_data['address']
            )
        order_products = [
            OrderProduct(
                product=product["product"],
                order=order,
                price=product['product'].price*product['quantity'],
                quantity=product["quantity"]
            )
            for product in validated_data['products']
        ]
        OrderProduct.objects.bulk_create(order_products)
        return order
