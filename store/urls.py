from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'store'

urlpatterns = [
    # Auth
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),

    # POS
    path('',                          views.pos_view,          name='pos'),
    path('save-cart/',                views.save_cart,         name='save_cart'),
    path('checkout/',                 views.checkout_view,     name='checkout'),
    path('process-payment/',          views.process_payment,   name='process_payment'),
    path('receipt/<str:receipt_no>/', views.receipt_view,      name='receipt'),

    # Customer
    path('customer/search/',          views.customer_search,   name='customer_search'),
    path('customer/register/',        views.customer_register, name='customer_register'),

     # Reports
    path('reports/',                  views.reports_view,      name='reports'),
    path('reports/daily/',            views.daily_report,      name='daily_report'),
    path('reports/orders/',           views.order_history,     name='order_history'),
    path('reports/customers/',        views.customer_list,     name='customer_list'),
]