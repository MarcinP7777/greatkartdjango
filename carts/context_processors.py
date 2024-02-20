'''
Plik context_processors.py w Django zawiera funkcje, które są używane do dodawania zmiennych do kontekstu wszystkich 
szablonów bez konieczności jawnego przekazywania tych zmiennych do każdego wywołania funkcji 
renderującej szablon. Kontekst procesora, który definiujesz, można potem używać w dowolnym szablonie w Twojej aplikacji Django. 
Poniżej znajduje się dokładny komentarz i opis znaczenia funkcji counter w twoim pliku context_processors.py.

'''


# Import funkcji pomocniczej _cart_id z widoków koszyka oraz modeli Cart i CartItem.
from carts.views import _cart_id
from .models import Cart, CartItem

# Definicja funkcji counter, która przyjmuje request jako argument.
# Ta funkcja służy do liczenia liczby przedmiotów w koszyku użytkownika.
def counter(request):
    # Inicjalizacja zmiennej cart_count wartością 0. Zmienna ta będzie przechowywać liczbę przedmiotów w koszyku.
    cart_count = 0

    # Sprawdzenie, czy ścieżka żądania zawiera 'admin', co sugeruje, że żądanie pochodzi z panelu administracyjnego.
    # W takim przypadku funkcja zwraca pusty słownik, ponieważ nie chcemy wykonywać logiki liczenia dla panelu administracyjnego.
    if 'admin' in request.path:
        return {}
    
    else:
        # Blok try-except służący do obsługi sytuacji, gdy koszyk nie istnieje lub występuje inny błąd.
        try: 
            # Pobranie koszyka dla bieżącego użytkownika na podstawie ID sesji (cart_id), które jest generowane przez funkcję _cart_id.
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            # Pobranie wszystkich przedmiotów w koszyku, korzystając z pierwszego znalezionego koszyka.
            cart_items = CartItem.objects.all().filter(cart=cart[:1])
            
            # Pętla przez wszystkie przedmioty w koszyku, aby zsumować ich ilości.
            for cart_item in cart_items:
                cart_count += cart_item.Quantity

        # Obsługa wyjątku, gdy obiekt Cart nie istnieje. W takim przypadku liczba przedmiotów w koszyku pozostaje równa 0.
        except Cart.DoesNotExist:
            cart_count = 0
    
    # Zwrócenie słownika z kluczem 'cart_count' i wartością będącą liczbą przedmiotów w koszyku.
    # Ten słownik będzie dostępny we wszystkich szablonach, umożliwiając wyświetlenie liczby przedmiotów w koszyku.
    return dict(cart_count=cart_count)





# po wykonaniu tego pliku idziemy do settings.py:

# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         # 'DIRS': ['templates'],
#         'DIRS': [os.path.join(BASE_DIR, 'templates')],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#                 'category.context_processors.menu_links',
#                 'carts.context_processors.counter',  i dołączamy tę linijkę!!!!
#             ],
#         },
#     },
# ]