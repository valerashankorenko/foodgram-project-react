# Проект FOODGRAM

## Автор проекта:
- Валерий Шанкоренко
Telegram: @valeron007
E-mail: valerashankorenko@yandex.by

## Стек технологий

- Python
- Django
- Django REST Framework
- PostgreSQL
- Docker
- Github Actions

## Описание проекта:
Проект «FOODGRAM» — сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

Инструкции по развертыванию проекта
- Клонируйте репозиторий:

git clone https://github.com/Имя_репозитория/foodgram-project-react.git

Собираем контейнеры:
Из папки infra/ разверните контейнеры при помощи docker-compose:

docker-compose up -d --build

Документация по API будет доступна http://localhost/api/docs/ 

В другом терминале выполните команды:

Применить миграции:

docker-compose exec backend python manage.py migrate
Создайте суперпользователя:

docker-compose exec backend python manage.py create_admin
Соберите статику:

docker-compose exec backend python manage.py collectstatic
Наполните базу данных ингредиентами и тегами. Выполняйте команду из дериктории где находится файл manage.py:

docker-compose exec backend python manage.py load_database


Подготовка к запуску проекта на удаленном сервере
Cоздать и заполнить .env файл в директории infra

POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_NAME=foodgram
DB_HOST=db
DB_PORT=5432
SECRET_KEY=
ALLOWED_HOSTS=
DEBUG=False
DJANGO_SUPERUSER_USERNAME=
DJANGO_SUPERUSER_EMAIL=
DJANGO_SUPERUSER_PASSWORD=
