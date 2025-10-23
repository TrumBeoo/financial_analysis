# Financial News Analysis Dashboard

Ứng dụng phân tích tin tức tài chính Việt Nam với dashboard tương tác.

## Tính năng

- 📰 Thu thập tin tức từ các trang web tài chính
- 🤖 Phân tích sentiment tự động
- 📊 Dashboard trực quan với biểu đồ
- 🔗 Phân tích URL tin tức trực tiếp
- 💾 Lưu trữ dữ liệu MongoDB

## Cài đặt

1. Clone repository
2. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

3. Cấu hình MongoDB trong file `.env`

4. Chạy ứng dụng:
```bash
python main.py
```

## Cấu trúc dự án

```
financial_analysis/
├── config/          # Cấu hình
├── src/
│   ├── crawler/     # Thu thập dữ liệu
│   ├── dashboard/   # Giao diện web
│   ├── database/    # Quản lý database
│   ├── models/      # Mô hình ML
│   ├── processing/  # Xử lý văn bản
│   └── utils/       # Tiện ích
├── main.py          # File chính
└── test_app.py      # Test script
```

## Sử dụng

1. Truy cập http://localhost:8050
2. Xem dashboard tổng quan
3. Phân tích URL tin tức tại /url-analysis
4. Dữ liệu được cập nhật tự động

## Test

```bash
python test_app.py
```

## Quản lý Database

### Xóa toàn bộ dữ liệu
```bash
python clear_database.py
```

### Xóa cache dashboard
```bash
python clear_cache.py
```

### Script nâng cao
```bash
# Xem thông tin database
python scripts/reset_database.py --info

# Xóa dữ liệu từ collections cụ thể
python scripts/reset_database.py --clear news_articles processed_articles

# Xóa toàn bộ dữ liệu
python scripts/reset_database.py --all

# Chỉ xóa cache
python scripts/reset_database.py --cache
```