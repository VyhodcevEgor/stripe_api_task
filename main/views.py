from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import DetailView
from django.views import View
from .models import Item, Order, ItemInOrder
from cart.cart import Cart
import stripe
import os


stripe.api_key = os.environ['API_SECRET_KEY']


class ItemDetailView(DetailView):
    model = Item
    template_name = 'main/item_details.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super(ItemDetailView, self).get_context_data(**kwargs)
        context.update({
            'STRIPE_PUBLIC_KEY': os.environ['API_PUB_KEY']
        })
        return context


class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        YOUR_DOMAIN = 'http://127.0.0.1:8000'
        item_id = self.kwargs['pk']
        item = Item.objects.get(pk=item_id)
        try:
            discount = item.discount_set.all()
            if discount:
                discount_id = discount[0].coupon_api_id
                checkout_session = stripe.checkout.Session.create(
                    line_items=[
                        {
                            'price': item.price_api_id,
                            'quantity': 1,
                            "adjustable_quantity": {"enabled": True, "minimum": 1,
                                                    "maximum": 100},
                        },
                    ],
                    mode='payment',
                    currency=item.currency,
                    discounts=[{
                        'coupon': discount_id,
                    }],
                    success_url=YOUR_DOMAIN + '/success/',
                    cancel_url=YOUR_DOMAIN + '/cancel/',
                )
            else:
                checkout_session = stripe.checkout.Session.create(
                    line_items=[
                        {
                            'price': item.price_api_id,
                            'quantity': 1,
                            "adjustable_quantity": {"enabled": True,
                                                    "minimum": 1,
                                                    "maximum": 100},
                        },
                    ],
                    mode='payment',
                    currency=item.currency,
                    success_url=YOUR_DOMAIN + '/success/',
                    cancel_url=YOUR_DOMAIN + '/cancel/',
                )
        except Exception as e:
            return str(e)

        return redirect(checkout_session.url, 200)


class CreateOrderCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        line_items = []
        YOUR_DOMAIN = 'http://127.0.0.1:8000'
        order_id = self.kwargs['pk']
        order = Order.objects.get(id=order_id)
        items_in_order = order.iteminorder_set.all()
        for item in items_in_order:
            item_id = item.item_id
            api_price = item_id.price_api_id
            line_items.append({
                'price': api_price,
                'quantity': item.quantity
            })
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=line_items,
                mode='payment',
                success_url=YOUR_DOMAIN + '/success/',
                cancel_url=YOUR_DOMAIN + '/cancel/',
            )
        except Exception as e:
            return str(e)

        return redirect(checkout_session.url, 200)


class StripeIntentView(View):
    def post(self, request, *args, **kwargs):
        try:
            item_id = self.kwargs['pk']
            item = Item.objects.get(pk=item_id)
            discount = item.discount_set.all()
            if discount:
                discount_amount = discount[0].discount_amount
                disc_amount_percents = 1 - discount_amount / 100
                discounted_amount = int(
                    round(item.price * 100 * disc_amount_percents)
                )
                intent = stripe.PaymentIntent.create(
                    amount=discounted_amount,
                    currency=item.currency,
                    automatic_payment_methods={
                        'enabled': True,
                    },
                )
                return JsonResponse({
                    'clientSecret': intent.client_secret
                })
            else:
                intent = stripe.PaymentIntent.create(
                    amount=int(round(item.price * 100)),
                    currency=item.currency,
                    automatic_payment_methods={
                        'enabled': True,
                    },
                )
                return JsonResponse({
                    'clientSecret': intent.client_secret
                })
        except Exception as e:
            return JsonResponse({'error': str(e)})


class StripeOrderIntentView(View):
    def post(self, request, *args, **kwargs):
        try:
            amount = 0
            order_id = self.kwargs['pk']
            order = Order.objects.get(id=order_id)
            items_in_order = order.iteminorder_set.all()
            for item in items_in_order:
                amount += int(item.quantity * item.price * 100)
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='usd',
                automatic_payment_methods={
                    'enabled': True,
                },
            )
            return JsonResponse({
                'clientSecret': intent.client_secret
            })
        except Exception as e:
            return JsonResponse({'error': str(e)})


def create_order(request):
    order_list = []
    cart = Cart(request)
    cart_items = cart.cart.items()
    order = Order.objects.create()
    for item in cart_items:
        order_items = ItemInOrder.objects.create(
            order_id=order,
            item_id=Item.objects.get(id=item[1]['product_id']),
            quantity=item[1]['quantity'],
            name=item[1]['name'],
            price=item[1]['price'],
        )
        order_list.append(order_items)
    context = {
        'order_id': order.id,
        'items': order_list,
        'STRIPE_PUBLIC_KEY': os.environ['API_PUB_KEY']
    }
    return render(request, 'main/order_creation.html', context)


def add_to_cart(request, id):
    cart = Cart(request)
    item = Item.objects.get(id=id)
    cart.add(product=item)
    return redirect('item_details', id)


def item_increment(request, id):
    cart = Cart(request)
    item = Item.objects.get(id=id)
    cart.add(product=item)
    return redirect('cart_detail')


def item_decrement(request, id):
    cart = Cart(request)
    item = Item.objects.get(id=id)
    cart.decrement(product=item)
    return redirect('cart_detail')


def clear_cart(request):
    cart = Cart(request)
    cart.clear()
    return redirect('cart_detail')


def cart_detail(request):
    return render(request, 'main/cart_detail.html')


def index(request):
    items = Item.objects.all()
    data = {
        'items': items,
    }
    return render(request, 'main/index.html', data)


def success_payment(request):
    cart = Cart(request)
    cart.clear()
    return render(request, 'main/success.html')


def payment_cancelled(request):
    return render(request, 'main/cancel.html')
