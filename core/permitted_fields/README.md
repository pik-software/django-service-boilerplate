Permitted Fields library provides per field permissions limitation.

permitted_fields - is Model, ModelAdmin or Serializer defined property. It 
defines permissions which are required for field edition.

Example:

```python
class Comment(Model):
	permitted_fields = {
		"comments.change_comment": ['user', 'text'],
		"comments.change_user_comment": ['user']
	}
	
	user = ForeignKey(User)
	text = TextField()
```

This construction defines `text` field `change_contact` permission requirement,
and `change_comment`+`change_user_comment` permissions for `user` field.

It is possible to use templates in permission names:

```python
class Comment(Model):
	permitted_fields = {
		"{app_label}.change_{model_name}": ['user', 'text'],
		"{app_label}.change_user_{model_name}": ['user']
	}

	user = ForeignKey(User)
	text = TextField()

```

These restrictions may be defined for `Model` as for 
`SecuredVersionedModelAdmin` and `StandardizedModelSerializer` if default model
behaviour overriding needed.

```python
@admin.register(Comment)
class CommentAdmin(SecuredVersionedModelAdmin):
	permitted_fields = {
		"{app_label}.change_{model_name}": ['user', 'text'],
		"{app_label}.change_user_{model_name}": ['user']
	}

```

```python
class CommentSerializer(StandardizedModelSerializer):
    permitted_fields = {
        "{app_label}.change_{model_name}": ['user', 'text'],
        "{app_label}.change_user_{model_name}": ['user']
    }
    class Meta:
        model = Comment
        read_only_fields = (
            '_uid', '_type', '_version', 'user',
        )
        fields = (
            '_uid', '_type', '_version', 'user', 'text',
        )

```
