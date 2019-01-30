from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from rest_framework.authtoken.models import Token
from rest_framework.authtoken.admin import TokenAdmin

from .admin_site import django_collect_offline_admin
from .models import IncomingTransaction, OutgoingTransaction, Client, Server

# registering TokenAdmin with model Token fails
# if you have not declared 'rest_framework.authtoken' in INSTALLED_APPS.

# unregister to re-register with our admin class
admin.site.unregister(Token)


class TransactionModelAdminMixin:
    def view(self):
        url = reverse(
            "django_collect_offline:render_url",
            kwargs={"model_name": self._meta.object_name.lower(), "pk": str(self.pk)},
        )
        ret = mark_safe(
            '<a href="{url}" class="add-another" id="add_id_report" '
            'onclick="return showAddAnotherPopup(this);"> '
            '<img src="/static/admin/img/icon_addlink.gif" '
            'width="10" height="10" alt="View"/></a>'.format(url=url)
        )
        return ret


@admin.register(Token, site=django_collect_offline_admin)
class MyTokenAdmin(TokenAdmin):
    raw_id_fields = ("user",)
    list_display = ("key", "user", "created")
    fields = ("user",)
    ordering = ("-created",)


@admin.register(IncomingTransaction, site=django_collect_offline_admin)
class IncomingTransactionAdmin(TransactionModelAdminMixin, admin.ModelAdmin):

    ordering = ("-timestamp",)

    list_display = (
        "tx_name",
        "view",
        "producer",
        "is_consumed",
        "is_error",
        "is_ignored",
        "consumer",
        "consumed_datetime",
        "action",
        "tx_pk",
        "timestamp",
        "hostname_modified",
    )

    list_filter = (
        "is_consumed",
        "is_error",
        "is_ignored",
        "consumer",
        "consumed_datetime",
        "producer",
        "action",
        "tx_name",
        "hostname_modified",
    )

    search_fields = ("tx_pk", "tx", "timestamp", "error", "id")


@admin.register(OutgoingTransaction, site=django_collect_offline_admin)
class OutgoingTransactionAdmin(TransactionModelAdminMixin, admin.ModelAdmin):

    ordering = ("-timestamp",)

    list_display = (
        "tx_name",
        "view",
        "producer",
        "is_consumed_server",
        "is_error",
        "consumer",
        "consumed_datetime",
        "action",
        "tx_pk",
        "timestamp",
        "hostname_modified",
    )

    list_filter = (
        "is_error",
        "is_consumed_server",
        "consumer",
        "consumed_datetime",
        "producer",
        "action",
        "tx_name",
        "hostname_modified",
    )

    search_fields = ("tx_pk", "tx", "timestamp", "error", "id")


class HostAdmin(admin.ModelAdmin):

    list_display = (
        "hostname",
        "port",
        "is_active",
        "last_sync_datetime",
        "last_sync_status",
        "comment",
    )

    list_filter = ("is_active", "last_sync_datetime", "last_sync_status")


@admin.register(Client, site=django_collect_offline_admin)
class ClientAdmin(HostAdmin):
    pass


@admin.register(Server, site=django_collect_offline_admin)
class ServerAdmin(HostAdmin):
    pass
