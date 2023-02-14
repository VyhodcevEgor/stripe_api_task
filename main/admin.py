from django.contrib import admin
from .models import Item, Discount, Order, ItemInOrder


admin.site.register(Item)
admin.site.register(Discount)
admin.site.register(Order)
admin.site.register(ItemInOrder)
