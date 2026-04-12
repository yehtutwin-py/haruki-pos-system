from django.db import models
from django.utils import timezone
import uuid

# Create your models here.
# Category model to organize products
class Category(models.Model):
    name = models.CharField(max_length=100)
    name_ja = models.CharField(max_length=100, blank=True, verbose_name="名前 （日本語）")
    order = models.PositiveIntegerField(default=0, help_text="Display order on cashier screen")

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']
        
    def __str__(self):
        return f"{self.name} / {self.name_ja}"
    
# Product model to represent items for sale
class Product(models.Model):
    TAX_CHOICES = [
        ('standard', 'Standard (10%)'),
        ('reduced', 'Reduced (8%)'),
        ('exempt', 'Exempt (0%)'),
    ]
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    name = models.CharField(max_length=200)
    name_ja = models.CharField(max_length=200, blank=True, verbose_name="名前 （日本語）")
    price = models.PositiveIntegerField(help_text="Price in yen (tax-inclusive)")
    tax_type = models.CharField(max_length=20, choices=TAX_CHOICES, default='standard')
    barcode = models.CharField(max_length=100, blank=True, null=True, unique=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['category', 'name']
        
    def __str__(self):
        return self.name
    
    def get_tax_rate(self):
        rates = {
            'standard': 0.10,
            'reduced': 0.08,
            'exempt': 0.00
        }
        return rates[self.tax_type]
    
    def get_tax_amount(self):
        rate = self.get_tax_rate()
        return round(self.price - (self.price / (1 + rate)))
    
    def get_price_before_tax(self):
        return self.price - self.get_tax_amount()
    
# Customer model to store customer information
class Customer(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    points = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        
    def __str__(self):
        return self.name
    
# Order model to represent a transaction
class Order(models.Model):
    PAYMENT_CHOICES = [
        ('cash', 'Cash / 現金'),
        ('card', 'Card / カード'),
        ('ic', 'IC Card / ICカード'),
        ('qr', 'QR Code / QRコード'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]
    
    receipt_number = models.CharField(max_length=20, unique=True, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    cashier = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash')
    subtotal = models.PositiveIntegerField(default=0)
    tax_total = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)
    cash_tendered = models.PositiveIntegerField(default=0)
    change_given = models.PositiveIntegerField(default=0)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-created_at']
        
    def save(self, *args, **kwargs):
        if not self.receipt_number:
            # Generate receipt number in format: HRK-YYYYMMDD-XXXX
            today = timezone.now().strftime('%Y%m%d')
            last = Order.objects.filter(receipt_number__contains=today).count()
            self.receipt_number = f"HRK-{today}-{str(last + 1).zfill(4)}"
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.receipt_number
    
    def calculate_totals(self):
        # Calculate subtotal, tax_total, and total based on order items
        items = self.items.all()
        self.subtotal = sum(i.get_subtotal_before_tax() for i in items)
        self.tax_total = sum(i.get_tax_total() for i in items)
        self.total = self.subtotal + self.tax_total
        self.save()
        
# OrderItem model to represent individual items in an order
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=200)      # snapshot at time of sale
    product_name_ja = models.CharField(max_length=200, blank=True)
    unit_price = models.PositiveIntegerField()            # snapshot at time of sale
    tax_type = models.CharField(max_length=20, default='standard')
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        verbose_name = "Order Item"

    def save(self, *args, **kwargs):
        if not self.product_name:
            self.product_name = self.product.name
            self.product_name_ja = self.product.name_ja
            self.unit_price = self.product.price
            self.tax_type = self.product.tax_type
        super().save(*args, **kwargs)
        
    def get_tax_rate(self):
        rates = {
            'standard': 0.10,
            'reduced': 0.08,
            'exempt': 0.00
        }
        return rates[self.tax_type]
    
    def get_line_total(self):
        return self.unit_price * self.quantity
    
    def get_tax_total(self):
        rate = self.get_tax_rate()
        return round(self.get_line_total() - (self.get_line_total() / (1 + rate)))
    
    def get_subtotal_before_tax(self):
        return self.get_line_total() - self.get_tax_total()
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
    
    