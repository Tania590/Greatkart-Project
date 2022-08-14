from django.shortcuts import render, redirect
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

def cart(request):
    return render(request, 'carts/cart.html')
