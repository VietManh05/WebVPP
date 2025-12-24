from django.apps import AppConfig


class ShopConfig(AppConfig):
    name = 'shop'
    verbose_name = 'Cửa hàng Văn Phòng Phẩm'
    
    def ready(self):
        import shop.signals
