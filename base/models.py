from django.db import models

# Create your models here.
from django.urls import reverse
from django.contrib.admin.utils import quote
from django.db import models
from django.urls import reverse, NoReverseMatch


class BaseManager(models.Manager):
    pass


class BaseModel(models.Model):
    FSM_FIELDS = ()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    @classmethod
    def full_path(cls):
        module = cls.__module__
        return module + '.' + cls.__name__

    def get_admin_url(self):
        """Returns the admin URL to edit this object
        """
        url_name = 'admin:{}_{}_change'.format(self._meta.app_label,
                                               self._meta.model_name)
        try:
            return reverse(url_name, args=(quote(self.pk),))
        except NoReverseMatch:
            pass

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, validate_unique=True):
        """Run full_clean on save"""
        self.full_clean(exclude=self.FSM_FIELDS, validate_unique=validate_unique)
        super().save(force_insert=force_insert, force_update=force_update,
                     using=using, update_fields=update_fields)

    class Meta:
        abstract = True


