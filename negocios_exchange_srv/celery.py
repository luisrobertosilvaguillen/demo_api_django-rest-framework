# from __future__ import absolute_import
# import os
# from celery import Celery
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'negocios_exchange_srv.settings')
# from django.conf import settings  # noqa
# app = Celery('negocios_exchange_srv', backend='rpc://', broker='amqp://guest@localhost//')
# app.config_from_object('django.conf:settings')
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
