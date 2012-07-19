from menus.base import Menu, NavigationNode
from menus.menu_pool import menu_pool
from django.utils.translation import ugettext_lazy as _

class TestMenu(Menu):
    def get_nodes(self, request):
        nodes = []
        n = NavigationNode(_('calendar'), "/calendar/Tech/", 1)
        nodes.append(n)
        return nodes

menu_pool.register_menu(TestMenu)
