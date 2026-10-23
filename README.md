<!--
  Это шаблон README проекта. После создания своего репозитория:
  1. Переименовать репозиторий в backend-<фамилия>-<тема>, например backend-ivanova-library.
  2. Заполнить разделы ниже под свою тему и удалить этот комментарий.
  Задания лаб лежат в папке docs/, начинать с docs/README.md.
-->

# Бронирование столиков

Тема №10: **Бронирование столиков**. Столики ресторана и брони гостей.

| | |
| --- | --- |
| Главная сущность | Столик |
| Связанная сущность (1:N) | Бронь |
| Фишка | Бизнес-правило (409): гостей не больше, чем мест, и брони одного столика не пересекаются. Статистика: число броней по дням недели. |
| Стек | Python, FastApi, база данных |

## Как запустить

```bash
git clone https://github.com/kofanya/backend-kofanova-tables.git
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
fastapi dev
# команды по порядку: от git clone до работающего сервиса
```

Сервис работает на `http://localhost:8000`. Запросы для демонстрации лежат в `requests.http`.

## Эндпоинты

| Метод | Путь | Что делает | Ответ |
| --- | --- | --- | --- |
| GET | `/health` | Проверка, что сервис жив | 200 `{"status":"ok"}` |
| POST | `/api/tables` | Создать столик | 201 и объект с `id`; 400 при ошибке |
| GET | `/api/tables` | Список столиков| 200 |
| GET | `/api/tables/{id}` | Получить одну запись | 200; 404 |
| PATCH | `/api/tables/{id}` | Изменить столик | 200; 400; 404 |
| DELETE | `/api/tables/{id}` | Удалить столик | 204; 404 |

## ER-диаграмма

<!-- С лабы 2. Блок mermaid GitHub рисует сам. -->

```mermaid
erDiagram
    parents ||--o{ children : "имеет"
    parents {
        int id PK
        varchar title
    }
    children {
        int id PK
        int parent_id FK
    }
```

## Интерфейс

<!-- С лабы 4: скриншот, например ![Интерфейс](docs/screenshot.png) -->
