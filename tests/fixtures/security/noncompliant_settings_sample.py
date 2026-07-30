"""Deliberately non-compliant sample for secret-literal scanner tests."""

API_SECRET = 'hardcoded-secret-value'

VOIP = [
    {
        'OPTIONS': {
            'key': 'literal-api-key',
            'secret': 'literal-api-secret',
        },
    },
]
