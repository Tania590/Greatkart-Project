from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from .models import Product, ReviewRating
from carts.views import __session_id
from carts.models import  Cart, CartItem
from orders.models import OrderedProduct
from .forms import ReviewForm

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
    product_purchased = OrderedProduct.objects.filter(user_id=request.user.id, product_id=product.id, ordered=True).exists()
    reviews = ReviewRating.objects.filter(product=product, status=True)
    context = {
        'product': product,
        'in_cart': in_cart,
        'product_purchased': product_purchased,
        'reviews': reviews
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


def submit_review(request, product_id):
    url = request.META['HTTP_REFERER']
    if request.method == "POST":
        #check if this user has already reviewd this product
        try:
            reviews = ReviewRating.objects.get(user = request.user, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank You. Your Review has been updated.')
            return redirect(url)

        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review_object = ReviewRating()
                review_object.product_id = product_id
                review_object.user = request.user
                review_object.subject = form.cleaned_data['subject']
                review_object.review = form.cleaned_data['review']
                review_object.rating = form.cleaned_data['rating']
                review_object.ip = request.META['REMOTE_ADDR']
                review_object.save()
                messages.success(request, 'Thank You. Your Review has been submitted.')
                return redirect(url)
