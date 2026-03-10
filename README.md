# admin-be (Django)

Backend Django cho trang quản trị Marketplace.

## Yêu cầu

- Python 3.10+ (khuyến nghị 3.11)
- pip

## Cài đặt & chạy local (Windows)

Mở PowerShell tại thư mục `be/`:

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Thiết lập biến môi trường `DJANGO_SECRET_KEY`:

- Cách nhanh (PowerShell):

```bash
$env:DJANGO_SECRET_KEY="replace-me"
```

- Hoặc tạo file `.env` dựa theo `.env.example` (file này đã được ignore, không push lên GitHub).

Chạy migrate + tạo admin:

```bash
python manage.py migrate
python manage.py createsuperuser
```

Chạy server:

```bash
python manage.py runserver
```

Mặc định BE chạy ở `http://127.0.0.1:8000`.

## API routes

Tất cả API admin được mount dưới:

- Base path: `/api/admin/`

Một số endpoints tiêu biểu:

- **CSRF**: `GET /api/admin/csrf/`
- **Listings**: `/api/admin/listings/`
- **Users**: `/api/admin/users/`
- **Reports**: `/api/admin/reports/`
- **Dashboard**:
  - `GET /api/admin/dashboard/summary/`
  - `GET /api/admin/dashboard/timeseries/`
  - `GET /api/admin/dashboard/`
  - `POST /api/admin/dashboard/save-report/`
- **Fees**:
  - `GET /api/admin/fees/statistics/?days=7`
  - `GET /api/admin/fees/top-transactions/`
  - `POST /api/admin/fees/save-report/`

## CORS (kết nối Frontend)

`backend/settings.py` đang whitelist FE chạy ở:

- `http://localhost:4200`
- `http://127.0.0.1:4200`

## Ghi chú

- Dự án đang dùng SQLite (`db.sqlite3`) cho local dev. File DB đã được ignore để tránh push lên repo.
