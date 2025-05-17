from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import F, Sum


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = PhoneNumberField(
        'контактный телефон',
        max_length=50,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class OrderQuerySet(models.QuerySet):
    def final_price(self):
        return self.annotate(order_price=F('orders__price'))


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Order(models.Model):
    class StatusCheck(models.TextChoices):
        CREATED = "CR", "Создан"
        IN_PROGRESS = "IP", "Принят в обработку"
        IN_KITCHEN = "IK", "Передан на приготовление"
        KICTHEN_PREPARATION = "KP", "Готовиться"
        DELIVERED_TO_COURIER = "DTC", "Передан курьеру"
        IN_TRANSIT = "IT", "В пути"
        DELIVERED = "DE", "Доставлен"
        CLOUSED = "CL", "Закрыт"
    status = models.CharField(
        max_length=25,
        choices=StatusCheck.choices,
        verbose_name="Статус",
        db_index=True,
        default=StatusCheck.CREATED
    )
    firstname = models.CharField(
        'имя',
        max_length=50
    )
    lastname = models.CharField(
        'фамилия',
        max_length=50
    )
    phonenumber = PhoneNumberField(
        'контактный телефон',
        max_length=50,
    )
    address = models.CharField(
        'адрес',
        max_length=250
    )
    comment = models.TextField(
        "Комментарий",
        max_length=250,
        blank=True
    )

    verbose_name = 'заказ'
    verbose_name_plural = 'заказы в ресторане'

    objects = OrderQuerySet.as_manager()

    def __str__(self):
        return f"{self.lastname} {self.firstname} {self.address}"


class OrderProduct(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_products',
        verbose_name='продукт',
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='заказ',
    )
    price = models.DecimalField(
        'цена в заказе',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
    )
    quantity = models.PositiveIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10)
            ],
        verbose_name='количество',
        default=1
    )

    def __str__(self):
        return f"{self.product.name}"
