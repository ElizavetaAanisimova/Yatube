# Yatube

## Описание

Проект Yatube — это платформа для публикаций, блог, в котором пользователи делятся мыслями на своей странице, имеют возможность посещать страницы других авторов, подписываться на них и комментировать их записи. Новая запись пользователя появляется в ленте тех, кто на него подписан и не появляется в ленте тех, кто не подписан.У каждого зарегистрированного пользователя есть профайл. При создании записи автор может выбрать группу, к тематике которой относится его пост. После публикации каждая запись доступна на странице автора, странице группы, если такая была выбрана, на главной странице, а также в ленте тех, кто подписан на автора. Пользователи могут добавлять картинки к своим постам.

Список постов на главной странице сайта хранится в кэше и обновляется раз в 20 секунд.

Проект содержит кастомные страницы ошибок:
-   404 page_not_found
-   500 server_error
-   403 permission_denied_view




## Запуск проекта
1. Клонирование репозитория
```
git clone git@github.com:ваш-аккаунт-на-гитхабе/api_yamdb.git
```

Откройте в своем редакторе кода локальный проекта из репозитория GitHub, клонированного ранее

2. Развертывание в репозитории виртуального окружения
```
python3 -m venv venv
```
3. Запуск виртуального окружения
```
source venv/Scripts/activate
```
4. Установка зависимостей в виртуальном окружении
```
pip install -r requirements.txt
```

5. Выполнение миграций
```
python manage.py migrate
```

6. Запуск проекта
```
python manage.py runserver
```

## Технологии

-   Python3
-   Django
-   Django ORM
-   Twitter Bootstrap
-   Unittest
-   SQLite3



## Авторы
Елизавета Анисимова