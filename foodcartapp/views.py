from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from .models import Product, Order, OrderProduct
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer, ListField
from django.db import transaction


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
    print("def product_list_api(request):")
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


@transaction.atomic
@api_view(['POST'])
def register_order(request):
    print("def register_order(request)")
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    order = Order.objects.create(
        firstname=serializer.validated_data['firstname'],
        lastname=serializer.validated_data['lastname'],
        phonenumber=serializer.validated_data['phonenumber'],
        address=serializer.validated_data['address']
        )
    for product in serializer.validated_data['products']:
        OrderProduct.objects.create(
            product=product["product"],
            order=order,
            price=product['product'].price*product['quantity'],
            quantity=product["quantity"]
            )
    order_front = OrderSerializer(order).data
    return Response(order_front)
