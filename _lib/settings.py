"""
Licensed under MIT
Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import codecs
import json
import sys
from os import mkdir
from os.path import expanduser, exists, join, getmtime
from _lib.custom_app import CustomApp, DebugFrameExtender, init_app_log
from _lib.file_strip.json import sanitize_json
from _lib.custom_app import debug, debug_struct, info, error
from _lib.generic_dialogs import *

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"

SETTINGS_FILE = "rummage.settings"
CACHE_FILE = "rummage.cache"
LOG_FILE = "rummage.log"

class Settings(object):
    filename = None
    allow_save = True

    @classmethod
    def load_settings(cls):
        cls.settings_file, cls.cache_file, log = cls.get_settings_files()
        init_app_log(log)
        cls.settings = {}
        cls.cache = {}
        cls.settings_time = None
        cls.cache_time = None
        cls.get_times()
        if cls.settings_file is not None:
            try:
                with codecs.open(cls.settings_file, "r", encoding="utf-8") as f:
                    cls.settings = json.loads(sanitize_json(f.read(), preserve_lines=True))
                with codecs.open(cls.cache_file, "r", encoding="utf-8") as f:
                    cls.cache = json.loads(sanitize_json(f.read(), preserve_lines=True))
            except Exception as e:
                errormsg("Failed to load settings file!\n\n%s" % str(e))
        debug(cls.settings)
        debug(cls.cache)

    @classmethod
    def get_times(cls):
        try:
            settings_time = getmtime(cls.settings_file)
            cache_time = getmtime(cls.cache_file)
            cls.settings_time = settings_time
            cls.cache_time = cache_time
        except Exception as e:
            debug(e)
            error("Could not get timestamp of file!")
            pass

    @classmethod
    def changed(cls):
        old_settings = cls.settings_time
        old_cache = cls.cache_time
        cls.get_times()
        try:
            changed =  old_settings != cls.settings_time or old_cache != cls.cache_time
        except:
            error("Could not compare timestamp of file!")
            changed = False
        return changed

    @classmethod
    def get_settings_files(cls):
        if _PLATFORM == "windows":
            folder = expanduser("~\\.rummage")
            if not exists(folder):
                mkdir(folder)
            settings = join(folder, SETTINGS_FILE)
            cache = join(folder, CACHE_FILE)
            log = join(folder, LOG_FILE)
        elif _PLATFORM == "osx":
            folder = expanduser("~/Library/Application Support/Rummage")
            if not exists(folder):
                mkdir(folder)
            settings = join(folder, SETTINGS_FILE)
            cache = join(folder, CACHE_FILE)
            log = join(folder, LOG_FILE)
        elif _PLATFORM == "linux":
            settings = SETTINGS_FILE
            cache = CACHE_FILE
            log = LOG_FILE
        try:
            for filename in [settings, cache]:
                if not exists(filename):
                    with codecs.open(filename, "w", encoding="utf-8") as f:
                        f.write(json.dumps({}, sort_keys=True, indent=4, separators=(',', ': ')))
        except Exception:
            pass
        return settings, cache, log

    @classmethod
    def reload_settings(cls):
        if cls.changed():
            debug("Reloading settings.")
            settings = None
            cache = None
            if cls.settings_file is not None:
                try:
                    with codecs.open(cls.settings_file, "r", encoding="utf-8") as f:
                        settings = json.loads(sanitize_json(f.read(), preserve_lines=True))
                    with codecs.open(cls.cache_file, "r", encoding="utf-8") as f:
                        cache = json.loads(sanitize_json(f.read(), preserve_lines=True))
                except Exception:
                    pass
            if settings is not None:
                cls.settings = settings
            if cache is not None:
                cls.cache = cache

    @classmethod
    def get_editor(cls, filename="${file}", line="${line}", col="${col}"):
        cls.reload_settings()
        editor = cls.settings.get("editor", [])
        if isinstance(editor, dict):
            editor = editor.get(_PLATFORM, [])

        return [arg.replace("{$file}", filename).replace("{$line}", str(line)).replace("{$col}", str(col)) for arg in editor]

    @classmethod
    def set_editor(cls, editor):
        cls.reload_settings()
        cls.settings["editor"] = editor
        cls.save_settings()

    @classmethod
    def add_search_settings(cls, history, toggles, strings):
        cls.reload_settings()
        debug(history)
        for i in history:
            key = i[0]
            value = i[1]
            if value is None or value == "":
                continue
            values = cls.cache.get(key, [])
            if value in values:
                values.remove(value)
            values.insert(0, value)
            if len(values) > 20:
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
    def get_search_setting(cls, key, default):
        cls.reload_settings()
        return cls.cache.get(key, default)

    @classmethod
    def save_settings(cls):
        try:
            with codecs.open(cls.settings_file, "w", encoding="utf-8") as f:
                f.write(json.dumps(cls.settings, sort_keys=True, indent=4, separators=(',', ': ')))
        except Exception as e:
            errormsg("Failed to save settings file!\n\n%s" % str(e))

    @classmethod
    def save_cache(cls):
        try:
            with codecs.open(cls.cache_file, "w", encoding="utf-8") as f:
                f.write(json.dumps(cls.cache, sort_keys=True, indent=4, separators=(',', ': ')))
        except Exception as e:
            errormsg("Failed to save settings file!\n\n%s" % str(e))
