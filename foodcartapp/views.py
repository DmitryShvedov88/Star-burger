import json
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
# import requests
from .models import Product, Order, OrderProduct


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
    # print("dumped_products")
    # print(dumped_products)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })

@api_view(['POST'])
def register_order(request):
    try:
        data = json.loads(request.body.decode())
        # print("data")
        # print(data)
        order = Order.objects.create(
            first_name=data["firstname"],
            last_name=data["lastname"],
            contact_phone=data["phonenumber"],
            adress=data["address"]
        )

        for product in data["products"]:
            # print("product")
            product_id = product["product"]
            quantity = product["quantity"]
            product = Product.objects.get(id=product_id)
            OrderProduct.objects.create(
                product=product,
                order=order,
                quantity=quantity
            )
    except ValueError:
        return JsonResponse({
            'error': 'ValueError',
        })
    return JsonResponse({})
