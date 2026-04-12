from urllib import request

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
import json
from .models import Product, Category, Order, OrderItem, Customer
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncDate, TruncMonth
from datetime import date, timedelta

# Create your views here.
# Login view
def login_view(request):
    if request.user.is_authenticated:
        return redirect('store:pos')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('store:pos')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'store/login.html')

# Logout view
def logout_view(request):
    # Clear any pending messages so they do not appear on the login page after logout
    list(messages.get_messages(request))
    logout(request)
    return redirect('store:login')

# POS view
@login_required(login_url='store:login')
def pos_view(request):
    categories = Category.objects.all().order_by('name')
    products = Product.objects.filter(is_active=True).select_related('category')
    return render(request, 'store/pos.html', {
        'categories': categories,
        'products': products,
    })
    
# Checkout view
@login_required(login_url='store:login')
def checkout_view(request):
    cart_data = request.session.get('haruki_cart', {})
    if not cart_data:
        return redirect('store:pos')
    items = []
    subtotal = 0
    tax_total = 0
    
    for product_id, item in cart_data.items():
        product = get_object_or_404(Product, id=product_id)
        qty = item['qty']
        line_total = product.price * qty
        tax = round(line_total - (line_total / (1 + product.get_tax_rate())))
        sub = line_total - tax
        
        subtotal += sub
        tax_total += tax
        items.append({
            'product': product,
            'qty': qty,
            'line_total': line_total,
            'tax': tax,
        })
    
    total = subtotal + tax_total
    
    return render(request, 'store/checkout.html', {
        'items': items,
        'subtotal': int(subtotal),
        'tax_total': int(tax_total),
        'total': str(int(total)),
    })
    
# Process payment view
@login_required(login_url='store:login')
@require_POST
def process_payment(request):
    cart_data      = request.session.get('haruki_cart', {})
    payment_method = request.POST.get('payment_method', 'cash')
    cash_tendered  = int(request.POST.get('cash_tendered', 0) or 0)
    customer_id    = request.session.get('haruki_customer_id')

    if not cart_data:
        return redirect('store:pos')

    # Get customer if attached
    customer = None
    if customer_id:
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            pass

    # Create order
    order = Order.objects.create(
        cashier=request.user,
        customer=customer,
        payment_method=payment_method,
        status='paid',
        paid_at=timezone.now(),
    )

    subtotal  = 0
    tax_total = 0

    # Create order items
    for product_id, item in cart_data.items():
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue

        qty        = item['qty']
        line_total = product.price * qty
        tax        = round(line_total - (line_total / (1 + product.get_tax_rate())))
        sub        = line_total - tax

        subtotal  += sub
        tax_total += tax

        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            product_name_ja=product.name_ja,
            unit_price=product.price,
            tax_type=product.tax_type,
            quantity=qty,
        )

        # Reduce stock
        product.stock = max(0, product.stock - qty)
        product.save()

    # Save totals
    order.subtotal      = subtotal
    order.tax_total     = tax_total
    order.total         = subtotal + tax_total
    order.cash_tendered = cash_tendered
    order.change_given  = max(0, cash_tendered - order.total)
    order.save()

    # Award points — ¥100 = 1 point
    points_earned = 0
    if customer:
        points_earned        = order.total // 100
        customer.points     += points_earned
        customer.save()

    # Clear session
    request.session['haruki_cart']        = {}
    request.session['haruki_customer_id'] = None
    request.session.modified              = True

    return redirect('store:receipt', receipt_no=order.receipt_number)

# Receipt view
@login_required(login_url='store:login')
def receipt_view(request, receipt_no):
    order         = get_object_or_404(Order, receipt_number=receipt_no)
    items         = order.items.all()
    points_earned = order.total // 100
    return render(request, 'store/receipt.html', {
        'order':         order,
        'items':         items,
        'points_earned': points_earned,
    })
    
# Save cart view (for AJAX)
@login_required(login_url='store:login')
@require_POST
def save_cart(request):
    try:
        data = json.loads(request.body)
        cart = data.get('cart', {})
        request.session['haruki_cart'] = cart
        request.session.modified = True
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
# Customer search view (for AJAX)
@login_required(login_url='store:login')
def customer_search(request):
    phone  = request.GET.get('phone', '').strip()
    result = None
    error  = None

    if phone:
        try:
            result = Customer.objects.get(phone=phone)
            # Store found customer in session
            request.session['haruki_customer_id'] = result.id
            request.session.modified = True
        except Customer.DoesNotExist:
            error = f'No member found with phone number {phone}'

    return JsonResponse({
        'found':    result is not None,
        'error':    error,
        'customer': {
            'id':     result.id,
            'name':   result.name,
            'phone':  result.phone,
            'points': result.points,
        } if result else None,
    })

# Customer register view (for AJAX)
@login_required(login_url='store:login')
@require_POST
def customer_register(request):
    try:
        data  = json.loads(request.body)
        name  = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        email = data.get('email', '').strip()

        if not name:
            return JsonResponse({'success': False, 'error': 'Name is required.'})
        if not phone:
            return JsonResponse({'success': False, 'error': 'Phone number is required.'})
        if Customer.objects.filter(phone=phone).exists():
            return JsonResponse({'success': False, 'error': 'Phone number already registered.'})

        customer = Customer.objects.create(
            name=name, phone=phone, email=email, points=0
        )
        request.session['haruki_customer_id'] = customer.id
        request.session.modified = True

        return JsonResponse({
            'success':  True,
            'customer': {
                'id':     customer.id,
                'name':   customer.name,
                'phone':  customer.phone,
                'points': customer.points,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
# Reports view

@login_required(login_url='store:login')
def reports_view(request):
    today      = date.today()
    this_month = today.replace(day=1)

    # Today's stats
    today_orders = Order.objects.filter(status='paid', paid_at__date=today)
    today_sales  = today_orders.aggregate(
        total=Sum('total'), count=Count('id')
    )

    today_total = today_sales['total'] or 0
    today_count = today_sales['count'] or 0
    today_avg   = today_total // today_count if today_count > 0 else 0

    # This month stats
    month_orders = Order.objects.filter(
        status='paid',
        paid_at__date__gte=this_month
    )
    month_sales  = month_orders.aggregate(
        total=Sum('total'), count=Count('id')
    )

    # Last 7 days chart data
    last_7 = []
    for i in range(6, -1, -1):
        day     = today - timedelta(days=i)
        day_total = Order.objects.filter(
            status='paid', paid_at__date=day
        ).aggregate(total=Sum('total'))['total'] or 0
        last_7.append({
            'date':  day.strftime('%a'),
            'total': day_total,
        })

    # Top 5 products this month
    top_products = OrderItem.objects.filter(
        order__status='paid',
        order__paid_at__date__gte=this_month
    ).values(
        'product_name'
    ).annotate(
        qty=Sum('quantity'),
        revenue=Sum('unit_price')
    ).order_by('-qty')[:5]

    # Recent orders
    recent_orders = Order.objects.filter(
        status='paid'
    ).select_related('cashier', 'customer').order_by('-paid_at')[:10]

    return render(request, 'store/reports.html', {
        'today':         today,
        'today_total':   today_total,
        'today_count':   today_count,
        'today_avg':     today_avg,
        'month_total':   month_sales['total'] or 0,
        'month_count':   month_sales['count'] or 0,
        'last_7':        last_7,
        'top_products':  top_products,
        'recent_orders': recent_orders,
    })

# Daily report view with date filter

@login_required(login_url='store:login')
def daily_report(request):
    report_date = request.GET.get('date', str(date.today()))
    try:
        report_date = date.fromisoformat(report_date)
    except ValueError:
        report_date = date.today()

    orders = Order.objects.filter(
        status='paid',
        paid_at__date=report_date
    ).select_related('cashier', 'customer').order_by('paid_at')

    totals = orders.aggregate(
        total=Sum('total'),
        subtotal=Sum('subtotal'),
        tax=Sum('tax_total'),
        count=Count('id'),
    )

    # Payment method breakdown
    payment_breakdown = orders.values('payment_method').annotate(
        count=Count('id'),
        total=Sum('total'),
    ).order_by('-total')

    # Items sold today
    items_sold = OrderItem.objects.filter(
        order__status='paid',
        order__paid_at__date=report_date,
    ).values('product_name', 'product_name_ja').annotate(
        qty=Sum('quantity'),
        total=Sum('unit_price'),
    ).order_by('-qty')

    return render(request, 'store/daily_report.html', {
        'report_date':       report_date,
        'orders':            orders,
        'totals':            totals,
        'payment_breakdown': payment_breakdown,
        'items_sold':        items_sold,
    })


# Order history view with date filtering

@login_required(login_url='store:login')
def order_history(request):
    orders = Order.objects.select_related(
        'cashier', 'customer'
    ).order_by('-created_at')

    # Filter by date
    date_from = request.GET.get('from')
    date_to   = request.GET.get('to')
    status    = request.GET.get('status', '')

    if date_from:
        orders = orders.filter(paid_at__date__gte=date_from)
    if date_to:
        orders = orders.filter(paid_at__date__lte=date_to)
    if status:
        orders = orders.filter(status=status)

    return render(request, 'store/order_history.html', {
        'orders':    orders[:100],
        'date_from': date_from or '',
        'date_to':   date_to or '',
        'status':    status,
    })

# Customer list view with search and points display
@login_required(login_url='store:login')
def customer_list(request):
    customers = Customer.objects.annotate(
        order_count=Count('order'),
        total_spent=Sum('order__total'),
    ).order_by('-points')

    search = request.GET.get('search', '')
    if search:
        customers = customers.filter(
            name__icontains=search
        ) | customers.filter(
            phone__icontains=search
        )

    return render(request, 'store/customer_list.html', {
        'customers': customers,
        'search':    search,
    })
    
# Error handlers
def error_404(request, exception):
    return render(request, 'store/404.html', status=404)

def error_500(request):
    return render(request, 'store/500.html', status=500)