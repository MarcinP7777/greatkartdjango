from django.shortcuts import get_object_or_404, render, redirect
from carts.models import Cart, CartItem  # Importowanie modeli koszyka i elementu koszyka
from store.models import Product, Variation  # Importowanie modelu produktu
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

# Funkcja pomocnicza do generowania lub pobierania identyfikatora koszyka
def _cart_id(request):
    cart = request.session.session_key  # Pobranie klucza sesji jako identyfikatora koszyka
    if not cart:
        cart = request.session.create()  # Jeśli sesja nie ma klucza, utwórz nową sesję
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)  # Pobranie produktu na podstawie ID
    
    cart, _ = Cart.objects.get_or_create(cart_id=_cart_id(request))
    
    # Spróbuj znaleźć istniejący CartItem z danym produktem, jeśli nie istnieje, utwórz nowy
    cart_item, created = CartItem.objects.get_or_create(product=product, cart=cart, defaults={'Quantity': 1})
    
    if not created:
        # Jeżeli produkt już istnieje w koszyku, zwiększ jego ilość
        cart_item.Quantity += 1
        cart_item.save()
    
    return redirect('cart')  # Przekieruj użytkownika do strony koszyka


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)  # Pobranie produktu na podstawie ID
    product_variation = []

    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST.get(key)
            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)
            except Variation.DoesNotExist:
                pass

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist: # type: ignore
        cart = Cart.objects.create(cart_id=_cart_id(request))
    
    cart.save()

    is_cart_item_exists =  CartItem.objects.filter(product = product, cart = cart).exists()

    if is_cart_item_exists:
        cart_item = CartItem.objects.filter(product=product, cart=cart)
        # existing variations
        # current variations 
        # item_id -> from database
        ex_var_list = []
        id = []
        for item in cart_item:
            existing_variation = item.variations.all()
            ex_var_list.append(list(existing_variation))
            id.append(item.id)

        if product_variation in ex_var_list:
            index = ex_var_list.index(product_variation)
            item_id = id[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.Quantity +=1
            item.save()
        
        else:
          item = CartItem.objects.create(product=product, Quantity=1, cart=cart)  
          if len(product_variation) > 0:
            item.variations.clear()
            item.variations.add(*product_variation)
          item.save()
    
    else:
        cart_item = CartItem.objects.create(
            product = product,
            Quantity =1,
            cart = cart,
        )
        if len(product_variation) >0:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variation)
        cart_item.save()

    return redirect('cart')


# def add_cart(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     cart, _ = Cart.objects.get_or_create(cart_id=_cart_id(request))

#     product_variation = []
#     if request.method == 'POST':
#         for key, value in request.POST.items():
#             if key != 'csrfmiddlewaretoken' and value:
#                 try:
#                     variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
#                     product_variation.append(variation)
#                 except Variation.DoesNotExist:
#                     continue

#     cart_item_qs = CartItem.objects.filter(product=product, cart=cart)
#     cart_item = None
#     for item in cart_item_qs:
#         existing_variations = set(item.variations.all())
#         if existing_variations == set(product_variation):
#             cart_item = item
#             break

#     if cart_item:
#         cart_item.Quantity += 1
#         cart_item.save()
#     else:
#         cart_item = CartItem.objects.create(product=product, Quantity=1, cart=cart)
#         if product_variation:
#             cart_item.variations.set(product_variation)

#     return redirect('cart')


def remove_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id= _cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
      cart_item = CartItem.objects.get(product = product, cart = cart, id=cart_item_id)
      if cart_item.Quantity > 1:
        cart_item.Quantity -= 1
        cart_item.save()
      else: 
        cart_item.delete()
    except:
        pass
    return redirect('cart')



# def remove_single_cart_item(request, product_id, cart_item_id):
#     cart = Cart.objects.get(cart_id=_cart_id(request))
#     product = get_object_or_404(Product, id=product_id)
#     cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
#     cart_item.delete()
#     return redirect('cart')

def remove_single_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__cart_id=_cart_id(request))
    cart_item.delete()
    return redirect('cart')

def remove_all_cart_items(request):
    cart_id = _cart_id(request)
    cart = Cart.objects.get(cart_id=cart_id)
    cart_items = CartItem.objects.filter(cart=cart)
    cart_items.delete()
    return redirect('cart')



# Widok wyświetlający koszyk
def cart(request, total=0, Quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.Quantity)
            Quantity += cart_item.Quantity
        
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    context = {'total': total, 
               'quantity': Quantity,
               'cart_items': cart_items,
               'tax': tax,
               'grand_total': grand_total,}
    return render(request, 'store/cart.html', context)  # Renderowanie strony koszyka z szablonu
