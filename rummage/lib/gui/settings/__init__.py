"""
Handles settings.

Licensed under MIT
Copyright (c) 2013 - 2015 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""
import codecs
import json
import os
import copy
from filelock import FileLock
from ..app import custom_app
from ..app.custom_app import debug, debug_struct, error
from ..dialogs.generic_dialogs import errormsg
from .. import localization
from ..localization import _
from .. import data
from .. import notify
from ..notify.util import which
from ... import rumcore
from ...rumcore import text_decode
from .. import util

DEV_MODE = False
SETTINGS_FILE = "rummage_dev.settings" if DEV_MODE else "rummage.settings"
CACHE_FILE = "rummage_dev.cache" if DEV_MODE else "rummage.cache"
LOG_FILE = "rummage.log"
FIFO = "rummage.fifo"

SETTINGS_FMT = '2.6.1'
CACHE_FMT = '2.0.0'

NOTIFY_STYLES = {
    "macos": ["default"],
    "windows": ["default"],
    "linux": ["default"]
}

NOTIFY_PLAYERS = {
    "macos": ["afplay"],
    "windows": ["windows"],
    "linux": ["paplay", "aplay", "play"]
}

NOTIFY_EXT = {
    "afplay": ['.wav', '.mp3', '.aiff'],
    "windows": ['.wav'],
    "paplay": ['.wav', '.mp3', '.ogg'],
    "aplay": ['.wav', '.mp3'],
    "play": ['.wav', '.mp3'],
}

BACKUP_FILE = 0
BACKUP_FOLDER = 1

DEFAULT_SETTINGS = {
    "__format__": SETTINGS_FMT,
    "alert_enabled": True,
    "alt_list_color": True,
    "backup_ext": "rum-bak",
    "backup_folder": ".rum-bak",
    "backup_type": BACKUP_FILE,
    "brace_expansion": False,
    "chains": {},
    "check_prerelease": False,
    "check_updates": False,
    "current_version": (0, 0, 0, 'final', 0, 0),
    "editor": "",
    "encoding_options": copy.deepcopy(text_decode.DEFAULT_ENCODING_OPTIONS),
    "extmatch": False,
    "file_case_sensitive": False,
    "full_exclude_path": False,
    "full_file_path": False,
    "globstar": False,
    "hide_cols_content": [],
    "hide_cols_file": [],
    "international_time": False,
    "locale": "en_US",
    "matchbase": False,
    "minusnegate": True,
    "notify_enabled": True,
    "notify_method": "default",
    "notify_player": NOTIFY_PLAYERS[util.platform()][0],
    "notify_sound": "",
    "pattern_limit": 1000,
    "pos_cols_content": [],
    "pos_cols_file": [],
    "regex_mode": rumcore.RE_MODE,
    "regex_version": 0,
    "saved_searches": {},
    "single_instance": False,
    "term_notifier": ""
}


class Settings:
    """Handle settings."""

    filename = None
    allow_save = True
    debug = False

    @classmethod
    def localize(cls):
        """Translate strings."""

        cls.ERR_LOAD_SETTINGS_FAILED = _("Failed to load settings file!")
        cls.ERR_LOAD_CACHE_FAILED = _("Failed to load cache file!")
        cls.ERR_SAVE_SETTINGS_FAILED = _("Failed to save settings file!")
        cls.ERR_SAVE_CACHE_FAILED = _("Failed to save cache file!")

    @classmethod
    def load_settings(cls):
        """Load the settings."""

        cls.localize()
        cls.setup_setting_files()
        cls.settings = {"__format__": SETTINGS_FMT}
        cls.cache = {"__format__": CACHE_FMT}
        cls.settings_time = None
        cls.cache_time = None
        cls.get_times()
        if cls.settings_file is not None:
            cls.open_settings()
            cls.open_cache()
        localization.setup('rummage', cls.get_language())
        cls.localize()
        debug_struct(cls.settings)
        debug_struct(cls.cache)
        cls.init_notify(True)

    @classmethod
    def get_available_players(cls):
        """Get the available players."""

        return NOTIFY_PLAYERS[util.platform()][:]

    @classmethod
    def get_settings(cls):
        """Get the entire settings object."""

        cls.reload_settings()
        return copy.deepcopy(cls.settings)

    @classmethod
    def get_log_file(cls):
        """Get location of log file."""

        return cls.log

    @classmethod
    def set_current_version(cls, value):
        """Set current version."""

        cls.reload_settings()
        cls._set_current_version(value)
        cls.save_settings()

    @classmethod
    def _set_current_version(cls, value):
        """Set current version."""

        cls.settings["current_version"] = value

    @classmethod
    def get_current_version(cls):
        """Get current version."""

        cls.reload_settings()
        value = cls.settings.get('current_version', DEFAULT_SETTINGS['current_version'])
        return value

    @classmethod
    def is_regex_available(cls):
        """Check if regex support is available."""

        return rumcore.REGEX_SUPPORT

    @classmethod
    def is_cchardet_available(cls):
        """Check if `cchardet` is available."""

        return text_decode.CCDetect is not None

    @classmethod
    def set_chardet_mode(cls, value):
        """Set `chardet` mode."""

        cls.reload_settings()
        cls._set_chardet_mode(value)
        cls.save_settings()

    @classmethod
    def _set_chardet_mode(cls, value):
        """Set `chardet` mode."""

        if not cls.is_cchardet_available() or value > text_decode.CHARDET_CLIB:
            value = text_decode.CHARDET_DEFAULT
        if 'encoding_options' not in cls.settings:
            cls.settings['encoding_options'] = copy.deepcopy(text_decode.DEFAULT_ENCODING_OPTIONS)
        cls.settings["encoding_options"]['chardet_mode'] = value

    @classmethod
    def get_chardet_mode(cls):
        """See if regex support is enabled."""

        cls.reload_settings()
        value = cls.settings.get('encoding_options', {}).get('chardet_mode', text_decode.CHARDET_DEFAULT)
        if text_decode.CCDetect is None or value > text_decode.CHARDET_CLIB:
            value = text_decode.CHARDET_DEFAULT
        return value

    @classmethod
    def set_alt_list_color(cls, value):
        """Set alternate list row color."""

        cls.reload_settings()
        cls._set_alt_list_color(value)
        cls.save_settings()

    @classmethod
    def _set_alt_list_color(cls, value):
        """Set alternate list row color."""

        cls.settings["alt_list_color"] = value

    @classmethod
    def get_alt_list_color(cls):
        """Get preference of alternative list row color."""

        cls.reload_settings()
        return cls.settings['alt_list_color']

    @classmethod
    def _set_encoding_ext(cls, values):
        """Set encoding options."""

        if 'encoding_options' not in cls.settings:
            cls.settings['encoding_options'] = copy.deepcopy(text_decode.DEFAULT_ENCODING_OPTIONS)

        for k, v in values.items():
            if k != 'chardet_mode' and k in text_decode.DEFAULT_ENCODING_OPTIONS:
                cls.settings['encoding_options'][k] = v[:]

    @classmethod
    def set_encoding_ext(cls, values):
        """Set `chardet` mode."""

        cls.reload_settings()
        cls._set_encoding_ext(values)
        cls.save_settings()

    @classmethod
    def get_encoding_ext(cls):
        """Get encoding extensions."""

        cls.reload_settings()
        value = cls.settings.get('encoding_options', {})
        options = {}
        for k, v in value.items():
            if k != "chardet_mode":
                options[k] = v[:]
        return options

    @classmethod
    def get_encoding_options(cls):
        """Get encoding extensions."""

        cls.reload_settings()
        options = cls.get_encoding_ext()
        options['chardet_mode'] = cls.get_chardet_mode()
        return options

    @classmethod
    def set_regex_mode(cls, value):
        """Set regex support."""

        cls.reload_settings()
        cls._set_regex_mode(value)
        cls.save_settings()

    @classmethod
    def _set_regex_mode(cls, value):
        """Set regex support."""

        if value in rumcore.REGEX_MODES and not rumcore.REGEX_SUPPORT:
            value = rumcore.REGEX_MODE
        cls.settings["regex_mode"] = value

    @classmethod
    def get_regex_mode(cls):
        """See if regex support is enabled."""

        cls.reload_settings()
        value = cls.settings.get('regex_mode', rumcore.RE_MODE)
        if value in rumcore.REGEX_MODES and not rumcore.REGEX_SUPPORT:
            value = rumcore.RE_MODE
        return value

    @classmethod
    def set_regex_version(cls, value):
        """Get the regex version."""

        cls.reload_settings()
        cls._set_regex_version(value)
        cls.save_settings()

    @classmethod
    def _set_regex_version(cls, value):
        """Get the regex version."""

        if 0 <= value <= 1:
            cls.settings["regex_version"] = value

    @classmethod
    def get_regex_version(cls):
        """Get the regex version."""

        cls.reload_settings()
        return cls.settings.get('regex_version', 0)

    @classmethod
    def get_hide_cols_file(cls):
        """Get hide cols file."""

        cls.reload_settings()
        return cls.settings.get("hide_cols_file", [])

    @classmethod
    def set_hide_cols_file(cls, hide):
        """Set hide cols file."""

        cls.reload_settings()
        cls._set_hide_cols_file(sorted(hide))
        cls.save_settings()

    @classmethod
    def _set_hide_cols_file(cls, hide):
        """Set hide cols file."""

        cls.settings["hide_cols_file"] = hide

    @classmethod
    def get_hide_cols_content(cls):
        """Get hide cols content."""

        cls.reload_settings()
        return cls.settings.get("hide_cols_content", [])

    @classmethod
    def set_hide_cols_content(cls, hide):
        """Set hide cols content."""

        cls.reload_settings()
        cls._set_hide_cols_content(sorted(hide))
        cls.save_settings()

    @classmethod
    def _set_hide_cols_content(cls, hide):
        """Set hide cols content."""

        cls.settings["hide_cols_content"] = hide

    @classmethod
    def get_pos_cols_file(cls):
        """Get position cols file."""

        cls.reload_settings()
        return cls.settings.get("pos_cols_file", [])

    @classmethod
    def set_pos_cols_file(cls, pos):
        """Set position cols file."""

        cls.reload_settings()
        cls._set_pos_cols_file(pos)
        cls.save_settings()

    @classmethod
    def _set_pos_cols_file(cls, pos):
        """Set position cols file."""

        cls.settings["pos_cols_file"] = pos

    @classmethod
    def get_pos_cols_content(cls):
        """Get position cols content."""

        cls.reload_settings()
        return cls.settings.get("pos_cols_content", [])

    @classmethod
    def set_pos_cols_content(cls, pos):
        """Set position cols content."""

        cls.reload_settings()
        cls._set_pos_cols_content(pos)
        cls.save_settings()

    @classmethod
    def _set_pos_cols_content(cls, pos):
        """Set position cols content."""

        cls.settings["pos_cols_content"] = pos

    @classmethod
    def get_international_time(cls):
        """Get international time setting."""

        cls.reload_settings()
        return cls.settings.get("international_time", False)

    @classmethod
    def set_international_time(cls, itime):
        """Set international time setting."""

        cls.reload_settings()
        cls._set_international_time(itime)
        cls.save_settings()

    @classmethod
    def _set_international_time(cls, hide):
        """Set international time setting."""

        cls.settings["international_time"] = hide

    @classmethod
    def get_language(cls):
        """Get locale language."""

        cls.reload_settings()
        locale = cls.settings.get("locale", "en_US")
        if locale == "en_US" and not os.path.exists(os.path.join(cls.config_folder, "locale", "en_US")):
            locale = None
        return locale

    @classmethod
    def set_language(cls, language):
        """Set locale language."""

        cls.reload_settings()
        cls._set_language(language)
        cls.save_settings()

    @classmethod
    def _set_language(cls, language):
        """Set locale language."""

        cls.settings["locale"] = language

    @classmethod
    def get_languages(cls):
        """Return languages."""

        languages = []
        base = localization.locale_path
        if os.path.exists(base):
            for file_obj in os.listdir(base):
                if os.path.isdir(os.path.join(base, file_obj)):
                    languages.append(file_obj)
        if len(languages) == 0 or "en_US" not in languages:
            languages.append("en_US")
        languages.sort()
        return languages

    @classmethod
    def set_debug(cls, enable):
        """Set debug level setting."""

        cls.reload_settings()
        cls.settings["debug"] = enable
        custom_app.set_debug_mode(enable)
        cls.save_settings()

    @classmethod
    def get_times(cls):
        """Get timestamp on files."""

        try:
            settings_time = os.path.getmtime(cls.settings_file)
            cache_time = os.path.getmtime(cls.cache_file)
            cls.settings_time = settings_time
            cls.cache_time = cache_time
        except Exception as e:
            debug(e)
            error("Could not get timestamp of file!")

    @classmethod
    def changed(cls):
        """Check if settings or cache have changed."""

        old_settings = cls.settings_time
        old_cache = cls.cache_time
        cls.get_times()
        try:
            changed = old_settings != cls.settings_time or old_cache != cls.cache_time
        except Exception:
            error("Could not compare timestamp of file!")
            changed = False
        return changed

    @classmethod
    def setup_setting_files(cls):
        """Get settings, cache, log, and FIFO location."""

        platform = util.platform()

        if platform == "windows":
            folder = os.path.expanduser("~\\.Rummage")
            if not os.path.exists(folder):
                os.mkdir(folder)
            plugin_folder = os.path.join(folder, 'plugins')
            if not os.path.exists(plugin_folder):
                os.mkdir(plugin_folder)
            cls.settings_file = os.path.join(folder, SETTINGS_FILE)
            cls.cache_file = os.path.join(folder, CACHE_FILE)
            cls.log = os.path.join(folder, LOG_FILE)
            cls.fifo = os.path.join(folder, '\\\\.\\pipe\\rummage')
            cls.config_folder = folder
        elif platform == "macos":
            old_folder = os.path.expanduser("~/Library/Application Support/Rummage")
            folder = os.path.expanduser("~/.Rummage")
            if os.path.exists(old_folder) and not os.path.exists(folder):
                import shutil
                shutil.move(old_folder, folder)
            if not os.path.exists(folder):
                os.mkdir(folder)
            plugin_folder = os.path.join(folder, 'plugins')
            if not os.path.exists(plugin_folder):
                os.mkdir(plugin_folder)
            cls.settings_file = os.path.join(folder, SETTINGS_FILE)
            cls.cache_file = os.path.join(folder, CACHE_FILE)
            cls.log = os.path.join(folder, LOG_FILE)
            cls.fifo = os.path.join(folder, FIFO)
            cls.config_folder = folder
        elif platform == "linux":
            folder = os.path.expanduser("~/.config/Rummage")
            if not os.path.exists(folder):
                os.mkdir(folder)
            plugin_folder = os.path.join(folder, 'plugins')
            if not os.path.exists(plugin_folder):
                os.mkdir(plugin_folder)
            cls.settings_file = os.path.join(folder, SETTINGS_FILE)
            cls.cache_file = os.path.join(folder, CACHE_FILE)
            cls.log = os.path.join(folder, LOG_FILE)
            cls.fifo = os.path.join(folder, FIFO)
            cls.config_folder = folder

        cls.settings_lock = FileLock(cls.settings_file + '.lock')
        cls.cache_lock = FileLock(cls.cache_file + '.lock')

        if not os.path.exists(cls.settings_file):
            cls.new_settings(cls.settings_file)
        if not os.path.exists(cls.cache_file):
            cls.new_cache(cls.cache_file)

    @classmethod
    def open_settings(cls):
        """Open settings file."""

        try:
            with cls.settings_lock.acquire(2):
                with codecs.open(cls.settings_file, "r", encoding="utf-8") as f:
                    cls.settings = json.loads(f.read())
        except Exception:
            errormsg(cls.ERR_LOAD_SETTINGS_FAILED)

        cls.update_settings()

    @classmethod
    def new_settings(cls, settings):
        """New settings."""

        default_settings = {'__format__': SETTINGS_FMT}

        try:
            with cls.settings_lock.acquire(2):
                with codecs.open(settings, "w", encoding="utf-8") as f:
                    f.write(json.dumps(default_settings, sort_keys=True, indent=4, separators=(',', ': ')))
        except Exception:
            # It's okay that we couldn't do it this time.
            pass

        return default_settings

    @classmethod
    def update_settings(cls):
        """Update settings."""

        updated = False
        settings_format = tuple([int(x) for x in cls.settings.get('__format__').split('.')])

        if settings_format < (2, 1, 0):
            updated = True
            searches = cls.settings.get("saved_searches", {})

            # Upgrade versions before format existed
            # TODO: Remove this in the future
            if isinstance(searches, list):
                searches = cls._update_search_object_to_unique(searches)

            # Remove old keys
            if "regex_support" in cls.settings:
                del cls.settings["regex_support"]

            # Convert list to dictionary
            for k, v in searches.items():
                new_search = {
                    "name": v[0],
                    "search": v[1],
                    "replace": v[2],
                    "flags": v[3],
                    "is_regex": v[4],
                    "is_function": v[5]
                }
                searches[k] = new_search
            cls.settings["saved_searches"] = searches

            # Ensure backup_type is an integer
            backup_type = cls.settings.get('backup_type')
            cls.settings["backup_type"] = 0 if backup_type is None or backup_type is False else 1

        if settings_format < (2, 2, 0):
            if 'editor' in cls.settings and isinstance(cls.settings['editor'], (list, tuple)):
                cls.settings['editor'] = ""

        # Update settings with any missing values
        for k, v in DEFAULT_SETTINGS.items():
            if k not in cls.settings:
                updated = True
                cls.settings[k] = copy.deepcopy(v)
            elif k == 'encoding_options':
                for k1, v1 in v.items():
                    if k1 not in cls.settings[k]:
                        updated = True
                        cls.settings[k][k1] = copy.copy(v1)

        if settings_format < tuple([int(x) for x in SETTINGS_FMT.split('.')]):
            updated = True
            cls.settings["__format__"] = SETTINGS_FMT

        if updated:
            cls.save_settings()

    @classmethod
    def open_cache(cls):
        """Open settings file."""

        success = False
        try:
            with cls.cache_lock.acquire(2):
                with codecs.open(cls.cache_file, "r", encoding="utf-8") as f:
                    cls.cache = json.loads(f.read())
            success = True
        except Exception:
            errormsg(cls.ERR_LOAD_CACHE_FAILED)
        if success:
            cls.update_cache()

    @classmethod
    def new_cache(cls, cache):
        """New settings."""

        default_cache = {'__format__': CACHE_FMT}

        try:
            with cls.cache_lock.acquire(2):
                with codecs.open(cache, "w", encoding="utf-8") as f:
                    f.write(json.dumps(default_cache, sort_keys=True, indent=4, separators=(',', ': ')))
        except Exception:
            # It's okay that we couldn't do it this time.
            pass

        return default_cache

    @classmethod
    def update_cache(cls):
        """Update settings."""

        cache_format = cls.cache.get('__format__')
        if cache_format is None:
            # Replace invalid cache
            cls.cache = cls.new_cache(cls.cache_file)
        if cache_format == '2.0.0':
            # Upgrade to 2.1.0
            pass

    @classmethod
    def get_config_folder(cls):
        """Return configuration folder."""

        return cls.config_folder

    @classmethod
    def get_fifo(cls):
        """Get FIFO pipe."""

        return cls.fifo

    @classmethod
    def reload_settings(cls):
        """Check if the settings have changed and reload if needed."""

        if cls.changed():
            debug("Reloading settings.")
            settings = None
            cache = None
            if cls.settings_file is not None:
                try:
                    with cls.settings_lock.acquire(2):
                        with codecs.open(cls.settings_file, "r", encoding="utf-8") as f:
                            settings = json.loads(f.read())
                    with cls.cache_lock:
                        with codecs.open(cls.cache_file, "r", encoding="utf-8") as f:
                            cache = json.loads(f.read())
                except Exception:
                    pass
            if settings is not None:
                cls.settings = settings
            if cache is not None:
                cls.cache = cache

    @classmethod
    def get_editor(cls, filename=None, line=None, col=None):
        """Get editor command and replace file, line, and col symbols."""

        cls.reload_settings()
        editor = cls.settings.get("editor", "")

        # Handle early, old dict format.
        if isinstance(editor, dict):
            editor = editor.get(util.platform(), "")

        if filename is None or line is None or col is None:
            return editor

        if isinstance(editor, (list, tuple)):
            # Handle old list format
            return [
                arg.replace(
                    "{$file}", filename
                ).replace(
                    "{$line}", str(line)
                ).replace(
                    "{$col}", str(col)
                ) for arg in editor
            ]
        else:
            # New string format
            return editor.replace(
                "{$file}", filename.replace('"', '\\"')
            ).replace(
                "{$line}", str(line)
            ).replace(
                "{$col}", str(col)
            ).replace(
                "{$col0}", str(col - 1)
            )

    @classmethod
    def set_editor(cls, editor):
        """Set editor command."""

        cls.reload_settings()
        cls._set_editor(editor)
        cls.save_settings()

    @classmethod
    def _set_editor(cls, editor):
        """Set editor command."""

        cls.settings["editor"] = editor

    @classmethod
    def get_single_instance(cls):
        """Get single instance setting."""

        cls.reload_settings()
        return cls.settings.get("single_instance", False)

    @classmethod
    def set_single_instance(cls, single):
        """Set single instance setting."""

        cls.reload_settings()
        cls._set_single_instance(single)
        cls.save_settings()

    @classmethod
    def _set_single_instance(cls, single):
        """Set single instance setting."""

        cls.settings["single_instance"] = single

    @classmethod
    def _update_search_object_to_unique(cls, searches):
        """Update search object."""

        import re

        not_word = re.compile(r'[^\w -]', re.UNICODE)
        new_search = {}

        for entry in searches:
            name = entry[0].strip()
            key_name = not_word.sub('', name).replace(' ', '-')
            entry = list(entry)

            # TODO: Remove in future
            # Upgrade old format for addition of replace feature
            if len(entry) == 3:
                entry.insert(2, '')
            if len(entry) == 4:
                entry.insert(3, '')
            if len(entry) == 5:
                entry.append(False)

            unique_id = 1
            unique_name = key_name
            while unique_name in new_search:
                unique_id += 1
                unique_name = "%s (%d)" % (key_name, unique_id)

            new_search[key_name] = tuple(entry)

        cls.settings["saved_searches"] = new_search
        cls.save_settings()
        return new_search

    @classmethod
    def add_search(cls, key, name, search, replace, flags, is_regex, is_function):
        """Add saved search."""

        cls.reload_settings()
        cls._add_search(key, name, search, replace, flags, is_regex, is_function)
        cls.save_settings()

    @classmethod
    def _add_search(cls, key, name, search, replace, flags, is_regex, is_function):
        """Add saved search."""

        searches = cls.settings.get("saved_searches", {})
        searches[key] = {
            "name": name,
            "search": search,
            "replace": replace,
            "flags": flags,
            "is_regex": is_regex,
            "is_function": is_function
        }
        cls.settings["saved_searches"] = searches

    @classmethod
    def get_search(cls):
        """Get saved searches or search at index if given."""

        cls.reload_settings()
        searches = cls.settings.get("saved_searches", {})
        return searches

    @classmethod
    def delete_search(cls, key):
        """Delete the search at given index."""

        cls.reload_settings()
        searches = cls.settings.get("saved_searches", {})
        if key in searches:
            del searches[key]
        cls.settings["saved_searches"] = searches
        cls.save_settings()

    @classmethod
    def get_chains(cls):
        """Get saved chains."""

        cls.reload_settings()
        return cls.settings.get("chains", {})

    @classmethod
    def add_chain(cls, key, searches):
        """Save chain."""

        cls.reload_settings()
        cls._add_chain(key, searches)
        cls.save_settings()

    @classmethod
    def _add_chain(cls, key, searches):
        """Save chain."""

        chains = cls.settings.get("chains", {})
        chains[key] = searches[:]
        cls.settings['chains'] = chains

    @classmethod
    def delete_chain(cls, key):
        """Delete chain."""

        cls.reload_settings()
        chains = cls.settings.get("chains", {})
        if key in chains:
            del chains[key]
        cls.settings["chains"] = chains
        cls.save_settings()

    @classmethod
    def get_alert(cls):
        """Get alert setting."""

        cls.reload_settings()
        return cls.settings.get("alert_enabled", True)

    @classmethod
    def set_alert(cls, enable):
        """Set alert setting."""

        cls.reload_settings()
        cls._set_alert(enable)
        cls.save_settings()

    @classmethod
    def _set_alert(cls, enable):
        """Set alert setting."""

        cls.settings["alert_enabled"] = enable

    @classmethod
    def init_notify(cls, first_time=False):
        """Setup notification."""

        pth = cls.get_config_folder()

        # Clean up old images
        png = os.path.join(pth, "rum-notify.png")
        icon = os.path.join(pth, "rum-notify.ico")
        icns = os.path.join(pth, "rum-notify.icns")
        for img in (png, icon, icns):
            try:
                if os.path.exists(img):
                    os.remove(img)
            except Exception:
                pass

        png = os.path.join(data.RESOURCE_PATH, "rummage_1024.png")
        icon = os.path.join(data.RESOURCE_PATH, "rummage.ico")
        icns = os.path.join(data.RESOURCE_PATH, "rummage.icns")

        if not os.path.exists(png):
            png = None

        if not os.path.exists(icon):
            icon = None

        if not os.path.exists(icns):
            icns = None

        # Set up notifications
        notifier = cls.get_term_notifier()
        if (
            os.path.isdir(notifier) and
            notifier.endswith('.app') and
            os.path.exists(os.path.join(notifier, 'Contents/MacOS/terminal-notifier'))
        ):
            notifier = os.path.join(notifier, 'Contents/MacOS/terminal-notifier')

        if util.platform() == "windows":
            img = icon
        elif util.platform() == "macos":
            img = icns
        else:
            img = png

        notify.setup_notifications(
            "Rummage",
            img,
            term_notify=notifier,
            sender=None,
            sound=cls.get_notify_sound(),
            sound_player=cls.get_notify_player()
        )

    @classmethod
    def get_notify(cls):
        """Get notification setting."""

        cls.reload_settings()
        return cls.settings.get("notify_enabled", True)

    @classmethod
    def set_notify(cls, enable):
        """Set notification setting."""

        cls.reload_settings()
        cls._set_notify(enable)
        cls.save_settings()

    @classmethod
    def _set_notify(cls, enable):
        """Set notification setting."""

        cls.settings["notify_enabled"] = enable

    @classmethod
    def get_platform_notify(cls):
        """Get all possible platform notification styles."""

        return NOTIFY_STYLES[util.platform()]

    @classmethod
    def get_notify_method(cls):
        """Get notification style."""

        cls.reload_settings()
        platform = util.platform()
        method = cls.settings.get("notify_method", NOTIFY_STYLES[platform][0])
        if method is None or method == "native" or method not in NOTIFY_STYLES[platform]:
            method = NOTIFY_STYLES[platform][0]
        return method

    @classmethod
    def set_notify_method(cls, notify_method):
        """Set notification style."""

        cls.reload_settings()
        cls._set_notify_method(notify_method)
        cls.save_settings()
        cls.init_notify()

    @classmethod
    def _set_notify_method(cls, notify_method):
        """Set notification style."""

        if notify_method not in ["native"]:
            notify_method = NOTIFY_STYLES[util.platform()][0]
        cls.settings["notify_method"] = notify_method

    @classmethod
    def get_term_notifier(cls):
        """Get term notifier location."""

        cls.reload_settings()
        return cls.settings.get('term_notifier', '')

    @classmethod
    def set_term_notifier(cls, value):
        """Set term notifier location."""

        cls.reload_settings()
        cls._set_term_notifier(value)
        cls.save_settings()
        cls.init_notify()

    @classmethod
    def _set_term_notifier(cls, value):
        """Set term notifier location."""

        cls.settings['term_notifier'] = value

    @classmethod
    def get_notify_sound(cls):
        """Get notifier sound."""

        cls.reload_settings()
        sound = cls.settings.get('notify_sound', '')
        player = cls._get_notify_player()
        if sound is None or not os.path.exists(sound) or not os.path.isfile(sound):
            sound = ''
        if os.path.splitext(sound)[1].lower() not in NOTIFY_EXT[player]:
            sound = ''
        return sound

    @classmethod
    def set_notify_sound(cls, value):
        """Set notifier sound."""

        cls.reload_settings()
        cls._set_notify_sound(value)
        cls.save_settings()
        cls.init_notify()

    @classmethod
    def _set_notify_sound(cls, sound):
        """Set notifier sound."""

        player = cls._get_notify_player()
        if sound is None or not os.path.exists(sound) or not os.path.isfile(sound):
            sound = ''
        if os.path.splitext(sound)[1].lower() not in NOTIFY_EXT[player]:
            sound = ''
        cls.settings['notify_sound'] = sound

    @classmethod
    def get_notify_player(cls):
        """Get notifier player."""

        cls.reload_settings()
        player = cls._get_notify_player()
        return player

    @classmethod
    def validate_player(cls, player):
        """Validate player."""

        if player is None or player not in NOTIFY_PLAYERS[util.platform()]:
            player = NOTIFY_PLAYERS[util.platform()][0]
        if util.platform() == "linux" and not which(player):
            player = None
            for p in NOTIFY_PLAYERS['linux']:
                if which(p):
                    player = p
                    break
        if player is None:
            # None exist, so just go with the first
            player = NOTIFY_PLAYERS[util.platform()][0]
        return player

    @classmethod
    def _get_notify_player(cls):
        """Get notifier player."""

        player = cls.settings.get('notify_player')
        player = cls.validate_player(player)
        return player

    @classmethod
    def set_notify_player(cls, player):
        """Set notifier player."""

        cls.reload_settings()
        cls._set_notify_player(player)
        cls.save_settings()
        cls.init_notify()

    @classmethod
    def _set_notify_player(cls, player):
        """Set notifier player."""

        player = cls.validate_player(player)
        cls.settings['notify_player'] = player

    @classmethod
    def get_search_setting(cls, key, default):
        """Get search history setting from cache."""

        cls.reload_settings()
        return cls.cache.get(key, default)

    @classmethod
    def set_toggles(cls, toggles, save=True):
        """Set toggles."""

        if save:
            cls.reload_settings()
        for t in toggles:
            key = t[0]
            value = t[1]
            if value is None:
                continue
            cls.cache[key] = value
        if save:
            cls.save_cache()

    @classmethod
    def set_strings(cls, strings, save=True):
        """Set strings."""

        if save:
            cls.reload_settings()
        for s in strings:
            key = s[0]
            value = s[1]
            if value is None:
                continue
            cls.cache[key] = value
        if save:
            cls.save_cache()

    @classmethod
    def set_history(cls, history, save=True):
        """Set history."""

        if save:
            cls.reload_settings()
        for i in history:
            key = i[0]
            value = i[1]
            if value is None:
                value = ""
            values = cls.cache.get(key, [])
            if value in values:
                values.remove(value)
            if values and values[0] == "":
                values.remove("")
            values.insert(0, value)
            if len(values) > (20 if value != "" else 21):
                del values[-1]
            cls.cache[key] = values
        if save:
            cls.save_cache()

    @classmethod
    def add_search_settings(cls, history, toggles, strings):
        """Add search settings to cache (more like history...but whatever)."""

        cls.reload_settings()
        debug(history)
        cls.set_history(history, False)
        cls.set_toggles(toggles, False)
        cls.set_strings(strings, False)
        cls.save_cache()

    @classmethod
    def get_backup_type(cls):
        """Get whether we should use folder backup or file backup."""

        cls.reload_settings()
        return cls.settings.get('backup_type', BACKUP_FILE)

    @classmethod
    def set_backup_type(cls, value):
        """Set backup type."""

        cls.reload_settings()
        cls._set_backup_type(value)
        cls.save_settings()

    @classmethod
    def _set_backup_type(cls, value):
        """Set backup type."""

        cls.settings['backup_type'] = value

    @classmethod
    def get_backup_ext(cls):
        """Get backup extension."""

        cls.reload_settings()
        return cls.settings.get('backup_ext', 'rum-bak')

    @classmethod
    def set_backup_ext(cls, value):
        """Set backup extension."""

        cls.reload_settings()
        cls._set_backup_ext(value)
        cls.save_settings()

    @classmethod
    def _set_backup_ext(cls, value):
        """Set backup extension."""

        cls.settings['backup_ext'] = value

    @classmethod
    def get_backup_folder(cls):
        """Get backup folder."""

        cls.reload_settings()
        return cls.settings.get('backup_folder', '.rum-bak')

    @classmethod
    def set_backup_folder(cls, value):
        """Set backup folder."""

        cls.reload_settings()
        cls._set_backup_folder(value)
        cls.save_settings()

    @classmethod
    def _set_backup_folder(cls, value):
        """Set backup folder."""

        cls.settings['backup_folder'] = value

    @classmethod
    def get_last_update_check(cls):
        """Get the last time an update check was performed."""

        cls.reload_settings()
        return cls.settings.get('last_update_check', None)

    @classmethod
    def set_last_update_check(cls, value):
        """Get the last time an update check was performed."""

        cls.reload_settings()
        cls.settings['last_update_check'] = value
        cls.save_settings()

    @classmethod
    def _set_check_updates(cls, value):
        """Set check updates."""

        cls.settings['check_updates'] = value

    @classmethod
    def set_check_updates(cls, value):
        """Set check updates."""

        cls.reload_settings()
        cls._set_check_updates(value)
        cls.save_settings()

    @classmethod
    def get_check_updates(cls):
        """Get check updates."""

        cls.reload_settings()
        return cls.settings.get('check_updates', False)

    @classmethod
    def _set_prerelease(cls, value):
        """Set check updates."""

        cls.settings['check_prerelease'] = value

    @classmethod
    def set_prerelease(cls, value):
        """Set prerelease."""

        cls.reload_settings()
        cls._set_prerelease(value)
        cls.save_settings()

    @classmethod
    def get_prerelease(cls):
        """Get check updates."""

        cls.reload_settings()
        return cls.settings.get('check_prerelease', False)

    @classmethod
    def get_update_options(cls):
        """Get the update options."""

        cls.reload_settings()
        return cls.settings.get('check_updates', False), cls.settings.get('check_prerelease', False)

    @classmethod
    def get_history_record_count(cls, history_types=None):
        """Get number of history items saved."""

        if history_types is None:
            history_types = []

        cls.reload_settings()
        count = 0
        for h in history_types:
            count += len(cls.cache.get(h, []))
        return count

    @classmethod
    def get_history(cls, history_types=None):
        """Get number of history items saved."""

        if history_types is None:
            history_types = []

        cls.reload_settings()
        history = {}
        for h in history_types:
            history[h] = cls.cache.get(h, [])
        return history

    @classmethod
    def clear_history_records(cls, history_types=None):
        """Clear history types."""

        if history_types is None:
            history_types = []

        cls.reload_settings()
        for h in history_types:
            if cls.cache.get(h, None) is not None:
                cls.cache[h] = []
        cls.save_cache()

    @classmethod
    def _set_extmatch(cls, value):
        """Set `extmatch`."""

        cls.settings['extmatch'] = value

    @classmethod
    def set_extmatch(cls, value):
        """Set `extmatch`."""

        cls.reload_settings()
        cls._set_extmatch(value)
        cls.save_settings()

    @classmethod
    def get_extmatch(cls):
        """Get `extmatch`."""

        cls.reload_settings()
        return cls.settings.get('extmatch', False)

    @classmethod
    def _set_brace_expansion(cls, value):
        """Set brace_expansion."""

        cls.settings['brace_expansion'] = value

    @classmethod
    def set_brace_expansion(cls, value):
        """Set brace_expansion."""

        cls.reload_settings()
        cls._set_brace_expansion(value)
        cls.save_settings()

    @classmethod
    def get_brace_expansion(cls):
        """Get brace_expansion."""

        cls.reload_settings()
        return cls.settings.get('brace_expansion', False)

    @classmethod
    def get_pattern_limit(cls):
        """Get pattern_limit."""

        cls.reload_settings()
        value = cls.settings.get('pattern_limit', DEFAULT_SETTINGS['pattern_limit'])
        if not isinstance(value, int):
            value = DEFAULT_SETTINGS['pattern_limit']
        return value

    @classmethod
    def set_pattern_limit(cls, value):
        """Set pattern_limit."""

        cls.reload_settings()
        cls._set_pattern_limit(value)
        cls.save_settings()

    @classmethod
    def _set_pattern_limit(cls, value):
        """Set pattern_limit."""

        if isinstance(value, int):
            cls.settings['pattern_limit'] = value

    @classmethod
    def _set_file_case_sensitive(cls, value):
        """Set file_case_sensitive."""

        cls.settings['file_case_sensitive'] = value

    @classmethod
    def set_file_case_sensitive(cls, value):
        """Set file_case_sensitive."""

        cls.reload_settings()
        cls._set_file_case_sensitive(value)
        cls.save_settings()

    @classmethod
    def get_file_case_sensitive(cls):
        """Get file_case_sensitive."""

        cls.reload_settings()
        return cls.settings.get('file_case_sensitive', False)

    @classmethod
    def _set_full_exclude_path(cls, value):
        """Set full_exclude_path."""

        cls.settings['full_exclude_path'] = value

    @classmethod
    def set_full_exclude_path(cls, value):
        """Set full_exclude_path."""

        cls.reload_settings()
        cls._set_full_exclude_path(value)
        cls.save_settings()

    @classmethod
    def get_full_exclude_path(cls):
        """Get full_exclude_path."""

        cls.reload_settings()
        return cls.settings.get('full_exclude_path', False)

    @classmethod
    def _set_full_file_path(cls, value):
        """Set full_file_path."""

        cls.settings['full_file_path'] = value

    @classmethod
    def set_full_file_path(cls, value):
        """Set full_file_path."""

        cls.reload_settings()
        cls._set_full_file_path(value)
        cls.save_settings()

    @classmethod
    def get_full_file_path(cls):
        """Get full_file_path."""

        cls.reload_settings()
        return cls.settings.get('full_file_path', False)

    @classmethod
    def _set_globstar(cls, value):
        """Set globstar."""

        cls.settings['globstar'] = value

    @classmethod
    def set_globstar(cls, value):
        """Set globstar."""

        cls.reload_settings()
        cls._set_globstar(value)
        cls.save_settings()

    @classmethod
    def get_globstar(cls):
        """Get globstar."""

        cls.reload_settings()
        return cls.settings.get('globstar', False)

    @classmethod
    def _set_matchbase(cls, value):
        """Set `matchbase`."""

        cls.settings['matchbase'] = value

    @classmethod
    def set_matchbase(cls, value):
        """Set `matchbase`."""

        cls.reload_settings()
        cls._set_matchbase(value)
        cls.save_settings()

    @classmethod
    def get_matchbase(cls):
        """Get `matchbase`."""

        cls.reload_settings()
        return cls.settings.get('matchbase', False)

    @classmethod
    def _set_minusnegate(cls, value):
        """Set `minusnegate`."""

        cls.settings['minusnegate'] = value

    @classmethod
    def set_minusnegate(cls, value):
        """Set `minusnegate`."""

        cls.reload_settings()
        cls._set_minusnegate(value)
        cls.save_settings()

    @classmethod
    def get_minusnegate(cls):
        """Get `minusnegate`."""

        cls.reload_settings()
        return cls.settings.get('minusnegate', False)

    @classmethod
    def import_settings(cls, obj):
        """Import settings."""

        cls.reload_settings()

        # Backup
        if 'backup_folder' in obj:
            cls._set_backup_folder(obj['backup_folder'])
        if 'backup_ext' in obj:
            cls._set_backup_ext(obj['backup_ext'])
        if 'backup_type' in obj:
            cls._set_backup_type(obj['backup_type'])

        # Updates
        if 'check_updates' in obj:
            cls._set_check_updates(obj['check_updates'])
        if 'check_prerelease' in obj:
            cls._set_prerelease(obj['check_prerelease'])

        if 'encoding_options' in obj:
            if 'chardet_mode' in obj['encoding_options']:
                cls._set_chardet_mode(obj['encoding_options']['chardet_mode'])
            cls._set_encoding_ext(obj['encoding_options'])

        # File matching
        if 'extmatch' in obj:
            cls._set_extmatch(obj['extmatch'])
        if 'brace_expansion' in obj:
            cls._set_brace_expansion(obj['brace_expansion'])
        if 'file_case_sensitive' in obj:
            cls._set_file_case_sensitive(obj['file_case_sensitive'])
        if 'full_exclude_path' in obj:
            cls._set_full_exclude_path(obj['full_exclude_path'])
        if 'full_file_path' in obj:
            cls._set_full_file_path(obj['full_file_path'])
        if 'globstar' in obj:
            cls._set_globstar(obj['globstar'])
        if 'matchbase' in obj:
            cls._set_matchbase(obj['matchbase'])
        if 'minusnegate' in obj:
            cls._set_minusnegate(obj['minusnegate'])
        if 'pattern_limit' in obj:
            cls._set_pattern_limit(obj['pattern_limit'])

        # Notifications
        update_notify = False
        if 'alert_enabled' in obj:
            cls._set_alert(obj['alert_enabled'])
        if 'notify_enabled' in obj:
            cls._set_notify(obj['notify_enabled'])
        if 'notify_method' in obj:
            cls._set_notify_method(obj['notify_method'])
            update_notify = True
        if 'term_notifier' in obj:
            cls._set_term_notifier(obj['term_notifier'])
            update_notify = True
        if 'notify_sound' in obj:
            cls._set_notify_sound(obj['notify_sound'])
            update_notify = True

        # Editor
        if 'editor' in obj:
            cls._set_editor(obj['editor'])

        # Single instance
        if 'single_instance' in obj:
            cls._set_single_instance(obj['single_instance'])

        # Locale
        if 'locale' in obj:
            cls._set_language(obj['locale'])

        # Hide columns
        if 'hide_cols_file' in obj:
            cls._set_hide_cols_file(obj['hide_cols_file'])
        if 'hide_cols_content' in obj:
            cls._set_hide_cols_content(obj['hide_cols_content'])

        # Alternate row colors for lists
        if 'alt_list_color' in obj:
            cls._set_alt_list_color(obj['alt_list_color'])

        # Position columns
        if 'pos_cols_file' in obj:
            cls._set_pos_cols_file(obj['pos_cols_file'])
        if 'pos_cols_content' in obj:
            cls._set_pos_cols_content(obj['pos_cols_content'])

        # International time
        if 'international_time' in obj:
            cls._set_international_time(obj['international_time'])

        # Regex
        if 'regex_mode' in obj:
            cls._set_regex_mode(obj['regex_mode'])
        if 'regex_version' in obj:
            cls._set_regex_version(obj['regex_version'])

        if 'chains' in obj:
            for k, v in obj['chains'].items():
                cls._add_chain(k, v)

        if 'saved_searches' in obj:
            for k, v in obj['saved_searches'].items():
                cls._add_search(
                    k,
                    v['name'],
                    v['search'],
                    v['replace'],
                    v['flags'],
                    v['is_regex'],
                    v['is_function']
                )

        cls.save_settings()

        # Update notifications
        if update_notify:
            cls.init_notify()

    @classmethod
    def save_settings(cls):
        """Save settings."""

        try:
            cls.settings['__format__'] = SETTINGS_FMT
            with cls.settings_lock.acquire(2):
                with codecs.open(cls.settings_file, "w", encoding="utf-8") as f:
                    f.write(json.dumps(cls.settings, sort_keys=True, indent=4, separators=(',', ': ')))
        except Exception:
            errormsg(cls.ERR_SAVE_SETTINGS_FAILED)

    @classmethod
    def save_cache(cls):
        """Save cache."""

        try:
            cls.cache['__format__'] = CACHE_FMT
            with cls.cache_lock.acquire(2):
                with codecs.open(cls.cache_file, "w", encoding="utf-8") as f:
                    f.write(json.dumps(cls.cache, sort_keys=True, indent=4, separators=(',', ': ')))
        except Exception:
            errormsg(cls.ERR_SAVE_CACHE_FAILED)

    @classmethod
    def unload(cls):
        """Perform needed actions when done with settings."""

        notify.destroy_notifications()
