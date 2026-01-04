from django.contrib import admin
from .models import Category,Product

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active')
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ('name',)
    list_filter = ('is_active',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_available')
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ('name',)
    list_filter = ('is_available', 'category')
