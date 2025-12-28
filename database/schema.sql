-- XStore Ürün Veritabanı Şeması
-- PostgreSQL

-- Kategoriler tablosu
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    name_en VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ürünler tablosu
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    name_en VARCHAR(200),
    category_id INTEGER REFERENCES categories(id),
    price DECIMAL(10,2) NOT NULL,
    description TEXT,
    description_en TEXT,
    material VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Beden ve stok tablosu
CREATE TABLE IF NOT EXISTS product_stock (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    size VARCHAR(10) NOT NULL,
    color VARCHAR(50) NOT NULL,
    color_en VARCHAR(50),
    stock INTEGER DEFAULT 0,
    UNIQUE(product_id, size, color)
);

-- Kategorileri ekle
INSERT INTO categories (name, name_en) VALUES
('Tişört', 'T-Shirt'),
('Gömlek', 'Shirt'),
('Pantolon', 'Pants'),
('Elbise', 'Dress'),
('Mont', 'Jacket'),
('Sweatshirt', 'Sweatshirt'),
('Ceket', 'Blazer'),
('Etek', 'Skirt');

-- Örnek ürünler ekle
INSERT INTO products (name, name_en, category_id, price, description, description_en, material) VALUES
-- Tişörtler
('Oversize Basic Tişört', 'Oversize Basic T-Shirt', 1, 299.90, 'Rahat kesim, günlük kullanım için ideal', 'Relaxed fit, perfect for everyday wear', '%100 Pamuk'),
('Baskılı Crop Tişört', 'Printed Crop T-Shirt', 1, 249.90, 'Şık baskı detaylı crop model', 'Stylish printed crop model', '%100 Pamuk'),
('Polo Yaka Tişört', 'Polo T-Shirt', 1, 399.90, 'Klasik polo yaka, şık görünüm', 'Classic polo collar, elegant look', '%95 Pamuk, %5 Elastan'),

-- Gömlekler
('Oxford Klasik Gömlek', 'Oxford Classic Shirt', 2, 599.90, 'İş ve günlük kullanıma uygun', 'Suitable for work and casual wear', '%100 Pamuk'),
('Keten Yazlık Gömlek', 'Linen Summer Shirt', 2, 699.90, 'Serin ve hafif, yaz ayları için', 'Cool and light, perfect for summer', '%100 Keten'),

-- Pantolonlar
('Slim Fit Jean', 'Slim Fit Jeans', 3, 699.90, 'Dar kesim, esnek kumaş', 'Slim cut, stretchy fabric', '%98 Pamuk, %2 Elastan'),
('Wide Leg Pantolon', 'Wide Leg Pants', 3, 549.90, 'Bol paça, trend model', 'Wide leg, trendy model', '%100 Pamuk'),
('Jogger Pantolon', 'Jogger Pants', 3, 449.90, 'Spor şık, rahat kullanım', 'Sporty chic, comfortable', '%80 Pamuk, %20 Polyester'),

-- Elbiseler
('Midi Boy Yazlık Elbise', 'Midi Summer Dress', 4, 799.90, 'Çiçek desenli, yazlık', 'Floral pattern, summer style', '%100 Viskon'),
('Triko Elbise', 'Knit Dress', 4, 899.90, 'Şık ve zarif, her ortama uygun', 'Elegant, suitable for any occasion', '%50 Akrilik, %50 Pamuk'),

-- Montlar
('Puffer Mont', 'Puffer Jacket', 5, 1299.90, 'Sıcak tutan, su geçirmez', 'Warm and waterproof', '%100 Polyester'),
('Deri Ceket', 'Leather Jacket', 5, 2499.90, 'Gerçek deri, zamansız stil', 'Genuine leather, timeless style', '%100 Gerçek Deri'),

-- Sweatshirtler
('Kapüşonlu Sweatshirt', 'Hoodie Sweatshirt', 6, 549.90, 'Yumuşak iç yüzey, sıcak tutar', 'Soft inner surface, keeps warm', '%80 Pamuk, %20 Polyester'),
('Oversize Sweatshirt', 'Oversize Sweatshirt', 6, 499.90, 'Bol kesim, rahat', 'Loose fit, comfortable', '%100 Pamuk'),

-- Ceketler
('Blazer Ceket', 'Blazer', 7, 1199.90, 'Şık ve profesyonel görünüm', 'Elegant and professional look', '%70 Polyester, %30 Viskon'),

-- Etekler
('Mini Etek', 'Mini Skirt', 8, 349.90, 'Şık ve trend', 'Stylish and trendy', '%95 Pamuk, %5 Elastan'),
('Pileli Midi Etek', 'Pleated Midi Skirt', 8, 449.90, 'Pile detaylı, zarif', 'Pleated detail, elegant', '%100 Polyester');

-- Stok bilgileri ekle
-- Oversize Basic Tişört (id: 1)
INSERT INTO product_stock (product_id, size, color, color_en, stock) VALUES
(1, 'S', 'Siyah', 'Black', 25),
(1, 'M', 'Siyah', 'Black', 30),
(1, 'L', 'Siyah', 'Black', 20),
(1, 'XL', 'Siyah', 'Black', 15),
(1, 'S', 'Beyaz', 'White', 20),
(1, 'M', 'Beyaz', 'White', 35),
(1, 'L', 'Beyaz', 'White', 25),
(1, 'XL', 'Beyaz', 'White', 10),
(1, 'M', 'Gri', 'Gray', 15),
(1, 'L', 'Gri', 'Gray', 10);

-- Baskılı Crop Tişört (id: 2)
INSERT INTO product_stock (product_id, size, color, color_en, stock) VALUES
(2, 'XS', 'Siyah', 'Black', 10),
(2, 'S', 'Siyah', 'Black', 20),
(2, 'M', 'Siyah', 'Black', 15),
(2, 'S', 'Pembe', 'Pink', 12),
(2, 'M', 'Pembe', 'Pink', 18);

-- Polo Yaka Tişört (id: 3)
INSERT INTO product_stock (product_id, size, color, color_en, stock) VALUES
(3, 'S', 'Lacivert', 'Navy', 15),
(3, 'M', 'Lacivert', 'Navy', 25),
(3, 'L', 'Lacivert', 'Navy', 20),
(3, 'XL', 'Lacivert', 'Navy', 10),
(3, 'M', 'Beyaz', 'White', 20),
(3, 'L', 'Beyaz', 'White', 15);

-- Oxford Klasik Gömlek (id: 4)
INSERT INTO product_stock (product_id, size, color, color_en, stock) VALUES
(4, 'S', 'Mavi', 'Blue', 10),
(4, 'M', 'Mavi', 'Blue', 20),
(4, 'L', 'Mavi', 'Blue', 15),
(4, 'M', 'Beyaz', 'White', 25),
(4, 'L', 'Beyaz', 'White', 20);

-- Slim Fit Jean (id: 6)
INSERT INTO product_stock (product_id, size, color, color_en, stock) VALUES
(6, '28', 'Koyu Mavi', 'Dark Blue', 10),
(6, '30', 'Koyu Mavi', 'Dark Blue', 20),
(6, '32', 'Koyu Mavi', 'Dark Blue', 25),
(6, '34', 'Koyu Mavi', 'Dark Blue', 15),
(6, '30', 'Siyah', 'Black', 18),
(6, '32', 'Siyah', 'Black', 22);

-- Puffer Mont (id: 11)
INSERT INTO product_stock (product_id, size, color, color_en, stock) VALUES
(11, 'S', 'Siyah', 'Black', 8),
(11, 'M', 'Siyah', 'Black', 12),
(11, 'L', 'Siyah', 'Black', 10),
(11, 'M', 'Haki', 'Khaki', 6),
(11, 'L', 'Haki', 'Khaki', 8);

-- Kapüşonlu Sweatshirt (id: 13)
INSERT INTO product_stock (product_id, size, color, color_en, stock) VALUES
(13, 'S', 'Gri', 'Gray', 15),
(13, 'M', 'Gri', 'Gray', 25),
(13, 'L', 'Gri', 'Gray', 20),
(13, 'XL', 'Gri', 'Gray', 10),
(13, 'M', 'Siyah', 'Black', 20),
(13, 'L', 'Siyah', 'Black', 15);

-- Midi Boy Yazlık Elbise (id: 9)
INSERT INTO product_stock (product_id, size, color, color_en, stock) VALUES
(9, 'XS', 'Çiçekli', 'Floral', 5),
(9, 'S', 'Çiçekli', 'Floral', 10),
(9, 'M', 'Çiçekli', 'Floral', 12),
(9, 'L', 'Çiçekli', 'Floral', 8);

-- Diğer ürünler için de bazı stoklar
INSERT INTO product_stock (product_id, size, color, color_en, stock) VALUES
(5, 'M', 'Bej', 'Beige', 10),
(5, 'L', 'Bej', 'Beige', 8),
(7, 'S', 'Siyah', 'Black', 12),
(7, 'M', 'Siyah', 'Black', 18),
(7, 'L', 'Siyah', 'Black', 15),
(8, 'S', 'Siyah', 'Black', 10),
(8, 'M', 'Siyah', 'Black', 15),
(8, 'L', 'Siyah', 'Black', 12),
(10, 'S', 'Bej', 'Beige', 6),
(10, 'M', 'Bej', 'Beige', 10),
(12, 'M', 'Siyah', 'Black', 5),
(12, 'L', 'Siyah', 'Black', 4),
(14, 'M', 'Ekru', 'Ecru', 12),
(14, 'L', 'Ekru', 'Ecru', 10),
(15, 'S', 'Siyah', 'Black', 8),
(15, 'M', 'Siyah', 'Black', 10),
(16, 'S', 'Siyah', 'Black', 6),
(16, 'M', 'Siyah', 'Black', 8),
(17, 'S', 'Siyah', 'Black', 10),
(17, 'M', 'Siyah', 'Black', 15);
