https://www.psycopg.org/docs/install.html#psycopg-vs-psycopg-binary

psycopg2 was used by the tutor.

psycopg2==2.9.1

## Alembic Guide
pip install alembic
alembic init alembic
alembic revision --autogenerate -m'create user and post tables'
alembic heads
alembic upgrade head

# Heroku
## To install heroku in Ubuntu
```
curl https://cli-assets.heroku.com/install-ubuntu.sh | sh\n
```

To check if heroku is installed successfully or not
```
heroku --version
```

To login to heroku cli
```
heroku login
```

To create heroku dyno
```
heroku create wishtracker
```

To push the app to heroku
```
git push heroku main
```

To see the logs
```
heroku logs --tail
```

To create heroku postgres addons
```
heroku addons:create heroku-postgresql:hobby-dev
```

To restart heroku dynos
```
heroku ps:restart
```

To get apps info
```
heroku apps:info wishtracker
```

To run a command in our heroku instance
```
heroku run "alembic upgrade head" // to run migration
```

To run bash shell
```
heroku run bash
```

# Procfile:
web: uvicorn app.main:app --host=0.0.0.0 --port=${PORT:-5000}