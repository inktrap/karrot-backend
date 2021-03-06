# Generated by Django 2.2.2 on 2019-06-18 14:25
from collections import defaultdict
from datetime import timedelta

from django.db import migrations
from django.utils.dateparse import parse_datetime
from django_enumfield import enum
from rest_framework import serializers

from karrot.pickups.serializers import DateTimeRangeField


class HistoryTypus(enum.Enum):
    GROUP_CREATE = 0
    GROUP_MODIFY = 1
    GROUP_JOIN = 2
    GROUP_LEAVE = 3
    STORE_CREATE = 4
    STORE_MODIFY = 5
    STORE_DELETE = 6
    PICKUP_CREATE = 7
    PICKUP_MODIFY = 8
    PICKUP_DELETE = 9
    SERIES_CREATE = 10
    SERIES_MODIFY = 11
    SERIES_DELETE = 12
    PICKUP_DONE = 13
    PICKUP_JOIN = 14
    PICKUP_LEAVE = 15
    PICKUP_MISSED = 16
    APPLICATION_DECLINED = 17
    MEMBER_BECAME_EDITOR = 18
    PICKUP_DISABLE = 19
    PICKUP_ENABLE = 20
    GROUP_LEAVE_INACTIVE = 21
    GROUP_CHANGE_PHOTO = 22
    GROUP_DELETE_PHOTO = 23
    MEMBER_REMOVED = 24


BATCH_SIZE = 1000


def migrate(apps, schema_editor):
    History = apps.get_model('history', 'History')
    PickupDate = apps.get_model('pickups', 'PickupDate')

    save_pickup_id = []

    # set foreign key to pickup date
    history_to_update = []
    for h in History.objects.filter(typus__in=(
            HistoryTypus.PICKUP_JOIN,
            HistoryTypus.PICKUP_LEAVE,
            HistoryTypus.PICKUP_DONE,
            HistoryTypus.PICKUP_MISSED,
    )):
        if not h.payload:
            continue
        pickup_id = h.payload.get('id') or h.payload.get('pickup_date')
        if not pickup_id:
            continue

        h.pickup_id = pickup_id
        history_to_update.append(h)

    requested_pickup_ids = set(h.pickup_id for h in history_to_update)
    valid_pickup_ids = PickupDate.objects.filter(id__in=requested_pickup_ids).values_list(flat=True)

    for h in history_to_update:
        if h.pickup_id in valid_pickup_ids:
            save_pickup_id.append(h)

    History.objects.bulk_update(save_pickup_id, fields=['pickup_id'], batch_size=BATCH_SIZE)

    # rewrite old pickup date payload to default duration
    save_payload = []
    for h in History.objects.filter(typus__in=(
            HistoryTypus.PICKUP_JOIN,
            HistoryTypus.PICKUP_LEAVE,
    ), payload__date__0__isnull=True):
        if h.payload and 'date' in h.payload:
            date = parse_datetime(h.payload['date'])
            h.payload['date'] = [d.isoformat() for d in [date, date + timedelta(minutes=30)]]
            save_payload.append(h)

    # always use pickup serializer for payload
    pickup_to_history = defaultdict(list)

    for h in History.objects.filter(typus__in=(
            HistoryTypus.PICKUP_DONE,
            HistoryTypus.PICKUP_MISSED,
    )).select_related('pickup').prefetch_related('pickup__pickupdatecollector_set'):
        if not h.pickup_id:
            continue
        pickup_to_history[h.pickup].append(h)

    class PickupDateSerializer(serializers.ModelSerializer):
        class Meta:
            model = PickupDate
            fields = [
                'id',
                'date',
                'series',
                'place',
                'max_collectors',
                'collectors',
                'description',
                'is_disabled',
            ]

        collectors = serializers.SerializerMethodField()

        date = DateTimeRangeField()

        def get_collectors(self, pickup):
            return [c.user_id for c in pickup.pickupdatecollector_set.all()]

    for pickup, history_list in pickup_to_history.items():
        pickup_data = PickupDateSerializer(pickup).data
        for h in history_list:
            h.payload = pickup_data
            save_payload.append(h)

    History.objects.bulk_update(save_payload, fields=['payload'], batch_size=BATCH_SIZE)


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0007_auto_20190123_1628'),
    ]

    operations = [migrations.RunPython(migrate, migrations.RunPython.noop, elidable=True)]
