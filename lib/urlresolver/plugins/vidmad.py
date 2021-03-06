'''
    urlresolver Kodi plugin
    Copyright (C) 2016 Gujal

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import re
from lib import helpers
from lib import jsunpack
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class VidMadResolver(UrlResolver):
    name = "vidmad.net"
    domains = ["vidmad.net", "tamildrive.com"]
    pattern = '(?://|\.)((?:vidmad|tamildrive)\.(?:net|com))/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content

        if 'Not Found' in html:
            raise ResolverError('File Removed')

        if 'Video is processing' in html:
            raise ResolverError('File still being processed')

        packed = re.search('(eval\(function.*?)\s*</script>', html, re.DOTALL)
        if packed:
            js = jsunpack.unpack(packed.group(1))
        else:
            js = html

        match = re.search('sources\s*:\s*\[(.*?)\]', js, re.DOTALL)
        if match:
            sources = eval(match.group(1).replace('file','"file"').replace('label','"label"'))
            if 'label' not in sources[0]:
                sources[0]['label']='HLS'
            sources = [(s['label'], s['file']) for s in sources]
            return helpers.pick_source(sources, self.get_setting('auto_pick') == 'true')

        raise ResolverError('Unable to find %s video'%(host))

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id)

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting id="%s_auto_pick" type="bool" label="Automatically pick best quality" default="false" visible="true"/>' % (cls.__name__))
        return xml
