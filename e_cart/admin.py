from django.contrib import admin
from .models import Category, Product, Order, OrderItem, Wallet, WalletTransaction


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
# OrderItem Inline (inside Order)
# -------------------------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ("product", "quantity", "price")
    readonly_fields = ("price",)

    def save_model(self, request, obj, form, change):
        obj.price = obj.product.price
        obj.save()


# OrderItem Admin (Optional standalone view)
# -------------------------
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price")
    search_fields = ("product__name", "order__user__username")


actions = ["mark_shipped", "mark_delivered"]


def mark_shipped(self, request, queryset):
    queryset.update(status="SHIPPED")


mark_shipped.short_description = "Mark selected orders as SHIPPED"


def mark_delivered(self, request, queryset):
    queryset.update(status="DELIVERED")


mark_delivered.short_description = "Mark selected orders as DELIVERED"


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance", "updated_at")
    search_fields = ("user__username",)


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ("wallet", "amount", "transaction_type", "source", "created_at")
    list_filter = ("transaction_type", "source", "created_at")
    search_fields = ("wallet__user__username",)
