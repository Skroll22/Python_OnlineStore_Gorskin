from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .models import Product, Cart, CartItem, Order

def product_list(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'store/product_list.html', {'products': products})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'store/product_detail.html', {'product': product})

def home_page(request):
    return render(request, 'store/home.html')


@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(customer=request.user)
    return render(request, 'store/cart.html', {'cart': cart})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(customer=request.user)
    cart.add_product(product)
    return redirect('cart')


@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__customer=request.user)
    cart_item.delete()
    return redirect('cart')


@login_required
def checkout_view(request):
    cart = get_object_or_404(Cart, customer=request.user)

    if request.method == 'POST':
        order = Order.objects.create(
            customer=request.user,
            shipping_address=request.POST.get('address'),
            total_amount=cart.total_price
        )
        order.create_order_from_cart(cart)
        return redirect('order_confirmation', order_id=order.id)

    return render(request, 'store/checkout.html', {'cart': cart})


@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, 'store/order_confirmation.html', {'order': order})


from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


@login_required
def my_account(request):
    user = request.user
    orders = Order.objects.filter(customer=user).order_by('-order_date')

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()

        password_form = PasswordChangeForm(user, request.POST)
        if 'old_password' in request.POST and password_form.is_valid():
            password_form.save()
            update_session_auth_hash(request, password_form.user)

    password_form = PasswordChangeForm(user)

    return render(request, 'store/my_account.html', {
        'user': user,
        'orders': orders,
        'password_form': password_form
    })

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, 'store/order_detail.html', {'order': order})
