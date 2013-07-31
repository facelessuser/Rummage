# -*- coding: utf-8 -*-
"""
Messages
https://gist.github.com/facelessuser/5749982

Licensed under MIT
Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import wx
import re
from collections import namedtuple
from wx.lib.embeddedimage import PyEmbeddedImage


# Styles
INFO = 0
PROMPT = 1
WARN = 2
ERROR = 3

# Icons
DEFAULT_ICON_SIZE = 64
DEFAULT_TEXT_MIN_SIZE = 250
DEFAULT_TEXT_MAX_SIZE = 500

HAS_CAPTION = re.compile(r"([^\r\n]+)(?:\r?\n){2,}(.*)", re.DOTALL | re.UNICODE)


# Icons by Isaac Muse
Info = PyEmbeddedImage(
    "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"
    "ZW17eYUAAAAASUVORK5CYII=")

#----------------------------------------------------------------------
Warn = PyEmbeddedImage(
    "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"
    "z36GQFrk1QAAAABJRU5ErkJggg==")

#----------------------------------------------------------------------
Error = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAABmJLR0QA/wD/AP+gvaeTAAAA"
    "CXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH3QYJBhYF+EMikQAAAB1pVFh0Q29tbWVudAAA"
    "AAAAQ3JlYXRlZCB3aXRoIEdJTVBkLmUHAAAUrklEQVR42u1beZAcV33+3tHdM7sze2nRSiuv"
    "ZMmyypduaS3bGGEsx9gEqiApCBDKQIAihISiSIoq4sTGKIgjguKyQpVT8IdDYhsDIdhlGQKY"
    "I3FiJMveFUYsq8uSJa2O1e7OTB/vyh/9Xu+b2V3hSwYqTNWrnunp6fd+3+/7na8H+P3r96//"
    "1y/yUkwyXK2SnUIEPYTQtzcamZ3XDeOPf29vD0a1xqjW8s4s0+d7bfx83Xh7qcQuoJS+sV7X"
    "APRD5fJrzxjzih0rVqzvXLZscTRvXhfjPFRpSuqnT2e1o0cnagcOHGbAPgL89/zVq7+Jxx47"
    "OVytksekZO+IY/k7wYAd5XL03kYj+1hPz/z2JLmtZ/36Ny654YZ5y7dswaLBQYAQEJJPq6WE"
    "SlMoIWB0ruzx0VFz6JFHyC+/9z0c+clP0hB4kIbh5/9mYuKHO8rl6M/jOP2tBGB7qRR+KEmy"
    "7aXSWwTnH1v5zncuW/O2txkeRcQohaCtDbxcBosisDAEoRTGGGghoLMMMk0hkwQyjiEaDRil"
    "QIMAow89pB+/+25aP3GiUQI+89eNxt+9mECwF3qD94UhfUwp84ddXa+7Bnh0zbvf/Zbrtm7t"
    "6lm6lBCS65oGAQiloJQChABawygFoxS0lDkI9miUAux5Ua+j3NNDVtx0E+ZddBE/MTz8iquU"
    "up0AeFjKH2wvlcKHpVS/MQZ8pVwuvSOOs21tbUPzV6++bNMHPgCjFMJKBbxUAosi8CgqtM6C"
    "IAeD89wMjIFWCkZKKCGg0hRaCMg0zQFoNCDjGCrLIOp1EM4x8sADZnTnTgitGyGl194M7Lli"
    "asr8RhhwTRS9eXMU7Vl3yy3zVrzmNQRag4UhKGP5oBSEUhBCmpHWGkbKnAVSFkNLCSMEKOeg"
    "QQDOOQjngDEwWiOr1VDp6yN9q1aRE7t28cSY9x7Qeul3hfiWY+JLBsCnqtX7FKV/e/X734+O"
    "/n5COZ8WnLFcaCc8Ic3Caz1tBhYILUT+XmvwKMpNwjcLAIxziHodxhgs2riRnHnySRhjVl3H"
    "+bs+EcefuS2KgkeUek6hkz4f4T9ZqQxTxv5o8D3vQVAugzIGWKFgbds4LTshpIROU6gsg7ZD"
    "pWlO+yzLrxECQblcCE20BtEaMAYwBqpeB7QGIwQsCLD6llvAo4jwMOz7eLWafjRN9fZSKTyv"
    "AHyio2OUcX7JJW94A2FBAEpIsVgfBEgJOHpbT2+kzIVNU+g0hcmy6e+EAGEMWspcYMsQaA1i"
    "P6skybMnSkEZA48iXPamNyGgNAiDgG7t6Mg+lCTqtigKzgsAn+zo2BUwtmTBmjWs3NkJSkix"
    "OOO079m0UQrGUdsJ6oS2nx0wRgjIWg3ZqVNIxsYgpqags6zwHdn4eAFwEIb53IQgCEMsu+km"
    "MMZ4xLn+h87OxkfTVAxXq8/KwT/rTPDTHR13McbWBe3t6Fu5clpLvta9Udi3zXG1MaDGAJTC"
    "AIVfMNbBOY1rKQGloJKkAMkABcOIUmClErSUoISAMoa27m7MX7kSY8PDHISIbZ2dT18xMTHw"
    "ojjBHeVytLmt7ToTBJ/ljGHxNdeAWQ/NPKdXeHzf81vvT3JJC9CgdS64pbjxACvAs5+1Urm5"
    "WKdIOQes2fmRpNTdjWRiArLRYASobomi5Z8Ngm/dmWUvDIAHpFTXVyqjIaWm0tNDupctA2Ms"
    "F57S4tg0XATwbIwAIMYUJoO5mGOdJzwzchGhACEMp0FyCZVNpxtjY9AASYFVo8B/3AScPley"
    "9GtN4NPd3d9llMogCHjXkiUwQgCe1ze+AE4gSnMnaOlPHM0phSEkzwiBXJO2BjCe0yuE9wBy"
    "EcFkGdJaDbRcLuoKZwqlahWMsTzbBHRKyI8+nCTtz4sB20sldnW5fDGLos9GjFHOObqXLwej"
    "FKyF/s4rUysc9ZIf3xMRYwphm8zBat4HtInivpYtOKJWgzEGhLH8e2NQHxuDaDSghAAhhBBj"
    "+B9EUfn1wI8fmIMFc0aBDyWJKofhNyNKFeUc5a4umCxrivW+dmY4P4+28GzbhUd45/2Q2XTe"
    "fmeEaGKBA06cPQs5OQnCcj1qIRBWKoWJEsYQM/bhcxVOfC7tT7W3X4QwvIwRgoBzhJVKoQm0"
    "xOdCeEoLE3DUdJGA2AgAQvKjNQ9YVsCYnOI+sN48Wsp8Lm9OojWyiQlQISCzDERr8DAE4xwa"
    "QGAMKRlj/rG39xPt9fptswFB59J+O6VfCglRjDGAUrAgyBfjp7K+phwglgFPpSmGFyzIr7ca"
    "dE7OaZt4WkbLvRxj9iqF0eXLm8FuMZf01ClkZ8+CGANmHbAzUcYYEsY+MBcL5jSBhLEtjFLm"
    "bsIoneH0jLcg4sKYlNinNRZu3oxNV12F4b4+UBfyfKE9b19ou2UMKYVlW7Zg/eAg9l96aTGn"
    "bwbuvUnTvLqUshDcHgnnvLS1u/v6r5TL/Nc6wX++/PLo5Uq9M4qi1waMIQgCUEoRtreDMwbK"
    "OZh1dH4IdLH/RBRh/g03YOPGjahUKujq6sLjZ89iwcRE7rVtPkC0LkJjUx1h3z8hJZZdfz3W"
    "rl2LakcHOqpV7MsyVI8ezRMk10OwQ7k0WyloL/abfD5lgJddp/W/tOYFMxjwZ3v3pobzP2WE"
    "KGYFY5RO27+zxZYFO5tcmKa4uL09nxhA38KFGNy0CU/29+cs8Wy7YE/L+z1CYKkV3iVMCwcG"
    "cMGuXfl97XXOHJ3pEQBQKneANh+huTOkgvMbZusbzBoGN3d0fLnMOQ85J4xS8CAoQh+jdJoF"
    "dgIX9iiloABqTz2Fcn8/gnnzQAhBpVpFZ2cndk9Oon9yctopesMxYXer8DZ/2PuRj+SfbaWo"
    "bRPFZ4LMsry/6FJsY6DzNJyklLIllH7paq0Tv29AW9tbACIEQUgZI04oYhMfo1S+YOewrO03"
    "JUF2PHPPPWiMjBRMWNDfjw2Dg9izaFHBAOpMwf5mt5S4sFV4QrDvttum5/XDsO0vFFHDmOa8"
    "xOYmjFJEhOCSIHjrkiVLwjlN4NUbNrBtvb2vDYDCrovmhp3MhaOi5vcFt4mL+/7Yvfci9kBY"
    "uGgR1g8OYs/AwHR2aEPbbqWw5FWvmiH8yO23T1/nZ4vGgFizc47R9R0dCP5glEpD6dXrSiUz"
    "JwAHjh/nhPN1gYvXrZmdF+aMr4mWbM5Pjo7fc8+sIDw+MABqDCiAXVJi8SzC77/jjjzb80Ot"
    "ny3a98SYQngn8Iz3jBFByIobhobSOQG4rL1da+AiQoh09IdzJJROJzAthUjhHFtCo6PsyXvv"
    "RfKrXzWBsGFwELsXL8YTxmDJli0zhD+4dWvuK2xF6Jff/rxOyCL5soyF35LLzxFDad8584CF"
    "Bw9mEugBIYR4JlDczB92sS7tdSwgfqnrGAPg1H33IfVAWLBoEdZu3Ii+zZuxZs2aJuEPf/zj"
    "OcVbI47PMqt1tGjbrdXZvycDEYRUzwnAFVNThjHWblwj00fSoelP5Ko4axJG61xbzixc6mo/"
    "n/7615GOjhYg9F9wAdatW1cITyjFkW3binpfW09eaN6xy7bFimNrH6KFFQgCV5iFrVsBM/IA"
    "YYw2hBRdG+L5A+Id3XmHvvHobzzfUIQ6m++fuf9+TB45Ml0G2+8IpTj6qU/lJbMQzVme8ytA"
    "TmfLysLZtSgGs6xTEwJNqT4nAMPVKs2MSYyr1Z2m/eGj609oGyBoaXE5UzDGwAB4ghCU5s8v"
    "NOilbHjm5S+fji7uPsbkwNuaBB7NnU+CryS/FU8ISBAUhZcGzl0MDff1RRoYV8bAeD07X0gQ"
    "UnxXTO6BMgMY5zS1xhOUove66xBF0XQ/0LGDEFywZAmevPTS6cUzVgjeSvEmIFq17n2mYQhj"
    "DJQxRmldd0XorACc0Bo1KQ9qQpgGckHdjV1Tw5+gZfLinO38FBpjDENhiPnXX4+NGzc2NUXS"
    "luiw/sorMbRqVd4itwD74MJjZavWC8AdqQCAc2gLgNB67JwAsI4OdULKJxMAylK2YKjTvD0W"
    "uz3+OSe4Dw6lGApDLLAFkhOeUIrjd96J8Z07kR4+3Bwir7wSe1euBGUMxt3Tmwv+PE4ibx2F"
    "9qMo33M0BtIYpErt/6cLL2ybE4BXjo6K+8bHf5YAELnNwBCSH2dsq04vwGlEe2C5hQ5HEfpv"
    "vBEbNmxoEv6ZO+8EwhDgHOMPPID00KFmEDZtwlOrV+eRxgpc+CbXVm9lofe9AUCiCJoQCK0h"
    "AHYyy3ZNBIE+VxgEgFgLMSG0NsoyAd6EpuWZluKcbwb2895SCYte/eoZwh/54hcBxvLfWy2f"
    "/s53kMwCwr61a3Mn6s3vNO2ubV0TIQSkVCrCspASDWNw3/j4Q685fjw9Zxi8Zt688aksG0q1"
    "1kJrKOuslDdZsZBZJnfjF21tuGAW4Q9/7nM5hV2LjLHCvE5++9uIDx5sAmHjVVdh/+BgXvc4"
    "U/Q3mn179xhIowhaa2RKQRhjjJQTABqtJXErAObNAwPxz2u1BzNCWGYF19NhpNjlmcEE7/2+"
    "SgUDN988w+YPbN+e/94mOVrrvJFhTJH0nPjGN9DYv38GEw5u2gRi54a3ltmUQCsVKCkhhEAm"
    "BFKtzak4fnRDR8fp1jxgRj/gwePH1eEsK2/q7n5rQCkCSgn36v+iC+SVnX5ucKqjA/2vf/20"
    "8EqBMIZfbdvWHLfdVrlLqbWGtrnD5NAQogULEHR3gxCCakcHqtUq9mmNyuHD0Jba2v5Ge7+n"
    "pRKk1pBpijhNUUsSTGhN7j969KNblPrZz1q2z2ftCfaF4dPj9fr3EilNqjWES0tbWKCNgXJp"
    "qs34eqemsNSL/4Qx/OKOO/LrhZhevBtu+8v1/u29nv7a11AbGSmKn/6BASx89NE8o7PXaLce"
    "uxYEAQznUEohkxJxliFRSss0HRuT8siOLJPPpiNEOrWuPTI1NbW+t/dNAaXgXmPUdYH8IoR6"
    "SQlhDJNDQyjNn4/yokUYvvXW3DHahMoB1dS1ccLbhMkdxx9/HKX+fkS9vdj1wQ/mwgsxQ/ta"
    "KWgAtK0NIk2RpSnqcYxGlqEuJXnqzJm7lDEPj0t59tnsC5hnjEkYcKZRrz/WTun6SErKOQfn"
    "HBQAtZp16a12fTrb4QEhOHD33Xj6/vvzO0oJMFY0QY3rBPk7xG54bDDGYP9Xv1rEfbf/VwBn"
    "/YgmBLyzE2m9DiEE4izLh1ImESJ+8MyZHwE4OFs0n2trjERA8ujk5KH1vb1/wikFt5rmzu5d"
    "YTJLJubOa9ewnC1qeOD59u+zQNsOk8qy3Fn6pqM1lFIAIWAdHRBJgixNkSYJpuIY9SxDTUoy"
    "dPLkZ8al/J9E6yPPaW9QArUKYxdfyHmpHEWXEEoJ81rhzAntFR/GttKaHF0r7M4EPOfnl9La"
    "MwGjNZT77AntrkEYgpTLkEmCNEmQpGkufJKgJoRuJMkz/3rs2F2J1j8FoJ7z9nhmTP2JWu30"
    "xq6um1kYBgYglJDcDFqLE3f0H35oiTlN2nc09rXvsaAQtlXz9jtarcJQiixNIdIUjThGI00x"
    "1WigJgRqSpHPj4y8gwNPa+DQ830+YDJibODJs2f/8/Kurj8OSqW8QrO9PL8ebyqaSPPTKcbb"
    "pGiyYV/7HguMbb46MJQ9p7SGZgy0owNKCIgsQxbHSJIE9TjGZL2OuhBoSIlfjo197liSHE2M"
    "+aGXLz1nAIgyZiwALg6E+GV3qXQtpRS8ra3o1BQPRLSkws2sNzOd3Wwm4IfIFrprAKRSAYIA"
    "MssgswxpHCNOEtTiGLU4Rl0IJFlmJmq1//23Y8e+lhmzC8DpF/qcYJYZow4libyQc5SD4HKt"
    "NUgUgZRKubOzzsjR3/UQiKd97TpAPhNsSVxo3Qrt+wTDGEilkhc2UiKzwidxjEYc55S3Ti/O"
    "Ml1P02M7Dhy41Qq+58V6UPKUAeYPTU3tXxFFXWEQLNdS5nk5Y2BtbXlYtGC4fQTn4Wc1gdmo"
    "74AAgFIJtFKBYQxaCKTW1tM4RhzHqFnBfc3HWXb6CyMjf2GL2R/MFvZeyJOiRwBcuGdy8onF"
    "jNGoVLpcCZFng0pBASCcg1cqQBQVjYwi0XEOz7d/lxAxlmdxpRJoezsM5zDGQNrnhoUQyJIE"
    "SaOBuhV+Ko5RSxI0pEQmBOpJcugLIyN/ZYX+AYDkxQYAAA4DWPrzqalftCk12lupXKuyzEil"
    "iLJpsRAiT48JgQkCoFTKGdLWBtrWBpTLoOUySLkMlMswFixj8waRpnkhk6YQWYY0SRAnSU73"
    "OEa90cBko4FGmiKR0sRakzNnz37/y/v3b7Vr/C8AZ87X0+IEQARgS4XSdkope9eKFV8Ow7Cd"
    "M0bCKEKpVEIYhog4RymKEAYBgiBAwDmofUqctT4/7CVD2mpeKYVMCGRZhkzKHIg0RSYlhJTI"
    "pNTCGLrr8OHbHxkfH7J3+imAE+f7cXliU+hXckI6pTH67QMDt/T09r4uAgxnjDDOEUURojAE"
    "DwIEjCHgPH++wNYUDoDiT0PW40ul8iEEhFI5AFkGaYsyKaXJANKYmtq7Y2Tk79so5Q2tUwA/"
    "AjD+Uv1fwP1uA4CBMqUs1lq9b/nyW8tdXWu5UsaW0IQzBs55vsXuhLfb6D4LXATwh1QKyp6X"
    "ShlJKckajWd2Hjq0dV+97jQ9CeDHmKXl/VL9ZaYfwAaas4JowLx72bK/7Ors3EwYI9wYg7yi"
    "JMR7rs8X3j0s5Rc5yhhjlIIyhghCkE5NDT185MiOkXr9BCeEyDy5eMoO8mwc3vn8zxADsArA"
    "UgogopTHWstX9vauuqyn58b2cvkKRFGFAWD5RoeZJVkyBKCKEEhCACllWq+PPD0x8f1vHjv2"
    "fQDwBD8JYDeA+m/bv8bKAC4DsBgAifLKiKRaKwC4tqfnkiXt7SuqUbQo5LwzYKwMY4gwJpVS"
    "TtWz7PiJJNm/8+TJ3dpmTiVKWWJ/bwXfa73889b6+QTALYpbEJYC6HStp4BSygBKAMRaK20F"
    "oDlYjOQlm5aAUVo74WIbfvfb9y+K4Oftf4OzvEIALwMwH0A3gHYAwdxVOGIAEwDG7Gi0gPui"
    "a+yleLUunlmWEM8PKgvAuX6H31UAns3c5jexiP8DSZJIhg4rsGIAAAAASUVORK5CYII=")

#----------------------------------------------------------------------
Prompt = PyEmbeddedImage(
    "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")


class MessageIcon (namedtuple('MessageIcon', ['bitmap', 'width', 'height'], verbose=False)):
    pass


###########################################################################
## Class Messages
###########################################################################
class Messages (wx.Dialog):
    def __init__(self, parent, text, title=wx.EmptyString, style=INFO, bitmap=None, yes="Okay", no="Cancel"):
        """
        Init Messages object
        """

        m = HAS_CAPTION.match(text)
        if m is not None:
            caption = m.group(1)
            msg = m.group(2)
        else:
            caption = None
            msg = text

        self.answer = wx.ID_CANCEL if style == PROMPT else wx.ID_OK

        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=title, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
        b_dialog_sizer = wx.BoxSizer(wx.VERTICAL)

        self.m_message_panel = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        fg_panel_sizer = wx.FlexGridSizer(2, 1, 0, 0)
        fg_panel_sizer.AddGrowableCol(0)
        fg_panel_sizer.AddGrowableRow(0)
        fg_panel_sizer.SetFlexibleDirection(wx.BOTH)
        fg_panel_sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self._setup_message(fg_panel_sizer, msg, caption, style, bitmap)

        fg_button_row_sizer = wx.FlexGridSizer(0, 3, 0, 0)
        fg_button_row_sizer.AddGrowableCol(0)
        fg_button_row_sizer.AddGrowableCol(2)
        fg_button_row_sizer.SetFlexibleDirection(wx.BOTH)
        fg_button_row_sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)
        fg_button_row_sizer.AddSpacer((0, 0), 1, wx.EXPAND, 5)

        self._setup_buttons(fg_button_row_sizer, style, yes, no)

        fg_button_row_sizer.AddSpacer((0, 0), 1, wx.EXPAND, 5)
        fg_panel_sizer.Add(fg_button_row_sizer, 1, wx.EXPAND, 5)

        self.m_message_panel.SetSizer(fg_panel_sizer)
        self.m_message_panel.Layout()
        fg_panel_sizer.Fit(self.m_message_panel)
        b_dialog_sizer.Add(self.m_message_panel, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(b_dialog_sizer)
        self.Layout()
        b_dialog_sizer.Fit(self)

        self.Centre(wx.BOTH)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)
        self.m_accept_button.SetFocus()

    def _setup_buttons(self, fg_button_row_sizer, style, yes, no):
        """
        Setup the appropriate buttons for the dialog
        """

        fg_button_sizer = wx.FlexGridSizer(0, 2, 0, 0) if style == PROMPT else wx.FlexGridSizer(0, 1, 0, 0)
        fg_button_sizer.SetFlexibleDirection(wx.BOTH)
        fg_button_sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        if style == PROMPT:
            self.m_cancel_button = wx.Button(self.m_message_panel, wx.ID_ANY, no, wx.DefaultPosition, wx.DefaultSize, 0)
            fg_button_sizer.Add(self.m_cancel_button, 0, wx.ALL, 5)
            self.m_cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel)

        self.m_accept_button = wx.Button(self.m_message_panel, wx.ID_ANY, yes, wx.DefaultPosition, wx.DefaultSize, 0)
        fg_button_sizer.Add(self.m_accept_button, 0, wx.ALL, 5)
        self.m_accept_button.Bind(wx.EVT_BUTTON, self.on_accept)

        fg_button_row_sizer.Add(fg_button_sizer, 1, wx.EXPAND, 5)

    def _setup_message(self, fg_panel_sizer, msg, caption, style, bitmap):
        """
        Setup the message
        """

        bm = self._get_bitmap(style, bitmap)

        if bm is not None:
            fg_message_sizer = wx.FlexGridSizer(1, 2, 0, 0)
            fg_message_sizer.AddGrowableCol(1)
        else:
            fg_message_sizer = wx.FlexGridSizer(1, 1, 0, 0)
            fg_message_sizer.AddGrowableCol(0)
        fg_message_sizer.AddGrowableRow(0)
        fg_message_sizer.SetFlexibleDirection(wx.BOTH)
        fg_message_sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        if bm is not None:
            self.m_bitmap = wx.StaticBitmap(self.m_message_panel, wx.ID_ANY, bm.bitmap, wx.DefaultPosition, wx.Size(bm.width, bm.height), 0)
            fg_message_sizer.Add(self.m_bitmap, 0, wx.ALL, 5)

        self.m_message_text = wx.StaticText(self.m_message_panel, wx.ID_ANY, msg, wx.DefaultPosition, wx.DefaultSize, 0)
        sz = self.m_message_text.GetSize()
        if sz[0] < DEFAULT_TEXT_MIN_SIZE:
            self.m_message_text.SetMinSize(wx.Size(DEFAULT_TEXT_MIN_SIZE, -1))
        elif sz[0] > DEFAULT_TEXT_MAX_SIZE:
            self.m_message_text.Wrap(DEFAULT_TEXT_MAX_SIZE)
        else:
            self.m_message_text.Wrap(-1)

        if caption is not None:
            fg_text_sizer = wx.FlexGridSizer(2, 1, 0, 0)
            fg_text_sizer.AddGrowableCol(0)
            fg_text_sizer.AddGrowableRow(1)
            fg_text_sizer.SetFlexibleDirection(wx.BOTH)
            fg_text_sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)
            self.m_caption_text = wx.StaticText(self.m_message_panel, wx.ID_ANY, caption, wx.DefaultPosition, wx.DefaultSize, 0)
            font = self.m_caption_text.GetFont()
            font.SetWeight(wx.FONTWEIGHT_BOLD)
            self.m_caption_text.SetFont(font)

            caption_sz = self.m_caption_text.GetSize()
            if caption_sz[0] < DEFAULT_TEXT_MIN_SIZE:
                self.m_caption_text.SetMinSize(wx.Size(DEFAULT_TEXT_MIN_SIZE, -1))
            elif caption_sz[0] > DEFAULT_TEXT_MAX_SIZE:
                self.m_caption_text.Wrap(DEFAULT_TEXT_MAX_SIZE)
            else:
                self.m_caption_text.Wrap(-1)

            fg_text_sizer.Add(self.m_caption_text, 1, wx.ALL | wx.EXPAND, 5)
            fg_text_sizer.Add(self.m_message_text, 1, wx.ALL | wx.EXPAND, 5)
            fg_message_sizer.Add(fg_text_sizer, 1, wx.EXPAND, 5)
        else:
            fg_message_sizer.Add(self.m_message_text, 1, wx.ALL | wx.EXPAND, 5)

        fg_panel_sizer.Add(fg_message_sizer, 1, wx.EXPAND, 5)

    def _get_bitmap(self, style, bitmap):
        """
        Get the appropriate icon
        """

        icon = None

        if bitmap is not None:
            icon = bitmap
        elif style == ERROR:
            icon = MessageIcon(Error.GetBitmap(), DEFAULT_ICON_SIZE, DEFAULT_ICON_SIZE)
        elif style == WARN:
            icon = MessageIcon(Warn.GetBitmap(), DEFAULT_ICON_SIZE, DEFAULT_ICON_SIZE)
        elif style == PROMPT:
            icon = MessageIcon(Prompt.GetBitmap(), DEFAULT_ICON_SIZE, DEFAULT_ICON_SIZE)
        elif style == INFO:
            icon = MessageIcon(Info.GetBitmap(), DEFAULT_ICON_SIZE, DEFAULT_ICON_SIZE)

        return icon

    def __del__(self):
        pass

    def on_char_hook(self, event):
        """
        Cancel on escape
        """

        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.answer = wx.ID_CANCEL
            self.EndModal(self.answer)

    def on_cancel(self, event):
        """
        Set cancel status
        """

        self.answer = wx.ID_CANCEL
        self.EndModal(self.answer)

    def on_accept(self, event):
        """
        Set OK status
        """

        self.answer = wx.ID_OK
        self.EndModal(self.answer)


def filepickermsg(msg, wildcard, save=False):
    """
    File picker
    """

    select = None
    style = wx.OPEN | wx.FILE_MUST_EXIST if not save else wx.SAVE | wx.OVERWRITE_PROMPT
    dlg = wx.FileDialog(
        None, msg,
        "", wildcard=wildcard,
        style=style
    )
    if dlg.ShowModal() == wx.ID_OK:
        select = dlg.GetPath()
    dlg.Destroy()
    return select


def dirpickermsg(msg, default_path=""):
    """
    Directory picker
    """

    select = None
    style = wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST
    dlg = wx.DirDialog(
        None, msg,
        default_path,
        style=style
    )
    if dlg.ShowModal() == wx.ID_OK:
        select = dlg.GetPath()
    dlg.Destroy()
    return select


def promptmsg(question, caption='PROMPT', bitmap=None, yes="Okay", no="Cancel"):
    """
    Prompt with "yes" "no" type object
    """

    dlg = Messages(None, question, caption, style=PROMPT, yes=yes, no=no, bitmap=bitmap)
    result = dlg.ShowModal() == wx.ID_OK
    dlg.Destroy()
    return result


def infomsg(msg, title="INFO", bitmap=None):
    """
    Info message
    """

    dlg = Messages(None, msg, title, style=INFO, bitmap=bitmap)
    dlg.ShowModal()
    dlg.Destroy()


def errormsg(msg, title="ERROR", bitmap=None):
    """
    Error message
    """

    dlg = Messages(None, msg, title, style=ERROR, bitmap=bitmap)
    dlg.ShowModal()
    dlg.Destroy()


def warnmsg(msg, title="WARNING", bitmap=None):
    """
    Warning message
    """

    dlg = Messages(None, msg, title, style=WARN, bitmap=bitmap)
    dlg.ShowModal()
    dlg.Destroy()
