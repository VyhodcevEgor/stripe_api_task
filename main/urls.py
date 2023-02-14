from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('item/<int:pk>', views.ItemDetailView.as_view(), name='item_details'),
    path('buy/<int:pk>', views.CreateCheckoutSessionView.as_view(), name='buy_item'),
    path('success/', views.success_payment, name='success'),
    path('cancel/', views.payment_cancelled, name='cancel'),
    path('create-payment-intent/<int:pk>', views.StripeIntentView.as_view(), name='create-payment-intent'),
    path('create-order/', views.create_order, name='create_order'),
    path('cart/add/<int:id>/', views.add_to_cart, name='cart_add'),
    path('cart/cart-detail/', views.cart_detail, name='cart_detail'),
    path('cart/cart-clear/', views.clear_cart, name='clear_cart'),
    path('cart/item_increment/<int:id>/',
         views.item_increment, name='item_increment'),
    path('cart/item_decrement/<int:id>/',
         views.item_decrement, name='item_decrement'),
    path('buy/order/<int:pk>', views.CreateOrderCheckoutSessionView.as_view(), name='buy_order'),
    path('create-order-payment-intent/<int:pk>', views.StripeOrderIntentView.as_view(), name='create-order-payment-intent'),
]
