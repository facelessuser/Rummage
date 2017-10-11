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
from __future__ import unicode_literals
import codecs
import json
import os
import traceback
import copy
from . import portalocker
from ..app import custom_app
from ..app.custom_app import debug, debug_struct, error
from ..generic_dialogs import errormsg
from .. import localization
from ..localization import _
from .. import data
from .. import notify
from ... import rumcore
from ... import util

DEV_MODE = False
SETTINGS_FILE = "rummage_dev.settings" if DEV_MODE else "rummage.settings"
CACHE_FILE = "rummage_dev.cache" if DEV_MODE else "rummage.cache"
LOG_FILE = "rummage.log"
FIFO = "rummage.fifo"

SETTINGS_FMT = '2.1.0'
CACHE_FMT = '2.0.0'

NOTIFY_STYLES = {
    "osx": ["default", "growl"],
    "windows": ["default", "growl"],
    "linux": ["default", "growl"]
}

BACKUP_FILE = 0
BACKUP_FOLDER = 1


class Settings(object):
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
    def load_settings(cls, debug_mode):
        """Load the settings."""

        cls.debug = debug_mode
        cls.localize()
        cls.settings_file, cls.cache_file, log = cls.get_settings_files()
        custom_app.init_app_log(log)
        cls.settings = {"__format__": SETTINGS_FMT}
        cls.cache = {"__format__": CACHE_FMT}
        cls.settings_time = None
        cls.cache_time = None
        cls.get_times()
        if cls.settings_file is not None:
            cls.open_settings()
            cls.open_cache()
        if cls.debug:
            custom_app.set_debug_mode(True)
        localization.setup('rummage', os.path.join(cls.config_folder, "locale"), cls.get_language())
        cls.localize()
        debug_struct(cls.settings)
        debug_struct(cls.cache)
        cls.init_notify(True)

    @classmethod
    def get_settings(cls):
        """Get the entire settings object."""

        cls.reload_settings()
        return copy.deepcopy(cls.settings)

    @classmethod
    def is_regex_available(cls):
        """Check if regex support is available."""

        return rumcore.REGEX_SUPPORT

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
    def get_hide_limit(cls):
        """Get hide limit setting."""

        cls.reload_settings()
        return cls.settings.get("hide_limit", False)

    @classmethod
    def set_hide_limit(cls, hide):
        """Set hide limit setting."""

        cls.reload_settings()
        cls._set_hide_limit(hide)
        cls.save_settings()

    @classmethod
    def _set_hide_limit(cls, hide):
        """Set hide limit setting."""

        cls.settings["hide_limit"] = hide

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
        base = os.path.join(cls.config_folder, "locale")
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
    def get_settings_files(cls):
        """Get settings, cache, log, and fifo location."""

        platform = util.platform()

        if platform == "windows":
            folder = os.path.expanduser("~\\.Rummage")
            if not os.path.exists(folder):
                os.mkdir(folder)
            plugin_folder = os.path.join(folder, 'plugins')
            if not os.path.exists(plugin_folder):
                os.mkdir(plugin_folder)
            settings = os.path.join(folder, SETTINGS_FILE)
            cache = os.path.join(folder, CACHE_FILE)
            log = os.path.join(folder, LOG_FILE)
            cls.fifo = os.path.join(folder, '\\\\.\\pipe\\rummage')
            cls.config_folder = folder
        elif platform == "osx":
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
            settings = os.path.join(folder, SETTINGS_FILE)
            cache = os.path.join(folder, CACHE_FILE)
            log = os.path.join(folder, LOG_FILE)
            cls.fifo = os.path.join(folder, FIFO)
            cls.config_folder = folder
        elif platform == "linux":
            folder = os.path.expanduser("~/.config/Rummage")
            if not os.path.exists(folder):
                os.mkdir(folder)
            plugin_folder = os.path.join(folder, 'plugins')
            if not os.path.exists(plugin_folder):
                os.mkdir(plugin_folder)
            settings = os.path.join(folder, SETTINGS_FILE)
            cache = os.path.join(folder, CACHE_FILE)
            log = os.path.join(folder, LOG_FILE)
            cls.fifo = os.path.join(folder, FIFO)
            cls.config_folder = folder

        if not os.path.exists(settings):
            cls.new_settings(settings)
        if not os.path.exists(cache):
            cls.new_cache(cache)

        return settings, cache, log

    @classmethod
    def open_settings(cls):
        """Open settings file."""

        try:
            locked = False
            with codecs.open(cls.settings_file, "r", encoding="utf-8") as f:
                assert portalocker.lock(f, portalocker.LOCK_SH), "Could not lock settings."
                locked = True
                cls.settings = json.loads(f.read())
                assert portalocker.unlock(f), "Could not unlock settings."
                locked = False
                cls.update_settings()
        except Exception:
            e = traceback.format_exc()
            try:
                error(e)
                if locked:
                    portalocker.unlock(f)
                errormsg(cls.ERR_LOAD_SETTINGS_FAILED)
            except Exception:
                print(str(e))

    @classmethod
    def new_settings(cls, settings):
        """New settings."""

        default_settings = {'__format__': SETTINGS_FMT}

        try:
            locked = False
            with codecs.open(settings, "w", encoding="utf-8") as f:
                assert portalocker.lock(f, portalocker.LOCK_EX), "Could not lock file."
                locked = True
                f.write(json.dumps(default_settings, sort_keys=True, indent=4, separators=(',', ': ')))
                assert portalocker.unlock(f), "Could not unlock file."
                locked = False
        except Exception:
            try:
                if locked:
                    portalocker.unlock(f)
            except Exception:
                pass

        return default_settings

    @classmethod
    def update_settings(cls):
        """Update settings."""

        settings_format = cls.settings.get('__format__')
        # if settings_format is None:
        #     # Replace invalid settings
        #     cls.settings = cls.new_settings(cls.settings_file)
        if settings_format < '2.1.0':
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

            # Update format
            cls.settings["__format__"] = SETTINGS_FMT
            cls.save_settings()

    @classmethod
    def open_cache(cls):
        """Open cache file."""

        try:
            locked = False
            with codecs.open(cls.cache_file, "r", encoding="utf-8") as f:
                assert portalocker.lock(f, portalocker.LOCK_SH), "Could not lock settings."
                locked = True
                cls.cache = json.loads(f.read())
                assert portalocker.unlock(f), "Could not unlock settings."
                locked = False
                cls.update_cache()
        except Exception:
            e = traceback.format_exc()
            try:
                error(e)
                if locked:
                    portalocker.unlock(f)
                errormsg(cls.ERR_LOAD_CACHE_FAILED)
            except Exception:
                print(str(e))

    @classmethod
    def new_cache(cls, cache):
        """New cache."""

        default_cache = {'__format__': CACHE_FMT}

        try:
            locked = False
            with codecs.open(cache, "w", encoding="utf-8") as f:
                assert portalocker.lock(f, portalocker.LOCK_EX), "Could not lock file."
                locked = True
                f.write(json.dumps(default_cache, sort_keys=True, indent=4, separators=(',', ': ')))
                assert portalocker.unlock(f), "Could not unlock file."
                locked = False
        except Exception:
            try:
                if locked:
                    portalocker.unlock(f)
            except Exception:
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
        """Return config folder."""

        return cls.config_folder

    @classmethod
    def get_fifo(cls):
        """Get fifo pipe."""

        return cls.fifo

    @classmethod
    def reload_settings(cls):
        """Check if the settings have changed and reload if needed."""

        if cls.changed():
            debug("Reloading settings.")
            settings = None
            cache = None
            if cls.settings_file is not None:
                locked = False
                try:
                    with codecs.open(cls.settings_file, "r", encoding="utf-8") as f:
                        assert portalocker.lock(f, portalocker.LOCK_SH), "Could not lock settings."
                        locked = True
                        settings = json.loads(f.read())
                        assert portalocker.unlock(f), "could not unlock settings."
                        locked = False
                    with codecs.open(cls.cache_file, "r", encoding="utf-8") as f:
                        assert portalocker.lock(f, portalocker.LOCK_SH), "Could not lock cache file."
                        locked = True
                        cache = json.loads(f.read())
                        assert portalocker.unlock(f), "could not unlock cache file."
                        locked = False
                except Exception:
                    try:
                        if locked:
                            portalocker.unlock(f)
                    except Exception:
                        pass
            if settings is not None:
                cls.settings = settings
            if cache is not None:
                cls.cache = cache

    @classmethod
    def get_editor(cls, filename="{$file}", line="{$line}", col="{$col}"):
        """Get editor command and replace file, line, and col symbols."""

        cls.reload_settings()
        editor = cls.settings.get("editor", "")

        # Handle early, old dict format.
        if isinstance(editor, dict):
            editor = editor.get(util.platform(), "")

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
            filename = filename.replace('"', '\\"')
            return editor.replace("{$file}", filename).replace("{$line}", str(line)).replace("{$col}", str(col))

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
        """Setup growl notification."""

        pth = cls.get_config_folder()

        # Clean up old images
        png = os.path.join(pth, "Rummage-notify.png")
        icon = os.path.join(pth, "Rummage-notify.ico")
        icns = os.path.join(pth, "Rummage-notify.icns")
        for img in (png, icon, icns):
            try:
                if os.path.exists(img):
                    os.remove(img)
            except Exception:
                pass

        # New file names
        png = os.path.join(pth, "rum-notify.png")
        icon = os.path.join(pth, "rum-notify.ico")
        icns = os.path.join(pth, "rum-notify.icns")

        try:
            if not os.path.exists(png):
                with open(png, "wb") as f:
                    f.write(data.get_image('rummage_hires.png').GetData())
        except Exception:
            png = None

        try:
            if not os.path.exists(icon):
                with open(icon, "wb") as f:
                    f.write(data.get_image('rummage_tray.ico').GetData())
        except Exception:
            icon = None

        try:
            if not os.path.exists(icns):
                with open(icns, "wb") as f:
                    f.write(data.get_image('rummage.icns').GetData())
        except Exception:
            icns = None

        # Set up notifications
        notifier = cls.get_term_notifier()
        if (
            os.path.isdir(notifier) and
            notifier.endswith('.app') and
            os.path.exists(os.path.join(notifier, 'Contents/MacOS/terminal-notifier'))
        ):
            notifier = os.path.join(notifier, 'Contents/MacOS/terminal-notifier')
        notify.setup_notifications(
            "Rummage",
            png,
            icon,
            (notifier, None, icns)
        )
        notify.enable_growl(cls.get_notify_method() == "growl" and notify.has_growl())

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

        if notify_method not in ["native", "growl"]:
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
    def get_search_setting(cls, key, default):
        """Get search history setting from cache."""

        cls.reload_settings()
        return cls.cache.get(key, default)

    @classmethod
    def add_search_settings(cls, history, toggles, strings):
        """Add search settings to cache (more like history...but whatever)."""

        cls.reload_settings()
        debug(history)
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
        for t in toggles:
            key = t[0]
            value = t[1]
            if value is None:
                continue
            cls.cache[key] = value
        for s in strings:
            key = s[0]
            value = s[1]
            if value is None:
                continue
            cls.cache[key] = value

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

        # Editor
        if 'editor' in obj:
            cls._set_editor(obj['editor'])

        # Single instance
        if 'single_instance' in obj:
            cls._set_single_instance(obj['single_instance'])

        # Locale
        if 'locale' in obj:
            cls._set_language(obj['locale'])

        # Hide limit panel
        if 'hide_limit' in obj:
            cls._set_hide_limit(obj['hide_limit'])

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
            locked = False
            cls.settings['__format__'] = SETTINGS_FMT
            with codecs.open(cls.settings_file, "w", encoding="utf-8") as f:
                assert portalocker.lock(f, portalocker.LOCK_EX), "Could not lock settings."
                locked = True
                f.write(json.dumps(cls.settings, sort_keys=True, indent=4, separators=(',', ': ')))
                assert portalocker.unlock(f), "could not unlock settings."
                locked = False
        except Exception:
            e = traceback.format_exc()
            try:
                if locked:
                    portalocker.unlock(f)
                errormsg(cls.ERR_SAVE_SETTINGS_FAILED)
                error(e)
            except Exception:
                print(str(e))

    @classmethod
    def save_cache(cls):
        """Save cache."""

        try:
            locked = False
            cls.cache['__format__'] = CACHE_FMT
            with codecs.open(cls.cache_file, "w", encoding="utf-8") as f:
                assert portalocker.lock(f, portalocker.LOCK_EX), "Could not lock cache file."
                locked = True
                f.write(json.dumps(cls.cache, sort_keys=True, indent=4, separators=(',', ': ')))
                assert portalocker.unlock(f), "could not unlock cache file."
                locked = False
        except Exception:
            e = traceback.format_exc()
            try:
                if locked:
                    portalocker.unlock(f)
                errormsg(cls.ERR_SAVE_CACHE_FAILED)
                error(e)
            except Exception:
                print(str(e))

    @classmethod
    def unload(cls):
        """Perfrom needed actions when done with settings."""

        notify.destroy_notifications()
