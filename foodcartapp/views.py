import json
from jsonschema import validate, ValidationError
from django.http import JsonResponse
import phonenumbers
from django.templatetags.static import static
from rest_framework.decorators import api_view
from .models import Product, Order, OrderProduct
from rest_framework import status
from rest_framework.response import Response


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


@api_view(['POST'])
def register_order(request):
    try:
        data = json.loads(request.body.decode())
        if data:
            print("data")
            print(data)
            if not ('firstname' and 'lastname' and 'phonenumber' and 'address') in data.keys():
                print("я тут1") 
                return Response(
                    {
                        'error': 'firstname, lastname, phonenumber, address: Обязательное поле'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                    )
            if not data['firstname'] and not data['lastname'] and not data['phonenumber'] and not data['address']:
                print(data)
                return Response(
                    {'error': 'firstname, lastname, phonenumber, address: Это поле не может быть пустым'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            phonenumber = data['phonenumber']
            print(phonenumber)
            parsed_number = phonenumbers.parse(phonenumber, "RU")
            print(parsed_number)
            if not phonenumbers.is_valid_number(parsed_number):
                print("elif not phonenumbers.is_valid_number(parsed_number)")
                return Response(
                    {'error': 'Введен некорректный номер телефона'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif isinstance(data['firstname'], list):
                print("я тут3") 
                return Response(
                    {'error': 'В поле firstname положили список.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif not data['phonenumber']:
                print("я тут4") 
                return Response(
                    {'error': 'phonenumber: Это поле не может быть пустым.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif data["firstname"] == None:
                print("я тут5") 
                return Response(
                    {'error': 'firstname: Это поле не может быть пустым.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif not data["lastname"]:
                print("я тут6") 
                return Response(
                    {'error': 'Фамилия обязательный парметр'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif not data["address"]:
                print("я тут7") 
                return Response(
                    {'error': 'Адрес обязательный парметр'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif not data["products"]:
                print("я тут8") 
                return Response(
                    {'error': 'products: Этот список не может быть пустым.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                if not isinstance(data['products'], list) or not data['products']:
                    print("я тут9")
                    return Response(
                        {
                            'error':  'products: Пустое значение или не список',
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                print("я тут10")    
                order = Order.objects.create(
                    first_name=data["firstname"],
                    last_name=data["lastname"],
                    contact_phone=data["phonenumber"],
                    adress=data["address"]
                )
                for product in data["products"]:
                    print(product)
                    try:
                        product_id = product["product"]
                        quantity = product["quantity"]
                        product = Product.objects.get(id=product_id)
                        OrderProduct.objects.create(
                            product=product,
                            order=order,
                            quantity=quantity
                        )
                        return Response(
                            {'message': 'Order created successfully'},
                            status=status.HTTP_201_CREATED
                        )
                    except Product.DoesNotExist:
                        return Response(
                            {'error':  f'There are no such {product} in your order'},
                            status=status.HTTP_404_NOT_FOUND
                        )
                else:
                    return Response(
                        {'error':  'There are no products in your order'},
                        status=status.HTTP_404_NOT_FOUND
                    )
    except KeyError as e:
        print("я тут11")
        return Response(
            {'error': f'Нет данных: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        print("я тут12")
        return Response(
            {'error': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
