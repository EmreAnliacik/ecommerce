from django.http import JsonResponse
import json
import datetime
from .models import *
from .utils import cookieCart, cartData, guestOrder
import random
from django.contrib.auth import authenticate, login, logout
from .forms import UserSignupForm
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import UserLoginForm
from .models import Customer  # Customer modelini ekleyin


# Create your views here.

def store(request):
    if request.user.is_authenticated:
        # Kullanıcıya bağlı Customer nesnesini al veya oluştur
        customer, created = Customer.objects.get_or_create(user=request.user)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']

    products = Product.objects.all()
    context = {"products": products, "cartItems": cartItems}
    return render(request, "store/store.html", context)


def cart(request):
    if request.user.is_authenticated:
        # Kullanıcıya bağlı Customer nesnesini al veya oluştur
        customer, created = Customer.objects.get_or_create(user=request.user)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    if request.user.is_authenticated:
        # Kullanıcıya bağlı Customer nesnesini al veya oluştur
        customer, created = Customer.objects.get_or_create(user=request.user)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, "store/checkout.html", context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True

    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            adress=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment complete!', safe=False)


# Kelime listesi
WORDS = ["python", "django", "development", "programming", "project", "template", "variable"]


def word_guess_game(request):
    # Oturum başına oyun durumunu takip edin
    if 'word' not in request.session:
        request.session['word'] = random.choice(WORDS)  # Rastgele bir kelime seç
        request.session['attempts'] = 0  # Tahmin sayısı
        request.session['correct_guesses'] = ['_'] * len(request.session['word'])  # Doğru tahmin edilen harfler

    word = request.session['word']
    correct_guesses = request.session['correct_guesses']
    attempts = request.session['attempts']
    message = None

    if request.method == 'POST':
        guess = request.POST.get('guess', '').lower()  # Oyuncunun tahmini

        if guess in word:
            for idx, letter in enumerate(word):
                if letter == guess:
                    correct_guesses[idx] = guess  # Doğru harfi yerleştir
            message = f"'{guess}' harfi doğru!"
        else:
            attempts += 1
            message = f"'{guess}' harfi yanlış!"

        request.session['correct_guesses'] = correct_guesses
        request.session['attempts'] = attempts

        # Oyunun bitip bitmediğini kontrol et
        if '_' not in correct_guesses:
            message = f"Tebrikler! Kelimeyi doğru tahmin ettiniz: {word}"
            del request.session['word']  # Oyunu sıfırla
        elif attempts >= 6:
            message = f"Maalesef, tüm haklarınızı kullandınız. Kelime: {word}"
            del request.session['word']  # Oyunu sıfırla

    return render(request, 'word_guess_game.html', {
        'correct_guesses': correct_guesses,
        'attempts': attempts,
        'message': message
    })


def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email_or_username = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Kullanıcı adı veya e-posta üzerinden giriş yap
            user = authenticate(request, username=email_or_username, password=password) or \
                   authenticate(request, username=User.objects.filter(email=email_or_username).first(),
                                password=password)

            if user is not None:
                login(request, user)
                messages.success(request, 'You have successfully logged in!')
                return redirect('store')
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Please fill out the form correctly.')
    else:
        form = UserLoginForm()

    return render(request, 'store/login.html', {'form': form, 'tab': 'login'})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('store')


from django.utils.crypto import get_random_string  # Rastgele string oluşturmak için


def signup_view(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            # Kullanıcıyı oluştur ve kaydet
            user = form.save(commit=False)

            # Benzersiz bir username oluştur
            random_username = get_random_string(10)
            user.username = random_username
            user.save()

            # Kullanıcı için bir Customer nesnesi oluştur
            Customer.objects.create(user=user)

            messages.success(request, 'Signup successful! You can now log in.')
            return redirect('login')  # Giriş sayfasına yönlendir
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserSignupForm()

    return render(request, 'store/login.html', {'form': form, 'tab': 'signup'})
