# DigiClips Docker Lab

A small 3-container version of my capstone data layer (DigiClips, ASU CSE 485).

| Container | What it does |
|---|---|
| `db` | MySQL 8. Loads my schema + seed data the first time it starts |
| `importer` | Python. Loads sample closed-caption lines, marks duplicate overlap lines, then stops |
| `api` | FastAPI. REST API to search the captions. Docs at http://localhost:8000/docs |

## Run it

You need Docker Desktop.

```bash
cp .env.example .env          # then change the passwords in .env
docker compose up --build
```

Then open http://localhost:8000/docs and try:

- `GET /outlets`
- `GET /outlets/1/chunks`
- `GET /mentions?keyword=broncos` → 1 result (duplicate overlap line hidden)
- `GET /mentions?keyword=broncos&include_overlap=true` → 2 results
- `GET /outlets/99/chunks` → 404

## Useful commands

```bash
docker compose ps                    # see the containers
docker compose logs importer         # see "import done: 10 lines added"
docker compose run --rm importer     # run importer again -> 0 added, 10 skipped
docker compose down                  # stop (data is kept in the volume)
docker compose down -v               # stop AND delete the data (init scripts run again next time)
docker exec -it digiclips-docker-lab-db-1 mysql -udigi -p digiclips
```

MySQL Workbench: host `127.0.0.1`, port **3307**, user/password from `.env`.

## Screenshot checklist for the report

1. `docker compose ps` with all 3 services
2. `docker compose logs importer` showing the import result
3. Swagger page at `/docs`
4. `/mentions?keyword=broncos` with and without `include_overlap`
5. MySQL Workbench (port 3307) showing the tables
6. After `docker compose down` and `up` again → data is still there
