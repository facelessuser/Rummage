"""
Common tokens shared between the different regex modules.

Licensed under MIT
Copyright (c) 2011 - 2015 Isaac Muse <isaacmuse@gmail.com>
"""
import re

REPLACE_TOKENS = 0
VERBOSE_TOKENS = 1
EMPTY = 2
LS_BRACKET = 3
RS_BRACKET = 4
B_SLASH = 5
ESC_END = 6
END = 7
QUOTE = 8
LC = 9
LC_SPAN = 10
UC = 11
UC_SPAN = 12
HASHTAG = 13
NL = 14
NEGATE = 15
VERBOSE_FLAG = 16
RE_REPLACE_REF = 17
UNICODE_FLAG = 18


# Unicode string related references
utokens = (
    set("cCElL"),                    # REPLACE_TOKENS
    set("# "),                       # VERBOSE_TOKENS
    "",                              # EMPTY
    "[",                             # LS_BRACKET
    "]",                             # RS_BRACKET
    "\\",                            # B_SLASH
    "\\E",                           # ESC_END
    "E",                             # END
    "Q",                             # QUOTE
    "l",                             # LC
    "L",                             # LC_SPAN
    "c",                             # UC
    "C",                             # UC_SPAN
    '#',                             # HASHTAG
    '\n',                            # NL
    '^',                             # NEGATE
    'x',                             # VERBOSE_FLAG
    re.compile(                      # RE_REPLACE_REF
        r'''(?x)
        (\\)+
        (
            [cClLE]
        )? |
        (
            [cClLE]
        )
        '''
    ),
    'u'                               # UNICODE_FLAG
)

# Byte string related references
btokens = (
    set(                              # REPLACE_TOKENS
        [b"c", b"C", b"E", b"l", b"L"]
    ),
    set([b"#", b" "]),                # VERBOSE_TOKENS
    b"",                              # EMPTY
    b"[",                             # LS_BRACKET
    b"]",                             # RS_BRACKET
    b"\\",                            # B_SLASH
    b"\\E",                           # ESC_END
    b"E",                             # END
    b"Q",                             # QUOTE
    b"l",                             # LC
    b"L",                             # LC_SPAN
    b"c",                             # UC
    b"C",                             # UC_SPAN
    b'#',                             # HASHTAG
    b'\n',                            # NL
    b'^',                             # NEGATE
    b'x',                             # VERBOSE_FLAG
    re.compile(                       # RE_REPLACE_REF
        br'''(?x)
        (\\)+
        (
            [cClLE]
        )? |
        (
            [cClLE]
        )
        '''
    ),
    re.compile(                        # RE_FLAGS
        br'(?s)(\\.)|\(\?([iLmsux]+)\)|(.)'
    ),
    b'u'                               # UNICODE_FLAG
)
