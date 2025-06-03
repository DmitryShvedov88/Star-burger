import requests
from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from places.models import Place
from django.db import transaction
from foodcartapp.models import Product, Restaurant, Order
from geopy.distance import geodesic
from django.conf import settings


YANDEX_API_KEY = settings.YANDEX_API_KEY


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def calculate_distance(delivery_coords, restaurant_coords):
    restaurant_coords = fetch_coordinates(YANDEX_API_KEY, restaurant_coords)
    delivery_coords = fetch_coordinates(YANDEX_API_KEY, delivery_coords)
    if delivery_coords is None or restaurant_coords is None:
        return None
    return geodesic(restaurant_coords, delivery_coords).km


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {
            item.restaurant_id: item.availability
            for item in product.menu_items.all()
        }
        ordered_availability = [
            availability.get(restaurant.id, False)
            for restaurant in restaurants
        ]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(
        request,
        template_name="products_list.html",
        context={
            'products_with_restaurant_availability': products_with_restaurant_availability,
            'restaurants': restaurants,
        }
    )


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):

    order_items = Order.objects.filter(
        status__in=["CR", "IP", "IK", "KP", "DTC", "IT", "DE"]
    ).final_price().prefetch_related(
        'orders__product'
        ).select_related("restaurant").get_restaurants_for_order()
    with transaction.atomic():
        for order in order_items:
            new_status = None
            if order.status == "IP" and order.restaurant:
                new_status = "IK"
            elif order.status == "IK" and order.restaurant:
                new_status = "KP"
            elif order.status == "KP" and order.restaurant:
                new_status = "DTC"

            restaurant_dist = []
            for restaurant in order.available_restaurants:
                order_place, _ = Place.objects.get_or_create(
                    address=order.address
                )
                restaurant_place, _ = Place.objects.get_or_create(
                    address=restaurant.address
                )
                distance = calculate_distance(
                    order_place.address, restaurant_place.address
                )
                if distance is None:
                    order.available_restaurants = None
                    break
                restaurant_dist.append(
                    {
                        "distance": round(distance, 3),
                        "restaurant": restaurant.name
                        }
                )
            order.available_restaurants = sorted(
                restaurant_dist, key=lambda x: ["distance"]
            )

        if new_status:
            order.status = new_status
            order.save()

    return render(request, template_name='order_items.html', context={
        'order_items': order_items,
    })
