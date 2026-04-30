from django.contrib import admin
from .models import Product, ProductCategory, Sale, SaleItem

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'min_stock', 'category')
    search_fields = ('name', 'barcode')
    list_filter = ('category',)

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'total', 'date')
    list_filter = ('date',)
    inlines = [SaleItemInline]
