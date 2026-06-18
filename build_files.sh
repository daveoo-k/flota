#!/bin/bash
# Skrypt buildu dla Vercela: instaluje zależności i zbiera pliki statyczne
# (m.in. panel admina) do katalogu staticfiles/ serwowanego przez CDN.
set -e

pip3.12 install -r requirements.txt
python3.12 manage.py collectstatic --noinput --clear
