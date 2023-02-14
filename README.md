# Дипломная работа
[![Build Status](https://scrutinizer-ci.com/g/altec3/Thesis_project/badges/build.png?b=main)](https://scrutinizer-ci.com/g/altec3/Thesis_project/build-status/main)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/altec3/Thesis_project/badges/quality-score.png?b=main)](https://scrutinizer-ci.com/g/altec3/Thesis_project/?branch=main)
### Итоговая работа по курсу Python-разработчик. 
*Стек: python:3.10, Django:4.1.4, Postgres:12.4*
####
### Описание работы

---

`Цель работы`  
Приложение для планирования целей.  

`Предварительные требования к работе`

1. Вход/регистрация/аутентификация через вк.
2. Создание целей.
   * Выбор временного интервала цели с отображением кол-ва дней до завершения цели.
   * Выбор категории цели (личные, работа, развитие, спорт и т. п.) с возможностью добавлять/удалять/обновлять категории.
   * Выбор приоритета цели (статичный список minor, major, critical и т. п.).
   * Выбор статуса выполнения цели (в работе, выполнен, просрочен, в архиве).
3. Изменение целей.
   * Изменение описания цели.
   * Изменение статуса.
   * Дать возможность менять приоритет и категорию у цели.
4. Удаление цели.
   * При удалении цель меняет статус на «в архиве».
5. Поиск по названию цели.
6. Фильтрация по статусу, категории, приоритету, году.
7. Комментарии к целям.
8. Все перечисленный функции должны быть реализованы в мобильном приложении.
####
## Запуск проекта

---
> Проверить работоспособность проекта можно по адресу [https://lesnikov-a.ga/](https://lesnikov-a.ga/).  
> В проекте реализован простой Telegram бот, который позволяет просмотреть созданные пользователем цели
> и создать новую цель.  
> Для проверки данного функционала в приложении Telegram необходимо начать чат с ботом по имени
> [todolist_lesnikov_bot](https://t.me/todolist_lesnikov_bot)

### Локальный сервер:  

Запуск проекта на локальном сервере проще всего производить с помощью платформы Docker.  
`Требования:`  
* [обязательно] установленная платформа [Docker](https://docs.docker.com/get-docker/) с
[Docker Compose](https://docs.docker.com/compose/install/);
* [желательно] созданное [приложение](https://dev.vk.com/) в соц.сети ВКОНТАКТЕ - для реализации авторизации через данную соц.сеть;
* [желательно] созданный [бот](https://telegram.me/BotFather) в приложении Telegram - для подключения бота к проекту.

1. Произвести настройку переменных окружения - в папке проекта разметить файл .env (см. файл **.env.example**):

2. Выполнить команду:
```python
docker compose up --build -d
```
Фронтенд-часть будет доступна по адресу `localhost:80` и будет ваимодействовать с запущенным бэкенд-сервером.  

3. При необходимости, создать администратора для админ-панели

```python
docker compose exec api python manage.py createsuperuser
```
### Staging сервер:

`Требования:`
* [обязательно] установленная на сервере платформа [Docker](https://docs.docker.com/get-docker/) с
[Docker Compose](https://docs.docker.com/compose/install/).
* [желательно] созданное [приложение](https://dev.vk.com/) в соц.сети ВКОНТАКТЕ - для реализации авторизации через данную соц.сеть;
* [желательно] созданный [бот](https://telegram.me/BotFather) в приложении Telegram - для подключения бота к проекту.

1. Произвести настройку переменных окружения - в папке проекта на сервере разметить файл .env (см. файл **.env.example**):

2. Отредактировать файл **docker-compose.yaml** в папке `\deploy` - изменить
значения параметров в секции **environments** сервиса **front**:  
SERVER_NAME - доменное имя для сертификата. Указать URL-адрес, по которому будет доступен проект;  
CERTBOT_EMAIL - email администратора веб-сервера. Служит для получения уведомлений о домене или регистрации.
Изменить по желанию.
```dockerfile
front:
    image: altec3/thesis-front:https-latest
    (...)
    environment:
      - SERVER_NAME=your_domain.com
      - CERTBOT_EMAIL=admin@mail.ru
    (...)
```
3. Скопировать файл **docker-compose.yaml** из папки `\deploy` на сервер (в папку проекта).
4. В папке проекта на сервере выполнить команду:
```python
docker compose up --build -d
```
Проект будет доступен по адресу SERVER_NAME:80.

### Запуск тестов:

1. Запустить контейнер с PostgreSQL:
```python
docker compose up db -d
```
2. Перейти в папку `\todolist`:
```python
cd todolist
```
3. Выполнить команду:
```python
pytest
```
