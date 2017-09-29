# -*- coding: utf-8 *-*
import json
from django.core import serializers


def serializer_generic_models(obj, fields=None):
    array_result = serializers.serialize(
        'json', [obj], ensure_ascii=False, fields=fields)
    return json.loads(array_result[1:-1])


def serializer_user(user):
    return {
        'pk': str(user.pk),
        'username': str(user.username),
        'first_name': str(user.first_name),
        'last_name': str(user.last_name),
        'email': str(user.email)
    }


def serializer_request_acess(request):
    if request is None:
        return {'method': "shell"}
    return {
        'method': str(request.method),
        'path_info': str(request.path_info),
        'REMOTE_HOST': str(request.META.get('REMOTE_HOST')),
        'REMOTE_ADDR': str(request.META.get('REMOTE_ADDR')),
        'HTTP_USER_AGENT': str(request.META.get('HTTP_USER_AGENT'))
    }
