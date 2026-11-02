# Разработка

Python 3.10+ нужен только для необязательной офлайн CLI. Установка пакета и сторонние зависимости не требуются. В Windows используйте `py -3`, в Ubuntu — `python3`.

Из корня проекта:

```console
python -m unittest discover -s tests -v
python -m compileall -q src
python src/flow_parity.py validate examples/demo.json --json
python src/flow_parity.py gate examples/demo.json --json
```

Сохраняйте небольшие понятные локальные коммиты Git. GitHub Actions настроен для Windows и Ubuntu с Python 3.10/3.13, минимальными разрешениями и закреплёнными SHA зависимостей. Hosted CI не считается проверенным до публикации репозитория и успешного завершения реального run.

Обновляйте английскую и русскую документацию вместе. Непроверенную активацию Codex и платформы помечайте `NOT_VERIFIED`. Не добавляйте сервер, телеметрию, CI-публикацию или зависимости без подтверждённой необходимости.
