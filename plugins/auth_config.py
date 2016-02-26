# config.py

from authomatic.providers import oauth2, oauth1

CONFIG = {

    'tw': { # Your internal provider name

        # Provider class
        'class_': oauth1.Twitter,

        # Twitter is an AuthorizationProvider so we need to set several other properties too:
        'consumer_key': 'ihZeB5R25jY6BTaIKw4YqtKGM',
        'consumer_secret': 'GVYgsp68PgxEXYPP4RQj6YO0DTyrGtK7TiWRcHO9IAsiYxtzJj',
    },

    'fb': {

        'class_': oauth2.Facebook,

        # Facebook is an AuthorizationProvider too.
        'consumer_key': '153041951709457',
        'consumer_secret': '41c6a4277b9d0dba15428c139d99bf68',

        # But it is also an OAuth 2.0 provider and it needs scope.
        'scope': ['public_profile', 'email'],
    }
}
