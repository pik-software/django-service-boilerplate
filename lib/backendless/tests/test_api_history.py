# TODO(pahaz): create it!

# def test_api_object_history(api_user, api_client):
#     obj = EntityFactory.create()
#     hist_obj = obj.history.last()
#     add_permissions(api_user, Entity.history.model, 'view')
#     res = api_client.get(
#         f'/api/v1/{obj.type.slug}-list/history/?_uid={obj.uid}')
#     assert res.status_code == status.HTTP_200_OK
#     _assert_api_object_list(res, [{
#         '_uid': str(obj.uid),
#         '_type': 'historical' + 'contact',
#         '_version': obj.version,
#         'created': obj.created.isoformat(),
#         'updated': obj.updated.isoformat(),
#         'foo': 1,
#         'bar': obj.value['bar'],
#         'history_change_reason': None,
#         'history_date': hist_obj.history_date.isoformat(),
#         'history_id': hist_obj.history_id,
#         'history_type': '+',
#         'history_user_id': None,
#         'history_user': None,
#     }])
