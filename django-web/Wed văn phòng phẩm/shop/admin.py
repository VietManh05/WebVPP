"""
Cấu hình Admin Django cho Cửa hàng Văn Phòng Phẩm
Thiết lập giao diện admin cho tất cả các model
"""

from django.contrib import admin
from .models import (
    Category, Product, Order, UserProfile,
    Warehouse, WarehouseStock, StockMovement
)


# ========== USER ADMIN ==========
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('👤 Thông tin người dùng', {
            'fields': ('user',)
        }),
        ('📱 Liên hệ', {
            'fields': ('phone', 'address')
        }),
        ('🖼️ Hình ảnh', {
            'fields': ('avatar',)
        }),
        ('📅 Ngày tạo/sửa', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ========== WAREHOUSE ADMIN ==========

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'manager_name', 'get_stock_status', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'location', 'manager_name']
    readonly_fields = ['created_at', 'updated_at', 'total_items', 'available_capacity']
    
    fieldsets = (
        ('🏭 Thông tin kho', {
            'fields': ('name', 'location', 'phone', 'manager_name')
        }),
        ('📦 Sức chứa', {
            'fields': ('capacity', 'total_items', 'available_capacity')
        }),
        ('🔧 Cài đặt', {
            'fields': ('is_active',)
        }),
        ('📅 Ngày tạo/sửa', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_stock_status(self, obj):
        """Hiển thị trạng thái tồn kho của kho hàng"""
        total = obj.total_items
        capacity = obj.capacity
        if capacity == 0:
            return "Không có sức chứa"
        percent = (total / capacity) * 100
        if percent >= 90:
            return f"🔴 {total}/{capacity} ({percent:.0f}%)"
        elif percent >= 70:
            return f"🟡 {total}/{capacity} ({percent:.0f}%)"
        else:
            return f"🟢 {total}/{capacity} ({percent:.0f}%)"
    get_stock_status.short_description = "Trạng thái kho"


# ========== STOCK MANAGEMENT ADMIN ==========

@admin.register(WarehouseStock)
class WarehouseStockAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'quantity', 'last_counted']
    list_filter = ['warehouse', 'product__category', 'last_counted']
    search_fields = ['product__name', 'warehouse__name', 'product__sku']
    readonly_fields = ['last_counted']
    
    fieldsets = (
        ('📦 Sản phẩm & Kho', {
            'fields': ('product', 'warehouse')
        }),
        ('📊 Số lượng', {
            'fields': ('quantity',)
        }),
        ('📝 Ghi chú', {
            'fields': ('notes', 'last_counted'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['movement_type', 'warehouse_stock', 'quantity', 'reference', 'created_by', 'created_at']
    list_filter = ['movement_type', 'created_at', 'warehouse_stock__warehouse']
    search_fields = ['reference', 'warehouse_stock__product__name', 'notes']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('📋 Chuyển động', {
            'fields': ('warehouse_stock', 'movement_type', 'quantity', 'reference')
        }),
        ('👤 Người thực hiện', {
            'fields': ('created_by', 'created_at')
        }),
        ('📝 Ghi chú', {
            'fields': ('notes',)
        }),
    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    
    fieldsets = (
        ('📂 Thông tin danh mục', {
            'fields': ('name',)
        }),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'price', 'category', 'stock', 'get_warehouse_stock']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description', 'sku']
    readonly_fields = ['created_at', 'updated_at', 'total_warehouse_stock']
    
    fieldsets = (
        ('📦 Thông tin cơ bản', {
            'fields': ('name', 'sku', 'category', 'price')
        }),
        ('📊 Tồn kho', {
            'fields': ('stock', 'total_warehouse_stock')
        }),
        ('📝 Chi tiết', {
            'fields': ('description', 'image')
        }),
        ('📅 Ngày tạo/sửa', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_warehouse_stock(self, obj):
        """Lấy tổng tồn kho của sản phẩm ở tất cả các kho"""
        return obj.total_warehouse_stock
    get_warehouse_stock.short_description = "Tồn kho kho"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'get_user', 'total_price', 'status', 'warehouse', 'created_at']
    list_filter = ['status', 'created_at', 'warehouse']
    search_fields = ['customer_name', 'phone', 'address', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('📋 Thông tin đơn hàng', {
            'fields': ('id', 'user', 'status', 'warehouse', 'created_at', 'updated_at')
        }),
        ('👤 Thông tin khách hàng', {
            'fields': ('customer_name', 'phone', 'address')
        }),
        ('💰 Thanh toán', {
            'fields': ('total_price',)
        }),
    )
    
    def get_user(self, obj):
        """Lấy tên người dùng hoặc hiển thị 'Khách' nếu chưa đăng nhập"""
        return obj.user.username if obj.user else "Khách (chưa đăng nhập)"
    get_user.short_description = "Người dùng"
