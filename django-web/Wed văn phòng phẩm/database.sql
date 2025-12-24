-- ========================================
-- CẤU HÌNH CƠSỞ DỮ LIỆU CHO DỰ ÁN VANPHONGPHAM
-- ========================================
-- Lược đồ Cơ Sở Dữ Liệu MySQL
-- Tạo lúc: 25 Tháng 12 Năm 2025
-- Phiên bản Django: 6.0
-- Mã hóa: UTF-8 MB4
-- ========================================

-- Tạo Cơ Sở Dữ Liệu
CREATE DATABASE IF NOT EXISTS `vanphongpham_db` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `vanphongpham_db`;

-- ========================================
-- 1. AUTH_USER (Bảng Người Dùng Django Built-in)
-- ========================================
CREATE TABLE IF NOT EXISTS `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL UNIQUE,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `username` (`username`),
  KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================================
-- 2. SHOP_USERPROFILE (Hồ Sơ Người Dùng Mở Rộng)
-- ========================================
CREATE TABLE IF NOT EXISTS `shop_userprofile` (
  `id` int NOT NULL AUTO_INCREMENT,
  `phone` varchar(15) NOT NULL,
  `address` longtext NOT NULL,
  `avatar` varchar(100),
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` int NOT NULL UNIQUE,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `shop_userprofile_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================================
-- 3. SHOP_WAREHOUSE (Kho Hàng)
-- ========================================
CREATE TABLE IF NOT EXISTS `shop_warehouse` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL UNIQUE,
  `location` longtext NOT NULL,
  `phone` varchar(15) NOT NULL,
  `manager_name` varchar(100) NOT NULL,
  `capacity` int NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `name` (`name`),
  KEY `is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================================
-- 4. SHOP_CATEGORY (Danh Mục Sản Phẩm)
-- ========================================
CREATE TABLE IF NOT EXISTS `shop_category` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================================
-- 5. SHOP_PRODUCT (Sản Phẩm)
-- ========================================
CREATE TABLE IF NOT EXISTS `shop_product` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `price` decimal(10,0) NOT NULL,
  `image` varchar(100),
  `description` longtext NOT NULL,
  `stock` int NOT NULL,
  `sku` varchar(100) UNIQUE,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `category_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `category_id` (`category_id`),
  KEY `sku` (`sku`),
  KEY `name` (`name`),
  CONSTRAINT `shop_product_category_id_fk` FOREIGN KEY (`category_id`) REFERENCES `shop_category` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================================
-- 6. SHOP_WAREHOUSESTOCK (Tồn Kho Từng Kho)
-- ========================================
CREATE TABLE IF NOT EXISTS `shop_warehousestock` (
  `id` int NOT NULL AUTO_INCREMENT,
  `quantity` int NOT NULL,
  `last_counted` datetime(6) NOT NULL,
  `notes` longtext NOT NULL,
  `warehouse_id` int NOT NULL,
  `product_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `warehouse_product_unique` (`warehouse_id`, `product_id`),
  KEY `warehouse_id` (`warehouse_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `shop_warehousestock_warehouse_id_fk` FOREIGN KEY (`warehouse_id`) REFERENCES `shop_warehouse` (`id`) ON DELETE CASCADE,
  CONSTRAINT `shop_warehousestock_product_id_fk` FOREIGN KEY (`product_id`) REFERENCES `shop_product` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================================
-- 7. SHOP_STOCKMOVEMENT (Lịch Sử Chuyển Động Hàng)
-- ========================================
CREATE TABLE IF NOT EXISTS `shop_stockmovement` (
  `id` int NOT NULL AUTO_INCREMENT,
  `movement_type` varchar(20) NOT NULL,
  `quantity` int NOT NULL,
  `reference` varchar(100) NOT NULL,
  `notes` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `warehouse_stock_id` int NOT NULL,
  `created_by_id` int,
  PRIMARY KEY (`id`),
  KEY `warehouse_stock_id` (`warehouse_stock_id`),
  KEY `created_by_id` (`created_by_id`),
  KEY `created_at` (`created_at`),
  KEY `movement_type` (`movement_type`),
  CONSTRAINT `shop_stockmovement_warehouse_stock_id_fk` FOREIGN KEY (`warehouse_stock_id`) REFERENCES `shop_warehousestock` (`id`) ON DELETE CASCADE,
  CONSTRAINT `shop_stockmovement_created_by_id_fk` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================================
-- 8. SHOP_ORDER (Đơn Hàng)
-- ========================================
CREATE TABLE IF NOT EXISTS `shop_order` (
  `id` int NOT NULL AUTO_INCREMENT,
  `customer_name` varchar(100) NOT NULL,
  `phone` varchar(15) NOT NULL,
  `address` longtext NOT NULL,
  `total_price` decimal(10,0) NOT NULL,
  `status` varchar(20) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` int,
  `warehouse_id` int,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `warehouse_id` (`warehouse_id`),
  KEY `status` (`status`),
  KEY `created_at` (`created_at`),
  CONSTRAINT `shop_order_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`) ON DELETE SET NULL,
  CONSTRAINT `shop_order_warehouse_id_fk` FOREIGN KEY (`warehouse_id`) REFERENCES `shop_warehouse` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================================
-- 9. CÁC BẢNG HỆ THỐNG DJANGO (TÙY CHỌN)
-- ========================================

CREATE TABLE IF NOT EXISTS `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL UNIQUE,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `content_type_codename` (`content_type_id`, `codename`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `auth_user_groups` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_group_unique` (`user_id`, `group_id`),
  KEY `group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `auth_user_groups_group_id_fk` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `auth_user_user_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_permission_unique` (`user_id`, `permission_id`),
  KEY `permission_id` (`permission_id`),
  CONSTRAINT `auth_user_user_permissions_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `auth_user_user_permissions_permission_id_fk` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `expire_date` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `django_migrations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `app_label_model` (`app_label`, `model`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================================
-- CHỈ MỤC ĐỂ TĂNG HIỆU SUẤT
-- ========================================

CREATE INDEX idx_user_username ON `auth_user` (`username`);
CREATE INDEX idx_user_email ON `auth_user` (`email`);
CREATE INDEX idx_userprofile_user ON `shop_userprofile` (`user_id`);
CREATE INDEX idx_warehouse_name ON `shop_warehouse` (`name`);
CREATE INDEX idx_warehouse_active ON `shop_warehouse` (`is_active`);
CREATE INDEX idx_product_category ON `shop_product` (`category_id`);
CREATE INDEX idx_product_sku ON `shop_product` (`sku`);
CREATE INDEX idx_product_name ON `shop_product` (`name`);
CREATE INDEX idx_warehousestock_warehouse ON `shop_warehousestock` (`warehouse_id`);
CREATE INDEX idx_warehousestock_product ON `shop_warehousestock` (`product_id`);
CREATE INDEX idx_stockmovement_warehouse_stock ON `shop_stockmovement` (`warehouse_stock_id`);
CREATE INDEX idx_stockmovement_created_by ON `shop_stockmovement` (`created_by_id`);
CREATE INDEX idx_stockmovement_created_at ON `shop_stockmovement` (`created_at`);
CREATE INDEX idx_stockmovement_type ON `shop_stockmovement` (`movement_type`);
CREATE INDEX idx_order_user ON `shop_order` (`user_id`);
CREATE INDEX idx_order_warehouse ON `shop_order` (`warehouse_id`);
CREATE INDEX idx_order_status ON `shop_order` (`status`);
CREATE INDEX idx_order_created_at ON `shop_order` (`created_at`);

-- ========================================
-- DỮ LIỆU MẪU (TÙY CHỌN)
-- ========================================

-- Thêm người dùng admin mẫu
-- Lưu ý: Thay đổi mật khẩu sau khi tạo qua admin interface!
-- Tài khoản mặc định: admin / (tùy ý)
INSERT INTO `auth_user` (
  `password`, `last_login`, `is_superuser`, `username`, 
  `first_name`, `last_name`, `email`, `is_staff`, 
  `is_active`, `date_joined`
) VALUES (
  'pbkdf2_sha256$600000$abcdefghijklmnop$xyz123abcdefghijklmnopqrstuvwxyz123456+', 
  NULL, 1, 'admin', 'Admin', 'User', 
  'admin@vanphongpham.local', 1, 1, NOW()
) ON DUPLICATE KEY UPDATE `id` = `id`;

-- Thêm các danh mục sản phẩm mẫu
INSERT INTO `shop_category` (`name`, `created_at`) VALUES
('Giấy A4', NOW()),
('Bút viết', NOW()),
('Tập vở', NOW()),
('Dán dích', NOW()),
('Kéo cắt', NOW()),
('Bao thư', NOW()),
('Thẻ bìa cứng', NOW()),
('Tẩy & Bút xóa', NOW()),
('Dây buộc', NOW()),
('Kẹp giấy', NOW())
ON DUPLICATE KEY UPDATE `id` = `id`;

-- Thêm kho hàng mẫu
INSERT INTO `shop_warehouse` (
  `name`, `location`, `phone`, `manager_name`, 
  `capacity`, `is_active`, `created_at`, `updated_at`
) VALUES 
('Kho chính TP.HCM', '123 Nguyễn Huệ, Quận 1, TP.HCM', '0901234567', 'Nguyễn Văn A', 10000, 1, NOW(), NOW()),
('Kho Hà Nội', '456 Trần Hưng Đạo, Hoàn Kiếm, Hà Nội', '0912345678', 'Trần Thị B', 8000, 1, NOW(), NOW()),
('Kho Đà Nẵng', '789 Hùng Vương, Hải Châu, Đà Nẵng', '0923456789', 'Lê Văn C', 5000, 1, NOW(), NOW())
ON DUPLICATE KEY UPDATE `id` = `id`;

-- ========================================
-- CHÚ THÍCH QUAN TRỌNG
-- ========================================
-- 1. Hãy thay đổi mật khẩu của tài khoản admin ngay sau khi tạo
-- 2. Tất cả các trường datetime được đặt thành NOW() (thời gian hiện tại)
-- 3. Các chỉ mục được tạo để tối ưu hóa hiệu suất truy vấn
-- 4. Sử dụng UTF-8 MB4 để hỗ trợ các ký tự Unicode, bao gồm emoji
-- 5. Khóa ngoại được cấu hình với ON DELETE CASCADE để dữ liệu phụ thuộc
-- 6. Tất cả các bảng sử dụng InnoDB engine để hỗ trợ giao dịch

-- ========================================
-- KẾT THÚC CẤU HÌNH CƠ SỞ DỮ LIỆU
-- ========================================
