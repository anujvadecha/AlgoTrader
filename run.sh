#!/usr/bin/env bash
echo "Hello starting script"
cd ~/Desktop/AlgoTrader
source venv/bin/activate
cd AlgoTrader
python manage.py makemigrations
python manage.py migrate
git add -u
git commit -m "server changes"
git pull
git push
python main.py
