from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product
from carts.views import __session_id
from carts.models import  Cart, CartItem


def store(request, category_slug=None):
    if category_slug != None:
        products = Product.objects.filter(is_available=True, category__slug=category_slug).order_by('id')
    else:
        products = Product.objects.filter(is_available=True).order_by('id')
    paginated_products = Paginator(products,3)
    page_number = request.GET.get('page')
    page_obj = paginated_products.get_page(page_number)
    product_count = products.count()
    context = {
        'products': page_obj,
        'paginated_products': paginated_products,
        'product_count': product_count
    }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    except Exception as e:
        raise e
    in_cart = CartItem.objects.filter(cart__cart_id=__session_id(request), product=product).exists()
    context = {
        'product': product,
        'in_cart': in_cart
    }
    return render(request, 'store/product_detail.html', context)


def search(request):
    keyword = request.GET['q']
    if keyword:
        result = Product.objects.filter(Q(name__icontains=keyword) | Q(description__icontains=keyword))
        product_count = result.count()
        context = {
            'products': result,
            'product_count': product_count
        }
    else:
        context = {}

    return render(request, 'store/store.html', context)
