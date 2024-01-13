from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Profile, Cart, CartItems, Coupon
from products.models import Product
import razorpay
from django.conf import settings


# Create your views here.

def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username = email)
        if not user_obj.exists():
            messages.warning(request, "User not found..")
            return HttpResponseRedirect(request.path_info)
        
        if not user_obj[0].profile.is_email_verified:
            messages.warning(request, "Please verify your email..")
            return HttpResponseRedirect(request.path_info)

        user_obj = authenticate(request, username = email, password = password)

        if user_obj:
            login(request, user_obj)
            return redirect('/')
        
        messages.error(request, "Invalid credentials..")
        return HttpResponseRedirect(request.path_info)
        
    return render(request,'Accounts/login_page.html')


def logout_page(request):
    if request.user:
        logout(request)
        messages.success(request, "Logout successfully")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return redirect('/')


def register(request):
    if request.method == 'POST':
        first_name=request.POST['first_name']
        last_name=request.POST['last_name']
        email = request.POST.get('email')
        password = request.POST.get('password')
        # print(request.POST)
        user_obj = User.objects.filter(username = email)
        print("usser object")
        print(user_obj)
        if user_obj.exists():
            messages.warning(request, "User already exists..")
            return HttpResponseRedirect(request.path_info)
        user_obj = User.objects.create(first_name=first_name, last_name=last_name, email=email, username=email)
        user_obj.set_password(password)
        user_obj.save()
        # print(user_obj.get_full_name())
        messages.success(request, "User created successfully..")
        return HttpResponseRedirect(request.path_info)
    return render(request,'Accounts/register.html')


def activate_mail(request, email_token):
    try:
        user = Profile.objects.get(email_token = email_token)
        user.is_email_verified = True
        user.save()
        return redirect('/')
    except Exception as e:
        return HttpResponse("not verified")
    

def add_to_cart(request, uid):
    product = Product.objects.get(uid = uid)
    user = request.user
    cart, _ = Cart.objects.get_or_create(user = user, is_paid = False)
    cart_item = CartItems.objects.create(cart = cart, product=product)
    cart_item.save()

    # print(CartItems.objects.all().count())

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
      

def get_cards(request):
    cart_obj = None
    try:
        cart_obj =  Cart.objects.get(is_paid=False , user = request.user)
    except Exception as e:
        print(e)
    if request.method=='POST':
        coupon = request.POST.get("coupon")
        coupon_obj = Coupon.objects.filter(coupon_code__icontains = coupon)
        if not coupon_obj.exists():
            messages.warning(request, "Invalid coupon")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if cart_obj.coupon:
            messages.warning(request, "Coupon already applied")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        if cart_obj.get_cart_total() < coupon_obj[0].minimum_price:
            messages.warning(request, f'Amount should be greater than{coupon_obj[0].minimum_price}')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        if coupon_obj[0].is_expired:
            messages.warning(request, "This coupon has been expired")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        cart_obj.coupon = coupon_obj[0]
        cart_obj.save()
        messages.success(request, "Coupon applied")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    if cart_obj and cart_obj.get_cart_total() * 100 > 0:
        client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID, settings.RAZOR_PAY_KEY_SECRET))
        payment = client.order.create({'amount': cart_obj.get_cart_total() * 100, 'currency': 'INR', 'payment_capture':1})
        cart_obj.razor_pay_order_id = payment['id']
        cart_obj.save()
    else:
        payment = None

    context = {'cart': cart_obj ,'payment': payment}
    return render(request, 'Accounts/carts.html', context)



def remove_cart(request, cart_item_id):
    try:
        cart_item = CartItems.objects.get(uid = cart_item_id)
        cart_item.delete()
    except Exception as e:
        print(e)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def remove_coupon(request, uid):
    cart = Cart.objects.get(uid = uid) 
    cart.coupon = None
    cart.save()
    messages.success(request, "Coupon Removed")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def success(request):
    order_id = request.GET.get('razorpay_order_id')
    cart_obj = Cart.objects.get(razor_pay_order_id = order_id)
    cart_obj.is_paid = True
    cart_obj.save()
    return HttpResponse("Payment Success")