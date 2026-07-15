import json, copy

ws5 = json.load(open(r'C:\Users\huhu\Desktop\json\GTM-PPLVHVWR_workspace5.json', 'r', encoding='utf-8'))
out = copy.deepcopy(ws5)
cv = out['containerVersion']
for key in ['builtInVariable', 'fingerprint', 'tagManagerUrl']:
    cv.pop(key, None)

AID, CID = '6355959832', '252791019'

# ── Helper ──
def tpl(k, v): return {'type': 'TEMPLATE', 'key': k, 'value': v}
def boo(k, v): return {'type': 'BOOLEAN', 'key': k, 'value': v}
def obj(*pairs):
    return {'type': 'MAP', 'map': [{'type': 'TEMPLATE', 'key': k, 'value': v} for k, v in pairs]}
def var(nm, tp, params):
    return {'accountId': AID, 'containerId': CID, 'name': nm, 'type': tp, 'parameter': params, 'formatValue': {}}
def trig(tid, nm, event):
    return {'accountId': AID, 'containerId': CID, 'triggerId': tid, 'name': nm, 'type': 'CUSTOM_EVENT',
            'customEventFilter': [{'type': 'EQUALS', 'parameter': [tpl('arg0', '{{_event}}'), tpl('arg1', event)]}]}
def tag(nm, tp, params, trigs, opt='ONCE_PER_EVENT'):
    return {'accountId': AID, 'containerId': CID, 'name': nm, 'type': tp, 'parameter': params,
            'firingTriggerId': trigs, 'tagFiringOption': opt, 'monitoringMetadata': {'type': 'MAP'}}

# ── 6 variables ──
cv['variable'] = cv['variable'] + [
    var('dlv - user_country', 'v', [
        {'type': 'INTEGER', 'key': 'dataLayerVersion', 'value': '2'},
        {'type': 'BOOLEAN', 'key': 'setDefaultValue', 'value': 'false'},
        tpl('name', 'user_country')
    ]),
    var('regex - legal region archetype', 'remm', [
        tpl('input', '{{dlv - user_country}}'),
        {'type': 'LIST', 'key': 'map', 'list': [
            obj(('pattern', '^(BY|SG|KR|GB|DE|FR|IT|ES|PL|NL|BE|IE|AT|PT|SE|DK|FI|CZ|RO)$'), ('output', 'strict-opt-in')),
            obj(('pattern', '^(US|CA)$'), ('output', 'notice-opt-out'))
        ]},
        boo('fullMatch', 'true'), boo('ignoreCase', 'true'), tpl('defaultValue', 'none')
    ]),
    var('lookup - silktide mode', 'smm', [
        tpl('input', '{{regex - legal region archetype}}'),
        {'type': 'LIST', 'key': 'map', 'list': [
            obj(('key', 'strict-opt-in'), ('value', 'opt-in')),
            obj(('key', 'notice-opt-out'), ('value', 'opt-out')),
            obj(('key', 'none'), ('value', 'opt-out'))
        ]},
        tpl('defaultValue', 'opt-out')
    ]),
    var('lookup - silktide banner description', 'smm', [
        tpl('input', '{{regex - legal region archetype}}'),
        {'type': 'LIST', 'key': 'map', 'list': [
            obj(('key', 'strict-opt-in'), ('value', 'We require your active consent to use cookies for advertising and analytics.')),
            obj(('key', 'notice-opt-out'), ('value', 'We use cookies for optimization. You have the right to opt-out.'))
        ]},
        tpl('defaultValue', '')
    ]),
    var('dlv-cta_name', 'v', [
        {'type': 'INTEGER', 'key': 'dataLayerVersion', 'value': '2'},
        {'type': 'BOOLEAN', 'key': 'setDefaultValue', 'value': 'false'},
        tpl('name', 'cta_name')
    ]),
    var('dlv-product_name', 'v', [
        {'type': 'INTEGER', 'key': 'dataLayerVersion', 'value': '2'},
        {'type': 'BOOLEAN', 'key': 'setDefaultValue', 'value': 'false'},
        tpl('name', 'product_name')
    ])
]

# ── 3 triggers ──
cv['trigger'] = cv['trigger'] + [
    trig('30', 'cta_click trigger', 'cta_click'),
    trig('31', 'inquiry_click trigger', 'inquiry_click'),
    trig('32', 'Custom Event - stcm_consent_update', 'stcm_consent_update')
]

# ── 5 tags ──
html_v = '<script>\n(function(){\n  var a = \'{{regex - legal region archetype}}\';\n  if(a === \'none\') return;\n\n  silktideConsentManager.init({\n    mode: \'{{lookup - silktide mode}}\',\n    text: {\n      title: \'Privacy Settings\',\n      description: \'{{lookup - silktide banner description}}\'\n    },\n    consentTypes: [\n      { id: \'analytics\', label: \'Analytics\', gtag: \'analytics_storage\' },\n      { id: \'advertising\', label: \'Marketing\', gtag: [\'ad_storage\',\'ad_user_data\',\'ad_personalization\'] }\n    ],\n    options: { expandedByDefault: a === \'strict-opt-in\' }\n  });\n})();\n</script>'

cv['tag'] = cv['tag'] + [
    tag('GA4 event-cta_click', 'gaawe', [
        boo('sendEcommerceData', 'false'),
        tpl('eventName', 'cta_click'), tpl('measurementIdOverride', '{{GA-measurement id}}'),
        {'type': 'LIST', 'key': 'eventSettingsTable', 'list': [obj(('parameter', 'cta_name'), ('parameterValue', '{{dlv-cta_name}}'))]}
    ], ['30']),

    tag('GA4 event-inquiry_click', 'gaawe', [
        boo('sendEcommerceData', 'false'),
        tpl('eventName', 'inquiry_click'), tpl('measurementIdOverride', '{{GA-measurement id}}'),
        {'type': 'LIST', 'key': 'eventSettingsTable', 'list': [obj(('parameter', 'product_name'), ('parameterValue', '{{dlv-product_name}}'))]}
    ], ['31']),

    tag('google ads-form_submit', 'awct', [
        tpl('conversionId', '18122392881'), tpl('conversionLabel', '3U3NCP7Ik9AcELGKt8FD'),
        boo('enableConversionLinker', 'true'), boo('enableNewCustomerReporting', 'false'),
        boo('enableProductReporting', 'false'), boo('enableShippingData', 'false'), boo('rdp', 'false')
    ], ['16']),

    tag('google ads-whatsapp_click', 'awct', [
        tpl('conversionId', '18122392881'), tpl('conversionLabel', 'Ug_iCPTZk9AcELGKt8FD'),
        boo('enableConversionLinker', 'true'), boo('enableNewCustomerReporting', 'false'),
        boo('enableProductReporting', 'false'), boo('enableShippingData', 'false'), boo('rdp', 'false')
    ], ['18']),

    tag('Consent - Silktide Initialization', 'html', [
        tpl('html', html_v), boo('supportDocumentWrite', 'true')
    ], ['2147479573'], opt='ONCE_PER_LOAD')
]

# NO consent modifications to existing tags

with open(r'C:\Users\huhu\Desktop\json\GTM_complete.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print('Done: {} vars, {} trigs, {} tags'.format(len(cv['variable']), len(cv['trigger']), len(cv['tag'])))
print('No consent settings, formatValue on vars')
