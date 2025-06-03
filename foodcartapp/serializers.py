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
