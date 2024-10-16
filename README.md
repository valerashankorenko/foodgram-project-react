# Проект FOODGRAM

## Описание проекта:
Проект «FOODGRAM» — сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Автор проекта:
Валерий Шанкоренко<br/>
Github: [Valera Shankorenko](https://github.com/valerashankorenko)<br/>
Telegram:[@valeron007](https://t.me/valeron007)<br/>
E-mail:valerashankorenko@yandex.by<br/>

## Стек технологий
- Python
- Django
- Django REST Framework
- PostgreSQL
- Docker
- Nginx
- Github Actions

### Развертывание проекта на удаленном сервере:
Клонировать репозиторий:
```shell
git clone git@github.com:valerashankorenko/foodgram-project-react.git
```
Установить на сервере Docker, Docker Compose:
```shell
sudo apt install curl                                   # установка утилиты для скачивания файлов
curl -fsSL https://get.docker.com -o get-docker.sh      # скачать скрипт для установки
sh get-docker.sh                                        # запуск скрипта
sudo apt-get install docker-compose-plugin              # последняя версия docker compose
```
Скопировать на сервер файлы docker-compose.yml, nginx.conf из папки infra (команды выполнять находясь в папке infra):
```shell
scp docker-compose.yml nginx.conf username@IP:/home/username/   # username - имя пользователя на сервере
                                                                # IP - публичный IP сервера
```
Для работы с GitHub Actions необходимо в репозитории в разделе Secrets > Actions создать переменные окружения:
```
SECRET_KEY              # секретный ключ Django проекта
DOCKER_PASSWORD         # пароль от Docker Hub
DOCKER_USERNAME         # логин Docker Hub
HOST                    # публичный IP сервера
USER                    # имя пользователя на сервере
PASSPHRASE              # *если ssh-ключ защищен паролем
SSH_KEY                 # приватный ssh-ключ
TELEGRAM_TO             # ID телеграм-аккаунта для посылки сообщения
TELEGRAM_TOKEN          # токен бота, посылающего сообщение

DB_ENGINE               # django.db.backends.postgresql
POSTGRES_DB             # postgres
POSTGRES_USER           # postgres
POSTGRES_PASSWORD       # postgres
DB_HOST                 # db
DB_PORT                 # 5432 (порт по умолчанию)
```
Создать и запустить контейнеры Docker, выполнить команду на сервере (версии команд "docker compose" или "docker-compose" отличаются в зависимости от установленной версии Docker Compose):
```shell
sudo docker compose up -d
```
После успешной сборки выполнить миграции:
```shell
sudo docker compose exec backend python manage.py migrate
```
Создать суперпользователя:
```shell
sudo docker compose exec backend python manage.py createsuperuser
```
Собрать статику:
```shell
sudo docker compose exec backend python manage.py collectstatic --noinput
```
Наполнить базу данных содержимым из файла ingredients.json:
```shell
sudo docker compose exec backend python manage.py loaddata ingredients.json
```
Для остановки контейнеров Docker:
```shell
sudo docker compose down -v      # с их удалением
sudo docker compose stop         # без удаления
```
После каждого обновления репозитория (push в ветку master) будет происходить:
Проверка кода на соответствие стандарту PEP8 (с помощью пакета flake8)
Сборка и доставка докер-образов frontend и backend на Docker Hub
Разворачивание проекта на удаленном сервере
Отправка сообщения в Telegram в случае успеха

### Запуск проекта на локальной машине:
Клонировать репозиторий:
```shell
git clone git@github.com:valerashankorenko/foodgram-project-react.git
```
В директории infra создать файл .env и заполнить своими данными по аналогии с example.env:
```
DB_ENGINE=django.db.backends.postgresql
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY='секретный ключ Django'
```
Создать и запустить контейнеры Docker, последовательно выполнить команды по созданию миграций, сбору статики, созданию суперпользователя, как указано выше.
```shell
docker-compose -f docker-compose-local.yml up -d
```
После запуска проект будут доступен по адресу: http://localhost/
Документация будет доступна по адресу: http://localhost/api/docs/
