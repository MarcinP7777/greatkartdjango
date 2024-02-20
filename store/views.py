from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from carts.models import CartItem
from carts.views import _cart_id
from .models import Product
from category.models import Category
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.db.models import Q



import sys
print(sys.path)
# Create your views here.
def store(request, category_slug=None):
       print("Requested category_slug:", category_slug)
       categories = None
       products = None
       if category_slug != None:
              categories = get_object_or_404(Category, slug=category_slug)
              products = Product.objects.filter(category=categories, is_available= True).order_by('id')
              paginator = Paginator(products, 2)
              page = request.GET.get('page')
              paged_products = paginator.get_page(page)
              products_count = products.count()
       else:
          products = Product.objects.filter(is_available=True)
          paginator = Paginator(products, 2)
          page = request.GET.get('page')
          paged_products = paginator.get_page(page)
          products_count = products.count()
            

       # products = Product.objects.all().filter(is_available=True)
       # product_count = products.count()

       context = {

         'products': paged_products,
         'product_count': products_count
                  }

       
       return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
      try:
            single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
            in_cart = CartItem.objects.filter(cart__cart_id =_cart_id(request), product=single_product).exists()
            # return HttpResponse(in_cart)
            # exit()
      except Exception as e:
            raise e
      
      context = {
            'single_product': single_product,
            'in_cart'       : in_cart,
      }
      return render(request, 'store/product_detail.html', context)

# To jest dobrze: 
# def search(request):
#     query = request.GET.get('keyword', '')
#     if query:
#         # Użyj 'product_name' zamiast 'name' do filtrowania produktów
#         products = Product.objects.filter(product_name__icontains=query)
#         context = {'products': products}
#     else:
#         context = {'message': 'No keywords entered.'}

#     return render(request, 'store/store.html', context)

# I to jest dobrze: http://
def search(request):
      if 'keyword' in request.GET:
            keyword = request.GET.get('keyword')
            if keyword:
                  products = Product.objects.order_by('created_date').filter(Q(description__icontains=keyword) |  Q(product_name__icontains=keyword))
                  products_count = products.count()
                  context = {'products': products, 'product_count': products_count}   
            else:
                  context = {'message': 'No keywords entered.'}                  

      return render(request, 'store/store.html', context)
