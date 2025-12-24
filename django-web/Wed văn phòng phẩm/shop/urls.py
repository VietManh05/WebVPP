from django.urls import path
from . import views

urlpatterns = [
    # Home & Products
    path('', views.home, name='home'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    
    # Shopping Cart
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:product_id>/', views.update_cart, name='update_cart'),
    
    # Checkout
    path('checkout/', views.checkout, name='checkout'),
    path('checkout-success/', views.checkout_success, name='checkout_success'),
    
    # Authentication - Đăng nhập, Đăng ký, Đăng xuất
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # User Profile
    path('profile/', views.user_profile, name='user_profile'),
    path('order-history/', views.order_history, name='order_history'),
    
    # Warehouse Management - Quản lý kho hàng
    path('warehouses/', views.warehouse_list, name='warehouse_list'),
    path('warehouse/<int:warehouse_id>/', views.warehouse_detail, name='warehouse_detail'),
    path('product/<int:product_id>/availability/', views.product_warehouse_availability, name='product_availability'),
    path('stock-movements/', views.stock_movement_log, name='stock_movement_log'),
    path('warehouse-statistics/', views.warehouse_statistics, name='warehouse_statistics'),
]
