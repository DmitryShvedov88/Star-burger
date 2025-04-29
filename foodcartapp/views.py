import json
from django.http import JsonResponse
import phonenumbers
from django.templatetags.static import static
from rest_framework.decorators import api_view
from .models import Product, Order, OrderProduct
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from django.shortcuts import get_object_or_404


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()
    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'contact_phone',
            'adress', 'order_products'
        ]


class OrderProductSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'product', 'order', 'quantity'
        ]


@api_view(['POST'])
def register_order(request):

    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    order = Order.objects.create(
        firstname=serializer.is_valid['firstname'],
        lastname=serializer.is_valid['lastname'],
        contact_phone=serializer.is_valid['phonenumber'],
        adress=serializer.is_valid['address']
        )

    serializer_product = OrderSerializer(data=request.data)
    serializer_product.is_valid(raise_exception=True)
    for product in serializer_product.is_valid['products']:
        product_id = get_object_or_404(Product, product["product"])
        OrderProduct.objects.create(
            product=serializer_product.is_valid["product_id"],
            order=order,
            quantity=serializer_product.is_valid["quantity"]
            )
    return Response({'error': 'Заказ записан'}, status=status.HTTP_201_CREATED)
