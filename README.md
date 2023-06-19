# Социальная сеть Yatube
## Описание
Сервис публикации записей пользователей, подписи на авторов,
а также комментирования чужих записей
## Технологии
Python 3.7 Django 2.2.19
## Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:oneome/yatube_project.git
```

```
cd api_final_yatube
```

Cоздать и активировать виртуальное окружение

Для MacOS:

```
python3 -m venv venv
```
```
source venv/bin/activate
```
Для Windows:
```
python -m venv venv
```
```
. venv/scripts/activate
```
Обновить pip
```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

## Авторы
Прылипко Егор