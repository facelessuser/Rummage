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
from ..file_strip.json import sanitize_json
from .. import notify
from .. import localization
from ..localization import _
from .custom_app import debug, debug_struct, error
from .custom_app import init_app_log, set_debug_mode
from . generic_dialogs import errormsg
from .. import data
from .. import rumcore
from .. import portalocker
from .. import util

SETTINGS_FILE = "rummage.settings"
CACHE_FILE = "rummage.cache"
LOG_FILE = "rummage.log"
FIFO = "rummage.fifo"

NOTIFY_STYLES = {
    "osx": ["default", "growl"],
    "windows": ["default", "growl"],
    "linux": ["default", "growl"]
}


class Settings(object):
    """Handle settings."""

    filename = None
    allow_save = True
    debug = False

    @classmethod
    def load_settings(cls, debug_mode):
        """Load the settings."""

        cls.debug = debug_mode
        cls.settings_file, cls.cache_file, log = cls.get_settings_files()
        init_app_log(log)
        cls.settings = {}
        cls.cache = {}
        cls.settings_time = None
        cls.cache_time = None
        cls.get_times()
        if cls.settings_file is not None:
            try:
                locked = False
                with codecs.open(cls.settings_file, "r", encoding="utf-8") as f:
                    assert portalocker.lock(f, portalocker.LOCK_SH), "Could not lock settings."
                    locked = True
                    cls.settings = json.loads(sanitize_json(f.read(), preserve_lines=True))
                    assert portalocker.unlock(f), "Could not unlock settings."
                    locked = False
                with codecs.open(cls.cache_file, "r", encoding="utf-8") as f:
                    assert portalocker.lock(f, portalocker.LOCK_SH), "Could not lock cache file."
                    locked = True
                    cls.cache = json.loads(sanitize_json(f.read(), preserve_lines=True))
                    assert portalocker.unlock(f), "Could not unlock cache file."
                    locked = False
            except Exception:
                e = traceback.format_exc()
                try:
                    error(e)
                    if locked:
                        portalocker.unlock(f)
                    errormsg(_("Failed to load settings file!"))
                except Exception:
                    print(str(e))
        if cls.debug:
            set_debug_mode(True)
        localization.setup('rummage', os.path.join(cls.config_folder, "locale"), cls.get_language())
        debug_struct(cls.settings)
        debug_struct(cls.cache)
        cls.init_notify(True)

    @classmethod
    def is_regex_available(cls):
        """Check if regex support is available."""

        return rumcore.REGEX_SUPPORT

    @classmethod
    def set_regex_mode(cls, value):
        """Set regex support."""

        cls.reload_settings()
        if value in rumcore.REGEX_MODES and not rumcore.REGEX_SUPPORT:
            value = rumcore.REGEX_MODE
        cls.settings["regex_mode"] = value
        cls.save_settings()

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
        if 0 <= value <= 1:
            cls.settings["regex_version"] = value
            cls.save_settings()

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
        cls.settings["hide_limit"] = hide
        cls.save_settings()

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
        cls.settings["locale"] = language
        cls.save_settings()

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
        set_debug_mode(enable)
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
            settings = os.path.join(folder, SETTINGS_FILE)
            cache = os.path.join(folder, CACHE_FILE)
            log = os.path.join(folder, LOG_FILE)
            cls.fifo = os.path.join(folder, FIFO)
            cls.config_folder = folder
        elif platform == "linux":
            folder = os.path.expanduser("~/.config/Rummage")
            if not os.path.exists(folder):
                os.mkdir(folder)
            settings = os.path.join(folder, SETTINGS_FILE)
            cache = os.path.join(folder, CACHE_FILE)
            log = os.path.join(folder, LOG_FILE)
            cls.fifo = os.path.join(folder, FIFO)
            cls.config_folder = folder
        try:
            locked = False
            for filename in (settings, cache):
                if not os.path.exists(filename):
                    with codecs.open(filename, "w", encoding="utf-8") as f:
                        assert portalocker.lock(f, portalocker.LOCK_EX), "Could not lock file."
                        locked = True
                        f.write(json.dumps({}, sort_keys=True, indent=4, separators=(',', ': ')))
                        assert portalocker.unlock(f), "Could not unlock file."
                        locked = False
        except Exception:
            try:
                if locked:
                    portalocker.unlock(f)
            except Exception:
                pass
        return settings, cache, log

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
                        settings = json.loads(sanitize_json(f.read(), preserve_lines=True))
                        assert portalocker.unlock(f), "could not unlock settings."
                        locked = False
                    with codecs.open(cls.cache_file, "r", encoding="utf-8") as f:
                        assert portalocker.lock(f, portalocker.LOCK_SH), "Could not lock cache file."
                        locked = True
                        cache = json.loads(sanitize_json(f.read(), preserve_lines=True))
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
        editor = cls.settings.get("editor", [])
        if isinstance(editor, dict):
            editor = editor.get(util.platform(), [])

        return [
            arg.replace("{$file}", filename).replace("{$line}", str(line)).replace("{$col}", str(col)) for arg in editor
        ]

    @classmethod
    def set_editor(cls, editor):
        """Set editor command."""

        cls.reload_settings()
        cls.settings["editor"] = editor
        cls.save_settings()

    @classmethod
    def get_single_instance(cls):
        """Get single instance setting."""

        cls.reload_settings()
        return cls.settings.get("single_instance", False)

    @classmethod
    def set_single_instance(cls, single):
        """Set single instance setting."""

        cls.reload_settings()
        cls.settings["single_instance"] = single
        cls.save_settings()

    @classmethod
    def add_search(cls, name, search, replace, flags, is_regex):
        """Add saved search."""

        cls.reload_settings()
        searches = cls.settings.get("saved_searches", [])
        searches.append((name, search, replace, flags, is_regex))
        cls.settings["saved_searches"] = searches
        cls.save_settings()

    @classmethod
    def get_search(cls, idx=None):
        """Get saved searches or search at index if given."""

        value = None
        cls.reload_settings()
        searches = cls.settings.get("saved_searches", [])
        if idx is None:
            value = searches
        elif idx < len(searches):
            value = searches[idx]
        return value

    @classmethod
    def delete_search(cls, idx):
        """Delete the search at given index."""

        cls.reload_settings()
        searches = cls.settings.get("saved_searches", [])
        if idx < len(searches):
            del searches[idx]
        cls.settings["saved_searches"] = searches
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
        cls.settings["alert_enabled"] = enable
        cls.save_settings()

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
        cls.settings["notify_enabled"] = enable
        cls.save_settings()

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

        if notify_method not in ["native", "growl"]:
            notify_method = NOTIFY_STYLES[util.platform()][0]
        if notify_method in ["native"]:
            notify_method = "native"
        cls.reload_settings()
        cls.settings["notify_method"] = notify_method
        cls.save_settings()
        cls.init_notify()

    @classmethod
    def get_term_notifier(cls):
        """Get term notifier location."""

        cls.reload_settings()
        return cls.settings.get('term_notifier', '')

    @classmethod
    def set_term_notifier(cls, value):
        """Set term notifier location."""

        cls.reload_settings()
        cls.settings['term_notifier'] = value
        cls.save_settings()
        cls.init_notify()

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
    def get_history_record_count(cls, history_types=[]):
        """Get number of history items saved."""

        cls.reload_settings()
        count = 0
        for h in history_types:
            count += len(cls.cache.get(h, []))
        return count

    @classmethod
    def clear_history_records(cls, history_types=[]):
        """Clear history types."""

        cls.reload_settings()
        for h in history_types:
            if cls.cache.get(h, None) is not None:
                cls.cache[h] = []
        cls.save_cache()

    @classmethod
    def save_settings(cls):
        """Save settings."""

        try:
            locked = False
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
                errormsg(_("Failed to save settings file!"))
                error(e)
            except Exception:
                print(str(e))

    @classmethod
    def save_cache(cls):
        """Save cache."""

        try:
            locked = False
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
                errormsg(_("Failed to save cache file!"))
                error(e)
            except Exception:
                print(str(e))
