# Deploying SprigAI to Vercel

## What this deployment includes

`requirements.txt` installs the website, chatbot, and PyMySQL database driver.
The large inference libraries are optional in `requirements-ml.txt`. The four
model-based features show their existing unavailable-model messages without
model files. For full local inference, install `pip install -r requirements-ml.txt`
and restore the trained artifacts under `ai_models/`.

Vercel detects `manage.py` and `sprigai_project.settings`, resolves the WSGI
application, and runs collectstatic automatically. Select the Django framework
preset and keep Build Command and Output Directory at their defaults. Use the
repository root as the Root Directory. Python is pinned to 3.12.

## Required Vercel environment variables

Set these in Project Settings > Environment Variables for the environments you deploy:

```text
SECRET_KEY=<unique randomly generated secret>
DEBUG=False
ALLOWED_HOSTS=<your-project.vercel.app>,<any custom domain>
CSRF_TRUSTED_ORIGINS=https://<your-project.vercel.app>,https://<any custom domain>
DB_NAME=<hosted database name>
DB_USER=<hosted database user>
DB_PASSWORD=<hosted database password>
DB_HOST=<hosted database hostname>
DB_PORT=3306
DB_SSL=True
```

Use the TLS settings required by your database provider. `DB_SSL=True` enables
certificate and hostname verification using system trust roots. If your provider
uses its own CA, set `DB_SSL_CA` to the path of that CA certificate included with
the deployment. Never upload the database password or `.env` to GitHub.
The deployment URL supplied by Vercel is also added to allowed hosts and CSRF origins.

Generate a secret locally with:

```powershell
venv/Scripts/python.exe -c "import secrets; print(secrets.token_urlsafe(50))"
```

Your XAMPP database at localhost cannot serve the deployed app. Create a hosted
MySQL database and allow connections from the deployment using your provider's
network access settings. No hosted database is provisioned by these code changes.

For the chatbot, also set `CHATBOT_PROVIDER` and its `GEMINI_API_KEY` or
`OPENAI_API_KEY`. Google login additionally requires OAuth credentials and the
deployed callback URL registered with Google.

## Prepare the hosted database once

From a machine that can reach the hosted database, install the web requirements
and provide its DB_* settings through process environment variables or your local
ignored `.env`. Then run:

```powershell
venv/Scripts/python.exe -m pip install -r requirements.txt
venv/Scripts/python.exe manage.py migrate
venv/Scripts/python.exe manage.py createsuperuser
```

These commands must target the hosted database, not your local XAMPP database.
Migrations are deliberately not run automatically during every Vercel build.
Redeploy after saving the environment variables.

## Remaining infrastructure for model inference and uploads

Full inference still needs the trained models and ML dependencies on suitable
compute, or a separate inference API wired into the services. Uploading source
alone does not enable prediction. Do not simply add all ML dependencies to the
Vercel requirements without checking its function size and memory limits.

The current media storage is a local filesystem. Vercel's filesystem is not
persistent upload storage. Before enabling successful image predictions or other
saved uploads on Vercel, configure durable object storage and its media URLs.
The application does not yet have a configured storage provider or inference API.

Check the deployment homepage, signup/login, dashboard, static images, and chatbot
after deployment. A live build and database connection cannot be verified locally
without your Vercel environment and hosted database credentials.

References:
- https://vercel.com/docs/frameworks/full-stack/django
- https://vercel.com/docs/functions/runtimes/python
- https://pymysql.readthedocs.io/en/latest/user/installation.html
