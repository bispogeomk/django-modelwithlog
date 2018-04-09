from django.test import TestCase
from model_mommy import mommy
from log_models.models import RegisterLog
from log_models.models import ACTION_ADDITION
from log_models.models import ACTION_CHANGE
from log_models.models import ACTION_DELETION
from log_models.model_test.models import GenericModel
from threadlocals.middleware import ThreadLocalMiddleware
from threadlocals.threadlocals import get_current_user
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from jsonfield import JSONField
import json
from mock import Mock


class LogTestModel(TestCase):
    """
    Class to test the model with log
    """

    def setUp(self):
        """
        Set up all the tests
        """

    def test_can_create_with_log(self):
        data = {
            'name': 'ThunderCats',
            'number': 5,
            'real': 25,
            'text': 'kaghslkahl',
            'json': {'1': 'bispo', '3': 'teste'}
        }
        obj_created = GenericModel.objects.create(**data)
        register = RegisterLog.objects.filter(object_pk=obj_created.pk).last()
        for key in data:
            if key == 'json':
                self.assertEqual(json.loads(
                    register.modifications['fields'][key]), data[key])
            else:
                self.assertEqual(
                    register.modifications['fields'][key], data[key])

    def test_can_save_new_data_with_log(self):
        obj_created = mommy.make(GenericModel, **{'name': 'Lion'})
        reg = RegisterLog.objects.filter(object_pk=obj_created.pk,
                                         action_flag=ACTION_ADDITION).last()
        self.assertTrue(reg.action_flag, 1)
        for field in GenericModel._meta.get_fields():
            if field.name != 'id':
                if field.get_internal_type() in ('FileField', 'DateField'):
                    self.assertEqual(
                        reg.modifications['fields'][field.name],
                        str(getattr(obj_created, field.name)))
                elif field.get_internal_type() == 'DateTimeField':
                    self.assertEqual(
                        reg.modifications['fields'][field.name].replace('T',
                                                                        ' '),
                        str(getattr(obj_created, field.name))[0:-3])
                elif isinstance(field, JSONField):
                    self.assertEqual(
                        json.loads(reg.modifications['fields'][field.name]),
                        getattr(obj_created, field.name))
                else:
                    self.assertEqual(
                        reg.modifications['fields'][field.name],
                        getattr(obj_created, field.name))

    def test_can_change_data_with_log(self):
        obj_created = mommy.make(GenericModel, **{'name': 'Lion'})
        obj_created.name = 'Panthro'
        obj_created.save()
        nreg = RegisterLog.objects.filter(object_pk=obj_created.pk).count()
        self.assertEqual(nreg, 2)
        reg = RegisterLog.objects.filter(object_pk=obj_created.pk,
                                         action_flag=ACTION_CHANGE).last()
        self.assertTrue(reg.action_flag, 2)
        self.assertTrue('name' in reg.modifications['fields'].keys())
        self.assertEqual(reg.modifications['fields'].get('name'), 'Panthro')

    def test_can_delete_data_with_log(self):
        obj_created = mommy.make(GenericModel, **{'name': 'Tiger'})
        obj_pk = obj_created.pk
        obj_created.delete()
        nreg = RegisterLog.objects.filter(object_pk=obj_pk).count()
        self.assertEqual(nreg, 2)
        reg = RegisterLog.objects.filter(object_pk=obj_pk,
                                         action_flag=ACTION_DELETION).last()
        self.assertTrue(reg.action_flag, 3)


class LogTestModelRequest(TestCase):
    """
    Class to test the model with log
    """

    def setUp(self):
        self.tm = ThreadLocalMiddleware()
        self.request = Mock()
        self.request.method = "POST"
        self.request.path_info = "/test"
        self.request.META = {
            'REMOTE_HOST': 'Mock remote host',
            'REMOTE_ADDR': '0.0.0.0',
            'HTTP_USER_AGENT': 'Mock user agent',
        }
        self.request.session = {}
        self.data_user = {
            'username': 'UserTest',
            'first_name': 'test1',
            'last_name': 'test2',
            'email': 'test@mail.com',
            'password': '1234'
        }
        self.user = User.objects.create(**self.data_user)

    def login_user(self):
        self.request.user = self.user
        self.assertEqual(self.tm.process_request(self.request), None)

    def login_user_anonymous(self):
        self.request.user = AnonymousUser()
        self.assertEqual(self.tm.process_request(self.request), None)

    def test_process_request_with_user(self):
        self.login_user()
        user = get_current_user()
        self.assertFalse(user.is_anonymous())
        self.assertEqual(user.username, self.data_user.get('username'))
        self.assertEqual(user.email, self.data_user.get('email'))

    def test_process_request_without_user(self):
        self.login_user_anonymous()
        user = get_current_user()
        self.assertTrue(user.is_anonymous())

    def test_log_user_in_register_on_create(self):
        self.login_user()
        obj_created = mommy.make(GenericModel, **{'name': 'Cheetara'})
        reg = RegisterLog.objects.filter(object_pk=obj_created.pk,
                                         action_flag=ACTION_ADDITION).last()
        self.assertEqual(reg.data_user.get('user').get('first_name'),
                         self.data_user.get('first_name'))

        self.assertEqual(reg.data_user.get('acess'), {
            'method': 'POST',
            'path_info': '/test',
            'REMOTE_HOST': 'Mock remote host',
            'REMOTE_ADDR': '0.0.0.0',
            'HTTP_USER_AGENT': 'Mock user agent'})

    def test_log_user_in_register_on_save(self):
        self.login_user()
        obj_created = mommy.make(GenericModel, **{'name': 'Cheetara 2'})
        obj_created.name = 'Cheetara 3'
        obj_created.save()
        reg = RegisterLog.objects.filter(object_pk=obj_created.pk,
                                         action_flag=ACTION_CHANGE).last()
        self.assertEqual(reg.data_user.get('user').get('first_name'),
                         self.data_user.get('first_name'))

        self.assertEqual(reg.data_user.get('acess'), {
                         'method': 'POST',
                         'path_info': '/test',
                         'REMOTE_HOST': 'Mock remote host',
                         'REMOTE_ADDR': '0.0.0.0',
                         'HTTP_USER_AGENT': 'Mock user agent'})

    def test_log_user_in_register_on_delete(self):
        self.login_user()
        # user = get_current_user()
        obj_created = mommy.make(GenericModel, **{'name': 'Cheetara 3'})
        obj_pk = obj_created.pk
        obj_created.delete()
        reg = RegisterLog.objects.filter(object_pk=obj_pk,
                                         action_flag=ACTION_DELETION).last()
        self.assertEqual(reg.data_user.get('user').get('first_name'),
                         self.data_user.get('first_name'))

        self.assertEqual(reg.data_user.get('acess'),
                         {'method': 'POST',
                          'path_info': '/test',
                          'REMOTE_HOST': 'Mock remote host',
                          'REMOTE_ADDR': '0.0.0.0',
                          'HTTP_USER_AGENT': 'Mock user agent'})
