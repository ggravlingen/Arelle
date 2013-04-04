'''
Created on Oct 22, 2010

@author: Mark V Systems Limited
(c) Copyright 2010 Mark V Systems Limited, All rights reserved.
'''
import re, os, sys
if sys.version[0] >= '3':
    from urllib.parse import urldefrag, unquote, quote
    isPy3 = True
else:
    from urlparse import urldefrag
    from urllib import quote
    from arelle.PythonUtil import py3unquote as unquote
    isPy3 = False

def authority(url, includeScheme=True):
    if url:
        authSep = url.find(':') 
        if authSep > -1:
            scheme = url[0:authSep]
            authPart = authSep + (3 if scheme in ("http", "https", "ftp") else 1) # allow urn:
            pathPart = url.find('/', authPart) 
            if pathPart > -1:
                if includeScheme:
                    return url[0:pathPart]
                else:
                    return url[authPart:pathPart]
            elif not includeScheme:
                return url[authPart:]
    return url  #no path part of url

absoluteUrlPattern = None
# http://www.ietf.org/rfc/rfc2396.txt section 4.3
# this pattern doesn't allow some valid unicode characters
#relativeUrlPattern = re.compile(r"(^[/:\.+-_@%;?&=!~\*'\(\)\w ]+(#[\w_%\-\.\(/\)]+)?$)|(^#[\w_%\-\.\(/\)]+$)")
# try this instead from http://www.ietf.org/rfc/rfc2396.txt (B)
relativeUrlPattern = re.compile(r"^(([^:/\?#]+):)?(//([^/\?#]*))?([^\?#]*)(\?([^#]*))?(#([^#]*))?$")

def splitDecodeFragment(url):
    urlPart, fragPart = urldefrag(url)
    if isPy3:
        return (urlPart, unquote(fragPart, "utf-8", errors=None))
    else:
        return _STR_UNICODE(urlPart), unquote(_STR_UNICODE(fragPart), "utf-8", errors=None)
    
def anyUriQuoteForPSVI(uri):
    # only quote if quotable character found
    if any(c in {' ', '<', '>', '"', '{', '}', '|', '\\', '^', '~', '`'} or
           not '\x1f' < c < '\x7f'
           for c in uri):
        if not isPy3:  # patch for unicode per http://hg.python.org/cpython/rev/1e21d94e05f4/
            return quote(uri.encode(b'utf-8', b'strict'),
                         safe=b"/_.-%#!~*'();?:@&=+$,")  # b'str' converts to 2.7 str type which is required here
        else:
            return quote(uri, safe="/_.-%#!~*'();?:@&=+$,")
    return uri

def isValidAbsolute(url):
    global absoluteUrlPattern
    if absoluteUrlPattern is None:
        absoluteUrlPattern = re.compile(
            ''' seems to have an error
            # from http://stackoverflow.com/questions/827557/how-do-you-validate-a-url-with-a-regular-expression-in-python
            "(?P<scheme>[a-zA-Z][a-zA-Z0-9+.-]*):(?://(?P<iauthority>(?:(?P<iuserinfo>(?:(?:[a-zA-Z0-9._~-]"
            "|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef])|%[0-9A-F][0-9A-F]|[!$&'()*+,;=]|:)*)@)?(?P<ihost>"
            "\\[(?:(?:[0-9A-F]{1,4}:){6}(?:[0-9A-F]{1,4}:[0-9A-F]{1,4}|(?:(?:(?:25[0-5]|2[0-4][0-9]"
            "|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)))|::(?:[0-9A-F]{1,4}"
            ":){5}(?:[0-9A-F]{1,4}:[0-9A-F]{1,4}|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}"
            "(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)))|[0-9A-F]{1,4}?::(?:[0-9A-F]{1,4}:){4}(?:[0-9A-F]{1,4}"
            ":[0-9A-F]{1,4}|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]"
            "|2[0-4][0-9]|[01]?[0-9][0-9]?)))|(?:(?:[0-9A-F]{1,4}:)?[0-9A-F]{1,4})?::(?:[0-9A-F]{1,4}"
            ":){3}(?:[0-9A-F]{1,4}:[0-9A-F]{1,4}|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}"
            "(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)))|(?:(?:[0-9A-F]{1,4}:){,2}[0-9A-F]{1,4})?::"
            "(?:[0-9A-F]{1,4}:){2}(?:[0-9A-F]{1,4}:[0-9A-F]{1,4}|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?"
            "[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)))|(?:(?:[0-9A-F]{1,4}:){,3}"
            "[0-9A-F]{1,4})?::(?:[0-9A-F]{1,4}:)(?:[0-9A-F]{1,4}:[0-9A-F]{1,4}|(?:(?:(?:25[0-5]|2[0-4][0-9]"
            "|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)))|(?:(?:[0-9A-F]{1,4}:){,4}"
            "[0-9A-F]{1,4})?::(?:[0-9A-F]{1,4}:[0-9A-F]{1,4}|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}"
            "(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)))|(?:(?:[0-9A-F]{1,4}:){,5}[0-9A-F]{1,4})?::[0-9A-F]{1,4}"
            "|(?:(?:[0-9A-F]{1,4}:){,6}[0-9A-F]{1,4})?::|v[0-9A-F]+\\.(?:[a-zA-Z0-9_.~-]|[!$&'()*+,;=]|:)+)\\]"
            "|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))"
            "|(?:(?:[a-zA-Z0-9._~-]|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef])|%[0-9A-F][0-9A-F]|[!$&'()*+,;=])*)"
            "(?::(?P<port>[0-9]*))?)(?P<ipath>(?:/(?:(?:[a-zA-Z0-9._~-]|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef])"
            "|%[0-9A-F][0-9A-F]|[!$&'()*+,;=]|:|@)*)*)|(?P<ipath>/(?:(?:(?:[a-zA-Z0-9._~-]"
            "|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef])|%[0-9A-F][0-9A-F]|[!$&'()*+,;=]|:|@)+(?:/(?:(?:[a-zA-Z0-9._~-]"
            "|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef])|%[0-9A-F][0-9A-F]|[!$&'()*+,;=]|:|@)*)*)?)"
            "|(?P<ipath>(?:(?:[a-zA-Z0-9._~-]|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef])|%[0-9A-F][0-9A-F]"
            "|[!$&'()*+,;=]|:|@)+(?:/(?:(?:[a-zA-Z0-9._~-]|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef])"
            "|%[0-9A-F][0-9A-F]|[!$&'()*+,;=]|:|@)*)*)|(?P<ipath>))(?:\\?(?P<iquery>(?:(?:(?:[a-zA-Z0-9._~-]"
            "|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef])|%[0-9A-F][0-9A-F]|[!$&'()*+,;=]|:|@)|[\ue000-\uf8ff]"
            "|/|\\?)*))?(?:\\#(?P<ifragment>(?:(?:(?:[a-zA-Z0-9._~-]|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef])"
            "|%[0-9A-F][0-9A-F]|[!$&'()*+,;=]|:|@)|/|\\?)*))?|(?:(?://(?P<iauthority>(?:(?P<iuserinfo>"
            "(?:(?:[a-zA-Z0-9._~-]|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef])|%[0-9A-F][0-9A-F]"
            "|[!$&'()*+,;=]|:)*)@)?(?P<ihost>\\[(?:(?:[0-9A-F]{1,4}:){6}(?:[0-9A-F]{1,4}:[0-9A-F]{1,4}"
            "|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)))"
            "|::(?:[0-9A-F]{1,4}:){5}(?:[0-9A-F]{1,4}:[0-9A-F]{1,4}|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?"
            "[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)))|[0-9A-F]{1,4}?::(?:[0-9A-F]{1,4}"
            ":){4}(?:[0-9A-F]{1,4}:[0-9A-F]{1,4}|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}"
            "(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)))|(?:(?:[0-9A-F]{1,4}:)?[0-9A-F]{1,4})?::(?:[0-9A-F]{1,4}:){3}"
            "(?:[0-9A-F]{1,4}:[0-9A-F]{1,4}|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]"
            "|[01]?[0-9][0-9]?)))|(?:(?:[0-9A-F]{1,4}:){,2}[0-9A-F]{1,4})?::(?:[0-9A-F]{1,4}:){2}"
            "(?:[0-9A-F]{1,4}:[0-9A-F]{1,4}|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]"
            "|2[0-4][0-9]|[01]?[0-9][0-9]?)))|(?:(?:[0-9A-F]{1,4}:){,3}[0-9A-F]{1,4})?::(?:[0-9A-F]{1,4}:)"
            "(?:[0-9A-F]{1,4}:[0-9A-F]{1,4}|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]"
            "|2[0-4][0-9]|[01]?[0-9][0-9]?)))|(?:(?:[0-9A-F]{1,4}:){,4}[0-9A-F]{1,4})?::(?:[0-9A-F]{1,4}:[0-9A-F]{1,4}"
            "|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)))"
            "|(?:(?:[0-9A-F]{1,4}:){,5}[0-9A-F]{1,4})?::[0-9A-F]{1,4}|(?:(?:[0-9A-F]{1,4}:){,6}[0-9A-F]{1,4})?"
            "::|v[0-9A-F]+\\.(?:[a-zA-Z0-9_.~-]|[!$&'()*+,;=]|:)+)\\]|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?"
            "[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))|(?:(?:[a-zA-Z0-9._~-]"
            "|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef])|%[0-9A-F][0-9A-F]|[!$&'()*+,;=])*)"
            "(?::(?P<port>[0-9]*))?)(?P<ipath>(?:/(?:(?:[a-zA-Z0-9._~-]|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef])"
            "|%[0-9A-F][0-9A-F]|[!$&'()*+,;=]|:|@)*)*)|(?P<ipath>/(?:(?:(?:[a-zA-Z0-9._~-]"
            "|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef])|%[0-9A-F][0-9A-F]|[!$&'()*+,;=]|:|@)+(?:/(?:(?:[a-zA-Z0-9._~-]"
            "|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef])|%[0-9A-F][0-9A-F]|[!$&'()*+,;=]|:|@)*)*)?)"
            "|(?P<ipath>(?:(?:[a-zA-Z0-9._~-]|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef])|%[0-9A-F]"
            "[0-9A-F]|[!$&'()*+,;=]|@)+(?:/(?:(?:[a-zA-Z0-9._~-]|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef])"
            "|%[0-9A-F][0-9A-F]|[!$&'()*+,;=]|:|@)*)*)|(?P<ipath>))(?:\\?(?P<iquery>(?:(?:(?:[a-zA-Z0-9._~-]"
            "|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef])|%[0-9A-F][0-9A-F]|[!$&'()*+,;=]|:|@)|[\ue000-\uf8ff]"
            "|/|\\?)*))?(?:\\#(?P<ifragment>(?:(?:(?:[a-zA-Z0-9._~-]|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef])"
            "|%[0-9A-F][0-9A-F]|[!$&'()*+,;=]|:|@)|/|\\?)*))?)"   
            '''         
            
            ''' for Python 3.3 only
            "(?P<scheme>[a-zA-Z][a-zA-Z0-9+.-]*):"
            "(?://(?P<iauthority>(?:(?P<iuserinfo>(?:(?:[a-zA-Z0-9._~-]|"
            "[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef\U00010000-\U0001fffd\U00020000-\U0002fffd"
            "\U00030000-\U0003fffd\U00040000-\U0004fffd\U00050000-\U0005fffd\U00060000-\U0006fffd"
            "\U00070000-\U0007fffd\U00080000-\U0008fffd\U00090000-\U0009fffd\U000a0000-\U000afffd"
            "\U000b0000-\U000bfffd\U000c0000-\U000cfffd\U000d0000-\U000dfffd\U000e1000-\U000efffd])"
            "|%[0-9A-F][0-9A-F]|[!$&'()*+,;=]|:)*)@)?(?P<ihost>\\[(?:(?:[0-9A-F]{1,4}:){6}"
            "(?:[0-9A-F]{1,4}:[0-9A-F]{1,4}|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}"
            "(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)))|::(?:[0-9A-F]{1,4}:){5}(?:[0-9A-F]{1,4}:[0-9A-F]{1,4}"
            "|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)))"
            "|[0-9A-F]{1,4}?::(?:[0-9A-F]{1,4}:){4}(?:[0-9A-F]{1,4}:[0-9A-F]{1,4}|(?:(?:(?:25[0-5]|2[0-4][0-9]"
            "|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)))|(?:(?:[0-9A-F]{1,4}:)?"
            "[0-9A-F]{1,4})?::(?:[0-9A-F]{1,4}:){3}(?:[0-9A-F]{1,4}:[0-9A-F]{1,4}|(?:(?:(?:25[0-5]|2[0-4][0-9]"
            "|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)))|(?:(?:[0-9A-F]{1,4}:){,2}"
            "[0-9A-F]{1,4})?::(?:[0-9A-F]{1,4}:){2}(?:[0-9A-F]{1,4}:[0-9A-F]{1,4}|(?:(?:(?:25[0-5]|2[0-4][0-9]"
            "|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)))|(?:(?:[0-9A-F]{1,4}:){,3}"
            "[0-9A-F]{1,4})?::(?:[0-9A-F]{1,4}:)(?:[0-9A-F]{1,4}:[0-9A-F]{1,4}|(?:(?:(?:25[0-5]|2[0-4][0-9]"
            "|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)))|(?:(?:[0-9A-F]{1,4}:){,4}"
            "[0-9A-F]{1,4})?::(?:[0-9A-F]{1,4}:[0-9A-F]{1,4}|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}"
            "(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)))|(?:(?:[0-9A-F]{1,4}:){,5}[0-9A-F]{1,4})?::[0-9A-F]{1,4}"
            "|(?:(?:[0-9A-F]{1,4}:){,6}[0-9A-F]{1,4})?::|v[0-9A-F]+\\.(?:[a-zA-Z0-9_.~-]|[!$&'()*+,;=]|:)+)\\]"
            "|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))"
            "|(?:(?:[a-zA-Z0-9._~-]|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef\U00010000-\U0001fffd\U00020000-\U0002fffd"
            "\U00030000-\U0003fffd\U00040000-\U0004fffd\U00050000-\U0005fffd\U00060000-\U0006fffd\U00070000-\U0007fffd"
            "\U00080000-\U0008fffd\U00090000-\U0009fffd\U000a0000-\U000afffd\U000b0000-\U000bfffd\U000c0000-\U000cfffd"
            "\U000d0000-\U000dfffd\U000e1000-\U000efffd])|%[0-9A-F][0-9A-F]|[!$&'()*+,;=])*)(?::(?P<port>[0-9]*))?)"
            "(?P<ipath>(?:/(?:(?:[a-zA-Z0-9._~-]|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef\U00010000-\U0001fffd"
            "\U00020000-\U0002fffd\U00030000-\U0003fffd\U00040000-\U0004fffd\U00050000-\U0005fffd\U00060000-\U0006fffd"
            "\U00070000-\U0007fffd\U00080000-\U0008fffd\U00090000-\U0009fffd\U000a0000-\U000afffd\U000b0000-\U000bfffd"
            "\U000c0000-\U000cfffd\U000d0000-\U000dfffd\U000e1000-\U000efffd])|%[0-9A-F][0-9A-F]|[!$&'()*+,;=]|:|@)*)*)"
            "|(?P<ipath>/(?:(?:(?:[a-zA-Z0-9._~-]|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef\U00010000-\U0001fffd"
            "\U00020000-\U0002fffd\U00030000-\U0003fffd\U00040000-\U0004fffd\U00050000-\U0005fffd\U00060000-\U0006fffd"
            "\U00070000-\U0007fffd\U00080000-\U0008fffd\U00090000-\U0009fffd\U000a0000-\U000afffd\U000b0000-\U000bfffd"
            "\U000c0000-\U000cfffd\U000d0000-\U000dfffd\U000e1000-\U000efffd])|%[0-9A-F][0-9A-F]|[!$&'()*+,;=]|:"
            "|@)+(?:/(?:(?:[a-zA-Z0-9._~-]|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef\U00010000-\U0001fffd\U00020000-\U0002fffd"
            "\U00030000-\U0003fffd\U00040000-\U0004fffd\U00050000-\U0005fffd\U00060000-\U0006fffd\U00070000-\U0007fffd"
            "\U00080000-\U0008fffd\U00090000-\U0009fffd\U000a0000-\U000afffd\U000b0000-\U000bfffd\U000c0000-\U000cfffd"
            "\U000d0000-\U000dfffd\U000e1000-\U000efffd])|%[0-9A-F][0-9A-F]|[!$&'()*+,;=]|:|@)*)*)?)|(?P<ipath>(?:(?:"
            "[a-zA-Z0-9._~-]|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef\U00010000-\U0001fffd\U00020000-\U0002fffd"
            "\U00030000-\U0003fffd\U00040000-\U0004fffd\U00050000-\U0005fffd\U00060000-\U0006fffd\U00070000-\U0007fffd"
            "\U00080000-\U0008fffd\U00090000-\U0009fffd\U000a0000-\U000afffd\U000b0000-\U000bfffd\U000c0000-\U000cfffd"
            "\U000d0000-\U000dfffd\U000e1000-\U000efffd])|%[0-9A-F][0-9A-F]|[!$&'()*+,;=]|:|@)+(?:/(?:(?:[a-zA-Z0-9._~-]"
            "|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef\U00010000-\U0001fffd\U00020000-\U0002fffd\U00030000-\U0003fffd"
            "\U00040000-\U0004fffd\U00050000-\U0005fffd\U00060000-\U0006fffd\U00070000-\U0007fffd\U00080000-\U0008fffd"
            "\U00090000-\U0009fffd\U000a0000-\U000afffd\U000b0000-\U000bfffd\U000c0000-\U000cfffd\U000d0000-\U000dfffd"
            "\U000e1000-\U000efffd])|%[0-9A-F][0-9A-F]|[!$&'()*+,;=]|:|@)*)*)|(?P<ipath>))(?:\\?(?P<iquery>(?:(?:(?:"
            "[a-zA-Z0-9._~-]|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef\U00010000-\U0001fffd\U00020000-\U0002fffd"
            "\U00030000-\U0003fffd\U00040000-\U0004fffd\U00050000-\U0005fffd\U00060000-\U0006fffd\U00070000-\U0007fffd"
            "\U00080000-\U0008fffd\U00090000-\U0009fffd\U000a0000-\U000afffd\U000b0000-\U000bfffd\U000c0000-\U000cfffd"
            "\U000d0000-\U000dfffd\U000e1000-\U000efffd])|%[0-9A-F][0-9A-F]|[!$&'()*+,;=]|:|@)|[\ue000-\uf8ff"
            "\U000f0000-\U000ffffd\U00100000-\U0010fffd]|/|\\?)*))?(?:\\#(?P<ifragment>(?:(?:(?:[a-zA-Z0-9._~-]"
            "|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef\U00010000-\U0001fffd\U00020000-\U0002fffd\U00030000-\U0003fffd"
            "\U00040000-\U0004fffd\U00050000-\U0005fffd\U00060000-\U0006fffd\U00070000-\U0007fffd\U00080000-\U0008fffd"
            "\U00090000-\U0009fffd\U000a0000-\U000afffd\U000b0000-\U000bfffd\U000c0000-\U000cfffd\U000d0000-\U000dfffd"
            "\U000e1000-\U000efffd])|%[0-9A-F][0-9A-F]|[!$&'()*+,;=]|:|@)|/|\\?)*))?|(?:(?://(?P<iauthority>(?:"
            "(?P<iuserinfo>(?:(?:[a-zA-Z0-9._~-]|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef\U00010000-\U0001fffd"
            "\U00020000-\U0002fffd\U00030000-\U0003fffd\U00040000-\U0004fffd\U00050000-\U0005fffd\U00060000-\U0006fffd"
            "\U00070000-\U0007fffd\U00080000-\U0008fffd\U00090000-\U0009fffd\U000a0000-\U000afffd\U000b0000-\U000bfffd"
            "\U000c0000-\U000cfffd\U000d0000-\U000dfffd\U000e1000-\U000efffd])|%[0-9A-F][0-9A-F]"
            "|[!$&'()*+,;=]|:)*)@)?(?P<ihost>\\[(?:(?:[0-9A-F]{1,4}:){6}(?:[0-9A-F]{1,4}:[0-9A-F]{1,4}"
            "|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)))"
            "|::(?:[0-9A-F]{1,4}:){5}(?:[0-9A-F]{1,4}:[0-9A-F]{1,4}|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}"
            "(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)))|[0-9A-F]{1,4}?::(?:[0-9A-F]{1,4}:){4}(?:[0-9A-F]{1,4}"
            ":[0-9A-F]{1,4}|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]"
            "|[01]?[0-9][0-9]?)))|(?:(?:[0-9A-F]{1,4}:)?[0-9A-F]{1,4})?::(?:[0-9A-F]{1,4}:){3}(?:[0-9A-F]{1,4}"
            ":[0-9A-F]{1,4}|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]"
            "|[01]?[0-9][0-9]?)))|(?:(?:[0-9A-F]{1,4}:){,2}[0-9A-F]{1,4})?::(?:[0-9A-F]{1,4}:){2}(?:[0-9A-F]{1,4}"
            ":[0-9A-F]{1,4}|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]"
            "|[01]?[0-9][0-9]?)))|(?:(?:[0-9A-F]{1,4}:){,3}[0-9A-F]{1,4})?::(?:[0-9A-F]{1,4}:)(?:[0-9A-F]{1,4}"
            ":[0-9A-F]{1,4}|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]"
            "|[01]?[0-9][0-9]?)))|(?:(?:[0-9A-F]{1,4}:){,4}[0-9A-F]{1,4})?::(?:[0-9A-F]{1,4}:[0-9A-F]{1,4}"
            "|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)))"
            "|(?:(?:[0-9A-F]{1,4}:){,5}[0-9A-F]{1,4})?::[0-9A-F]{1,4}|(?:(?:[0-9A-F]{1,4}:){,6}[0-9A-F]{1,4})?::"
            "|v[0-9A-F]+\\.(?:[a-zA-Z0-9_.~-]|[!$&'()*+,;=]|:)+)\\]|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9]"
            "[0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))|(?:(?:[a-zA-Z0-9._~-]|[\xa0-\ud7ff\uf900-\ufdcf"
            "\ufdf0-\uffef\U00010000-\U0001fffd\U00020000-\U0002fffd\U00030000-\U0003fffd\U00040000-\U0004fffd"
            "\U00050000-\U0005fffd\U00060000-\U0006fffd\U00070000-\U0007fffd\U00080000-\U0008fffd"
            "\U00090000-\U0009fffd\U000a0000-\U000afffd\U000b0000-\U000bfffd\U000c0000-\U000cfffd"
            "\U000d0000-\U000dfffd\U000e1000-\U000efffd])|%[0-9A-F][0-9A-F]|[!$&'()*+,;=])*)"
            "(?::(?P<port>[0-9]*))?)(?P<ipath>(?:/(?:(?:[a-zA-Z0-9._~-]|[\xa0-\ud7ff\uf900-\ufdcf"
            "\ufdf0-\uffef\U00010000-\U0001fffd\U00020000-\U0002fffd\U00030000-\U0003fffd"
            "\U00040000-\U0004fffd\U00050000-\U0005fffd\U00060000-\U0006fffd\U00070000-\U0007fffd"
            "\U00080000-\U0008fffd\U00090000-\U0009fffd\U000a0000-\U000afffd\U000b0000-\U000bfffd"
            "\U000c0000-\U000cfffd\U000d0000-\U000dfffd\U000e1000-\U000efffd])|%[0-9A-F][0-9A-F]"
            "|[!$&'()*+,;=]|:|@)*)*)|(?P<ipath>/(?:(?:(?:[a-zA-Z0-9._~-]|[\xa0-\ud7ff\uf900-\ufdcf"
            "\ufdf0-\uffef\U00010000-\U0001fffd\U00020000-\U0002fffd\U00030000-\U0003fffd"
            "\U00040000-\U0004fffd\U00050000-\U0005fffd\U00060000-\U0006fffd\U00070000-\U0007fffd"
            "\U00080000-\U0008fffd\U00090000-\U0009fffd\U000a0000-\U000afffd\U000b0000-\U000bfffd"
            "\U000c0000-\U000cfffd\U000d0000-\U000dfffd\U000e1000-\U000efffd])|%[0-9A-F][0-9A-F]"
            "|[!$&'()*+,;=]|:|@)+(?:/(?:(?:[a-zA-Z0-9._~-]|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef"
            "\U00010000-\U0001fffd\U00020000-\U0002fffd\U00030000-\U0003fffd\U00040000-\U0004fffd"
            "\U00050000-\U0005fffd\U00060000-\U0006fffd\U00070000-\U0007fffd\U00080000-\U0008fffd"
            "\U00090000-\U0009fffd\U000a0000-\U000afffd\U000b0000-\U000bfffd\U000c0000-\U000cfffd"
            "\U000d0000-\U000dfffd\U000e1000-\U000efffd])|%[0-9A-F][0-9A-F]|[!$&'()*+,;=]|:|@)*)*)?)"
            "|(?P<ipath>(?:(?:[a-zA-Z0-9._~-]|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef\U00010000-\U0001fffd"
            "\U00020000-\U0002fffd\U00030000-\U0003fffd\U00040000-\U0004fffd\U00050000-\U0005fffd"
            "\U00060000-\U0006fffd\U00070000-\U0007fffd\U00080000-\U0008fffd\U00090000-\U0009fffd"
            "\U000a0000-\U000afffd\U000b0000-\U000bfffd\U000c0000-\U000cfffd\U000d0000-\U000dfffd"
            "\U000e1000-\U000efffd])|%[0-9A-F][0-9A-F]|[!$&'()*+,;=]|@)+(?:/(?:(?:[a-zA-Z0-9._~-]"
            "|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef\U00010000-\U0001fffd\U00020000-\U0002fffd"
            "\U00030000-\U0003fffd\U00040000-\U0004fffd\U00050000-\U0005fffd\U00060000-\U0006fffd"
            "\U00070000-\U0007fffd\U00080000-\U0008fffd\U00090000-\U0009fffd\U000a0000-\U000afffd"
            "\U000b0000-\U000bfffd\U000c0000-\U000cfffd\U000d0000-\U000dfffd\U000e1000-\U000efffd])"
            "|%[0-9A-F][0-9A-F]|[!$&'()*+,;=]|:|@)*)*)|(?P<ipath>))(?:\\?(?P<iquery>(?:(?:(?:[a-zA-Z0-9._~-]"
            "|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef\U00010000-\U0001fffd\U00020000-\U0002fffd"
            "\U00030000-\U0003fffd\U00040000-\U0004fffd\U00050000-\U0005fffd\U00060000-\U0006fffd"
            "\U00070000-\U0007fffd\U00080000-\U0008fffd\U00090000-\U0009fffd\U000a0000-\U000afffd"
            "\U000b0000-\U000bfffd\U000c0000-\U000cfffd\U000d0000-\U000dfffd\U000e1000-\U000efffd])"
            "|%[0-9A-F][0-9A-F]|[!$&'()*+,;=]|:|@)|[\ue000-\uf8ff\U000f0000-\U000ffffd"
            "\U00100000-\U0010fffd]|/|\\?)*))?(?:\\#(?P<ifragment>(?:(?:(?:[a-zA-Z0-9._~-]"
            "|[\xa0-\ud7ff\uf900-\ufdcf\ufdf0-\uffef\U00010000-\U0001fffd\U00020000-\U0002fffd"
            "\U00030000-\U0003fffd\U00040000-\U0004fffd\U00050000-\U0005fffd\U00060000-\U0006fffd"
            "\U00070000-\U0007fffd\U00080000-\U0008fffd\U00090000-\U0009fffd\U000a0000-\U000afffd"
            "\U000b0000-\U000bfffd\U000c0000-\U000cfffd\U000d0000-\U000dfffd\U000e1000-\U000efffd])"
            "|%[0-9A-F][0-9A-F]|[!$&'()*+,;=]|:|@)|/|\\?)*))?)"
            '''
            
            # note this pattern does not process urn: as valid!!!
            # regex to validate a full URL from http://stackoverflow.com/questions/827557/how-do-you-validate-a-url-with-a-regular-expression-in-python/835527#835527
            r"(?:http://(?:(?:(?:(?:(?:[a-zA-Z\d](?:(?:[a-zA-Z\d]|-)*[a-zA-Z\d])?)\."
            r")*(?:[a-zA-Z](?:(?:[a-zA-Z\d]|-)*[a-zA-Z\d])?))|(?:(?:\d+)(?:\.(?:\d+)"
            r"){3}))(?::(?:\d+))?)(?:/(?:(?:(?:(?:[a-zA-Z\d$\-_.+!*'(),]|(?:%[a-fA-F"
            r"\d]{2}))|[;:@&=])*)(?:/(?:(?:(?:[a-zA-Z\d$\-_.+!*'(),]|(?:%[a-fA-F\d]{"
            r"2}))|[;:@&=])*))*)(?:\?(?:(?:(?:[a-zA-Z\d$\-_.+!*'(),]|(?:%[a-fA-F\d]{"
            r"2}))|[;:@&=])*))?)?)|(?:ftp://(?:(?:(?:(?:(?:[a-zA-Z\d$\-_.+!*'(),]|(?"
            r":%[a-fA-F\d]{2}))|[;?&=])*)(?::(?:(?:(?:[a-zA-Z\d$\-_.+!*'(),]|(?:%[a-"
            r"fA-F\d]{2}))|[;?&=])*))?@)?(?:(?:(?:(?:(?:[a-zA-Z\d](?:(?:[a-zA-Z\d]|-"
            r")*[a-zA-Z\d])?)\.)*(?:[a-zA-Z](?:(?:[a-zA-Z\d]|-)*[a-zA-Z\d])?))|(?:(?"
            r":\d+)(?:\.(?:\d+)){3}))(?::(?:\d+))?))(?:/(?:(?:(?:(?:[a-zA-Z\d$\-_.+!"
            r"*'(),]|(?:%[a-fA-F\d]{2}))|[?:@&=])*)(?:/(?:(?:(?:[a-zA-Z\d$\-_.+!*'()"
            r",]|(?:%[a-fA-F\d]{2}))|[?:@&=])*))*)(?:;type=[AIDaid])?)?)|(?:news:(?:"
            r"(?:(?:(?:[a-zA-Z\d$\-_.+!*'(),]|(?:%[a-fA-F\d]{2}))|[;/?:&=])+@(?:(?:("
            r"?:(?:[a-zA-Z\d](?:(?:[a-zA-Z\d]|-)*[a-zA-Z\d])?)\.)*(?:[a-zA-Z](?:(?:["
            r"a-zA-Z\d]|-)*[a-zA-Z\d])?))|(?:(?:\d+)(?:\.(?:\d+)){3})))|(?:[a-zA-Z]("
            r"?:[a-zA-Z\d]|[_.+-])*)|\*))|(?:nntp://(?:(?:(?:(?:(?:[a-zA-Z\d](?:(?:["
            r"a-zA-Z\d]|-)*[a-zA-Z\d])?)\.)*(?:[a-zA-Z](?:(?:[a-zA-Z\d]|-)*[a-zA-Z\d"
            r"])?))|(?:(?:\d+)(?:\.(?:\d+)){3}))(?::(?:\d+))?)/(?:[a-zA-Z](?:[a-zA-Z"
            r"\d]|[_.+-])*)(?:/(?:\d+))?)|(?:telnet://(?:(?:(?:(?:(?:[a-zA-Z\d$\-_.+"
            r"!*'(),]|(?:%[a-fA-F\d]{2}))|[;?&=])*)(?::(?:(?:(?:[a-zA-Z\d$\-_.+!*'()"
            r",]|(?:%[a-fA-F\d]{2}))|[;?&=])*))?@)?(?:(?:(?:(?:(?:[a-zA-Z\d](?:(?:[a"
            r"-zA-Z\d]|-)*[a-zA-Z\d])?)\.)*(?:[a-zA-Z](?:(?:[a-zA-Z\d]|-)*[a-zA-Z\d]"
            r")?))|(?:(?:\d+)(?:\.(?:\d+)){3}))(?::(?:\d+))?))/?)|(?:gopher://(?:(?:"
            r"(?:(?:(?:[a-zA-Z\d](?:(?:[a-zA-Z\d]|-)*[a-zA-Z\d])?)\.)*(?:[a-zA-Z](?:"
            r"(?:[a-zA-Z\d]|-)*[a-zA-Z\d])?))|(?:(?:\d+)(?:\.(?:\d+)){3}))(?::(?:\d+"
            r"))?)(?:/(?:[a-zA-Z\d$\-_.+!*'(),;/?:@&=]|(?:%[a-fA-F\d]{2}))(?:(?:(?:["
            r"a-zA-Z\d$\-_.+!*'(),;/?:@&=]|(?:%[a-fA-F\d]{2}))*)(?:%09(?:(?:(?:[a-zA"
            r"-Z\d$\-_.+!*'(),]|(?:%[a-fA-F\d]{2}))|[;:@&=])*)(?:%09(?:(?:[a-zA-Z\d$"
            r"\-_.+!*'(),;/?:@&=]|(?:%[a-fA-F\d]{2}))*))?)?)?)?)|(?:wais://(?:(?:(?:"
            r"(?:(?:[a-zA-Z\d](?:(?:[a-zA-Z\d]|-)*[a-zA-Z\d])?)\.)*(?:[a-zA-Z](?:(?:"
            r"[a-zA-Z\d]|-)*[a-zA-Z\d])?))|(?:(?:\d+)(?:\.(?:\d+)){3}))(?::(?:\d+))?"
            r")/(?:(?:[a-zA-Z\d$\-_.+!*'(),]|(?:%[a-fA-F\d]{2}))*)(?:(?:/(?:(?:[a-zA"
            r"-Z\d$\-_.+!*'(),]|(?:%[a-fA-F\d]{2}))*)/(?:(?:[a-zA-Z\d$\-_.+!*'(),]|("
            r"?:%[a-fA-F\d]{2}))*))|\?(?:(?:(?:[a-zA-Z\d$\-_.+!*'(),]|(?:%[a-fA-F\d]"
            r"{2}))|[;:@&=])*))?)|(?:mailto:(?:(?:[a-zA-Z\d$\-_.+!*'(),;/?:@&=]|(?:%"
            r"[a-fA-F\d]{2}))+))|(?:file://(?:(?:(?:(?:(?:[a-zA-Z\d](?:(?:[a-zA-Z\d]"
            r"|-)*[a-zA-Z\d])?)\.)*(?:[a-zA-Z](?:(?:[a-zA-Z\d]|-)*[a-zA-Z\d])?))|(?:"
            r"(?:\d+)(?:\.(?:\d+)){3}))|localhost)?/(?:(?:(?:(?:[a-zA-Z\d$\-_.+!*'()"
            r",]|(?:%[a-fA-F\d]{2}))|[?:@&=])*)(?:/(?:(?:(?:[a-zA-Z\d$\-_.+!*'(),]|("
            r"?:%[a-fA-F\d]{2}))|[?:@&=])*))*))|(?:prospero://(?:(?:(?:(?:(?:[a-zA-Z"
            r"\d](?:(?:[a-zA-Z\d]|-)*[a-zA-Z\d])?)\.)*(?:[a-zA-Z](?:(?:[a-zA-Z\d]|-)"
            r"*[a-zA-Z\d])?))|(?:(?:\d+)(?:\.(?:\d+)){3}))(?::(?:\d+))?)/(?:(?:(?:(?"
            r":[a-zA-Z\d$\-_.+!*'(),]|(?:%[a-fA-F\d]{2}))|[?:@&=])*)(?:/(?:(?:(?:[a-"
            r"zA-Z\d$\-_.+!*'(),]|(?:%[a-fA-F\d]{2}))|[?:@&=])*))*)(?:(?:;(?:(?:(?:["
            r"a-zA-Z\d$\-_.+!*'(),]|(?:%[a-fA-F\d]{2}))|[?:@&])*)=(?:(?:(?:[a-zA-Z\d"
            r"$\-_.+!*'(),]|(?:%[a-fA-F\d]{2}))|[?:@&])*)))*)|(?:ldap://(?:(?:(?:(?:"
            r"(?:(?:[a-zA-Z\d](?:(?:[a-zA-Z\d]|-)*[a-zA-Z\d])?)\.)*(?:[a-zA-Z](?:(?:"
            r"[a-zA-Z\d]|-)*[a-zA-Z\d])?))|(?:(?:\d+)(?:\.(?:\d+)){3}))(?::(?:\d+))?"
            r"))?/(?:(?:(?:(?:(?:(?:(?:[a-zA-Z\d]|%(?:3\d|[46][a-fA-F\d]|[57][Aa\d])"
            r")|(?:%20))+|(?:OID|oid)\.(?:(?:\d+)(?:\.(?:\d+))*))(?:(?:%0[Aa])?(?:%2"
            r"0)*)=(?:(?:%0[Aa])?(?:%20)*))?(?:(?:[a-zA-Z\d$\-_.+!*'(),]|(?:%[a-fA-F"
            r"\d]{2}))*))(?:(?:(?:%0[Aa])?(?:%20)*)\+(?:(?:%0[Aa])?(?:%20)*)(?:(?:(?"
            r":(?:(?:[a-zA-Z\d]|%(?:3\d|[46][a-fA-F\d]|[57][Aa\d]))|(?:%20))+|(?:OID"
            r"|oid)\.(?:(?:\d+)(?:\.(?:\d+))*))(?:(?:%0[Aa])?(?:%20)*)=(?:(?:%0[Aa])"
            r"?(?:%20)*))?(?:(?:[a-zA-Z\d$\-_.+!*'(),]|(?:%[a-fA-F\d]{2}))*)))*)(?:("
            r"?:(?:(?:%0[Aa])?(?:%20)*)(?:[;,])(?:(?:%0[Aa])?(?:%20)*))(?:(?:(?:(?:("
            r"?:(?:[a-zA-Z\d]|%(?:3\d|[46][a-fA-F\d]|[57][Aa\d]))|(?:%20))+|(?:OID|o"
            r"id)\.(?:(?:\d+)(?:\.(?:\d+))*))(?:(?:%0[Aa])?(?:%20)*)=(?:(?:%0[Aa])?("
            r"?:%20)*))?(?:(?:[a-zA-Z\d$\-_.+!*'(),]|(?:%[a-fA-F\d]{2}))*))(?:(?:(?:"
            r"%0[Aa])?(?:%20)*)\+(?:(?:%0[Aa])?(?:%20)*)(?:(?:(?:(?:(?:[a-zA-Z\d]|%("
            r"?:3\d|[46][a-fA-F\d]|[57][Aa\d]))|(?:%20))+|(?:OID|oid)\.(?:(?:\d+)(?:"
            r"\.(?:\d+))*))(?:(?:%0[Aa])?(?:%20)*)=(?:(?:%0[Aa])?(?:%20)*))?(?:(?:[a"
            r"-zA-Z\d$\-_.+!*'(),]|(?:%[a-fA-F\d]{2}))*)))*))*(?:(?:(?:%0[Aa])?(?:%2"
            r"0)*)(?:[;,])(?:(?:%0[Aa])?(?:%20)*))?)(?:\?(?:(?:(?:(?:[a-zA-Z\d$\-_.+"
            r"!*'(),]|(?:%[a-fA-F\d]{2}))+)(?:,(?:(?:[a-zA-Z\d$\-_.+!*'(),]|(?:%[a-f"
            r"A-F\d]{2}))+))*)?)(?:\?(?:base|one|sub)(?:\?(?:((?:[a-zA-Z\d$\-_.+!*'("
            r"),;/?:@&=]|(?:%[a-fA-F\d]{2}))+)))?)?)?)|(?:(?:z39\.50[rs])://(?:(?:(?"
            r":(?:(?:[a-zA-Z\d](?:(?:[a-zA-Z\d]|-)*[a-zA-Z\d])?)\.)*(?:[a-zA-Z](?:(?"
            r":[a-zA-Z\d]|-)*[a-zA-Z\d])?))|(?:(?:\d+)(?:\.(?:\d+)){3}))(?::(?:\d+))"
            r"?)(?:/(?:(?:(?:[a-zA-Z\d$\-_.+!*'(),]|(?:%[a-fA-F\d]{2}))+)(?:\+(?:(?:"
            r"[a-zA-Z\d$\-_.+!*'(),]|(?:%[a-fA-F\d]{2}))+))*(?:\?(?:(?:[a-zA-Z\d$\-_"
            r".+!*'(),]|(?:%[a-fA-F\d]{2}))+))?)?(?:;esn=(?:(?:[a-zA-Z\d$\-_.+!*'(),"
            r"]|(?:%[a-fA-F\d]{2}))+))?(?:;rs=(?:(?:[a-zA-Z\d$\-_.+!*'(),]|(?:%[a-fA"
            r"-F\d]{2}))+)(?:\+(?:(?:[a-zA-Z\d$\-_.+!*'(),]|(?:%[a-fA-F\d]{2}))+))*)"
            r"?))|(?:cid:(?:(?:(?:[a-zA-Z\d$\-_.+!*'(),]|(?:%[a-fA-F\d]{2}))|[;?:@&="
            r"])*))|(?:mid:(?:(?:(?:[a-zA-Z\d$\-_.+!*'(),]|(?:%[a-fA-F\d]{2}))|[;?:@"
            r"&=])*)(?:/(?:(?:(?:[a-zA-Z\d$\-_.+!*'(),]|(?:%[a-fA-F\d]{2}))|[;?:@&=]"
            r")*))?)|(?:vemmi://(?:(?:(?:(?:(?:[a-zA-Z\d](?:(?:[a-zA-Z\d]|-)*[a-zA-Z"
            r"\d])?)\.)*(?:[a-zA-Z](?:(?:[a-zA-Z\d]|-)*[a-zA-Z\d])?))|(?:(?:\d+)(?:\."
            r"(?:\d+)){3}))(?::(?:\d+))?)(?:/(?:(?:(?:[a-zA-Z\d$\-_.+!*'(),]|(?:%[a"
            r"-fA-F\d]{2}))|[/?:@&=])*)(?:(?:;(?:(?:(?:[a-zA-Z\d$\-_.+!*'(),]|(?:%[a"
            r"-fA-F\d]{2}))|[/?:@&])*)=(?:(?:(?:[a-zA-Z\d$\-_.+!*'(),]|(?:%[a-fA-F\d"
            r"]{2}))|[/?:@&])*))*))?)|(?:imap://(?:(?:(?:(?:(?:(?:(?:[a-zA-Z\d$\-_.+"
            r"!*'(),]|(?:%[a-fA-F\d]{2}))|[&=~])+)(?:(?:;[Aa][Uu][Tt][Hh]=(?:\*|(?:("
            r"?:(?:[a-zA-Z\d$\-_.+!*'(),]|(?:%[a-fA-F\d]{2}))|[&=~])+))))?)|(?:(?:;["
            r"Aa][Uu][Tt][Hh]=(?:\*|(?:(?:(?:[a-zA-Z\d$\-_.+!*'(),]|(?:%[a-fA-F\d]{2"
            r"}))|[&=~])+)))(?:(?:(?:(?:[a-zA-Z\d$\-_.+!*'(),]|(?:%[a-fA-F\d]{2}))|["
            r"&=~])+))?))@)?(?:(?:(?:(?:(?:[a-zA-Z\d](?:(?:[a-zA-Z\d]|-)*[a-zA-Z\d])"
            r"?)\.)*(?:[a-zA-Z](?:(?:[a-zA-Z\d]|-)*[a-zA-Z\d])?))|(?:(?:\d+)(?:\.(?:"
            r"\d+)){3}))(?::(?:\d+))?))/(?:(?:(?:(?:(?:(?:[a-zA-Z\d$\-_.+!*'(),]|(?:"
            r"%[a-fA-F\d]{2}))|[&=~:@/])+)?;[Tt][Yy][Pp][Ee]=(?:[Ll](?:[Ii][Ss][Tt]|"
            r"[Ss][Uu][Bb])))|(?:(?:(?:(?:[a-zA-Z\d$\-_.+!*'(),]|(?:%[a-fA-F\d]{2}))"
            r"|[&=~:@/])+)(?:\?(?:(?:(?:[a-zA-Z\d$\-_.+!*'(),]|(?:%[a-fA-F\d]{2}))|["
            r"&=~:@/])+))?(?:(?:;[Uu][Ii][Dd][Vv][Aa][Ll][Ii][Dd][Ii][Tt][Yy]=(?:[1-"
            r"9]\d*)))?)|(?:(?:(?:(?:[a-zA-Z\d$\-_.+!*'(),]|(?:%[a-fA-F\d]{2}))|[&=~"
            r":@/])+)(?:(?:;[Uu][Ii][Dd][Vv][Aa][Ll][Ii][Dd][Ii][Tt][Yy]=(?:[1-9]\d*"
            r")))?(?:/;[Uu][Ii][Dd]=(?:[1-9]\d*))(?:(?:/;[Ss][Ee][Cc][Tt][Ii][Oo][Nn"
            r"]=(?:(?:(?:[a-zA-Z\d$\-_.+!*'(),]|(?:%[a-fA-F\d]{2}))|[&=~:@/])+)))?))"
            r")?)|(?:nfs:(?:(?://(?:(?:(?:(?:(?:[a-zA-Z\d](?:(?:[a-zA-Z\d]|-)*[a-zA-"
            r"Z\d])?)\.)*(?:[a-zA-Z](?:(?:[a-zA-Z\d]|-)*[a-zA-Z\d])?))|(?:(?:\d+)(?:"
            r"\.(?:\d+)){3}))(?::(?:\d+))?)(?:(?:/(?:(?:(?:(?:(?:[a-zA-Z\d\$\-_.!~*'"
            r"(),])|(?:%[a-fA-F\d]{2})|[:@&=+])*)(?:/(?:(?:(?:[a-zA-Z\d\$\-_.!~*'(),"
            r"])|(?:%[a-fA-F\d]{2})|[:@&=+])*))*)?)))?)|(?:/(?:(?:(?:(?:(?:[a-zA-Z\d"
            r"\$\-_.!~*'(),])|(?:%[a-fA-F\d]{2})|[:@&=+])*)(?:/(?:(?:(?:[a-zA-Z\d\$\-"
            r"_.!~*'(),])|(?:%[a-fA-F\d]{2})|[:@&=+])*))*)?))|(?:(?:(?:(?:(?:[a-zA-"
            r"Z\d\$\-_.!~*'(),])|(?:%[a-fA-F\d]{2})|[:@&=+])*)(?:/(?:(?:(?:[a-zA-Z\d"
            r"\$\-_.!~*'(),])|(?:%[a-fA-F\d]{2})|[:@&=+])*))*)?)))" 
            )
    return absoluteUrlPattern.match(url) is not None
       
def isValid(url):
    return relativeUrlPattern.match(url) is not None
    
def isAbsolute(url):
    if url:
        scheme, sep, path = url.partition(":")
        if scheme in ("http", "https", "ftp"):
            return path.startswith("//")
        if scheme == "urn":
            return True
    return False

def parseRfcDatetime(rfc2822date):
    from email.utils import parsedate
    from datetime import datetime
    if rfc2822date:
        d = parsedate(rfc2822date)
        if d:
            return datetime(d[0],d[1],d[2],d[3],d[4],d[5])
    return None
       
def relativeUri(baseUri, relativeUri): # return uri relative to this modelDocument uri
    if relativeUri.startswith('http://'):
        return relativeUri
    else:
        return os.path.relpath(relativeUri, os.path.dirname(baseUri)).replace('\\','/')

