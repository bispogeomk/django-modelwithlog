# -*- coding: utf-8 *-*
import json

from django.core import serializers
from django.forms.models import model_to_dict
from django.contrib.auth.models import User
# from rest_framework.utils import encoders
# from log_models.midleware.put_request_in_thread_locals import get_current_user


def serializer_generic_models(obj, fields=None):
    array_result = serializers.serialize('json', [obj], ensure_ascii=False, fields=fields)
    return json.loads(array_result[1:-1])


def serializer_user(user):
    data_user = model_to_dict(user)
    return {
        'username': data_user.pop('username'),
        'first_name': data_user.pop('first_name'),
        'last_name': data_user.pop('last_name'),
        'email': data_user.pop('email')
    }
