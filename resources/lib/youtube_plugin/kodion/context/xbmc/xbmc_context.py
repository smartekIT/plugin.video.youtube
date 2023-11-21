# -*- coding: utf-8 -*-
"""

    Copyright (C) 2014-2016 bromix (plugin.video.youtube)
    Copyright (C) 2016-2018 plugin.video.youtube

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only for more information.
"""

import datetime
import json
import os
import sys
import weakref
from urllib.parse import parse_qsl, quote, unquote, urlparse

import xbmc
import xbmcaddon
import xbmcplugin
import xbmcvfs

from ..abstract_context import AbstractContext
from ...player.xbmc.xbmc_playlist import XbmcPlaylist
from ...player.xbmc.xbmc_player import XbmcPlayer
from ...settings.xbmc.xbmc_plugin_settings import XbmcPluginSettings
from ...ui.xbmc.xbmc_context_ui import XbmcContextUI
from ... import utils


try:
    xbmc.translatePath = xbmcvfs.translatePath
except AttributeError:
    pass


class XbmcContext(AbstractContext):
    def __init__(self, path='/', params=None, plugin_name='', plugin_id='', override=True):
        super(XbmcContext, self).__init__(path, params, plugin_name, plugin_id)

        if plugin_id:
            self._addon = xbmcaddon.Addon(id=plugin_id)
        else:
            self._addon = xbmcaddon.Addon(id='plugin.video.youtube')

        """
        I don't know what xbmc/kodi is doing with a simple uri, but we have to extract the information from the
        sys parameters and re-build our clean uri.
        Also we extract the path and parameters - man, that would be so simple with the normal url-parsing routines.
        """
        num_args = len(sys.argv)

        # first the path of the uri
        if override:
            self._uri = sys.argv[0]
            parsed_url = urlparse(self._uri)
            self._path = unquote(parsed_url.path)

            # after that try to get the params
            if num_args > 2:
                params = sys.argv[2][1:]
                if params:
                    self._uri = '?'.join([self._uri, params])
                    self.parse_params(dict(parse_qsl(params)))

            if num_args > 3 and sys.argv[3].lower() == 'resume:true':
                self._params['resume'] = True

        self._ui = None
        self._video_playlist = None
        self._audio_playlist = None
        self._video_player = None
        self._audio_player = None
        self._plugin_handle = int(sys.argv[1]) if num_args > 1 else -1
        self._plugin_id = plugin_id or self._addon.getAddonInfo('id')
        self._plugin_name = plugin_name or self._addon.getAddonInfo('name')
        self._version = self._addon.getAddonInfo('version')
        self._native_path = xbmc.translatePath(self._addon.getAddonInfo('path'))
        self._settings = XbmcPluginSettings(self._addon)

        """
        Set the data path for this addon and create the folder
        """
        try:
            self._data_path = xbmc.translatePath(self._addon.getAddonInfo('profile')).decode('utf-8')
        except AttributeError:
            self._data_path = xbmc.translatePath(self._addon.getAddonInfo('profile'))

        if not xbmcvfs.exists(self._data_path):
            xbmcvfs.mkdir(self._data_path)

    def get_region(self):
        pass  # implement from abstract

    def addon(self):
        return self._addon

    def is_plugin_path(self, uri, uri_path):
        return uri.startswith('plugin://%s/%s/' % (self.get_id(), uri_path))

    @staticmethod
    def format_date_short(date_obj, short_isoformat=False):
        if short_isoformat:
            if isinstance(date_obj, datetime.datetime):
                date_obj = date_obj.date()
            return date_obj.isoformat()
            
        date_format = xbmc.getRegion('dateshort')
        _date_obj = date_obj
        if isinstance(_date_obj, datetime.date):
            _date_obj = datetime.datetime(_date_obj.year, _date_obj.month, _date_obj.day)

        return _date_obj.strftime(date_format)

    @staticmethod
    def format_time(time_obj, short_isoformat=False):
        if short_isoformat:
            return '{:02d}:{:02d}'.format(time_obj.hour, time_obj.minute)

        time_format = xbmc.getRegion('time')
        _time_obj = time_obj
        if isinstance(_time_obj, datetime.time):
            _time_obj = datetime.time(_time_obj.hour, _time_obj.minute, _time_obj.second)

        return _time_obj.strftime(time_format.replace("%H%H", "%H"))

    def get_language(self):
        """
        The xbmc.getLanguage() method is fucked up!!! We always return 'en-US' for now
        """

        '''
        if self.get_system_version().get_release_name() == 'Frodo':
            return 'en-US'

        try:
            language = xbmc.getLanguage(0, region=True)
            language = language.split('-')
            language = '%s-%s' % (language[0].lower(), language[1].upper())
            return language
        except Exception, ex:
            self.log_error('Failed to get system language (%s)', ex.__str__())
            return 'en-US'
        '''

        return 'en-US'

    def get_language_name(self, lang_id=None):
        if lang_id is None:
            lang_id = self.get_language()
        return xbmc.convertLanguage(lang_id, xbmc.ENGLISH_NAME).split(';')[0]

    def get_video_playlist(self):
        if not self._video_playlist:
            self._video_playlist = XbmcPlaylist('video', weakref.proxy(self))
        return self._video_playlist

    def get_audio_playlist(self):
        if not self._audio_playlist:
            self._audio_playlist = XbmcPlaylist('audio', weakref.proxy(self))
        return self._audio_playlist

    def get_video_player(self):
        if not self._video_player:
            self._video_player = XbmcPlayer('video', weakref.proxy(self))
        return self._video_player

    def get_audio_player(self):
        if not self._audio_player:
            self._audio_player = XbmcPlayer('audio', weakref.proxy(self))
        return self._audio_player

    def get_ui(self):
        if not self._ui:
            self._ui = XbmcContextUI(self._addon, weakref.proxy(self))
        return self._ui

    def get_handle(self):
        return self._plugin_handle

    def get_data_path(self):
        return self._data_path

    def get_debug_path(self):
        if not self._debug_path:
            self._debug_path = os.path.join(self.get_data_path(), 'debug')
            if not xbmcvfs.exists(self._debug_path):
                xbmcvfs.mkdir(self._debug_path)
        return self._debug_path

    def get_native_path(self):
        return self._native_path

    def get_settings(self):
        return self._settings

    def localize(self, text_id, default_text=''):
        if not isinstance(text_id, int):
            try:
                text_id = int(text_id)
            except ValueError:
                return default_text
        if text_id <= 0:
            return default_text

        """
        We want to use all localization strings!
        Addons should only use the range 30000 thru 30999 (see: http://kodi.wiki/view/Language_support) but we
        do it anyway. I want some of the localized strings for the views of a skin.
        """
        source = self._addon if 30000 <= text_id < 31000 else xbmc
        result = source.getLocalizedString(text_id)
        result = utils.to_unicode(result) if result else default_text
        return result

    def set_content_type(self, content_type):
        self.log_debug('Setting content-type: "%s" for "%s"' % (content_type, self.get_path()))
        xbmcplugin.setContent(self._plugin_handle, content_type)

    def add_sort_method(self, *sort_methods):
        for sort_method in sort_methods:
            xbmcplugin.addSortMethod(self._plugin_handle, sort_method)

    def clone(self, new_path=None, new_params=None):
        if not new_path:
            new_path = self.get_path()

        if not new_params:
            new_params = self.get_params()

        new_context = XbmcContext(path=new_path, params=new_params, plugin_name=self._plugin_name,
                                  plugin_id=self._plugin_id, override=False)
        new_context._function_cache = self._function_cache
        new_context._search_history = self._search_history
        new_context._favorite_list = self._favorite_list
        new_context._watch_later_list = self._watch_later_list
        new_context._access_manager = self._access_manager
        new_context._ui = self._ui
        new_context._video_playlist = self._video_playlist
        new_context._video_player = self._video_player

        return new_context

    def execute(self, command):
        xbmc.executebuiltin(command)

    def sleep(self, milli_seconds):
        xbmc.sleep(milli_seconds)

    def addon_enabled(self, addon_id):
        rpc_request = json.dumps({"jsonrpc": "2.0",
                                  "method": "Addons.GetAddonDetails",
                                  "id": 1,
                                  "params": {"addonid": "%s" % addon_id,
                                             "properties": ["enabled"]}
                                  })
        response = json.loads(xbmc.executeJSONRPC(rpc_request))
        try:
            return response['result']['addon']['enabled'] is True
        except KeyError:
            message = response['error']['message']
            code = response['error']['code']
            error = 'Requested |%s| received error |%s| and code: |%s|' % (rpc_request, message, code)
            self.log_debug(error)
            return False

    def set_addon_enabled(self, addon_id, enabled=True):
        rpc_request = json.dumps({"jsonrpc": "2.0",
                                  "method": "Addons.SetAddonEnabled",
                                  "id": 1,
                                  "params": {"addonid": "%s" % addon_id,
                                             "enabled": enabled}
                                  })
        response = json.loads(xbmc.executeJSONRPC(rpc_request))
        try:
            return response['result'] == 'OK'
        except KeyError:
            message = response['error']['message']
            code = response['error']['code']
            error = 'Requested |%s| received error |%s| and code: |%s|' % (rpc_request, message, code)
            self.log_debug(error)
            return False

    def send_notification(self, method, data):
        data = json.dumps(data)
        self.log_debug('send_notification: |%s| -> |%s|' % (method, data))
        data = '\\"[\\"%s\\"]\\"' % quote(data)
        self.execute('NotifyAll(plugin.video.youtube,%s,%s)' % (method, data))

    def use_inputstream_adaptive(self):
        if self._settings.use_isa():
            if self.addon_enabled('inputstream.adaptive'):
                success = True
            elif self.get_ui().on_yes_no_input(self.get_name(), self.localize(30579)):
                success = self.set_addon_enabled('inputstream.adaptive')
            else:
                success = False
        else:
            success = False
        return success

    # Values of capability map can be any of the following:
    # - required version number as string for comparison with actual installed InputStream.Adaptive version
    # - any Falsey value to exclude capability regardless of version
    # - True to include capability regardless of version
    _ISA_CAPABILITIES = {
        'live': '2.0.12',
        'drm': '2.2.12',
        # audio codecs
        'vorbis': '2.3.14',
        'opus': '19.0.0',  # unknown when Opus audio support was first implemented
        'mp4a': True,
        'ac-3': '2.1.15',
        'ec-3': '2.1.15',
        'dts': '2.1.15',
        # video codecs
        'avc1': True,
        'av01': '20.3.0',
        'vp8': False,
        'vp9': '2.3.14',
    }

    def inputstream_adaptive_capabilities(self, capability=None):
        # return a list inputstream.adaptive capabilities, if capability set return version required

        try:
            inputstream_version = xbmcaddon.Addon('inputstream.adaptive').getAddonInfo('version')
        except RuntimeError:
            inputstream_version = ''

        if not self.use_inputstream_adaptive() or not inputstream_version:
            return frozenset() if capability is None else None

        isa_loose_version = utils.loose_version(inputstream_version)
        if capability is None:
            capabilities = frozenset(
                capability for capability, version in self._ISA_CAPABILITIES.items()
                if version is True
                or version and isa_loose_version >= utils.loose_version(version)
            )
            return capabilities
        version = self._ISA_CAPABILITIES.get(capability)
        return version is True or version and isa_loose_version >= utils.loose_version(version)

    @staticmethod
    def inputstream_adaptive_auto_stream_selection():
        try:
            return xbmcaddon.Addon('inputstream.adaptive').getSetting('STREAMSELECTION') == '0'
        except RuntimeError:
            return False

    def abort_requested(self):
        return str(self.get_ui().get_home_window_property('abort_requested')).lower() == 'true'
