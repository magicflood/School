1. python -m venv .venv
2. .venv\Scripts\activate
3. pip install django
4. django-admin startproject root .
5. python manage.py startapp xohlagannom
6. python manage.py migrate
7. python manage.py runserver
8. pip install psycopg
9. pip install psycopg2-binary

# admin
1: python manage.py createsuperuser
    username: admin
    email: xohalsa yozish kerak (shartmas)
    password: 123456(misol) yozganda korinmaydi
    conf_pass: 123456
    Y/N: y

# jazzmin
pip install django-jazzmin
install_apps=[
    'jazmin'
]

# python manage.py makemigrations
# python manage.py migrate