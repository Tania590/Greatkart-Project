from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product
from .models import Cart, CartItem

def __session_id(request):
    cartid = request.session.session_key
    if not cartid:
        cartid = request.session.create()
    return cartid


def add_cart(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
        #wrangler shirt
        try:
            cart = Cart.objects.get(cart_id=__session_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=__session_id(request))
            cart.save()
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            #wrangler shirt already in  cart
            cart_item.quantity +=1
            cart_item.save()
        except CartItem.DoesNotExist:
            #wrangler shirt not in cart
            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=1
            )
            cart_item.save()
        return redirect('cart')
    except Product.DoesNotExist:
        return redirect('home')


def remove_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart =  Cart.objects.get(cart_id=__session_id(request))
    cart_item = CartItem.objects.get(cart=cart,product=product)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')


def remove_cart_item(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart =  Cart.objects.get(cart_id=__session_id(request))

    cart_item = CartItem.objects.get(cart=cart, product=product)
    cart_item.delete()
    return redirect('cart')


def cart(request, total=0):
    cart_items = CartItem.objects.filter(cart__cart_id=__session_id(request), is_active=True)

    if cart_items:
        for item in cart_items:
            total += item.sub_total()
    tax = (2*total)/100
    grand_total = total+tax
    context = {
        'cart_items' : cart_items,
        'total': total,
        'tax': tax,
        'grand_total': grand_total
    }
    return render(request, 'carts/cart.html', context)
