from collections import defaultdict
import datetime
import json

from dateutil.parser import parse as parse
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import get_default_timezone

from constance import config


HARBOR_AUTH_NEVER = 'n'
HARBOR_AUTH_ALWAYS = 'a'
HARBOR_AUTH_SCHEDULE = 's'
HARBOR_AUTH_CHOICES = (
    (HARBOR_AUTH_ALWAYS, 'Always'),
    (HARBOR_AUTH_NEVER, 'Never'),
    (HARBOR_AUTH_SCHEDULE, 'Schedule Based'),
)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    harbor_auth = models.CharField(max_length=1, choices=HARBOR_AUTH_CHOICES)


class ScheduledGCalShow(models.Model):
    gcal_id = models.CharField(max_length=1024, unique=True)
    title = models.CharField(max_length=1024)
    start = models.DateTimeField()
    end = models.DateTimeField()
    users = models.ManyToManyField(User)

    def __str__(self):
        server_tz = get_default_timezone()
        return f'{self.title} - {self.start.astimezone(server_tz)} to {self.end.astimezone(server_tz)}'

    @classmethod
    def create_or_update_from_gcal_item(cls, item):
        server_tz = get_default_timezone()
        emails = {attendee['email'] for attendee in item.get('attendees', [])}
        creator = item.get('creator', {}).get('email')
        if creator is not None:
            emails.add(creator)

        defaults = {
            'title': item.get('summary', 'Untitled Show'),
            # Start time / end time, server time if full day event
            'start': (server_tz.localize(parse(item['start']['date']))
                      if item['start'].get('dateTime') is None else parse(item['start'].get('dateTime'))),
            'end': (server_tz.localize(parse(item['end']['date']).replace(hour=23, minute=59, second=59))
                    if item['end'].get('dateTime') is None else parse(item['end'].get('dateTime'))),
        }

        return cls.objects.update_or_create(
            gcal_id=item['id'],
            defaults=defaults,
        )[0]

    @classmethod
    def sync_with_gcal(cls):
        server_tz = get_default_timezone()
        credentials = Credentials.from_service_account_info(json.loads(config.GCAL_AUTH_CREDENTIALS_JSON))
        service = build('calendar', 'v3', credentials=credentials)
        emails_to_users = {}

        seen_gcal_ids = set()

        page_token = None
        while True:
            response = service.events().list(
                calendarId='shoutingfirehq@gmail.com',
                maxResults=2500,
                timeMin=(datetime.datetime.utcnow() - datetime.timedelta(days=60)).isoformat() + 'Z',
                timeMax=(datetime.datetime.utcnow() + datetime.timedelta(days=120)).isoformat() + 'Z',
                timeZone='UTC',
                singleEvents='true',
                pageToken=page_token,
            ).execute()

            for item in response['items']:
                scheduled_show, created = cls.objects.update_or_create(
                    gcal_id=item['id'],
                    defaults={
                        'title': item.get('summary', 'Untitled Show'),
                        # Start time / end time, server time if full day event
                        'start': (server_tz.localize(parse(item['start']['date']))
                                  if item['start'].get('dateTime') is None else parse(item['start'].get('dateTime'))),
                        'end': (server_tz.localize(parse(item['end']['date']).replace(hour=23, minute=59, second=59))
                                if item['end'].get('dateTime') is None else parse(item['end'].get('dateTime'))),
                    },
                )
                emails = {attendee['email'] for attendee in item.get('attendees', [])}
                creator = item.get('creator', {}).get('email')
                if creator is not None:
                    emails.add(creator)

                allowed_users = set()
                for email in emails:
                    if email not in emails_to_users:
                        try:
                            emails_to_users[email] = User.objects.get(email=email)
                        except User.DoesNotExist:
                            emails_to_users[email] = None

                    user = emails_to_users[email]
                    if user is not None:
                        allowed_users.add(user)
                        scheduled_show.users.add(user)

                for user in scheduled_show.users.all():
                    if user not in allowed_users:
                        scheduled_show.users.remove(user)
                seen_gcal_ids.add(scheduled_show.gcal_id)

            page_token = response.get('nextPageToken')
            if page_token is None:
                break

        cls.objects.exclude(gcal_id__in=seen_gcal_ids).delete()
