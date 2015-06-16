# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from unsubscribe.mail import UnsubscribableEmailMessage
from unsubscribe.utils import get_token_for_user
from unsubscribe.models import SubscriptionList, Unsubscription


class UnsubscribeTest(TestCase):

    def setUp(self):
        self.user = User(
            username='unsubscribe-testuser', email='testuser@sdaf.com')
        self.unsubscribe_list = SubscriptionList(name="test_list")
        self.unsubscribe_list.save()
        self.user.save()

    def test_list_unsubscribe_headers(self):
        msg = UnsubscribableEmailMessage(self.user, self.unsubscribe_list, "Test Message", "Body",
                                         from_email="test@testserver.com", to=["testemail@somewhereelse.com"])
        msg.send()

        from django.core.mail import outbox
        self.assertEquals(len(outbox), 1)
        self.assertTrue('List-Unsubscribe' in outbox[0].extra_headers.keys())
        self.assertEquals(
            outbox[0].extra_headers['List-Unsubscribe'], '<' + msg.unsubscribe_url + '>')

    def test_list_unsubscribe_view(self):
        closure_test = [0]

        def test_callback(sender, list, user, **kwargs):
            self.assertEqual(list, self.unsubscribe_list)
            closure_test[0] = 1

        from unsubscribe.signals import user_unsubscribed
        user_unsubscribed.connect(test_callback)

        from django.test.client import Client
        c = Client()
        url = reverse('unsubscribe_unsubscribe',
                      args=(self.user.pk, self.unsubscribe_list.sid, get_token_for_user(self.user)))
        c.get(url)
        self.assertEqual(Unsubscription.objects.filter(uid=self.user, slist=self.unsubscribe_list).count(), 1)
        self.assertTrue(closure_test[0])

    def test_try_sending_email_after_unsubscribing(self):
        from django.test.client import Client
        c = Client()
        url = reverse('unsubscribe_unsubscribe',
                      args=(self.user.pk, self.unsubscribe_list.sid, get_token_for_user(self.user)))
        c.get(url)
        self.assertEqual(Unsubscription.objects.filter(uid=self.user, slist=self.unsubscribe_list).count(), 1)

        msg = UnsubscribableEmailMessage(self.user, self.unsubscribe_list, "Test Message", "Body",
                                         from_email="test@testserver.com", to=["testemail@somewhereelse.com"])
        msg.send()

        from django.core.mail import outbox
        self.assertEquals(len(outbox), 0)
