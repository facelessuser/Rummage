"""
Import Settings Dialog.

Licensed under MIT
Copyright (c) 2013 - 2017 Isaac Muse <isaacmuse@gmail.com>

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
# from .app.custom_app import error
import re
from .localization import _
from .settings import Settings
from .generic_dialogs import errormsg  # , infomsg
from . import gui
from .. import util
from .overwrite_dialog import OverwriteDialog


class ImportSettingsDialog(gui.ImportSettingsDialog):
    """Import settings dialog."""

    BOOLEAN = ("alert_enabled", "debug", "hide_limit", "notify_enabled", "single_instance")
    STRING = ("backup_ext", "backup_folder", "term_notifier", "editor", "notify_method")
    INTEGER = ("backup_type", "regex_mode", "regex_version")
    RE_LITERAL_FLAGS = re.compile(r'[iuf]*')
    RE_REGEXP_FLAGS = re.compile(r'[iufsbewrpF]*')
    RE_STRING_REFS = re.compile(r'[\a\b\f\r\t\n\v]')
    RE_NAME = re.compile(r'[\w-]', re.UNICODE)

    BACK_SLASH_TRANSLATION = {
        "\a": '\\a',
        "\b": '\\b',
        "\f": '\\f',
        "\r": '\\r',
        "\t": '\\t',
        "\n": '\\n',
        "\v": '\\v'
    }

    def __init__(self, parent, obj):
        """Init ImportSettingsDialog."""

        super(ImportSettingsDialog, self).__init__(parent)
        self.localize()
        self.refresh_localization()

        self.m_import_panel.Fit()
        self.Fit()
        self.SetMinSize(self.GetSize())

        self.remember = False
        self.status = False
        self.settings = obj

    def localize(self):
        """Translate strings."""

        self.TITLE = _("Import Settings")
        self.GENERAL_SETTINGS = _("General settings")
        self.CHAINS = _("Chains")
        self.PATTERNS = _("Search/replace patterns")
        self.CANCEL = _("Close")
        self.IMPORT = _("Import")
        self.ERR_NO_SELECT = _("There are no settings selected for import!")
        self.IMPORT_FAIL = _("Could not import '%s'")
        self.IMPORT_DONE = _('Finished import!')

    def refresh_localization(self):
        """Localize dialog."""

        self.SetTitle(self.TITLE)
        self.m_general_settings_checkbox.SetLabel(self.GENERAL_SETTINGS)
        self.m_chains_checkbox.SetLabel(self.CHAINS)
        self.m_patterns_checkbox.SetLabel(self.PATTERNS)
        self.m_close_button.SetLabel(self.CANCEL)
        self.m_import_button.SetLabel(self.IMPORT)
        self.Fit()

    def is_bool(self, value):
        """Check if boolean."""

        return isinstance(value, bool)

    def is_integer(self, value, minimum=None, maximum=None):
        """Check if integer."""

        return (
            isinstance(value, int) and
            (minimum is None or value >= minimum) and
            (maximum is None and value <= maximum)
        )

    def is_string(self, value):
        """Check if string."""

        return isinstance(value, util.ustr)

    def is_dict(self, value):
        """Check if a dict."""

        return isinstance(value, dict)

    def is_list(self, value):
        """Check if a list."""

        return isinstance(value, list)

    def is_valid_flags(self, is_regex, flags):
        """Test if flags are valid."""

        return (self.RE_LITERAL_FLAGS if not is_regex else self.RE_REGEXP_FLAGS).match(flags) is not None

    def request_overwrite(self):
        """Request a settings overwrite."""

        if not self.remember:
            dlg = OverwriteDialog(self)
            dlg.ShowModal()
            self.remember = dlg.remember
            self.status = dlg.status
            dlg.Destroy()

        return self.status

    def import_bool(self, key, value):
        """Import boolean setting."""

        if not self.is_bool(value):
            value = None
        return value

    def import_str(self, key, value):
        """Import string setting."""

        if not self.is_string(value):
            value = None
        if value is not None:
            if key == "notify_method" and value not in Settings.get_platform_notify():
                value = None
            if key == "locale" and value not in Settings.get_languages():
                value = None
        return value

    def import_int(self, key, value):
        """Import integer setting."""

        minimum = None
        maximum = None
        if key == 'backup_type':
            minimum = 0
            maximum = 1
        elif key in "regex_mode":
            minimum = 0
            maximum = 3
        elif key in "regex_version":
            minimum = 0
            maximum = 1
        if not self.is_integer(value, minimum, maximum):
            value = None
        return value

    def import_chain(self, key, value):
        """Import chain setting."""

        chains = Settings.get_chains()
        bad_keys = set()
        if not self.is_dict(value):
            value = None
        else:
            for k, v in value.items():
                if not self.is_string(k) or self.RE_NAME.match(k) is None:
                    bad_keys.add(k)
                    continue

                if k in chains and not self.request_overwrite():
                    bad_keys.add(k)
                    continue

                if not self.is_list(v):
                    bad_keys.add(k)
                    continue

                for chain in v:
                    if not self.is_string(chain) or self.RE_NAME.match(chain) is None:
                        bad_keys.add(k)
                        break

        for k in bad_keys:
            del value[k]

        if not value:
            value = None
        return value

    def import_search(self, key, value):
        """Import search settings."""

        searches = Settings.get_search()
        bad_keys = set()
        if not self.is_dict(value):
            value = None
        else:
            for k, v in value.items():
                if not self.is_string(k) or self.RE_NAME.match(k) is None:
                    bad_keys.add(k)
                    continue

                if k in searches and not self.request_overwrite():
                    bad_keys.add(k)
                    continue

                if not self.is_dict(v):
                    bad_keys.add(k)
                    continue

                if "name" not in v or not self.is_string(v["name"]):
                    bad_keys.add(k)
                    continue

                if "is_regex" not in v or not self.is_bool(v["is_regex"]):
                    bad_keys.add(k)
                    continue

                if (
                    "flags" not in v or not self.is_string(v["flags"]) or
                    not self.is_valid_flags(v["is_regex"], v["flags"])
                ):
                    bad_keys.add(k)
                    continue

                if "is_function" not in v or not self.is_bool(v["is_function"]):
                    bad_keys.add(k)
                    continue

                if "replace" not in v or not self.is_string(v["replace"]):
                    bad_keys.add(k)
                    continue
                else:
                    v["replace"] = self.RE_STRING_REFS.sub(self.tx_refs, v["replace"])

                if "search" not in v or not self.is_string(v["search"]):
                    bad_keys.add(k)
                    continue
                else:
                    v["search"] = self.RE_STRING_REFS.sub(self.tx_refs, v["search"])

        for k in bad_keys:
            del value[k]

        if not value:
            value = None
        return value

    def tx_refs(self, m):
        """Translate references."""

        return self.BACK_SLASH_TRANSLATION[m.group(0)]

    def validate(self, key, value):
        """Validate settings."""

        if key in self.BOOLEAN:
            value = self.import_bool(key, value)

        elif key in self.STRING:
            value = self.import_str(key, value)

        elif key in self.INTEGER:
            value = self.import_int(key, value)

        elif key == "chains":
            value = self.import_chain(key, value)

        elif key == "saved_searches":
            value = self.import_search(key, value)

        return value

    def on_import_click(self, event):
        """Import settings."""

        general = self.m_general_settings_checkbox.GetValue()
        chains = self.m_chains_checkbox.GetValue()
        patterns = self.m_patterns_checkbox.GetValue()

        if not general and not chains and not patterns:
            errormsg(self.ERR_NO_SELECT)
            return

        import_obj = {}
        bad_keys = set()
        for k, v in self.settings.items():
            if k == 'chains' and chains:
                v = self.validate(k, v)
            elif k == 'saved_searches' and patterns:
                v = self.validate(k, v)
            elif k not in ('__format__', 'chains', 'saved_searches', 'debug') and general:
                v = self.validate(k, v)
            else:
                # Non-valid key, or we don't want to import it
                v = None
                continue

            if v is not None:
                # Okay to import
                import_obj[k] = v
            else:
                # Issue with validation
                bad_keys.add(k)

        self.m_results_textbox.SetValue(
            '\n'.join([(self.IMPORT_FAIL % k) for k in bad_keys]) + '\n' + self.IMPORT_DONE
        )

        if import_obj:
            Settings.import_settings(import_obj)
            self.m_import_button.Enable(False)

    def on_cancel_click(self, event):
        """Close window."""

        self.Close()
