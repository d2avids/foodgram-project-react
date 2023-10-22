# Kittygram
![Kittygram Deploy Badge](https://github.com/d2avids/foodgram-project-react/actions/workflows/main.yml/badge.svg)


## Описание проекта
### Foodgram представляет собой не просто платформу для публикации рецептов, а целую вселенную, где страсть к кулинарии объединяет сердца и умы. Это место, где традиции переплетаются с инновациями, а секреты великих поваров становятся доступными каждому энтузиасту кулинарного искусства.

Здесь нет границ для кулинарного творчества. Каждый, от новичка до опытного шеф-повара, может принести в наше дружное сообщество частичку своего мира, открывая новые вкусы и ароматы. Наша миссия проста, но в то же время глубока — мы хотим превратить процесс приготовления пищи в приключение, доступное каждому, и наполнить его радостью открытия и творчества.

Foodgram — это не только рецепты, это истории о еде, о людях, которые её создают, и о волшебстве, которое происходит на кухне, когда мы готовим с любовью. Это место, где можно найти вдохновение и мотивацию, научиться новому и поделиться своим, создавая неповторимые кулинарные шедевры. Мы приглашаем каждого присоединиться и сделать процесс приготовления пищи ярким, веселым и вдохновляющим путешествием.

---

### Ссылка на сайт: https://d2avids.sytes.net/

---

## Технологии
•	Python 3.9
•	Django
•	Django REST Framework
•   PostgreSQL
•   React
•   Node.js
•   Docker
•   Nginx
•	Gunicorn
---
### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/d2avids/foodgram-project-react.git 
```

Перейти в корневую директорию
```
cd foodgram-project-react/
```

Создать файл .evn и передать переменные окружения:

```
SECRET_KEY='указать секретный ключ'
ALLOWED_HOSTS='указать имя или IP хоста'
POSTGRES_DB=kittygram
POSTGRES_USER=kittygram_user
POSTGRES_PASSWORD=kittygram_password
DB_NAME=kittygram
DB_HOST=db
DB_PORT=5432
DEBUG=False
```

Запустить docker-compose.production:

```
docker compose up
```

Выполнить миграции, собрать статику бэкенда:

```
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic
docker compose exec backend cp -r /app/collected_static/. /backend_static/static/

```
---
## Автор
- Saidov David, delightxxls@gmail.com