# -*- coding: utf-8 *-*
from django.core.exceptions import PermissionDenied
from django.contrib.admin.utils import quote
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import NoReverseMatch, reverse
from django.db import models
from django.forms import model_to_dict
from django.utils import timezone
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField
from django.db import transaction
from log_models.serializer_model import serializer_user
from log_models.serializer_model import serializer_request_acess
from log_models.serializer_model import serializer_generic_models
from threadlocals.threadlocals import get_current_user
from threadlocals.threadlocals import get_current_request


ACTION_ADDITION = 1
ACTION_CHANGE = 2
ACTION_DELETION = 3


class ManagerWithLog(models.Manager):
    use_in_migrations = True

    def create(self, *args, **kwargs):
        self.__action_flag__ = ACTION_ADDITION
        return super(ManagerWithLog, self).create(*args, **kwargs)


class ModelWithLog(models.Model):

    __old__ = None
    __action_flag__ = None

    flag_msg = {
        ACTION_ADDITION: _('added'),
        ACTION_CHANGE: _('changed'),
        ACTION_DELETION: _('deleted')
    }

    class Meta:
        abstract = True

    def __modifications__(self):
        if self.__action_flag__ == ACTION_CHANGE:
            self.__old__ = self.__class__.objects.filter(pk=self.pk).last()
            # Becouse the record may have been deleted.
            if self.__old__:
                serial_old = model_to_dict(self.__old__)
                serial_new = model_to_dict(self)
                keys = []
                for key in serial_new.keys():
                    if hasattr(serial_old[key], 'get_internal_type'):
                        mytype = serial_new[key].get_internal_type()
                        if mytype == 'FileField':
                            if str(serial_old[key]) != str(serial_new[key]):
                                keys.append(key)
                        else:
                            if serial_old[key] != serial_new[key]:
                                keys.append(key)
                    else:
                        if serial_old[key] != serial_new[key]:
                            keys.append(key)
                return serializer_generic_models(self, keys)
        return serializer_generic_models(self)

    def __content_type__(self):
        return ContentType.objects.get_for_model(
            model=self._meta.model,
            for_concrete_model=True)

    @transaction.atomic
    def save_with_log(self, user=None, action_flag=None,
                      change_message='', *args, **kwargs):
        content_type = self.__content_type__()
        if self.__action_flag__ == ACTION_ADDITION:
            saved = super(ModelWithLog, self).save(*args, **kwargs)
            modifications = self.__modifications__()
            change_message = change_message or self.make_log_message()
        else:
            modifications = self.__modifications__()
            change_message = change_message or self.make_log_message()
            saved = super(ModelWithLog, self).save(*args, **kwargs)
        RegisterLog.objects.log_action(
            content_type=content_type,
            object_pk=self.pk,
            object_repr=str(self),
            action_flag=self.__action_flag__,
            modifications=modifications,
            change_message=change_message)
        return saved

    def make_log_message(self):
        self.full_clean()
        flag_msg = self.flag_msg.get(self.__action_flag__)
        if self.__old__:
            msg = '{0} "{1}" to "{2}"'.format(
                flag_msg, repr(self.__old__), repr(self))
        else:
            msg = '{0} "{1}"'.format(flag_msg, repr(self))
        return msg

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.__action_flag__ = ACTION_ADDITION
        else:
            self.__action_flag__ = ACTION_CHANGE
        action_flag = kwargs.pop('action_flag', None)
        change_message = kwargs.pop('change_message', '')
        self.save_with_log(action_flag, change_message, *args, **kwargs)

    @transaction.atomic
    def delete(self, *args, **kwargs):
        self.__action_flag__ = ACTION_DELETION
        RegisterLog.objects.log_action(
            content_type=self.__content_type__(),
            object_pk=self.pk,
            object_repr=str(self),
            action_flag=ACTION_DELETION,
            modifications=serializer_generic_models(self),
            change_message=self.make_log_message())
        super(ModelWithLog, self).delete(*args, **kwargs)

    objects = ManagerWithLog()


class RegisterLogManager(models.Manager):

    use_in_migrations = True

    def log_action(self, content_type, object_pk, object_repr, action_flag,
                   modifications, user=None, change_message=''):
        if user is None:
            user = get_current_user()
        # the current user is None on shell
        if user is None:
            data_user = {
                'pk': None,
                'username': None,
                'full_name': None,
                'email': None
            }
        elif user.is_anonymous():
            data_user = {
                'pk': None,
                'username': _('Anonymous'),
                'full_name': _('Anonymous'),
                'email': ''
            }
        else:
            data_user = serializer_user(user)
        data_acess = serializer_request_acess(get_current_request())
        self.model.objects.create(
            data_user={'user': data_user, 'acess': data_acess},
            content_type=content_type,
            object_pk=smart_text(object_pk),
            object_repr=str(object_repr)[:200],
            modifications=modifications,
            action_flag=action_flag,
            change_message=change_message
        )


class RegisterLog(models.Model):
    action_time = models.DateTimeField(
        _('action time'),
        default=timezone.now,
        editable=False,
    )
    content_type = models.ForeignKey(
        ContentType,
        models.SET_NULL,
        verbose_name=_('content type'),
        blank=True, null=True,
    )
    data_user = JSONField()  # dados do usuario logado
    modifications = JSONField()  # chave e valor só dos campos modificados
    object_pk = models.TextField(_('object id'), blank=True, null=True)
    object_repr = models.CharField(_('object repr'), max_length=200)
    action_flag = models.PositiveSmallIntegerField(_('action flag'))
    change_message = models.TextField(_('change message'), blank=True)

    objects = RegisterLogManager()

    class Meta:
        verbose_name = _('log entry')
        verbose_name_plural = _('log entries')
        db_table = 'log_monitored_models'
        ordering = ('-action_time',)

    def __repr__(self):
        return smart_text(self.action_time)

    def __str__(self):
        return self.change_message

    def is_addition(self):
        return self.action_flag == ACTION_ADDITION

    def is_change(self):
        return self.action_flag == ACTION_CHANGE

    def is_deletion(self):
        return self.action_flag == ACTION_DELETION

    def get_edited_object(self):
        "Returns the edited object represented by this log entry"
        return self.content_type.get_object_for_this_type(pk=self.object_id)

    def get_admin_url(self):
        """
        Returns the admin URL to edit the object represented by this log entry.
        """
        if self.content_type and self.object_id:
            url_name = 'admin:%s_%s_change' % (
                self.content_type.app_label, self.content_type.model)
            try:
                return reverse(url_name, args=(quote(self.object_id),))
            except NoReverseMatch:
                pass
        return None

    def save(self, *args, **kwargs):
        if self.pk is None:
            super(RegisterLog, self).save(*args, **kwargs)
        else:
            raise PermissionDenied("You can not change the registry log.")

    def delete(self, *args, **kwargs):
        raise PermissionDenied("You can not erase the registry log.")
