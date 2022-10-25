from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserForm, UserProfileForm
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from .models import Account, UserProfile
from orders.models import Order, OrderedProduct
from carts.models import CartItem
from carts.views import __session_id
import requests


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            username = email.split('@')[0]
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']

            user = Account.objects.create_user(
                first_name = first_name,
                last_name = last_name,
                email = email,
                username = username,
                password = password
            )
            user.phone_number = phone_number
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Please Activate Your Account.'
            message = render_to_string('accounts/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            from_email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            from_email.send()
            return redirect('/accounts/login?command=verification&email='+email)
    else:
        form = RegistrationForm()
    context = {
        'form': form
    }
    return render(request, 'accounts/register.html',context)

def activate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Account.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request, 'Email Verification successful. You can now log in to your account.')
        return redirect('login')

    else:
        messages.error(request, 'Invalid Activation Link.')
        return redirect('register')

def login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(request, email=email, password=password)
        if user is not None:
            cart_items = CartItem.objects.filter(cart__cart_id=__session_id(request))
            if cart_items:
                item_variations = []
                item_ids = []
                for item in cart_items:
                    ex_vars = item.variations.all()
                    item_variations.append(list(ex_vars))
                    item_ids.append(item.id)
                users_cart_items = CartItem.objects.filter(user=user)
                if users_cart_items:

                    users_existing_variations = []
                    ids = []
                    for item in users_cart_items:
                        existing_variations = item.variations.all()
                        users_existing_variations.append(list(existing_variations))
                        ids.append(item.id)
                    for item in item_variations:
                        if item in users_existing_variations:
                            index = users_existing_variations.index(item)
                            item_id = ids[index]
                            item = CartItem.objects.get(pk=item_id)
                            item.quantity += 1
                            item.save()
                        else:
                            index = item_variations.index(item)
                            item_id = item_ids[index]
                            item = CartItem.objects.get(pk=item_id)
                            item.user = user
                            item.save()
                else:
                    for item in cart_items:
                        item.user = user
                        item.save()
            auth.login(request,user)
            messages.success(request, 'You are now logged in.')
            url = request.META['HTTP_REFERER']
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    next_page = params['next']
                    return redirect(next_page)
            except:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid Login Credentials.')
            return redirect('login')
    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You have successfully logged out.')
    return redirect('login')

@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True)
    user_profile = UserProfile.objects.get(user=request.user)
    context = {
        'orders': orders,
        'order_count': orders.count(),
        'user_profile': user_profile
    }
    return render(request, 'accounts/dashboard.html', context)


def forgot_password(request):
    if request.method == "POST":
        email = request.POST['email']
        try:
            user = Account.objects.get(email__exact=email)
            current_site = get_current_site(request)
            mail_subject = 'Please Reset Your Password.'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            from_email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            from_email.send()
            messages.success(request, 'Password Reset email has been sent at your email address.')
            return redirect('login')
        except Account.DoesNotExist:
            messages.error(request, 'Account with this email address does not exist.')
            return redirect('forgot_password')
    return render(request, 'accounts/forgot_password.html')

def reset_password_validation(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        request.session['uid'] = uid
        user = Account.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user,token):
        messages.success(request, 'Please Reset Your Password')
        return redirect('reset_password')
    else:
        messages.error(request, 'This Link has expired .')
        return redirect('login')

def reset_password(request):
    if request.method == "POST":
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            uid = request.session['uid']
            user = Account.objects.get(pk=uid)
            user.set_password(password1)
            user.save()
            messages.success(request, 'Password Reset Successful')
            return redirect('login')
        else:
            messages.error(request, 'Passwords did not match.')
            return redirect('reset_password')
    return render(request, 'accounts/reset_password.html')

@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True)
    context = {
        'orders': orders
    }
    return render(request, 'accounts/my_orders.html', context)


@login_required(login_url='login')
def edit_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        user_profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid() and user_profile_form.is_valid():
            user_form.save()
            user_profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        user_profile_form = UserProfileForm(instance=user_profile)
    context = {
        'user_form': user_form,
        'user_profile_form': user_profile_form
    }
    return render(request, 'accounts/edit_profile.html', context)

@login_required(login_url='login')
def change_password(request):
    if request.method == "POST":
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            check = user.check_password(current_password)
            if check:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password Updated Successfully')
                return redirect('change_password')
            else:
                messages.error(request, 'Incorrect Password')
                return redirect('change_password')
        else:
            messages.error(request, 'Passwords did not match.')
            return redirect('change_password')
    return render(request, 'accounts/change_password.html')

@login_required(login_url='login')
def order_detail(request, order_id):
    order = Order.objects.get(order_number=order_id)
    ordered_products = OrderedProduct.objects.filter(order__order_number=order_id)
    sub_total=0
    for item in ordered_products:
        sub_total += item.quantity * item.product_price
    context = {
        'order': order,
        'ordered_products': ordered_products,
        'sub_total': sub_total
    }
    return render(request, 'accounts/order_detail.html', context)
