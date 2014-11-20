# -*- coding: utf-8 -*-

import os

from django.core.exceptions import ObjectDoesNotExist

from grab import spider, Grab as GrabLib

import defaults
import models


APP_ROOT = os.path.normpath(os.path.dirname(__file__))
USER_AGENT_FILE = os.path.join(APP_ROOT, 'data/agents.txt')


def get_proxies():
    proxies = []
    proxies_list = models.Proxy.objects.filter(
        errors=0, last_check__isnull=False)
    if not proxies_list.exists():
        raise ObjectDoesNotExist('Active proxy not found!')
    for obj in proxies_list:
        proxy = '%s:%d' % (obj.hostname, obj.port)
        if obj.user and obj.password:
            proxy += ':%s:%s' % (obj.user, obj.password)
        proxies.append(proxy)
    return proxies


def get_default_settings():
    return {
        'user_agent_file': USER_AGENT_FILE,
        'connect_timeout': defaults.GRABBER_CONNECT_TIMEOUT,
        'timeout': defaults.GRABBER_TIMEOUT,
        'hammer_mode': True,
        'hammer_timeouts': defaults.GRABBER_HAMMER_TIMEOUTS,
        'headers': defaults.GRABBER_HEADERS
    }


class Grab(GrabLib):
    def __init__(self, *args, **kwargs):
        default_settings = get_default_settings()
        use_proxy = kwargs.pop('use_db_proxy', True)
        default_settings.update(kwargs)

        kwargs.update(default_settings)

        super(Grab, self).__init__(*args, **kwargs)

        if use_proxy is True:
            self.load_proxylist(
                source=get_proxies(),
                source_type='list',
                auto_init=True,
                auto_change=True
            )


class Spider(spider.base.Spider):
    def create_grab_instance(self):
        return Grab(**self.grab_config)
