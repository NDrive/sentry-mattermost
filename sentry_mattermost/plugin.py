# Copyright (c) 2015 NDrive SA
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import json
import urllib2
import operator

from django import forms
from django.db.models import Q

from sentry.plugins.bases import notify
from sentry.models import TagKey, TagValue

import sentry_mattermost


def get_project_full_name(project):
    if project.team.name not in project.name:
        return '%s %s' % (project.team.name, project.name)
    return project.name


def get_rules(notification, group, project):
    rules = []
    for rule in notification.rules:
        rules.append(rule.label.encode('utf-8'))
    return ', '.join('%s' % r for r in rules)


def get_tags(event):
    tag_list = event.get_tags()
    if not tag_list:
        return ()

    key_labels = {
        o.key: o.get_label()
        for o in TagKey.objects.filter(
            project=event.project,
            key__in=[t[0] for t in tag_list],
        )
    }
    value_labels = {
        (o.key, o.value): o.get_label()
        for o in TagValue.objects.filter(
            reduce(operator.or_, (Q(key=k, value=v) for k, v in tag_list)),
            project=event.project,
        )
    }
    return (
        (key_labels.get(k, k), value_labels.get((k, v), v))
        for k, v in tag_list
    )


class PayloadFactory:
    @classmethod
    def render_text(cls, params):
        template = "__[{title}]({link})__ \n" \
                 + "__Culprit__\n" \
                 + "{culprit}\n" \
                 + "__Project__\n" \
                 + "{project} \n" \

        if "rules" in params:
            template += "__Triggered By__\n" \
                     + "{rules} \n"
        if "tags" in params:
            for k, v in params["tags"]:
                template += "__%s__ \n%s\n" % (k, v)

        return template.format(**params)

    @classmethod
    def create(cls, plugin, notification):
        event = notification.event
        group = event.group
        project = group.project

        params = {
            "title": group.message_short.encode('utf-8'),
            "link": group.get_absolute_url(),
            "culprit": group.culprit.encode('utf-8'),
            "project": get_project_full_name(project).encode('utf-8')
        }

        if plugin.get_option('include_rules', project):
            params["rules"] = get_rules(notification, group, project)

        if plugin.get_option('include_tags', project):
            params["tags"] = get_tags(event)

        text = cls.render_text(params)

        payload = {
            "username": "Sentry",
            "icon_url": "http://myovchev.github.io/sentry-slack/images/logo32.png", #noqa
            "text": text
        }
        return payload


def request(url, payload):
    data = "payload=" + json.dumps(payload)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    return response.read()


class MattermostOptionsForm(notify.NotificationConfigurationForm):
    webhook = forms.URLField(
        help_text='Incoming Webhook URL',
        widget=forms.URLInput(attrs={'class': 'span8'})
    )
    include_rules = forms.BooleanField(
        help_text='Include triggering rules with notifications',
        required=False,
    )
    include_tags = forms.BooleanField(
        help_text='Include tags with notifications',
        required=False,
    )


class Mattermost(notify.NotificationPlugin):
    title = 'Mattermost'
    slug = 'mattermost'
    description = 'Enables notifications for Mattermost Open Source Chat'
    version = sentry_mattermost.VERSION
    author = 'Andre Freitas <andre.freitas@ndrive.com>'
    author_url = 'https://github.com/NDrive/sentry-mattermost'
    project_conf_form = MattermostOptionsForm

    def is_configured(self, project):
        return all((self.get_option(k, project) for k in ('webhook',)))

    def notify(self, notification):
        project = notification.event.group.project
        if not self.is_configured(project):
            return

        webhook = self.get_option('webhook', project)
        payload = PayloadFactory.create(self, notification)
        return request(webhook, payload)
