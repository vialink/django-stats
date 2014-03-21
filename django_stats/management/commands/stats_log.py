# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django_stats import parselog

class Command(BaseCommand):
    args = u'<log>'
    help = u'Gera estatísticas de acesso aos webservices processando um arquivo de log do nginx'

    def handle(self, log, *args, **kwargs):
        parselog(log)
