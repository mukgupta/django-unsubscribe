# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

from .utils import get_token_for_user
from .models import Unsubscription


class UnsubscribableEmailMessage(EmailMultiAlternatives):

    """
    A simple wrapper around EmailMultiAlternatives that requires a User
    object and appends a `List-Unsubscribe` header to the email message
    """

    def __init__(self, user, slist, subject='', body='', from_email=None, to=None,
                 bcc=None, connection=None, attachments=None,
                 headers=None, alternatives=None):
        self.user = user
        self.list = slist
        unsub_headers = headers or {}
        unsub_url = reverse('unsubscribe_unsubscribe',
                            args=[user.pk, slist.sid, get_token_for_user(user)])

        # TODO fix scheme not to be hard coded.
        protocol = 'http'
        site_url = '%s://%s' % (protocol, Site.objects.get_current().domain)
        self.unsubscribe_url = '%s%s' % (site_url, unsub_url)
        unsub_headers['List-Unsubscribe'] = '<%s>' % self.unsubscribe_url
        super(UnsubscribableEmailMessage, self).__init__(subject=subject,
                                                         body=body, from_email=from_email, to=to, bcc=bcc,
                                                         connection=connection, attachments=attachments,
                                                         headers=unsub_headers, alternatives=alternatives)

    def render_message(self, template, context=None):
        """
        A wrapper around render_to_string which feeds the template the
        additional context, `unsubscribe_url` which is the url for the user to
        unsubscribe
        """
        if not context:
            context = {}
        context['unsubscribe_url'] = self.unsubscribe_url
        return render_to_string(template, context)

    def send(self, fail_silently=False):
        user_unsubscribed = Unsubscription.objects.filter(uid=self.user, slist=self.list).count() > 0
        if user_unsubscribed:
            return
        super(UnsubscribableEmailMessage, self).send(fail_silently)
