from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import OrderForm
from .models import Order, Payment, OrderedProduct
from carts.models import CartItem
from store.models import Product
import datetime
import json
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

#login required
def place_order(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items:
        return redirect('store')
    total = 0
    for cart_item in cart_items:
        total += cart_item.sub_total()
    tax = (2*total)/100
    grand_total = total+tax

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.user = request.user
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.email = form.cleaned_data['email']
            order.phone_number = form.cleaned_data['phone_number']
            order.address_line_1 = form.cleaned_data['address_line_1']
            order.address_line_2 = form.cleaned_data['address_line_2']
            order.city = form.cleaned_data['city']
            order.state = form.cleaned_data['state']
            order.country = form.cleaned_data['country']
            order.order_note = form.cleaned_data['order_note']
            order.order_total = grand_total
            order.tax = tax
            order.ip = request.META['REMOTE_ADDR']
            order.save()
            date_time = datetime.datetime.now().strftime("%Y%m%d")
            order_number = date_time + str(order.id)
            #202209101
            order.order_number = order_number
            order.save()
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
            }
            return render(request, 'orders/payments.html', context)

        else:
            return redirect('checkout')


def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, order_number=body['orderId'],is_ordered=False)
    payment = Payment()
    payment.user = request.user
    payment.payment_id = body['transId']
    payment.payment_method = body['paymentMethod']
    payment.amount_paid = order.order_total
    payment.status = body['status']
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()

    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        ordered_product = OrderedProduct()
        ordered_product.order_id = order.id
        ordered_product.payment = payment
        ordered_product.user_id = request.user.id
        ordered_product.product_id = item.product.id
        ordered_product.quantity = item.quantity
        ordered_product.product_price = item.product.price
        ordered_product.ordered = True
        ordered_product.save()
        cart_item = CartItem.objects.get(pk=item.id)
        product_variations = cart_item.variations.all()
        ordered_product.variations.set(product_variations)
        ordered_product.save()

        product = Product.objects.get(pk=ordered_product.product_id)
        product.stock -= ordered_product.quantity
        product.save()
    cart_items.delete()
    mail_subject = 'Thank You For Ordering With Us.'
    message = render_to_string('orders/order_received_email.html', {
        'user': request.user,
        'order': order,

    })
    to_email = request.user.email
    from_email = EmailMessage(
        mail_subject, message, to=[to_email]
    )
    from_email.send()
    data = {
        'order_number': order.order_number,
        'transId': payment.payment_id
    }
    return JsonResponse(data)


def order_complete(request):
    order_number = request.GET['order_number']
    transaction_id = request.GET['payment_id']
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        payment = Payment.objects.get(payment_id=transaction_id)
        ordered_products = OrderedProduct.objects.filter(order__order_number=order_number, payment__payment_id=transaction_id)
        sub_total = 0
        for item in ordered_products:
            sub_total += item.quantity * item.product_price
        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transaction_id': payment.payment_id,
            'payment': payment,
            'sub_total': sub_total
        }
    except (Order.DoesNotExist, Payment.DoesNotExist, OrderedProduct.DoesNotExist) :
        return redirect('home')
    return render(request, 'orders/order_complete.html', context)
