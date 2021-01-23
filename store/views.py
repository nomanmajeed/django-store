from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from .models import *
import json
import datetime
from .utils import cookieCart, cartData, guestOrder
import stripe

stripe.api_key = "sk_test_rmWA5f4bTEsGnxrOresgQHVp"

# Create your views here.


def store(request):

    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    print("User: ", request.user)
    context = {'products': products, 'cartItems': cartItems, 'user': request.user}
    return render(request, 'store/store.html', context)


def cart(request):

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print(productId)
    print(action)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(
        order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)
    # this is returned as response to fetch api as JS promise


def processOrder(request):
    
    if request.method == 'POST':
        print("Payment data: ", request.POST)

        transaction_id = datetime.datetime.now().timestamp()

        # loading the data sent from checkout.html using fetch POST method
        data = request.POST

        if request.user.is_authenticated:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(
                customer=customer, complete=False)

        else:
            customer, order = guestOrder(request, data)

        order.transaction_id = transaction_id

        if order.get_cart_total > 0:
            order.complete = True
        order.save()
        if order.shipping == True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=request.POST.get('address'),
                city=request.POST.get('city'),
                state=request.POST.get('state'),
                zipcode=request.POST.get('zipcode'),
            )

        customer = stripe.Customer.create(
            email = request.POST.get('email'),
            name = request.POST.get('name'),
            source = request.POST.get('stripeToken')
        )

        print("Amount type: ", type(order.get_cart_total))
        charge = stripe.Charge.create(
            customer=customer,
            amount=int(order.get_cart_total) * 100,
            currency='usd',
        )

        messages.success(request, f"Transaction of Successful. You did shopping of ${order.get_cart_total}")

        response = redirect("store")

        response.set_cookie('cart', {}, max_age=None)

        return response

        # return JsonResponse("Payment completed!....", safe=False)

def processPayment(request):

    if request.method == 'POST':
        print("Payment data: ", request.POST)
        print("name: ", request.POST.get('name'))

    return HttpResponse("making payment")