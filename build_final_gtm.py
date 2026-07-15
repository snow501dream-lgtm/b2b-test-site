import json

with open(r'C:\Users\huhu\b2b-test-site\GTM-PPLVHVWR_v4.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

cv = d['containerVersion']

# Remove sections not valid for import
for key in ['builtInVariable', 'fingerprint', 'tagManagerUrl']:
    cv.pop(key, None)

# ── 6 new variables ──
new_vars = [
    {
        'name': 'dlv - user_country', 'type': 'v',
        'parameter': [
            {'type': 'INTEGER', 'key': 'dataLayerVersion', 'value': '2'},
            {'type': 'BOOLEAN', 'key': 'setDefaultValue', 'value': 'false'},
            {'type': 'TEMPLATE', 'key': 'name', 'value': 'user_country'}
        ]
    },
    {
        'name': 'regex - legal region archetype', 'type': 'REM',
        'parameter': [
            {'type': 'TEMPLATE', 'key': 'input', 'value': '{{dlv - user_country}}'},
            {'type': 'LIST', 'key': 'map', 'list': [
                {'type': 'MAP', 'map': [
                    {'type': 'TEMPLATE', 'key': 'pattern', 'value': '^(BY|SG|KR|GB|DE|FR|IT|ES|PL|NL|BE|IE|AT|PT|SE|DK|FI|CZ|RO)$'},
                    {'type': 'TEMPLATE', 'key': 'output', 'value': 'strict-opt-in'}
                ]},
                {'type': 'MAP', 'map': [
                    {'type': 'TEMPLATE', 'key': 'pattern', 'value': '^(US|CA)$'},
                    {'type': 'TEMPLATE', 'key': 'output', 'value': 'notice-opt-out'}
                ]}
            ]},
            {'type': 'BOOLEAN', 'key': 'fullMatch', 'value': 'true'},
            {'type': 'BOOLEAN', 'key': 'ignoreCase', 'value': 'true'},
            {'type': 'TEMPLATE', 'key': 'defaultValue', 'value': 'none'}
        ]
    },
    {
        'name': 'lookup - silktide mode', 'type': 'SML',
        'parameter': [
            {'type': 'TEMPLATE', 'key': 'input', 'value': '{{regex - legal region archetype}}'},
            {'type': 'LIST', 'key': 'map', 'list': [
                {'type': 'MAP', 'map': [{'type': 'TEMPLATE', 'key': 'key', 'value': 'strict-opt-in'}, {'type': 'TEMPLATE', 'key': 'val', 'value': 'opt-in'}]},
                {'type': 'MAP', 'map': [{'type': 'TEMPLATE', 'key': 'key', 'value': 'notice-opt-out'}, {'type': 'TEMPLATE', 'key': 'val', 'value': 'opt-out'}]},
                {'type': 'MAP', 'map': [{'type': 'TEMPLATE', 'key': 'key', 'value': 'none'}, {'type': 'TEMPLATE', 'key': 'val', 'value': 'opt-out'}]}
            ]},
            {'type': 'TEMPLATE', 'key': 'defaultValue', 'value': 'opt-out'}
        ]
    },
    {
        'name': 'lookup - silktide banner description', 'type': 'SML',
        'parameter': [
            {'type': 'TEMPLATE', 'key': 'input', 'value': '{{regex - legal region archetype}}'},
            {'type': 'LIST', 'key': 'map', 'list': [
                {'type': 'MAP', 'map': [{'type': 'TEMPLATE', 'key': 'key', 'value': 'strict-opt-in'}, {'type': 'TEMPLATE', 'key': 'val', 'value': 'We require your active consent to use cookies for advertising and analytics.'}]},
                {'type': 'MAP', 'map': [{'type': 'TEMPLATE', 'key': 'key', 'value': 'notice-opt-out'}, {'type': 'TEMPLATE', 'key': 'val', 'value': 'We use cookies for optimization. You have the right to opt-out.'}]}
            ]},
            {'type': 'TEMPLATE', 'key': 'defaultValue', 'value': ''}
        ]
    },
    {
        'name': 'dlv-cta_name', 'type': 'v',
        'parameter': [
            {'type': 'INTEGER', 'key': 'dataLayerVersion', 'value': '2'},
            {'type': 'BOOLEAN', 'key': 'setDefaultValue', 'value': 'false'},
            {'type': 'TEMPLATE', 'key': 'name', 'value': 'cta_name'}
        ]
    },
    {
        'name': 'dlv-product_name', 'type': 'v',
        'parameter': [
            {'type': 'INTEGER', 'key': 'dataLayerVersion', 'value': '2'},
            {'type': 'BOOLEAN', 'key': 'setDefaultValue', 'value': 'false'},
            {'type': 'TEMPLATE', 'key': 'name', 'value': 'product_name'}
        ]
    }
]

# ── 3 new triggers (with explicit triggerId) ──
new_triggers = [
    {
        'triggerId': '30',
        'name': 'cta_click trigger', 'type': 'CUSTOM_EVENT',
        'customEventFilter': [{
            'type': 'EQUALS',
            'parameter': [
                {'type': 'TEMPLATE', 'key': 'arg0', 'value': '{{_event}}'},
                {'type': 'TEMPLATE', 'key': 'arg1', 'value': 'cta_click'}
            ]
        }]
    },
    {
        'triggerId': '31',
        'name': 'inquiry_click trigger', 'type': 'CUSTOM_EVENT',
        'customEventFilter': [{
            'type': 'EQUALS',
            'parameter': [
                {'type': 'TEMPLATE', 'key': 'arg0', 'value': '{{_event}}'},
                {'type': 'TEMPLATE', 'key': 'arg1', 'value': 'inquiry_click'}
            ]
        }]
    },
    {
        'triggerId': '32',
        'name': 'Custom Event - stcm_consent_update', 'type': 'CUSTOM_EVENT',
        'customEventFilter': [{
            'type': 'EQUALS',
            'parameter': [
                {'type': 'TEMPLATE', 'key': 'arg0', 'value': '{{_event}}'},
                {'type': 'TEMPLATE', 'key': 'arg1', 'value': 'stcm_consent_update'}
            ]
        }]
    }
]

# ── 5 new tags ──
html_val = '<script>\n(function(){\n  var a = \'{{regex - legal region archetype}}\';\n  if(a === \'none\') return;\n\n  silktideConsentManager.init({\n    mode: \'{{lookup - silktide mode}}\',\n    text: {\n      title: \'Privacy Settings\',\n      description: \'{{lookup - silktide banner description}}\'\n    },\n    consentTypes: [\n      { id: \'analytics\', label: \'Analytics\', gtag: \'analytics_storage\' },\n      { id: \'advertising\', label: \'Marketing\', gtag: [\'ad_storage\',\'ad_user_data\',\'ad_personalization\'] }\n    ],\n    options: { expandedByDefault: a === \'strict-opt-in\' }\n  });\n})();\n</script>'

new_tags = [
    {
        'name': 'GA4 event-cta_click', 'type': 'gaawe',
        'parameter': [
            {'type': 'TEMPLATE', 'key': 'eventName', 'value': 'cta_click'},
            {'type': 'TEMPLATE', 'key': 'measurementId', 'value': 'G-50PJHKG2M5'},
            {'type': 'LIST', 'key': 'eventParameters', 'list': [
                {'type': 'MAP', 'map': [
                    {'type': 'TEMPLATE', 'key': 'parameterName', 'value': 'cta_name'},
                    {'type': 'TEMPLATE', 'key': 'parameterValue', 'value': '{{dlv-cta_name}}'}
                ]}
            ]}
        ],
        'firingTriggerId': ['30'], 'tagFiringOption': 'ONCE_PER_EVENT'
    },
    {
        'name': 'GA4 event-inquiry_click', 'type': 'gaawe',
        'parameter': [
            {'type': 'TEMPLATE', 'key': 'eventName', 'value': 'inquiry_click'},
            {'type': 'TEMPLATE', 'key': 'measurementId', 'value': 'G-50PJHKG2M5'},
            {'type': 'LIST', 'key': 'eventParameters', 'list': [
                {'type': 'MAP', 'map': [
                    {'type': 'TEMPLATE', 'key': 'parameterName', 'value': 'product_name'},
                    {'type': 'TEMPLATE', 'key': 'parameterValue', 'value': '{{dlv-product_name}}'}
                ]}
            ]}
        ],
        'firingTriggerId': ['31'], 'tagFiringOption': 'ONCE_PER_EVENT'
    },
    {
        'name': 'google ads-form_submit', 'type': 'awct',
        'parameter': [
            {'type': 'TEMPLATE', 'key': 'conversionId', 'value': '18122392881'},
            {'type': 'TEMPLATE', 'key': 'conversionLabel', 'value': '3U3NCP7Ik9AcELGKt8FD'},
            {'type': 'BOOLEAN', 'key': 'enableConversionLinker', 'value': 'true'},
            {'type': 'BOOLEAN', 'key': 'enableNewCustomerReporting', 'value': 'false'},
            {'type': 'BOOLEAN', 'key': 'enableProductReporting', 'value': 'false'},
            {'type': 'BOOLEAN', 'key': 'enableShippingData', 'value': 'false'},
            {'type': 'BOOLEAN', 'key': 'rdp', 'value': 'false'}
        ],
        'firingTriggerId': ['16'], 'tagFiringOption': 'ONCE_PER_EVENT'
    },
    {
        'name': 'google ads-whatsapp_click', 'type': 'awct',
        'parameter': [
            {'type': 'TEMPLATE', 'key': 'conversionId', 'value': '18122392881'},
            {'type': 'TEMPLATE', 'key': 'conversionLabel', 'value': 'Ug_iCPTZk9AcELGKt8FD'},
            {'type': 'BOOLEAN', 'key': 'enableConversionLinker', 'value': 'true'},
            {'type': 'BOOLEAN', 'key': 'enableNewCustomerReporting', 'value': 'false'},
            {'type': 'BOOLEAN', 'key': 'enableProductReporting', 'value': 'false'},
            {'type': 'BOOLEAN', 'key': 'enableShippingData', 'value': 'false'},
            {'type': 'BOOLEAN', 'key': 'rdp', 'value': 'false'}
        ],
        'firingTriggerId': ['18'], 'tagFiringOption': 'ONCE_PER_EVENT'
    },
    {
        'name': 'Consent - Silktide Initialization', 'type': 'html',
        'parameter': [
            {'type': 'TEMPLATE', 'key': 'html', 'value': html_val},
            {'type': 'BOOLEAN', 'key': 'supportDocumentWrite', 'value': 'true'}
        ],
        'firingTriggerId': ['2147479571'], 'tagFiringOption': 'ONCE_PER_LOAD'
    }
]

# ── Merge ──
cv['variable'] = cv.get('variable', []) + new_vars
cv['trigger'] = cv.get('trigger', []) + new_triggers
cv['tag'] = cv.get('tag', []) + new_tags

# ── Summary ──
print(f'Variables: {len(cv["variable"])}')
for v in cv['variable']:
    print(f'  [{v["type"]}] {v["name"]}')
print(f'\nTriggers: {len(cv["trigger"])}')
for t in cv['trigger']:
    tid = t.get('triggerId', '?')
    print(f'  [{tid}] {t["name"]}')
print(f'\nTags: {len(cv["tag"])}')
for t in cv['tag']:
    trigs = ','.join(t.get('firingTriggerId', []))
    opt = t.get('tagFiringOption', '')
    print(f'  [{t["type"]}] {t["name"]} -> triggers={trigs} ({opt})')

# ── Save ──
out = r'C:\Users\huhu\Desktop\GTM_complete.json'
with open(out, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print(f'\nSaved: {out}')
