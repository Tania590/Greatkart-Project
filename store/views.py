from django.shortcuts import render
from .models import Product

def store(request, category_slug=None):
    if category_slug != None:
        products = Product.objects.filter(is_available=True, category__slug=category_slug)
    else:
        products = Product.objects.filter(is_available=True)
    product_count = products.count()
    context = {
        'products': products,
        'product_count': product_count
    }
    return render(request, 'store/store.html', context)
