from django.db import models
from jsonfield import JSONField
from log_models.models import ModelWithLog


class GenericModel(ModelWithLog):

    name = models.CharField(max_length=40, blank=True, null=True)
    number = models.PositiveSmallIntegerField()
    file = models.FileField(upload_to='temp/file', blank=True, null=True)
    json = JSONField()
    text = models.TextField()
    boolean = models.BooleanField(default=False)
    real = models.FloatField()
    date = models.DateField(auto_now_add=True)
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (f"GenericModel with name:{self.name}, "
                f"number:{self.number}, "
                f"date_time:{self.date_time}")
