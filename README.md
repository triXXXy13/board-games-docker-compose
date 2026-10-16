# Настольные игры клуба — вариант №30

Многокомпонентное приложение для поиска настольных игр по числу игроков и длительности партии, а также ведения коллекции настольного клуба.

## Архитектура

- **frontend** — HTML/CSS/JavaScript, Nginx, порт `8080` на компьютере.
- **backend** — REST API на Python/Flask; соединяет интерфейс, PostgreSQL и сервис каталога.
- **db** — PostgreSQL, начальные записи загружаются из `db/init.sql`, данные сохраняются в volume.
- **web-service** — отдельный микросервис-эмулятор каталога настольных игр, фильтрующий игры по числу игроков и времени партии.

## Запуск

Требуется установленный Docker Desktop (или Docker Engine с Compose).

```bash
docker compose up --build -d
```

Откройте http://localhost:8080

Остановка:

```bash
docker compose down
```

Остановка с удалением сохранённых данных БД (осторожно: удалит коллекцию):

```bash
docker compose down -v
```

## Функции

1. **Найти игры** — обращается через backend к отдельному web-service и показывает игры, подходящие по числу игроков и максимальному времени партии.
2. **Сохранить в коллекцию** — добавляет игру в PostgreSQL.
3. Просмотр коллекции и удаление записей из неё.

REST API:
- `GET /api/games?players=4&max_minutes=90` — поиск игр во внешнем сервисе.
- `GET /api/collection` — список игр клуба из БД.
- `POST /api/collection` — сохранение игры; JSON содержит `id`, `title`, `players_min`, `players_max`, `duration_minutes`, `genre`, `description`.
- `DELETE /api/collection/<id>` — удаление игры из коллекции.
- `GET /health` — проверка backend.

## Проверка контейнеров

```bash
docker compose ps
docker compose logs -f backend
docker compose logs -f web-service
```

Все четыре сервиса запускаются в общей сети Docker Compose. База данных и backend имеют healthcheck; frontend ждёт готовности backend, а backend — готовности БД и web-service. Пароль БД в учебном проекте демонстрационный; для реального развертывания используйте `.env` и секреты.
