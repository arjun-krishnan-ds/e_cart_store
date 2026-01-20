from django.contrib import admin
from .models import Category, Product, Order, OrderItem

# -------------------------
# Category Admin
# -------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)

# -------------------------
# Product Admin
# -------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "is_available")
    search_fields = ("name",)
    list_filter = ("is_available", "category")

# -------------------------
# OrderItem Inline
# -------------------------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ("product", "quantity", "price")  # editable

# -------------------------
# Order Admin
# -------------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_amount", "status", "created_at")
    list_filter = ("status", "created_at")
    readonly_fields = ("created_at",)
    inlines = [OrderItemInline]

    # Hide the products M2M field completely
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "products":
            kwargs["queryset"] = Product.objects.none()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

# -------------------------
# OrderItem Admin
# -------------------------
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price")
