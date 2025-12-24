"""
Các Model Cơ Sở Dữ Liệu cho Cửa hàng Văn Phòng Phẩm

Các Models:
- UserProfile: Thông tin profile mở rộng của user
- Warehouse: Vị trí kho hàng/lưu trữ
- Category: Danh mục sản phẩm
- Product: Kho sản phẩm
- WarehouseStock: Quản lý tồn kho từng kho
- StockMovement: Lịch sử chuyển động hàng
- Order: Đơn hàng của khách hàng
"""

from django.db import models
from django.contrib.auth.models import User


# ========== USER MODELS ==========

class UserProfile(models.Model):
    """Mở rộng profile của user"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile của {self.user.username}"

    class Meta:
        verbose_name = "Hồ sơ người dùng"
        verbose_name_plural = "Hồ sơ người dùng"


# ========== WAREHOUSE MODELS ==========

class Warehouse(models.Model):
    """Model quản lý kho hàng"""
    name = models.CharField(max_length=200, unique=True)
    location = models.TextField()
    phone = models.CharField(max_length=15, blank=True)
    manager_name = models.CharField(max_length=100, blank=True)
    capacity = models.IntegerField(default=0, help_text="Sức chứa tối đa (đơn vị)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def total_items(self):
        """Tính tổng số lượng hàng trong kho"""
        return sum(stock.quantity for stock in self.warehouse_stocks.all())

    @property
    def available_capacity(self):
        """Tính sức chứa còn lại"""
        return self.capacity - self.total_items

    class Meta:
        verbose_name = "Kho hàng"
        verbose_name_plural = "Kho hàng"


# ========== PRODUCT MODELS ==========

class Category(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục sản phẩm"


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    stock = models.IntegerField(default=0, help_text="Tồn kho chung")
    sku = models.CharField(max_length=100, unique=True, blank=True, help_text="SKU/Mã sản phẩm")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def total_warehouse_stock(self):
        """Tính tổng tồn kho từ tất cả các kho"""
        return sum(ws.quantity for ws in self.warehouse_stocks.all())

    @property
    def is_in_stock(self):
        """Kiểm tra còn hàng hay không"""
        return self.stock > 0 or self.total_warehouse_stock > 0

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Sản phẩm"


# ========== STOCK MANAGEMENT MODELS ==========

class WarehouseStock(models.Model):
    """Model quản lý tồn kho từng sản phẩm ở từng kho"""
    warehouse = models.ForeignKey(
        Warehouse, 
        on_delete=models.CASCADE, 
        related_name='warehouse_stocks'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='warehouse_stocks'
    )
    quantity = models.IntegerField(default=0, help_text="Số lượng trong kho")
    last_counted = models.DateTimeField(auto_now=True, help_text="Lần cuối kiểm kê")
    notes = models.TextField(blank=True, help_text="Ghi chú")
    
    class Meta:
        unique_together = ('warehouse', 'product')
        verbose_name = "Tồn kho"
        verbose_name_plural = "Tồn kho"
        ordering = ['warehouse', 'product']

    def __str__(self):
        return f"{self.product.name} - {self.warehouse.name} ({self.quantity} cái)"


class StockMovement(models.Model):
    """Theo dõi lịch sử chuyển động hàng hóa"""
    MOVEMENT_TYPES = [
        ('import', 'Nhập hàng'),
        ('export', 'Xuất hàng'),
        ('transfer', 'Chuyển kho'),
        ('adjust', 'Điều chỉnh'),
        ('sale', 'Bán hàng'),
    ]
    
    warehouse_stock = models.ForeignKey(
        WarehouseStock, 
        on_delete=models.CASCADE, 
        related_name='movements'
    )
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField(help_text="Số lượng thay đổi")
    reference = models.CharField(max_length=100, blank=True, help_text="ID đơn hàng, PO, ...")
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.warehouse_stock} ({self.quantity})"

    class Meta:
        verbose_name = "Chuyển động hàng"
        verbose_name_plural = "Chuyển động hàng"


# ========== ORDER MODELS ==========

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    customer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    total_price = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Chờ xác nhận'),
            ('confirmed', 'Đã xác nhận'),
            ('shipped', 'Đã gửi'),
            ('delivered', 'Đã giao'),
            ('cancelled', 'Đã hủy'),
        ],
        default='pending'
    )
    warehouse = models.ForeignKey(
        Warehouse, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='orders',
        help_text="Kho hàng xuất hàng"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.customer_name}"

    class Meta:
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Đơn hàng"
        ordering = ['-created_at']
