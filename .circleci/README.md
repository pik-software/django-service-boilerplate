# SENTRY #

If you want to config a SENTRY DSN discovery. You need to export the next variables: SENTRY_URL, SENTRY_TEAM, SENTRY_API_KEY

You can define it in your `config.yml` or inside CircleCI Environment Variables.

Example:
```
export SENTRY_URL='https://sentry.pik-software.ru/api/'
export SENTRY_TEAM='nsi'
export SENTRY_API_KEY='qwe23adawd21a'
```

# LETSENCRYPT #

If you want to config Letsencrypt certs. You need to export the next variables: LETSENCRYPT, DOKKU_LETSENCRYPT_EMAIL

You can define it in your `config.yml` or inside CircleCI Environment Variables.

Example:
```
export LETSENCRYPT=1
export LETSENCRYPT_EMAIL=pik-software-team@pik-comfort.ru
```
