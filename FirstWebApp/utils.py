import json
from .models import *

def cookiesCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    print(cart)
    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0}
    cartItems = order['get_cart_items'] 
    try:
        for i in cart:
            cartItems += cart[i]['quantity']
            item = Item.objects.get(slug=i)
            total = (item.price * cart[i]['quantity'])
            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']
            if item.discount_price:
                saving = (item.price - item.discount_price)
            else:
                saving = 0
            product = {
                'item': {
                    'slug': item.slug,
                    'title': item.title,
                    'price': item.price,
                    'discount_price': item.discount_price,
                    'saving': saving,
                    },
                'quantity': cart[i]['quantity'],
                'get_total': total,
            }
            items.append(product)
    except:
        pass
    return {'order': order, 'items': items, 'cartItems': cartItems}
