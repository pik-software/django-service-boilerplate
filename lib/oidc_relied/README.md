# Реализация ПИК-Комфорт OpenID Connect

Данная библиотека реализует механизм авторизации пользователей сервисов
ПИК-Комфорт по протоколу [OpenID Connect](http://openid.net/developers/specs/), 
включая реализацию протокола 
[Back-channel logout](http://openid.net/specs/openid-connect-backchannel-1_0.html). 
В данный момент поддерживаются 
[два механизма](http://openid.net/specs/oauth-v2-multiple-response-types-1_0.html):

- Code (Authorization Code Flow) для авторизации классических приложений,
- id_token token (Implicit Flow) для авторизации SPA.


## Предварительная подготовка

Обратиться к подразделению, обслуживающему auth.pik-software.ru для
прохождения процесса регистрации и получения `client_id` и `secret`
регистрируемого сервиса.


## Порядок подключения

1 Скопировать `lib/oidc_relied`

2 В settings.py

Для удобства интеграции предусмотрено два способа подключения необходимых настроек:

- `set_oidc_settings()`,
- ручная настройка.

2.1 set_oidc_settings

В конец settings.py нужно добавить:

```python

from lib.oidc_relied.settings import set_oidc_settings
set_oidc_settings(globals())

```

2.2 Ручная настройка

В случае необходимости тонкой настройки OIDC потребуется применение настроек 
врунчную. Описанная ниже последовательность приведет settings к тому же 
состоянию, что и вызов `set_oidc_settings`.

2.2.1 Подключить приложение `social_django` в `INSTALLED_APPS`

```patch
    INSTALLED_APPS = [
         ...
+        'social_django',
    ]
```

2.2.2  Подключить `MIDDLEWARE` `OIDCExceptionMiddleware`, для правильного вывода
ошибок

```patch
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
+    'lib.oidc_relied.middleware.OIDCExceptionMiddleware',
    ...
]
```

2.2.3 Импортировать настройки:

```patch
...
+ # OPENID Relied conf
+ from lib.oidc_relied.settings import *
...
```

2.2.4 Подключить `PIKOpenIdConnectAuth` в `AUTHENTICATION_BACKENDS`


```
AUTHENTICATION_BACKENDS = [
    ...
+    'lib.oidc_relied.backends.PIKOpenIdConnectAuth',  # OIDC relied backend
]
```

2.2.5 Добавить `SocialAuthentication` `REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES`:

```patch
REST_FRAMEWORK = {
    ...
    DEFAULT_AUTHENTICATION_CLASSES: {
        ...
+        'rest_framework_social_oauth2.authentication.SocialAuthentication',
    }
    ...
}
```

3 Указать OIDC_PIK_ENDPOINT, OIDC_PIK_CLIENT_ID, OIDC_PIK_CLIENT_SECRET в
настройках или ENV переменных.

```python
OIDC_PIK_ENDPOINT = 'http://auth.pik-software.ru/openid'
OIDC_PIK_CLIENT_ID = '42'
OIDC_PIK_CLIENT_SECRET = 'SOMESECRET'
```

```bash
dokku config:set django-service-boilerplate \
OIDC_PIK_ENDPOINT = http://auth.pik-software.ru/openid \
OIDC_PIK_CLIENT_ID = 42 \
OIDC_PIK_CLIENT_SECRET = SOMESECRET
```
