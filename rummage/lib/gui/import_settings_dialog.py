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

CHAIN_TYPE = 0
SEARCH_TYPE = 1


class ImportSettingsDialog(gui.ImportSettingsDialog):
    """Import settings dialog."""

    BOOLEAN = (
        "alert_enabled", "check_updates", "check_prerelease", "debug",
        "hide_limit", "notify_enabled", "single_instance"
    )
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

        self.chain_remember = False
        self.chain_action = False
        self.search_remember = False
        self.search_action = False
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
        self.IMPORT_FAIL = _("ERROR: Could not import key '%s'")
        self.IMPORT_FAIL_CHAIN = _("ERROR: Could not import chain '%s'")
        self.IMPORT_FAIL_SEARCH = _("ERROR: Could not import search '%s'")
        self.IMPORT_SKIP_CHAIN = _("SKIPPED: Chain '%s'")
        self.IMPORT_SKIP_SEARCH = _("SKIPPED: Search '%s'")
        self.IMPORT_SUCCESS = _("SUCCESS: Imported '%s'")
        self.IMPORT_SUCCESS_CHAIN = _("SUCCESS: Imported chain '%s'")
        self.IMPORT_SUCCESS_SEARCH = _("SUCCESS: Imported search '%s'")
        self.IMPORT_DONE = _("=== Finished import! ===")
        self.OW_CHAIN = _("Overwrite the chain (%s)?")
        self.OW_SEARCH = _("Overwrite the search (%s)?")

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
            (maximum is None or value <= maximum)
        )

    def is_string(self, value):
        """Check if string."""

        return isinstance(value, str)

    def is_dict(self, value):
        """Check if a dict."""

        return isinstance(value, dict)

    def is_list(self, value):
        """Check if a list."""

        return isinstance(value, list)

    def is_valid_flags(self, is_regex, flags):
        """Test if flags are valid."""

        return (self.RE_LITERAL_FLAGS if not is_regex else self.RE_REGEXP_FLAGS).match(flags) is not None

    def request_overwrite(self, msg, ow_type):
        """Request a settings overwrite."""

        remember = self.search_remember if ow_type == SEARCH_TYPE else self.chain_remember

        if not remember:
            dlg = OverwriteDialog(self, msg)
            dlg.ShowModal()
            if ow_type == SEARCH_TYPE:
                self.search_remember = dlg.remember
                self.search_action = dlg.action
            else:
                self.chain_remember = dlg.remember
                self.chain_action = dlg.action
            dlg.Destroy()

        return self.search_action if ow_type == SEARCH_TYPE else self.chain_action

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
            if key == "term_notifier" and util.platform() != "osx":
                value = ""
        return value

    def import_int(self, key, value):
        """Import integer setting."""

        minimum = None
        maximum = None
        if key == 'backup_type':
            minimum = 0
            maximum = 1
        elif key == "regex_mode":
            minimum = 0
            maximum = 3
        elif key == "regex_version":
            minimum = 0
            maximum = 1
        elif key == 'chardet_mode':
            minimum = 0
            maximum = 2
        if not self.is_integer(value, minimum, maximum):
            value = None
        return value

    def import_encoding_options(self, key, value):
        """Import encoding options."""

        bad_keys = set()
        good_keys = set()
        new_value = {}
        if not self.is_dict(value):
            new_value = None
            bad_keys.add('encoding_options')
        else:
            for k, v in value.items():
                if k == "chardet_mode":
                    value = self.import_int(k, v)
                    if value is not None:
                        good_keys.add('encoding_options.%s' % k)
                    else:
                        bad_keys.add('encoding_options.%s' % k)
                    new_value[k] = v
                    continue

                if not self.is_list(v):
                    bad_keys.add(k)
                    continue

                for i in v:
                    if not self.is_string(i):
                        bad_keys.add('encoding_options.%s' % k)
                        break

                new_value[k] = v
                good_keys.add('encoding_options.%s' % k)

        for k in bad_keys:
            self.results.append(self.IMPORT_FAIL_CHAIN % k)

        for k in good_keys:
            self.results.append(self.IMPORT_SUCCESS_CHAIN % k)

        return new_value

    def import_chain(self, key, value):
        """Import chain setting."""

        chains = Settings.get_chains()
        bad_keys = set()
        skip_keys = set()
        good_keys = set()
        if not self.is_dict(value):
            value = None
        else:
            for k, v in value.items():
                if not self.is_string(k) or self.RE_NAME.match(k) is None:
                    bad_keys.add(k)
                    continue

                if k in chains and not self.request_overwrite(self.OW_CHAIN % k, CHAIN_TYPE):
                    skip_keys.add(k)
                    continue

                if not self.is_list(v):
                    bad_keys.add(k)
                    continue

                failed = False
                for chain in v:
                    if not self.is_string(chain) or self.RE_NAME.match(chain) is None:
                        failed = True
                        bad_keys.add(k)
                        break
                if failed:
                    continue

                good_keys.add(k)

        for k in bad_keys:
            self.results.append(self.IMPORT_FAIL_CHAIN % k)
            del value[k]

        for k in skip_keys:
            self.results.append(self.IMPORT_SKIP_CHAIN % k)
            del value[k]

        for k in good_keys:
            self.results.append(self.IMPORT_SUCCESS_CHAIN % k)

        if not value:
            value = None
        return value

    def import_search(self, key, value):
        """Import search settings."""

        searches = Settings.get_search()
        bad_keys = set()
        skip_keys = set()
        good_keys = set()
        if not self.is_dict(value):
            value = None
        else:
            for k, v in value.items():
                if not self.is_string(k) or self.RE_NAME.match(k) is None:
                    bad_keys.add(k)
                    continue

                if k in searches and not self.request_overwrite(self.OW_SEARCH % k, SEARCH_TYPE):
                    skip_keys.add(k)
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

                good_keys.add(k)

        for k in bad_keys:
            self.results.append(self.IMPORT_FAIL_SEARCH % k)
            del value[k]

        for k in skip_keys:
            self.results.append(self.IMPORT_SKIP_SEARCH % k)
            del value[k]

        for k in good_keys:
            self.results.append(self.IMPORT_SUCCESS_SEARCH % k)

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

        elif key == 'encoding_options':
            value = self.import_encoding_options(key, value)

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
        self.results = []
        for k, v in self.settings.items():
            if k == 'chains' and chains:
                v = self.validate(k, v)
            elif k == 'saved_searches' and patterns:
                v = self.validate(k, v)
            elif k not in ('__format__', 'chains', 'saved_searches', 'last_update_check', 'debug') and general:
                v = self.validate(k, v)
            else:
                # Non-valid key, or we don't want to import it
                v = None
                continue

            if v is not None:
                # Okay to import
                import_obj[k] = v
                self.results.append(self.IMPORT_SUCCESS % k)
            else:
                # Issue with validation
                self.results.append(self.IMPORT_FAIL % k)

        self.results.append(self.IMPORT_DONE)
        self.m_results_textbox.SetValue('\n'.join(self.results))

        if import_obj:
            Settings.import_settings(import_obj)
        self.m_import_button.Enable(False)

    def on_cancel_click(self, event):
        """Close window."""

        self.Close()
