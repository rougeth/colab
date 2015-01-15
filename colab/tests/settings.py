from ..settings import *

LOGGING = {
    'version': 1,

    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
    },

    'loggers': {
        'colab.mailman': {
            'handlers': ['null'],
            'propagate': False,
        },
        'haystack': {
            'handlers': ['null'],
            'propagate': False,
        },
        'pysolr': {
            'handlers': ['null'],
            'propagate': False,
        },
    },
}

import os
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
    },
}
