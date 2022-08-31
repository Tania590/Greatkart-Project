from .models import CartItem
from .views import __session_id

def counter(request, item_total=0):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
    else:
        cart_items = CartItem.objects.filter(cart__cart_id=__session_id(request), is_active=True)
    if cart_items:
        for item in cart_items:
            item_total += item.quantity
    return {'item_total': item_total}
