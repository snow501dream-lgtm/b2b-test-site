import json

with open(r'C:\Users\huhu\Desktop\json\GTM-PPLVHVWR_workspace5.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

cv = d['containerVersion']
for key in ['builtInVariable', 'fingerprint', 'tagManagerUrl']:
    cv.pop(key, None)

AID, CID = '6355959832', '252791019'
def tag_base(nm, tp, params, trigs, opt='ONCE_PER_EVENT', consent=None):
    t = {
        'accountId': AID, 'containerId': CID,
        'name': nm, 'type': tp,
        'parameter': params,
        'firingTriggerId': trigs,
        'tagFiringOption': opt,
        'monitoringMetadata': {'type': 'MAP'}
    }
    if consent:
        t['consentSettings'] = consent
    return t

def obj(*items):
    """Build MAP parameter with key-value pairs"""
    return {'type': 'MAP', 'map': [{'type': 'TEMPLATE', 'key': k, 'value': v} for k, v in items]}

def tpl(k, v):
    return {'type': 'TEMPLATE', 'key': k, 'value': v}

def boo(k, v):
    return {'type': 'BOOLEAN', 'key': k, 'value': v}

# ── 6 new variables ──
new_vars = [
    {
        'accountId': AID, 'containerId': CID,
        'name': 'dlv - user_country', 'type': 'v',
        'parameter': [
            {'type': 'INTEGER', 'key': 'dataLayerVersion', 'value': '2'},
            {'type': 'BOOLEAN', 'key': 'setDefaultValue', 'value': 'false'},
            {'type': 'TEMPLATE', 'key': 'name', 'value': 'user_country'}
        ]
    },
    {
        'accountId': AID, 'containerId': CID,
        'name': 'regex - legal region archetype', 'type': 'regex',
        'parameter': [
            tpl('input', '{{dlv - user_country}}'),
            {'type': 'LIST', 'key': 'map', 'list': [
                obj(('pattern', '^(BY|SG|KR|GB|DE|FR|IT|ES|PL|NL|BE|IE|AT|PT|SE|DK|FI|CZ|RO)$'), ('output', 'strict-opt-in')),
                obj(('pattern', '^(US|CA)$'), ('output', 'notice-opt-out'))
            ]},
            boo('fullMatch', 'true'),
            boo('ignoreCase', 'true'),
            tpl('defaultValue', 'none')
        ]
    },
    {
        'accountId': AID, 'containerId': CID,
        'name': 'lookup - silktide mode', 'type': 'lookup',
        'parameter': [
            tpl('input', '{{regex - legal region archetype}}'),
            {'type': 'LIST', 'key': 'map', 'list': [
                obj(('key', 'strict-opt-in'), ('value', 'opt-in')),
                obj(('key', 'notice-opt-out'), ('value', 'opt-out')),
                obj(('key', 'none'), ('value', 'opt-out'))
            ]},
            tpl('defaultValue', 'opt-out')
        ]
    },
    {
        'accountId': AID, 'containerId': CID,
        'name': 'lookup - silktide banner description', 'type': 'lookup',
        'parameter': [
            tpl('input', '{{regex - legal region archetype}}'),
            {'type': 'LIST', 'key': 'map', 'list': [
                obj(('key', 'strict-opt-in'), ('value', 'We require your active consent to use cookies for advertising and analytics.')),
                obj(('key', 'notice-opt-out'), ('value', 'We use cookies for optimization. You have the right to opt-out.'))
            ]},
            tpl('defaultValue', '')
        ]
    },
    {
        'accountId': AID, 'containerId': CID,
        'name': 'dlv-cta_name', 'type': 'v',
        'parameter': [
            {'type': 'INTEGER', 'key': 'dataLayerVersion', 'value': '2'},
            {'type': 'BOOLEAN', 'key': 'setDefaultValue', 'value': 'false'},
            {'type': 'TEMPLATE', 'key': 'name', 'value': 'cta_name'}
        ]
    },
    {
        'accountId': AID, 'containerId': CID,
        'name': 'dlv-product_name', 'type': 'v',
        'parameter': [
            {'type': 'INTEGER', 'key': 'dataLayerVersion', 'value': '2'},
            {'type': 'BOOLEAN', 'key': 'setDefaultValue', 'value': 'false'},
            {'type': 'TEMPLATE', 'key': 'name', 'value': 'product_name'}
        ]
    }
]

# ── 3 new triggers ──
new_triggers = [
    {
        'accountId': AID, 'containerId': CID,
        'triggerId': '30', 'name': 'cta_click trigger', 'type': 'CUSTOM_EVENT',
        'customEventFilter': [{'type': 'EQUALS', 'parameter': [
            tpl('arg0', '{{_event}}'), tpl('arg1', 'cta_click')
        ]}]
    },
    {
        'accountId': AID, 'containerId': CID,
        'triggerId': '31', 'name': 'inquiry_click trigger', 'type': 'CUSTOM_EVENT',
        'customEventFilter': [{'type': 'EQUALS', 'parameter': [
            tpl('arg0', '{{_event}}'), tpl('arg1', 'inquiry_click')
        ]}]
    },
    {
        'accountId': AID, 'containerId': CID,
        'triggerId': '32', 'name': 'Custom Event - stcm_consent_update', 'type': 'CUSTOM_EVENT',
        'customEventFilter': [{'type': 'EQUALS', 'parameter': [
            tpl('arg0', '{{_event}}'), tpl('arg1', 'stcm_consent_update')
        ]}]
    }
]

# ── 5 new tags ──
html_val = '<script>\n(function(){\n  var a = \'{{regex - legal region archetype}}\';\n  if(a === \'none\') return;\n\n  silktideConsentManager.init({\n    mode: \'{{lookup - silktide mode}}\',\n    text: {\n      title: \'Privacy Settings\',\n      description: \'{{lookup - silktide banner description}}\'\n    },\n    consentTypes: [\n      { id: \'analytics\', label: \'Analytics\', gtag: \'analytics_storage\' },\n      { id: \'advertising\', label: \'Marketing\', gtag: [\'ad_storage\',\'ad_user_data\',\'ad_personalization\'] }\n    ],\n    options: { expandedByDefault: a === \'strict-opt-in\' }\n  });\n})();\n</script>'

consent_ad = {'consentStatus': 'NEEDED', 'manualConsentConstraint': [{'type': 'TEMPLATE', 'value': 'ad_storage'}]}
consent_ga = {'consentStatus': 'NEEDED', 'manualConsentConstraint': [{'type': 'TEMPLATE', 'value': 'analytics_storage'}]}

new_tags = [
    tag_base('GA4 event-cta_click', 'gaawe', [
        tpl('eventName', 'cta_click'),
        tpl('measurementId', 'G-50PJHKG2M5'),
        {'type': 'LIST', 'key': 'eventParameters', 'list': [
            obj(('parameter', 'cta_name'), ('parameterValue', '{{dlv-cta_name}}'))
        ]}
    ], ['30', '32'], consent=consent_ga),

    tag_base('GA4 event-inquiry_click', 'gaawe', [
        tpl('eventName', 'inquiry_click'),
        tpl('measurementId', 'G-50PJHKG2M5'),
        {'type': 'LIST', 'key': 'eventParameters', 'list': [
            obj(('parameter', 'product_name'), ('parameterValue', '{{dlv-product_name}}'))
        ]}
    ], ['31', '32'], consent=consent_ga),

    tag_base('google ads-form_submit', 'awct', [
        tpl('conversionId', '18122392881'),
        tpl('conversionLabel', '3U3NCP7Ik9AcELGKt8FD'),
        boo('enableConversionLinker', 'true'),
        boo('enableNewCustomerReporting', 'false'),
        boo('enableProductReporting', 'false'),
        boo('enableShippingData', 'false'),
        boo('rdp', 'false')
    ], ['16', '32'], consent=consent_ad),

    tag_base('google ads-whatsapp_click', 'awct', [
        tpl('conversionId', '18122392881'),
        tpl('conversionLabel', 'Ug_iCPTZk9AcELGKt8FD'),
        boo('enableConversionLinker', 'true'),
        boo('enableNewCustomerReporting', 'false'),
        boo('enableProductReporting', 'false'),
        boo('enableShippingData', 'false'),
        boo('rdp', 'false')
    ], ['18', '32'], consent=consent_ad),

    tag_base('Consent - Silktide Initialization', 'html', [
        tpl('html', html_val),
        boo('supportDocumentWrite', 'true')
    ], ['2147479571'], opt='ONCE_PER_LOAD')
]

# ── Add consent + trigger 32 to existing tags ──
for tag in cv['tag']:
    ttype = tag.get('type', '')
    name = tag.get('name', '')
    if ttype == 'gclidw': continue
    cval = 'ad_storage' if (ttype in ('awct',) or 'AW' in name) else 'analytics_storage'
    tag['consentSettings'] = {'consentStatus': 'NEEDED', 'manualConsentConstraint': [{'type': 'TEMPLATE', 'value': cval}]}
    ft = tag.get('firingTriggerId', [])
    if '32' not in ft: ft.append('32')
    tag['firingTriggerId'] = ft
    print(f'  +consent({cval}) +t32: {name}')

# ── Merge ──
cv['variable'] = cv.get('variable', []) + new_vars
cv['trigger'] = cv.get('trigger', []) + new_triggers
cv['tag'] = cv.get('tag', []) + new_tags

# ── Save ──
out = r'C:\Users\huhu\Desktop\json\GTM_complete.json'
with open(out, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print(f'\nSaved: {out}')
print(f'  Variables: {len(cv["variable"])}')
print(f'  Triggers:  {len(cv["trigger"])}')
print(f'  Tags:      {len(cv["tag"])}')
