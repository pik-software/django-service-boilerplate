# To manually update data via integra use the following Django command

`python manage.py download_integra_updates <app> <model>`

Required arguments:
- `app` Application name from integra config (case insensitive)
- `model` Model name from integra config (case insensitive)

Additional options (`True` or `False`, default `False`):
- `--clean-state` Clean last updated timestamp before update.
- `--ignore-version` Ignore version check. Use this option to force object update.
