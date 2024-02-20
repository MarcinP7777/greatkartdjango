from django.db import models
from category.models import Category  # Import modelu kategorii, aby stworzyć relację.
from django.urls import reverse  # Import funkcji reverse do tworzenia URL-i.

# Model produktu reprezentuje produkt sprzedawany w sklepie.
class Product(models.Model):
    # Nazwa produktu, unikalna w obrębie bazy danych.
    product_name = models.CharField(max_length=250, unique=True)
    
    # Przyjazny URL (slug) produktu, także unikalny.
    slug = models.SlugField(max_length=250, unique=True)
    
    # Opis produktu, opcjonalne pole, może być puste.
    description = models.TextField(max_length=500, blank=True)
    
    # Cena produktu, z dokładnością do dwóch miejsc po przecinku.
    price = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Ścieżka do obrazu produktu, zapisywanego w folderze 'photos/products'.
    images = models.ImageField(upload_to='photos/products')
    
    # Dostępna ilość produktu na magazynie.
    stock = models.IntegerField()
    
    # Pole wskazujące, czy produkt jest dostępny.
    is_available = models.BooleanField(default=True)
    
    # Klucz obcy do modelu Category, określa kategorię produktu. Usunięcie kategorii 
    # spowoduje usunięcie wszystkich powiązanych produktów.
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    # Data utworzenia produktu, automatycznie dodawana przy tworzeniu obiektu.
    created_date = models.DateTimeField(auto_now_add=True)
    
    # Data ostatniej modyfikacji produktu, automatycznie dodawana przy tworzeniu.
    modified_date = models.DateTimeField(auto_now_add=True)

    # Metoda zwracająca pełny URL do strony szczegółów produktu. 
    # Używa 'product_detail' jako nazwę wzorca URL oraz slugi kategorii i produktu jako argumenty.
    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    # Reprezentacja tekstowa modelu, używana np. w panelu administracyjnym.
    def __str__(self):
        return self.product_name
    

class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)
    
    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)
# Wybory dla kategorii wariacji, np. kolor, rozmiar.
variation_category_choice = (
    ('color', 'color'),
    ('size', 'size'),
)

# Model Variation reprezentuje różne warianty produktu, np. kolor lub rozmiar.
class Variation(models.Model):
    # Klucz obcy do modelu Product, wskazuje, do którego produktu należy wariant.
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    # Kategoria wariacji (np. kolor, rozmiar), z predefiniowanymi wyborami.
    variation_category = models.CharField(max_length=100, choices=variation_category_choice)
    
    # Wartość wariacji, np. konkretny kolor lub rozmiar.
    variation_value = models.CharField(max_length=100)
    
    # Pole wskazujące, czy wariant jest aktywny (dostępny).
    is_active = models.BooleanField(default=True)
    
    # Data utworzenia wariantu, automatycznie ustawiana przy jego tworzeniu.
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    # Reprezentacja tekstowa modelu, zazwyczaj zwraca nazwę produktu.
    def __str__(self):
        return self.variation_value
