"""
View Django cho Cửa hàng Văn Phòng Phẩm
Xử lý: Sản phẩm, Giỏ hàng, Đơn hàng, Người dùng, Kho hàng, Quản lý tồn kho
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from decimal import Decimal

from .models import (
    Product, Category, Order, UserProfile,
    Warehouse, WarehouseStock, StockMovement
)
from .forms import RegisterForm, LoginForm, UserProfileForm


# ========== HELPER FUNCTIONS ==========

def get_cart_from_session(request):
    """Lấy giỏ hàng từ session và chuyển đổi key thành string"""
    cart = request.session.get('cart', {})
    return {str(k): v for k, v in cart.items()}


def save_cart_to_session(request, cart):
    """Lưu giỏ hàng vào session"""
    request.session['cart'] = cart
    request.session.modified = True


def calculate_cart_totals(cart):
    """
    Tính toán tổng giá và danh sách sản phẩm từ giỏ hàng.
    
    Trả về:
        tuple: (danh sách cart_items, Decimal tổng_giá)
    """
    cart_items = []
    total_price = Decimal('0')
    
    for product_id_str, quantity in cart.items():
        product = get_object_or_404(Product, id=int(product_id_str))
        subtotal = product.price * quantity
        
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })
        total_price += subtotal
    
    return cart_items, total_price


def clear_cart_session(request):
    """Xóa giỏ hàng trong session"""
    request.session['cart'] = {}
    request.session.modified = True


# ============================================================
# HOME & PRODUCT VIEWS
# ============================================================

def home(request):
    """Hiển thị danh sách sản phẩm với lọc theo danh mục"""
    categories = Category.objects.all()
    category_id = request.GET.get('category')
    
    # Lọc sản phẩm theo danh mục nếu được chỉ định
    if category_id:
        products = Product.objects.filter(category_id=category_id)
    else:
        products = Product.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
    }
    return render(request, 'home.html', context)


def product_detail(request, id):
    """Hiển thị chi tiết sản phẩm"""
    product = get_object_or_404(Product, id=id)
    return render(request, 'product_detail.html', {'product': product})


# ============================================================
# SHOPPING CART VIEWS
# ============================================================

def add_to_cart(request, product_id):
    """Thêm sản phẩm vào giỏ hàng"""
    cart = get_cart_from_session(request)
    product_id_str = str(product_id)
    
    # Tăng số lượng hoặc thêm mới
    cart[product_id_str] = cart.get(product_id_str, 0) + 1
    save_cart_to_session(request, cart)
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def remove_from_cart(request, product_id):
    """Xóa sản phẩm khỏi giỏ hàng"""
    cart = get_cart_from_session(request)
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        del cart[product_id_str]
        save_cart_to_session(request, cart)
    
    return redirect('cart')


def update_cart(request, product_id):
    """Cập nhật số lượng sản phẩm trong giỏ hàng"""
    if request.method != 'POST':
        return redirect('cart')
    
    quantity = int(request.POST.get('quantity', 1))
    cart = get_cart_from_session(request)
    product_id_str = str(product_id)
    
    if quantity > 0:
        cart[product_id_str] = quantity
    elif product_id_str in cart:
        del cart[product_id_str]
    
    save_cart_to_session(request, cart)
    return redirect('cart')


def cart_view(request):
    """Hiển thị trang giỏ hàng"""
    cart = get_cart_from_session(request)
    cart_items, total_price = calculate_cart_totals(cart)
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'cart_count': len(cart),
    }
    return render(request, 'cart.html', context)


# ============================================================
# CHECKOUT VIEWS
# ============================================================

def checkout(request):
    """Xử lý thanh toán từ giỏ hàng"""
    cart = get_cart_from_session(request)
    
    # Kiểm tra giỏ hàng không trống
    if not cart:
        messages.warning(request, 'Giỏ hàng của bạn trống!')
        return redirect('home')
    
    # Nếu POST: Tạo đơn hàng từ giỏ hàng
    if request.method == 'POST':
        return _create_order(request, cart)
    
    # Nếu GET: Hiển thị form thanh toán với giỏ hàng hiện tại
    cart_items, total_price = calculate_cart_totals(cart)
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'checkout.html', context)


def _create_order(request, cart):
    """
    Hàm trợ giúp: Tạo đơn hàng từ giỏ hàng.
    
    Tham số:
        request: Đối tượng request của Django
        cart: Dictionary giỏ hàng chứa ID sản phẩm và số lượng
    
    Trả về:
        redirect: Chuyển hướng đến trang xác nhận đơn hàng
    """
    # Lấy thông tin từ form POST
    customer_name = request.POST.get('name', '').strip()
    phone = request.POST.get('phone', '').strip()
    address = request.POST.get('address', '').strip()
    
    # Kiểm tra xác thực dữ liệu cơ bản
    if not all([customer_name, phone, address]):
        messages.error(request, 'Vui lòng điền đầy đủ thông tin!')
        return redirect('checkout')
    
    # Tính tổng tiền của đơn hàng
    _, total_price = calculate_cart_totals(cart)
    
    # Tạo bản ghi đơn hàng trong cơ sở dữ liệu
    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        customer_name=customer_name,
        phone=phone,
        address=address,
        total_price=total_price,
    )
    
    # Xóa giỏ hàng sau khi đặt hàng thành công
    clear_cart_session(request)
    messages.success(request, 'Đặt hàng thành công! Cảm ơn bạn!')
    
    return redirect('checkout_success')


def checkout_success(request):
    """Hiển thị trang xác nhận đặt hàng thành công"""
    return render(request, 'checkout_success.html')


# ============================================================
# VÍ DỤ AUTHENTICATE - Đăng nhập, Đăng ký, Đăng xuất người dùng
# ============================================================

def register(request):
    """Trang đăng ký tài khoản"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Tài khoản {user.username} được tạo thành công! Vui lòng đăng nhập.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RegisterForm()
    
    context = {
        'form': form,
        'page_title': 'Đăng Ký',
    }
    return render(request, 'auth/register.html', context)


def user_login(request):
    """Trang đăng nhập"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember = form.cleaned_data.get('remember')
            
            # Kiểm tra đăng nhập bằng username hoặc email
            user = None
            if '@' in username:
                # Tìm user bằng email và xác thực
                user_obj = User.objects.filter(email=username).first()
                if user_obj:
                    user = authenticate(request, username=user_obj.username, password=password)
            else:
                # Xác thực trực tiếp bằng username
                user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Thiết lập session timeout nếu người dùng không chọn "Nhớ mật khẩu"
                if not remember:
                    request.session.set_expiry(0)
                
                messages.success(request, f'Chào mừng quay lại, {user.username}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Tên đăng nhập hoặc mật khẩu không chính xác!')
    else:
        form = LoginForm()
    
    context = {
        'form': form,
        'page_title': 'Đăng Nhập',
    }
    return render(request, 'auth/login.html', context)


def user_logout(request):
    """Đăng xuất"""
    logout(request)
    messages.success(request, 'Bạn đã đăng xuất thành công!')
    return redirect('home')


@login_required(login_url='login')
def user_profile(request):
    """Hiển thị và chỉnh sửa hồ sơ người dùng"""
    user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật hồ sơ thành công!')
            return redirect('user_profile')
    else:
        form = UserProfileForm(instance=user_profile)
    
    context = {
        'form': form,
        'user_profile': user_profile,
        'page_title': 'Hồ Sơ Của Tôi',
    }
    return render(request, 'auth/profile.html', context)


@login_required(login_url='login')
def order_history(request):
    """Hiển thị lịch sử đơn hàng của người dùng"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
        'page_title': 'Lịch Sử Đơn Hàng',
    }
    return render(request, 'auth/order_history.html', context)


# ============================================================
# VÍ DỤ KHO HÀNG - Quản lý kho hàng và tồn kho
# ============================================================

def warehouse_list(request):
    """Hiển thị danh sách kho hàng"""
    warehouses = Warehouse.objects.filter(is_active=True)
    
    context = {
        'warehouses': warehouses,
        'page_title': 'Kho Hàng',
    }
    return render(request, 'warehouse/warehouse_list.html', context)


def warehouse_detail(request, warehouse_id):
    """Xem chi tiết kho và danh sách hàng trong kho"""
    warehouse = get_object_or_404(Warehouse, id=warehouse_id, is_active=True)
    warehouse_stocks = warehouse.warehouse_stocks.all().select_related('product')
    
    context = {
        'warehouse': warehouse,
        'warehouse_stocks': warehouse_stocks,
        'page_title': f'Kho: {warehouse.name}',
    }
    return render(request, 'warehouse/warehouse_detail.html', context)


def product_warehouse_availability(request, product_id):
    """Xem tồn kho của một sản phẩm ở các kho khác nhau"""
    product = get_object_or_404(Product, id=product_id)
    warehouse_stocks = product.warehouse_stocks.filter(
        warehouse__is_active=True
    ).select_related('warehouse')
    
    total_warehouse_stock = sum(ws.quantity for ws in warehouse_stocks)
    
    context = {
        'product': product,
        'warehouse_stocks': warehouse_stocks,
        'total_warehouse_stock': total_warehouse_stock,
        'total_stock': product.stock + total_warehouse_stock,
        'page_title': f'Tồn kho: {product.name}',
    }
    return render(request, 'warehouse/product_availability.html', context)


def stock_movement_log(request):
    """Xem lịch sử chuyển động hàng hóa"""
    movements = StockMovement.objects.all().select_related(
        'warehouse_stock__product',
        'warehouse_stock__warehouse',
        'created_by'
    ).order_by('-created_at')
    
    # Lọc theo loại chuyển động nếu được chỉ định
    movement_type = request.GET.get('type')
    if movement_type:
        movements = movements.filter(movement_type=movement_type)
    
    # Lọc theo kho hàng nếu được chỉ định
    warehouse_id = request.GET.get('warehouse')
    if warehouse_id:
        movements = movements.filter(warehouse_stock__warehouse_id=warehouse_id)
    
    context = {
        'movements': movements[:100],  # Giới hạn lấy 100 bản ghi chuyển động gần nhất
        'movement_types': StockMovement.MOVEMENT_TYPES,
        'warehouses': Warehouse.objects.filter(is_active=True),
        'selected_type': movement_type,
        'selected_warehouse': warehouse_id,
        'page_title': 'Lịch Sử Chuyển Động Hàng',
    }
    return render(request, 'warehouse/stock_movement_log.html', context)


def warehouse_statistics(request):
    """Thống kê chi tiết kho hàng"""
    warehouses = Warehouse.objects.filter(is_active=True)
    products = Product.objects.all()
    
    warehouse_data = []
    for warehouse in warehouses:
        total_items = warehouse.total_items
        capacity = warehouse.capacity
        percent = (total_items / capacity * 100) if capacity > 0 else 0
        
        warehouse_data.append({
            'warehouse': warehouse,
            'total_items': total_items,
            'capacity': capacity,
            'available': warehouse.available_capacity,
            'percent': percent,
        })
    
    # Tính toán các thống kê tổng hợp
    total_warehouses = warehouses.count()
    total_capacity = sum(w.capacity for w in warehouses)
    total_items = sum(w.total_items for w in warehouses)
    total_products = products.count()
    
    context = {
        'warehouse_data': warehouse_data,
        'total_warehouses': total_warehouses,
        'total_capacity': total_capacity,
        'total_items': total_items,
        'total_products': total_products,
        'page_title': 'Thống Kê Kho Hàng',
    }
    return render(request, 'warehouse/statistics.html', context)
