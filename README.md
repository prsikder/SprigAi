# SprigAI - Smart Crop Guardian

For Vercel deployment with PyMySQL, see [DEPLOYMENT.md](DEPLOYMENT.md).
`requirements.txt` installs the web application; use
`pip install -r requirements-ml.txt` for the full local ML environment.

An AI-powered smart agriculture platform for Bangladesh farmers, combining **crop
recommendation**, **fertilizer recommendation**, **crop disease detection**, **soil
classification**, and a **farmer AI chatbot** into one Django + MySQL web application.

---

## 1. Technology Stack

| Layer      | Technology                                                   |
|------------|---------------------------------------------------------------|
| Frontend   | HTML5, CSS3, Bootstrap 5, vanilla JavaScript                  |
| Backend    | Python, Django 5, Django REST Framework                       |
| Database   | MySQL (via XAMPP / phpMyAdmin)                                 |
| AI / ML    | scikit-learn, CatBoost, PyTorch, torchvision, Pillow, joblib   |
| Chatbot    | Gemini API or OpenAI API (configurable via `.env`)             |

---

## 2. Project Structure

```
sprigai/
├── manage.py
├── requirements.txt
├── .env.example
├── sprigai_project/          # Django project settings, urls, wsgi/asgi
├── core/                     # Landing page, about/features/FAQ, shared layout,
│                              #   error handling, shared image-model service
├── accounts/                 # Custom User model, signup/login/admin-login, profile
├── dashboard/                # User dashboard + admin dashboard (no models)
├── crop_recommendation/      # Crop recommendation form, service, history
├── fertilizer_recommendation/# Fertilizer recommendation form, service, history
├── disease_detection/        # Crop disease image upload, PyTorch inference, history
├── soil_classification/      # Soil image upload, PyTorch inference, history
├── chatbot/                  # Farmer AI chatbot (Gemini/OpenAI), conversation history
├── contact/                  # Contact form + message storage
├── ai_models/                # <-- put your trained model files here (see §5)
│   ├── crop_recommendation/
│   ├── fertilizer_recommendation/
│   ├── disease_detection/
│   └── soil_classification/
└── media/                    # uploaded images (disease_uploads/, soil_uploads/, ...)
```

---

## 3. Local Setup (Windows + XAMPP)

### 3.1 Prerequisites
- Python 3.11
- XAMPP running **Apache + MySQL** (only MySQL is needed for this project)
- Git (optional)

### 3.2 Create the MySQL database
1. Start MySQL from the XAMPP control panel.
2. Open **phpMyAdmin** (`http://localhost/phpmyadmin`).
3. Click **New**, create a database named `sprigai_db` (or any name you like)
   with collation `utf8mb4_general_ci`.

### 3.3 Configure environment variables
```bash
copy .env.example .env        # Windows
# or: cp .env.example .env    # macOS/Linux
```
Edit `.env` and set at minimum:
```
SECRET_KEY=<generate a long random string>
DB_NAME=sprigai_db
DB_USER=root
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=3306
```
For the chatbot, set `CHATBOT_PROVIDER=gemini` or `openai` and the matching API key.
**If you leave the API key blank, the website still runs fine** - the chatbot page
will just show a friendly "not configured" message instead of crashing.

### 3.4 Install dependencies
```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

> **mysqlclient install issues on Windows?** Install the "Microsoft C++ Build Tools"
> or use `pip install mysqlclient` from a prebuilt wheel matching your Python version.

### 3.5 Run migrations and start the server
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Visit `http://127.0.0.1:8000/`.

- Regular users: sign up at `/accounts/signup/`.
- Admin dashboard: log in as a superuser, then visit `/accounts/admin-login/`
  (or just log in normally and use the "Admin" link in the navbar) then
  `/dashboard/admin/`.

---

## 4. Running Tests
Each app includes a `tests.py` covering model creation, access control (login
required), and safe-fallback behaviour. Run all of them with:
```bash
python manage.py test
```

---

## 5. Placing Your AI Model Files

Copy your trained files into the matching folder under `ai_models/`
(already pre-filled if you used the provided ZIP):

| Folder                              | Expected files |
|--------------------------------------|-----------------|
| `ai_models/crop_recommendation/`     | `crop_encoder.pkl`, `district_encoder.pkl`, `growth_encoder.pkl`, `harvest_encoder.pkl`, `season_encoder.pkl`, `rf_classifier.pkl`, `rf_regressor.pkl` |
| `ai_models/fertilizer_recommendation/` | `catboost_fertilizer_model.pkl`, `fertilizer_cat_features.pkl`, `fertilizer_categorical_columns.pkl`, `fertilizer_input_columns.pkl` |
| `ai_models/disease_detection/`       | `crop_disease_model.pth`, `class_names.json`, `metrics.json` |
| `ai_models/soil_classification/`     | `soil_classifier.pth`, `class_names.json`, `metrics.json` |

If any file is missing, that specific AI module shows a clear "model is currently
unavailable" message instead of crashing the whole site - every other module keeps
working normally.

Model contract notes (see code comments in each `services/*.py` for full detail):
- **Crop recommendation**: features are `[Area, District, Season, Current_Temp,
  Current_Humidity, Growing_Time]`; the classifier predicts `[crop, harvest]` and the
  regressor predicts `[production, suitable_temperature, suitable_humidity]`.
- **Fertilizer recommendation**: CatBoost handles categorical columns natively, so
  unseen categories never crash prediction. NPK fields are optional and imputed with
  a safe default (editable in `fertilizer_recommendation/constants.py`).
- **Disease detection / Soil classification**: both use a MobileNetV3-Small
  classifier at 224x224 with ImageNet normalization, configured from each module's
  `metrics.json` (this file doubles as the "single config file" for image size /
  mean / std, per project spec).

---

## 6. Final Feature Checklist

- [x] Public pages (landing, about, features, FAQ, contact) + protected AI pages
- [x] Separate visual flows for user login (`/accounts/login/`) and admin login
      (`/accounts/admin-login/`)
- [x] MySQL stores users, contact messages, uploaded images, and all prediction
      histories
- [x] Crop recommendation outputs crop, production, harvest, suitable temperature,
      suitable humidity - never crashes on unseen categories (falls back safely)
- [x] Fertilizer recommendation supports optional NPK values
- [x] Crop disease detection accepts image upload, outputs disease + confidence +
      top-3 + advisory
- [x] Soil classification accepts image upload, outputs soil type + confidence +
      suitable crop list
- [x] AI chatbot works with an API key and fails gracefully without one
- [x] Admin dashboard shows analytics (Chart.js), recent activity, user list,
      contact-message status management
- [x] Responsive Bootstrap 5 UI with a consistent green agriculture theme
- [x] Custom 404 / 500 pages, centralized friendly-error middleware, logging via
      `logger.exception` (no `print()` debugging, no raw tracebacks to users)
- [x] REST API endpoints (`/api/predict/`) for all four prediction modules

## 7. How to Test Every Feature Manually

1. **Signup/Login** - create an account at `/accounts/signup/`, log out, log back in
   with either username or email.
2. **Crop Recommendation** - `/crop-recommendation/`, fill the form, confirm a result
   page appears and is saved under `/crop-recommendation/history/`.
3. **Fertilizer Recommendation** - `/fertilizer-recommendation/`, leave N/P/K blank
   to confirm the "safe default" info message appears.
4. **Disease Detection** - `/disease-detection/`, upload a leaf photo (try an invalid
   file type too, to confirm the friendly validation message).
5. **Soil Classification** - `/soil-classification/`, upload a soil photo, confirm
   suitable crops are listed.
6. **Chatbot** - `/chatbot/`, ask a farming question; without an API key configured
   you should see a graceful fallback message, not an error page.
7. **Contact** - `/contact/`, submit the form, then check it appears in
   `/dashboard/admin/contacts/` (as an admin/staff user).
8. **Admin Dashboard** - log in as a superuser, visit `/dashboard/admin/` to see
   totals, the module-usage chart, and recent activity across all four AI modules.

---

## 8. Security Notes
- `SECRET_KEY`, database credentials, and chatbot API keys are all read from `.env`
  and are never hardcoded.
- All AI feature views require `@login_required`.
- CSRF protection is enabled on every form.
- Uploaded images are validated for file type and size before any AI processing.
- Unhandled exceptions are caught by `core.middleware.FriendlyErrorMiddleware` and
  logged via `logger.exception` - end users never see a raw Python traceback.
