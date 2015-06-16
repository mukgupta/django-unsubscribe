from django.contrib import admin
from .models import SubscriptionList, Unsubscription


class SubscriptionListAdmin(admin.ModelAdmin):
    list_display = ('sid', 'name',)


class UnsubscriptionAdmin(admin.ModelAdmin):
    list_display = ('uid', 'slist', 'time',)


admin.site.register(SubscriptionList, SubscriptionListAdmin)
admin.site.register(Unsubscription, UnsubscriptionAdmin)
