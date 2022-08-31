from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from store.models import Product, Variation
from .models import Cart, CartItem

def __session_id(request):
    cartid = request.session.session_key
    if not cartid:
        cartid = request.session.create()
    return cartid


def add_cart(request, product_id):
    product = Product.objects.get(pk=product_id)
    #wrangler shirt
    product_variation = []
    #[<Variation: Red>, <Variation: Medium>]

    if request.method == "POST":
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)
            except Variation.DoesNotExist:
                pass
        #this for loop above populoates the product_variation array

        try:
                cart = Cart.objects.get(cart_id=__session_id(request))
        except Cart.DoesNotExist:
                cart = Cart.objects.create(cart_id=__session_id(request))
                cart.save()

        # obs 1: we create the cart item even if the item already exists with or without variations

        #check if we already have this item in cart with same  variations
        cart_item_exists = CartItem.objects.filter(cart=cart, product=product).exists()
        if cart_item_exists:
            cart_item = CartItem.objects.filter(cart=cart, product=product)
            existing_variations = []
            #[[<Variation: Red>, <Variation: Medium>], [<Variation: Green>, <Variation: Small>]]
            ids = []
            #ids =  [2, 3, 4]
            #this  cart already has this wrangler shirt

            for item in cart_item:
                ex_vars = item.variations.all()
                existing_variations.append(list(ex_vars))
                ids.append(item.id)

            if product_variation in existing_variations:
                index = existing_variations.index(product_variation)
                item_id = ids[index]
                item = CartItem.objects.get(pk=item_id)
                item.quantity += 1
                item.save()
            else:
                cart_item = CartItem.objects.create(
                    cart = cart,
                    product = product,
                    quantity = 1
                )
                if len(product_variation) > 0:
                    cart_item.variations.set(product_variation)
                cart_item.save()

        else:
            #cart doesnt have tthis wrangler shirt
            cart_item = CartItem.objects.create(
                cart = cart,
                product = product,
                quantity = 1
            )
            if len(product_variation) > 0:
                cart_item.variations.set(product_variation)
            cart_item.save()

    return redirect('cart')

def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, pk=product_id)
    cart =  Cart.objects.get(cart_id=__session_id(request))
    try:
        cart_item = CartItem.objects.get(cart=cart,product=product,pk=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, pk=product_id)
    cart =  Cart.objects.get(cart_id=__session_id(request))
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product, pk=cart_item_id)
        cart_item.delete()
    except:
        pass
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

@login_required(login_url='login')
def checkout(request):
    cart_items = CartItem.objects.filter(cart__cart_id=__session_id(request), is_active=True)
    context = {
        'cart_items': cart_items
    }
    return render(request, 'store/checkout.html', context)
