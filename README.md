Проект Foodgram - сервис для публикации кулинарных рецептов.

Адрес: http://84.252.129.10

Тестовый пользователь:

login: admin
password: admin

Возможности сервиса:

Регистрация пользователей.

Создание, Изменение, Удаление рецептов.

Добавление рецептов в избранное и простмотр всех избранных рецептов.

Фильтрация рецептов по тегам.

Подписка на авторов и просмотр рецептов определенного автора.

Добавление рецептов и формирование списка покупок для их приготовления.

###Установка Для работы с проектом необходимо установить Docker: https://docs.docker.com/engine/install/

Клонируйте репозиторий к себе на сервер командой:

https://github.com/dansen95/foodgram-project-react
Перейдите в каталок проекта:

cd foodgram-project-react
Создайте файл окружений

touch .env
И заполните его:

DB_NAME=postgres  # имя базы postgres
POSTGRES_USER=postgres # имя пользователя postgres
POSTGRES_PASSWORD=postgres # пароль для базы postgres
DB_HOST=db   #имя хоста базы данных
DB_PORT=5432  #порт
Перейдите в каталог infra и запустите создание контейнеров:

docker-compose up -d --build
Первоначальная настройка проекта:

- docker-compose exec backend python manage.py migrate --noinput
- docker-compose exec backend python manage.py collectstatic --no-input
Создание суперпользователя:

- docker-compose exec backend python manage.py createsuperuser
Загрузка фикстур

docker exec -it backend python manage.py loaddata fixtures.json
После сборки, проект будет доступен по имени хоста вашей машины, на которой был развернут проект.

Проект подготовил Сень Даниил, в рамках учебной программы по бекенд разработке ЯПрактикум.