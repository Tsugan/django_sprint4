# Веб-приложение для публикации постов «Blogicum»

## _Описание проекта:_

#### **_*Blogicum*_ - сервис для публикации постов и комментариев к ним.**


### _Технологии:_

* Python 3.9
* Django
* SQLite
* HTML
* Pillow

### _Возможности проекта:_
* регистрация пользователей
* возможность добавления/редактирования/удаления своих публикаций
* просмотр публикаций других пользователей
* возможность добавления комментариев к публикациям
* добавление к публикациям фото
* просмотр публикаций в разрезе категорий и локаций 

### _Запуск проекта:_
- Склонировать репозиторий:
```
git clone git@github.com:FedorovaDasha/django_sprint4.git
```
- Создать и активировать виртуальное окружение:
```
python3 -m venv venv
source venv/bin/activate
```
- Обновить pip:
```
python3 -m pip install --upgrade pip
```
- Установить библиотеки:
```
pip install -r requirements.txt
```
- Выполнить миграции:
```
python3 blogicum/manage.py migrate
```
- Загрузить фикстуры DB:
```
python3 blogicum/manage.py loaddata db.json
```
- Создать суперпользователя:
```
python3 blogicum/manage.py createsuperuser
```
- Запустить сервер django:
```
python3 blogicum/manage.py runserver
```
##
### _Демо-версия проекта:_
[Blogicum](https://fedorovadasha.pythonanywhere.com/)

##
Над проектом работала [FedorovaDasha](https://github.com/FedorovaDasha).

##
