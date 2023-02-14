from django.db import models


class Item(models.Model):
    name = models.CharField('Название', max_length=50)
    description = models.CharField('Описание', max_length=300)
    price = models.FloatField('Цена в долларах')
    price_api_id = models.TextField('ID цены')
    image = models.ImageField('Изображение', null=True)
    currency = models.CharField('Валюта покупки', max_length=3, default='usd')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class Discount(models.Model):
    name = models.CharField('Название купона', max_length=50)
    coupon_api_id = models.CharField('ID купона', max_length=50)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    discount_amount = models.PositiveIntegerField(
        'Размер скидки',
        max_length=3,
        null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Скидка'
        verbose_name_plural = 'Скидки'


class Order(models.Model):
    id = models.AutoField(null=False, primary_key=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class ItemInOrder(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField('Количество')
    name = models.CharField('Название', max_length=50)
    price = models.FloatField('Цена')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Содержимое заказа'
        verbose_name_plural = 'Содержимое заказов'
