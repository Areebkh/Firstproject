from django.urls import path
from .views import (
    checkout_view,
    Home_page_view,
    ProductDetails_view,
    add_to_cart,
    remove_from_cart,
    OrderSummaryView,
    remove_single_item_from_cart,
    Search_view,
    PaymentView,
    )

app_name = 'ecommerce'
urlpatterns = [
    path('',  Home_page_view.as_view(), name='homepage'),
    path('checkout/', checkout_view, name='checkout'),
    path('search/', Search_view, name='search'),
    path('product/<slug>/', ProductDetails_view.as_view(), name='product'),
    path('add_to_cart/<slug>/', add_to_cart, name='add_to_cart'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('remove_from_cart/<slug>/', remove_from_cart, name='remove_from_cart'),
    path('remove_item_from_cart/<slug>/', remove_single_item_from_cart, name='remove_single_item_from_cart'),
    path('payment/', PaymentView.as_view(), name='payment')
    ]
