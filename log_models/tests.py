# from django.db import models
from jsonfield import JSONField
from log_models.models import ModelWithLog
from django.test import TestCase
from model_mommy import mommy
from django.db import models
# from model_mommy.recipe import Recipe, foreign_key
from log_models.models import RegisterLog
# from log_models.serializer_model import serializer_generic_models
# from .models import GenericModel
from django.core.management import call_command
from log_models.model_test.models import GenericModel


# class GenericModel(ModelWithLog):

#     name = models.CharField(max_length=40, blank=True, null=True)
#     number = models.PositiveSmallIntegerField()
#     file = models.FileField(upload_to='temp/file', blank=True, null=True)
#     json = JSONField()
#     text = models.TextField()
#     boolean = models.BooleanField(default=False)
#     real = models.FloatField()
#     date = models.DateField(auto_now_add=True)
#     date_time = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return (f"GenericModel with name:{self.name}, "
#                 f"number:{self.number}, "
#                 f"date_time:{self.date_time}")


class LogTestModel(TestCase):
    """
    Class to test the model with log
    """

    def setUp(self):
        """
        Set up all the tests
        """
        # create
        # self.test0 = GenericModel.objects.create(**{
        #     'name': 'ThunderCats',
        #     'number': 5,
        #     'real': 25,
        #     'text':'kaghslkahl'
        # })
        # self.test1 = mommy.make(GenericModel, **{'name': 'Lion'})
        # self.test2 = mommy.make(GenericModel, **{'name': 'Tiger'})
        # self.test3 = mommy.make(GenericModel, **{'name': 'Panthro'})

        # # change
        # self.test2.name = "Snarf"
        # self.test2.save()

        # # deletion
        # self.test3.delete()

    def test_can_create_with_log(self):
        data = {
            'name': 'ThunderCats',
            'number': 5,
            'real': 25,
            'text': 'kaghslkahl'
        }
        obj_created = GenericModel.objects.create(**data)
        register = RegisterLog.objects.filter(object_pk=obj_created.pk).last()
        for key in data:
            self.assertEqual(register.modifications['fields'][key], data[key])

    def test_can_save_new_data_with_log(self):
        obj_created = mommy.make(GenericModel, **{'name': 'Lion'})
        r = RegisterLog.objects.filter(object_pk=obj_created.pk).last()
        self.assertTrue(r.action_flag, 1)
        for field in GenericModel._meta.get_fields():
            if field.name != 'id':
                if field.get_internal_type() in ('FileField', 'DateField'):
                    self.assertEqual(
                        r.modifications['fields'][field.name],
                        str(getattr(obj_created, field.name)))
                elif field.get_internal_type() == 'DateTimeField':
                    self.assertEqual(
                        r.modifications['fields'][field.name].replace('T',
                                                                      ' '),
                        str(getattr(obj_created, field.name))[0:-3])
                else:
                    self.assertEqual(
                        r.modifications['fields'][field.name],
                        getattr(obj_created, field.name))

    def test_can_change_data_with_log(self):
        obj_created = mommy.make(GenericModel, **{'name': 'Lion'})
        obj_created.name = 'Panthro'
        obj_created.save()
        nreg = RegisterLog.objects.filter(object_pk=obj_created.pk).count()
        self.assertEqual(nreg, 2)
        r = RegisterLog.objects.filter(object_pk=obj_created.pk).last()
        self.assertTrue(r.action_flag, 2)
        self.assertTrue('name' in r.modifications['fields'].keys())
        print(repr(r))
        self.assertEqual(r.modifications['fields'].get('name'), 'Panthro')

    def test_can_delete_data_with_log(self):
        obj_created = mommy.make(GenericModel, **{'name': 'Tiger'})
        # obj_created.save()
        obj_pk = obj_created.pk
        obj_created.delete()
        nreg = RegisterLog.objects.filter(object_pk=obj_pk).count()
        self.assertEqual(nreg, 2)
        r = RegisterLog.objects.filter(object_pk=obj_created.pk).last()
        self.assertTrue(r.action_flag, 3)