# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django_stats import parselog
from optparse import make_option

import datetime

class Command(BaseCommand):
    args = u'<log>'
    help = u'Gera estatísticas de acesso aos webservices processando um arquivo de log do nginx'

    option_list = BaseCommand.option_list + (
        make_option('--slow-threshold',
            action='store',
            dest='slow_threshold',
            default=None,
            help='Print only views which worst case is more than X seconds.',
        ),
        make_option('--since',
            action='store',
            dest='since',
            default=None,
            help='The log will be analysed since which date. It could be a date or expressions like "today", "yesterday", "last-7-days"'),
        )

    def handle(self, log, *args, **kwargs):
        # Parse since argument.
        since_raw = kwargs.pop('since', None)
        since = None
        if since_raw:
            since_raw = since_raw.strip().lower()
            if since_raw == 'today':
                since = datetime.datetime.today()
            elif since_raw == 'yesterday':
                since = datetime.datetime.today() - datetime.timedelta(days=1)
            elif since_raw == 'last-7-days':
                since = datetime.datetime.today() - datetime.timedelta(days=7)
            else:
                raise CommandError('Invalid since value.')

        # Parse slow threshold.
        slow_threshold = kwargs.pop('slow_threshold', None)
        if slow_threshold:
            slow_threshold = float(slow_threshold.strip().lower())

        # Run the log analyser.
        parselog(log, since=since, slow_threshold=slow_threshold)
