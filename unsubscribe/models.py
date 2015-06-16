from django.db import models
from django.contrib.auth.models import User
import uuid
from .signals import user_unsubscribed
from django.dispatch.dispatcher import receiver


class SubscriptionList(models.Model):
    sid = models.CharField(
        default=lambda: uuid.uuid4().hex[:8], unique=True, editable=False, max_length=8)
    name = models.CharField(max_length=50, blank=False, null=False)

    def __unicode__(self):
        return self.name


class Unsubscription(models.Model):
    uid = models.ForeignKey(
        User, related_name='unsubscriptions', blank=False, null=False)
    slist = models.ForeignKey(SubscriptionList, verbose_name="Subscription List",
                              related_name='unsubscriptions', blank=False, null=False)
    time = models.DateTimeField(
        verbose_name="Unsubsription Time", auto_now_add=True, blank=False, null=False)

    @classmethod
    @receiver(user_unsubscribed)
    def unsubscribe_user_from_list(sender, list, user, **kwargs):
        Unsubscription.objects.get_or_create(uid=user, slist=list)
