import re

from datetime import datetime

from django.core import serializers
from django.apps import apps

from django_crypto_fields.classes import Cryptor

from .. import transaction_producer
from django.core.exceptions import ImproperlyConfigured


class SyncMixin(object):

    aes_mode = 'local'
    use_encryption = True

    def to_json(self):
        """Converts current instance to json, usually encrypted."""
        self.pk_is_uuid()
        use_natural_foreign_key = True if 'natural_key' in dir(self) else False
        json_tx = serializers.serialize(
            "json", [self, ],
            ensure_ascii=False,
            use_natural_foreign_keys=use_natural_foreign_key)
        if self.use_encryption:
            json_tx = Cryptor().aes_encrypt(json_tx, self.aes_mode)
        return json_tx

    def pk_is_uuid(self):
        """Raises an exception if pk of current instance is not a UUID."""
        regex = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z', re.I)
        if not regex.match(str(self.pk)):
            raise ImproperlyConfigured('Sync failed. Expected pk to be a UUID. Got pk=\'{}\''.format(self.pk))

    def action(self, created=None, deleted=None):
        if created is True:
            return 'I'
        elif created is False:
            return 'U'
        elif deleted is True:
            return 'D'
        else:
            return None

    def to_outgoing(self, action, using=None):
        """Saves the current instance to the OutgoingTransaction model."""
        OutgoingTransaction = apps.get_model('edc_sync.OutgoingTransaction')
        return OutgoingTransaction.objects.using(using).create(
            tx_name=self._meta.object_name,
            tx_pk=self.id,
            tx=self.to_json(),
            timestamp=datetime.today().strftime('%Y%m%d%H%M%S%f'),
            producer=transaction_producer,
            action=action)

    def to_inspector(self):
        pass
