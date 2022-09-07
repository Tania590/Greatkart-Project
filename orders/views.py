from django.shortcuts import render, redirect
from .forms import OrderForm
from .models import Order
from carts.models import CartItem
import datetime

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
    return render(request, 'orders/payments.html')
