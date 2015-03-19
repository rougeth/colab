from collections import OrderedDict

from django import template
from django.core.cache import cache
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

register = template.Library()


@register.simple_tag(takes_context=True)
def plugins_menu(context):
    if context['user'].is_authenticated():
        cache_key = 'colab-proxy-menu-authenticated'
    else:
        cache_key = 'colab-proxy-menu-anonymous'

    menu_from_cache = cache.get(cache_key)

    if menu_from_cache:
        return menu_from_cache

    menu_links = OrderedDict()
    proxied_apps = context.get('proxy', {})

    for app_name, app in proxied_apps.items():
        if not app.get('menu'):
            continue

        menu = app.get('menu')
        title = menu.get('title', app_name)
        links = menu.get('links', tuple()).items()
        if context['user'].is_active:
            links += menu.get('auth_links', tuple()).items()

        if not links:
            continue

        if title not in menu_links:
            menu_links[_(title)] = []

        for text, link in links:
            url = link
            menu_links[_(title)].append((_(text), url))

    menu = render_to_string('plugins/menu_template.html',
                            {'menu_links': menu_links})

    cache.set(cache_key, menu)
    return menu