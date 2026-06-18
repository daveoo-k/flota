# Wdrożenie na Vercel — JNB Fleet Manager

Aplikacja Django przygotowana pod Vercela: **PostgreSQL** (baza), **Cloudinary**
(pliki/zdjęcia), **WhiteNoise** (statyki). Lokalnie działa bez tego — na SQLite
i katalogu `media/`.

## 1. Załóż usługi i zdobądź dane dostępowe

| Usługa | Po co | Zmienna |
|--------|-------|---------|
| **Neon** (neon.tech) lub Vercel Postgres | baza danych | `DATABASE_URL` |
| **Cloudinary** (cloudinary.com) | zdjęcia, rachunki PDF | `CLOUDINARY_URL` |
| Konto e-mail SMTP (np. Gmail App Password) | formularz kontaktowy | `EMAIL_*` |

- `DATABASE_URL` — format `postgres://user:haslo@host:5432/baza`
- `CLOUDINARY_URL` — z dashboardu Cloudinary: `cloudinary://API_KEY:API_SECRET@CLOUD_NAME`

## 2. Ustaw zmienne środowiskowe w Vercel

Vercel → projekt → **Settings → Environment Variables**. Dodaj (patrz `.env.example`):

```
SECRET_KEY=<losowy klucz>
DEBUG=False
DATABASE_URL=postgres://...
CLOUDINARY_URL=cloudinary://...
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
CONTACT_RECIPIENT=...
```

Klucz wygenerujesz:
```
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 3. Zainicjalizuj bazę (jednorazowo, lokalnie celując w zdalny Postgres)

```bash
# tymczasowo wskaż zdalną bazę
export DATABASE_URL="postgres://user:haslo@host:5432/baza"   # PowerShell: $env:DATABASE_URL="..."
python manage.py migrate
python manage.py createsuperuser
```

Opcjonalnie przeniesienie istniejących danych z SQLite do Postgresa:
```bash
# 1) eksport z SQLite (bez DATABASE_URL)
python manage.py dumpdata --natural-primary --natural-foreign \
  --exclude contenttypes --exclude auth.permission -o dump.json
# 2) import do Postgresa (z ustawionym DATABASE_URL)
python manage.py loaddata dump.json
```

## 4. Deploy

Repo jest już podpięte do Vercela — każdy `git push` na `main` uruchamia deploy.
Vercel czyta `vercel.json`:
- `Flota/wsgi.py` → funkcja serverless (aplikacja),
- `build_files.sh` → `collectstatic` do `staticfiles/` (serwowane na `/static/`).

## 5. Uruchomienie lokalne

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows;  source .venv/bin/activate na Linux/Mac
pip install -r requirements.txt
copy .env.example .env        # i uzupełnij wartości (albo zostaw puste = SQLite)
python manage.py migrate
python manage.py runserver
```

## Uwagi / ograniczenia

- Panel admina: `/admin99/`.
- Bez `CLOUDINARY_URL` uploady idą lokalnie do `media/` — na Vercelu **muszą** być
  na Cloudinary (system plików jest tylko do odczytu).
- Stary, zaszyty login do Gmaila został usunięty z kodu. **Zmień to hasło** —
  wyciekło do historii git.
