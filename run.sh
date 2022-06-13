#!/usr/bin/env bash
echo "Hello starting script"
cd ~/Desktop/AlgoTrader || exit
source venv/bin/activate
cd AlgoTrader || exit
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
git add -u
git commit -m "server changes"
git pull
git push
python main.py
