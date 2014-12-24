import pkg_resources
import requests

from urlparse import urlparse

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String
from xblock.fragment import Fragment

class SimpleVideoBlock(XBlock):
    """
    An XBlock providing oEmbed capabilities for video
    """

    href = String(help="URL of the video page at the provider", default=None, scope=Scope.content)
    maxwidth = Integer(help="Maximum width of the video", default=800, scope=Scope.content)
    maxheight = Integer(help="Maximum height of the video", default=450, scope=Scope.content)    

    def student_view(self, context):
        """
        Create a fragment used to display the XBlock to a student.
        `context` is a dictionary used to configure the display (unused).

        Returns a `Fragment` object specifying the HTML, CSS, and JavaScript
        to display.
        """
        provider, embed_code = self.get_embed_code_for_url(self.href)

        # Load the HTML fragment from within the package and fill in the template
        html_str = pkg_resources.resource_string(__name__, "static/html/simplevideo.html")
        frag = Fragment(unicode(html_str).format(self=self, embed_code=embed_code))

        return frag

    def get_embed_code_for_url(self, url):
        """
        Get the code to embed from the oEmbed provider.
        """
        hostname = url and urlparse(url).hostname
        # Check that the provider is supported
        if hostname == 'vimeo.com':
            oembed_url = 'https://vimeo.com/api/oembed.json'
        else:
            return hostname, '<p>Unsupported video provider ({0})</p>'.format(hostname)

        params = {
            'url': url,
            'format': 'json',
            'maxwidth': self.maxwidth,
            'maxheight': self.maxheight,
            'api': True
        }

        try:
            r = requests.get(oembed_url, params=params)
            r.raise_for_status()
        except Exception as e:
            return hostname, '<p>Error getting video from provider ({error})</p>'.format(error=e)
        response = r.json()
        return hostname, response['html']
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("simple video",
            """
            <vertical_demo>
                <simplevideo href="https://vimeo.com/46100581" maxwidth="800" />
                <html_demo><div>Rate the video:</div></html_demo>
                <thumbs />
            </vertical_demo>
            """)
        ]
