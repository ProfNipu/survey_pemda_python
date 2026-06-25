# Commands - survey_pemda_python

```bash
docker logs -f survey_pemda_python_app
docker exec -it survey_pemda_python_app python manage.py check
```

MySQL (shared):
```bash
docker exec -it mysql-main mysql -uroot -p
```

Redis (shared):
```bash
docker exec -it redis-main redis-cli -a '5406@Pessel!23#' ping
```

