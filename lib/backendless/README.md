Easy way to create standardized api endpoints without code.
1. You should create EntityType model with required OpenAPI Schema (Swagger)
2. Use your API

# Install #

 1. you need to inject routes to your exists rest framework router by `inject_backendless_routes`

```
from lib.backendless.injects import inject_backendless_routes, \
    inject_backendless_schema
from core.api.router import StandardizedRouter

router = StandardizedRouter()
...

inject_backendless_routes(router)  # !!! 1

```

 2. you need to inject schema to your yasg schema generator by `inject_backendless_schema`

```
from lib.backendless.injects import inject_backendless_routes, \
    inject_backendless_schema
from core.api.router import StandardizedRouter

router = StandardizedRouter()
...

inject_backendless_routes(router)  # !!! 1
inject_backendless_schema()        # !!! 2
```

 3. add `'lib.backendless'` to `INSTALLED_APPS`

```
INSTALLES_APPS = [
    ...
    'lib.backendless',
    ...
]
```

 4. run migrations
 5. create new EntityType by admin interface

