# -*- coding: utf-8 -*-
import os
import urllib2

from django.db import models
from django.conf import settings

from hitcounter.models import HitCounterModelMixin

from colab.proxy.utils.models import Collaboration
from colab.accounts.models import User
from django.utils.translation import ugettext_lazy as _


class Attachment(models.Model, HitCounterModelMixin):
    type = 'attachment'
    icon_name = 'file'
    url = models.TextField(primary_key=True)
    attach_id = models.TextField()
    used_by = models.TextField()
    filename = models.TextField()
    author = models.TextField(blank=True)
    title = models.TextField(blank=True)
    description = models.TextField(blank=True)
    created = models.DateTimeField(blank=True)
    mimetype = models.TextField(blank=True)
    size = models.IntegerField(blank=True)
    ipnr = models.TextField(blank=True)

    class Meta:
        verbose_name = _('Attachment')
        verbose_name_plural = _('Attachment')

    @property
    def filepath(self):
        return os.path.join(
            settings.ATTACHMENTS_FOLDER_PATH,
            self.used_by,
            self.attach_id,
            urllib2.quote(self.filename.encode('utf8'))
        )

    def get_absolute_url(self):
        return u'/raw-attachment/{}'.format(self.url)

    def get_author(self):
        try:
            return User.objects.get(username=self.author)
        except User.DoesNotExist:
            return None

class Revision(models.Model, HitCounterModelMixin):
    update_field = 'created'
    icon_name = 'align-right'
    rev = models.TextField(blank=True)
    author = models.TextField(blank=True)
    message = models.TextField(blank=True)
    description = models.TextField(blank=True)
    repository_name = models.TextField(blank=True)
    created = models.DateTimeField(blank=True, null=True)

    @property
    def title(self):
        return u'{} [{}]'.format(self.repository_name, self.rev)

    class Meta:
        verbose_name = _('Revision')
        verbose_name_plural = _('Revision')

    def get_absolute_url(self):
        return u'/changeset/{}/{}'.format(self.rev, self.repository_name)

    def get_author(self):
        try:
            return User.objects.get(username=self.author)
        except User.DoesNotExist:
            return None


class Ticket(Collaboration, HitCounterModelMixin):
    icon_name = 'tag'
    type = 'ticket'
    summary = models.TextField(blank=True)
    description_ticket = models.TextField(blank=True)
    milestone = models.TextField(blank=True)
    priority = models.TextField(blank=True)
    component = models.TextField(blank=True)
    version = models.TextField(blank=True)
    severity = models.TextField(blank=True)
    reporter = models.TextField(blank=True)
    author = models.TextField(blank=True)
    status = models.TextField(blank=True)
    tag = models.TextField(blank=True)
    keywords = models.TextField(blank=True)
    collaborators = models.TextField(blank=True)
    created = models.DateTimeField(blank=True, null=True)
    modified = models.DateTimeField(blank=True, null=True)
    owner = models.TextField(blank=True)
    resolution = models.TextField(blank=True)

    @property
    def title(self):
        return u'#{} - {}'.format(self.id, self.summary)

    @property
    def description(self):
        return u'{}\n{}\n{}\n{}\n{}\n{}\n{}'.format(
            self.description_ticket, self.milestone, self.component,
            self.severity, self.reporter, self.keywords, self.collaborators
        )

    class Meta:
        verbose_name = _('Ticket')
        verbose_name_plural = _('Ticket')

    def get_absolute_url(self):
        return u'/ticket/{}'.format(self.id)

    def get_author(self):
        try:
            return User.objects.get(username=self.author)
        except User.DoesNotExist:
            return None

    def get_modified_by(self):
        try:
            return User.objects.get(username=self.modified_by)
        except User.DoesNotExist:
            return None


class Wiki(Collaboration, HitCounterModelMixin):
    type = "wiki"
    icon_name = "book"
    title = models.TextField(primary_key=True)
    wiki_text = models.TextField(blank=True)
    author = models.TextField(blank=True)
    collaborators = models.TextField(blank=True)
    created = models.DateTimeField(blank=True, null=True)
    modified = models.DateTimeField(blank=True, null=True)

    @property
    def description(self):
        return u'{}\n{}'.format(self.wiki_text, self.collaborators)

    class Meta:
        verbose_name = _('Wiki')
        verbose_name_plural = _('Wiki')

    def get_absolute_url(self):
        return u'/wiki/{}'.format(self.title)

    def get_author(self):
        try:
            return User.objects.get(username=self.author)
        except User.DoesNotExist:
            return None

    def get_modified_by(self):
        try:
            return User.objects.get(username=self.author)
        except User.DoesNotExist:
            return None