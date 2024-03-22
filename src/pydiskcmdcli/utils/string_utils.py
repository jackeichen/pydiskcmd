# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

def decode_bytes(bytes_to_decode):
    string = ''
    if bytes_to_decode:
        for encode_t in ("UTF-8", "GBK", "GB2312"):
            try:
                string = bytes_to_decode.decode(encoding=encode_t, errors="strict")
            except:
                pass
            else:
                break
    return string

def string_strip(string, *args):
    for symbol in args:
        string = string.strip(symbol)
    return string
