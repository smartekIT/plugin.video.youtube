# -*- coding: utf-8 -*-
"""

    Copyright (C) 2014-2016 bromix (plugin.video.youtube)
    Copyright (C) 2016-2018 plugin.video.youtube

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only for more information.
"""


import hashlib
import datetime

from html import unescape


class BaseItem(object):
    VERSION = 3
    INFO_DATE = 'date'  # (string) iso 8601

    def __init__(self, name, uri, image='', fanart=''):
        self._version = BaseItem.VERSION

        try:
            self._name = unescape(name)
        except:
            self._name = name

        self._uri = uri

        self._image = ''
        self.set_image(image)

        self._fanart = fanart
        self._context_menu = None
        self._replace_context_menu = False
        self._added_utc = None
        self._date = None
        self._dateadded = None
        self._short_details = None

        self._next_page = False

    def __str__(self):
        name = self._name
        uri = self._uri
        image = self._image
        obj_str = "------------------------------\n'%s'\nURI: %s\nImage: %s\n------------------------------" % (name, uri, image)
        return obj_str

    def get_id(self):
        """
        Returns a unique id of the item.
        :return: unique id of the item.
        """
        m = hashlib.md5()
        m.update(self._name.encode('utf-8'))
        m.update(self._uri.encode('utf-8'))
        return m.hexdigest()

    def get_name(self):
        """
        Returns the name of the item.
        :return: name of the item.
        """
        return self._name

    def set_uri(self, uri):
        self._uri = uri if uri and isinstance(uri, str) else ''

    def get_uri(self):
        """
        Returns the path of the item.
        :return: path of the item.
        """
        return self._uri

    def set_image(self, image):
        if image is None:
            self._image = ''
        else:
            self._image = image

    def get_image(self):
        return self._image

    def set_fanart(self, fanart):
        self._fanart = fanart

    def get_fanart(self):
        return self._fanart

    def set_context_menu(self, context_menu, replace=False):
        self._context_menu = context_menu
        self._replace_context_menu = replace

    def get_context_menu(self):
        return self._context_menu

    def replace_context_menu(self):
        return self._replace_context_menu

    def set_date(self, year, month, day, hour=0, minute=0, second=0):
        date = datetime.datetime(year, month, day, hour, minute, second)
        self._date = date.isoformat(sep=' ')

    def set_date_from_datetime(self, date_time):
        self.set_date(year=date_time.year,
                      month=date_time.month,
                      day=date_time.day,
                      hour=date_time.hour,
                      minute=date_time.minute,
                      second=date_time.second)

    def set_dateadded(self, year, month, day, hour=0, minute=0, second=0):
        date = datetime.datetime(year, month, day, hour, minute, second)
        self._dateadded = date.isoformat(sep=' ')

    def set_dateadded_from_datetime(self, date_time):
        self.set_dateadded(year=date_time.year,
                           month=date_time.month,
                           day=date_time.day,
                           hour=date_time.hour,
                           minute=date_time.minute,
                           second=date_time.second)

    def set_added_utc(self, dt):
        self._added_utc = dt

    def get_added_utc(self):
        return self._added_utc

    def get_date(self):
        return self._date

    def get_dateadded(self):
        return self._dateadded

    def get_short_details(self):
        return self._short_details

    def set_short_details(self, details):
        self._short_details = details or ''

    @property
    def next_page(self):
        return self._next_page

    @next_page.setter
    def next_page(self, value):
        self._next_page = bool(value)
