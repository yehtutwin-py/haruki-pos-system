from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum 
from .models import Category, Product, Customer, Order, OrderItem

# Register your models here.
# admin.site.register(Category)
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_ja', 'order', 'product_count']
    list_editable = ['order']
    search_fields = ['name', 'name_ja']
    
    def product_count(self, obj):
        return obj.products.filter(is_active=True).count()
    product_count.short_description = 'Active Products'

# admin.site.register(Product)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_ja', 'category', 'price_display', 'tax_type', 'stock_display', 'is_active']
    list_filter = ['category', 'tax_type', 'is_active']
    search_fields = ['name', 'name_ja', 'barcode']
    list_per_page = 20
    
    fieldsets = (
        ('Product Info', {
            'fields': ('category', ('name', 'name_ja'), 'image')
        }),
        ('Pricing', {
            'fields': (('price', 'tax_type'),)
        }),
        ('Inventory', {
            'fields': ('stock', 'barcode', 'is_active')
        }),
    )
    
    def price_display(self, obj):
        formatted_price = format(obj.price, ',')
        return format_html('¥{}', formatted_price)
    price_display.short_description = 'Price'

    def stock_display(self, obj):
        color = 'green' if obj.stock > 10 else 'orange' if obj.stock > 0 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: 500;">{}</span>',
            color, obj.stock
        )
    stock_display.short_description = 'Stock'

# admin.site.register(Customer)
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'points', 'created_at']
    search_fields = ['name', 'phone', 'email']

# admin.site.register(OrderItem)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'product_name_ja',
                       'unit_price', 'tax_type', 'quantity', 'line_total']
    fields = ['product_name', 'product_name_ja',
              'unit_price', 'tax_type', 'quantity', 'line_total']
    can_delete = False

    def line_total(self, obj):
        formatted_total = format(obj.get_line_total(), ',')
        return format_html('¥{}', formatted_total)
    line_total.short_description = 'Total'
    
# admin.site.register(Order)
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'cashier', 'customer',
                    'status_badge', 'payment_method',
                    'total_display', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['receipt_number', 'customer__name']
    readonly_fields = ['receipt_number', 'subtotal', 'tax_total',
                       'total', 'created_at', 'paid_at']
    inlines = [OrderItemInline]
    line_per_page = 20
    fieldsets = (
        ('Order Info', {
            'fields': ('receipt_number', 'cashier', 'customer', 'status')
        }),
        ('Payment', {
            'fields': ('payment_method', 'cash_tendered', 'change_given')
        }),
        ('Totals', {
            'fields': ('subtotal', 'tax_total', 'total')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'paid_at')
        }),
    )

    def status_badge(self, obj):
        color_map = {
            'open': '#f39c12',
            'paid': '#27ae60',
            'refunded': '#8e44ad',
            'cancelled': '#e74c3c',
        }

        color = color_map.get(obj.status, '#888')
        return format_html(
            '<span style="background:{}; color:white; padding:2px 10px;'
            'border-radius:10px; font-size:11px; font-weight:500;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def total_display(self, obj):
        formatted_total = format(obj.total, ',')
        return format_html('¥{}', formatted_total)
    total_display.short_description = 'Total'

# ─── Admin Site Branding ─────────────────────────────────────────────────────
admin.site.site_header = 'HARUKI 春木'
admin.site.site_title = 'Haruki POS'
admin.site.index_title = 'Store Management'
