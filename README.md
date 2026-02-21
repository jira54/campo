# CampoPawa (MVP)

Lightweight customer retention and loyalty tracking for campus vendors.

Quick start (local development)

1. Activate virtualenv

Windows (PowerShell):

```powershell
& D:\campo\venv\Scripts\Activate.ps1
```

2. Run migrations

```powershell
D:/campo/venv/Scripts/python.exe manage.py migrate
```

3. Seed sample data (creates superuser and a test vendor)

```powershell
D:/campo/venv/Scripts/python.exe scripts/seed_sample_data.py
```

4. Start dev server

```powershell
D:/campo/venv/Scripts/python.exe manage.py runserver
```

Open http://127.0.0.1:8000/ to view the app and http://127.0.0.1:8000/admin/ for admin.

Credentials created by seeder

- Superuser: `admin@campopawa.test` / `adminpass`
- Vendor: `vendor@campopawa.test` / `vendorpass`

Notes

- The project expects PostgreSQL for production. For local dev we use your configured DB.
- If you see a warning about `D:\campo\static` not existing, create a `static/` directory at project root or update `STATICFILES_DIRS` in `config/settings.py`.

Next steps

- Improve mobile UI and progress bars
- Add search on `Customers` page
- Add small chart for weekly revenue
