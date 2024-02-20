from . import views
from django.urls import path


urlpatterns = [
    path('', views.cart, name='cart'),
    path('add_cart/<int:product_id>', views.add_cart, name='add_cart'),
    path('remove_cart/<int:product_id>/<int:cart_item_id>/', views.remove_cart, name='remove_cart'),
    # Usunięto zakomentowaną linię dla remove_cart_item, zakładam, że nie jest używana
    path('remove_single_cart_item/<int:cart_item_id>/', views.remove_single_cart_item, name='remove_single_cart_item'),
    path('remove_all_cart_items/', views.remove_all_cart_items, name='remove_all_cart_items'),

]