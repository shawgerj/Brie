from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _

class RicottaApp(CMSApp):
    name = _("Ricotta App")
    urls = ["ricotta.urls"]

apphook_pool.register(RicottaApp)
