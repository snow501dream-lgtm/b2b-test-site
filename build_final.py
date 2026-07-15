import json, copy

ws5 = json.load(open(r'C:\Users\huhu\Desktop\json\GTM-PPLVHVWR_workspace6-1.json', 'r', encoding='utf-8'))
out = copy.deepcopy(ws5)
cv = out['containerVersion']
for key in ['builtInVariable', 'fingerprint', 'tagManagerUrl']:
    cv.pop(key, None)

# filter out test items
cv['variable'] = [v for v in cv.get('variable', []) if not v.get('name', '').startswith('test-')]
cv['tag'] = [t for t in cv.get('tag', []) if not t.get('name', '').startswith('test-')]

AID, CID = '6355959832', '252791019'

def tpl(k, v): return {'type': 'TEMPLATE', 'key': k, 'value': v}
def boo(k, v): return {'type': 'BOOLEAN', 'key': k, 'value': v}
def obj(*pairs): return {'type': 'MAP', 'map': [{'type': 'TEMPLATE', 'key': k, 'value': v} for k, v in pairs]}

# ── 6 variables ──
new_vars = [
    # 3 dataLayer
    {'accountId': AID, 'containerId': CID, 'name': 'dlv - user_country', 'type': 'v',
     'parameter': [
         {'type': 'INTEGER', 'key': 'dataLayerVersion', 'value': '2'},
         {'type': 'BOOLEAN', 'key': 'setDefaultValue', 'value': 'false'},
         tpl('name', 'user_country')
     ], 'formatValue': {}},
    {'accountId': AID, 'containerId': CID, 'name': 'dlv-cta_name', 'type': 'v',
     'parameter': [
         {'type': 'INTEGER', 'key': 'dataLayerVersion', 'value': '2'},
         {'type': 'BOOLEAN', 'key': 'setDefaultValue', 'value': 'false'},
         tpl('name', 'cta_name')
     ], 'formatValue': {}},
    {'accountId': AID, 'containerId': CID, 'name': 'dlv-product_name', 'type': 'v',
     'parameter': [
         {'type': 'INTEGER', 'key': 'dataLayerVersion', 'value': '2'},
         {'type': 'BOOLEAN', 'key': 'setDefaultValue', 'value': 'false'},
         tpl('name', 'product_name')
     ], 'formatValue': {}},

    # 1 regex (remm) — key=key/value NOT pattern/output
    {'accountId': AID, 'containerId': CID, 'name': 'regex - legal region archetype', 'type': 'remm',
     'parameter': [
         boo('setDefaultValue', 'false'),
         tpl('input', '{{dlv - user_country}}'),
         boo('fullMatch', 'true'),
         boo('replaceAfterMatch', 'true'),
         boo('ignoreCase', 'true'),
         {'type': 'LIST', 'key': 'map', 'list': [
             obj(('key', '^(BY|SG|KR|GB|DE|FR|IT|ES|PL|NL|BE|IE|AT|PT|SE|DK|FI|CZ|RO|BR|CH|ZA)$'), ('value', 'strict-opt-in')),
             obj(('key', '^(US|CA|JP|AU)$'), ('value', 'notice-opt-out'))
         ]}
     ], 'formatValue': {}},

    # 2 lookup (smm)
    {'accountId': AID, 'containerId': CID, 'name': 'lookup - silktide mode', 'type': 'smm',
     'parameter': [
         boo('setDefaultValue', 'true'),
         tpl('input', '{{regex - legal region archetype}}'),
         tpl('defaultValue', 'opt-out'),
         {'type': 'LIST', 'key': 'map', 'list': [
             obj(('key', 'strict-opt-in'), ('value', 'opt-in')),
             obj(('key', 'notice-opt-out'), ('value', 'opt-out')),
             obj(('key', 'none'), ('value', 'opt-out'))
         ]}
     ], 'formatValue': {}},

    {'accountId': AID, 'containerId': CID, 'name': 'lookup - silktide banner description', 'type': 'smm',
     'parameter': [
         boo('setDefaultValue', 'true'),
         tpl('input', '{{regex - legal region archetype}}'),
         tpl('defaultValue', ''),
         {'type': 'LIST', 'key': 'map', 'list': [
             obj(('key', 'strict-opt-in'), ('value', 'We require your active consent to use cookies for advertising and analytics.')),
             obj(('key', 'notice-opt-out'), ('value', 'We use cookies for optimization. You have the right to opt-out.'))
         ]}
     ], 'formatValue': {}}
]
cv['variable'] = cv['variable'] + new_vars

# ── 3 triggers ──
for tid, tname, event in [
    ('30', 'cta_click trigger', 'cta_click'),
    ('31', 'inquiry_click trigger', 'inquiry_click'),
    ('32', 'Custom Event - stcm_consent_update', 'stcm_consent_update')
]:
    cv['trigger'].append({
        'accountId': AID, 'containerId': CID,
        'triggerId': tid, 'name': tname, 'type': 'CUSTOM_EVENT',
        'customEventFilter': [{'type': 'EQUALS', 'parameter': [tpl('arg0', '{{_event}}'), tpl('arg1', event)]}]
    })

# ── 5 tags ──
html_v = '<script>\n(function(){\n  var a = \'{{regex - legal region archetype}}\';\n  if(a === \'none\') return;\n\n  var s = document.createElement(\'script\');\n  s.src = \'/js/silktide-consent-manager.js\';\n  s.onload = function(){\n    window.silktideConsentManager.init({\n      mode: \'{{lookup - silktide mode}}\',\n      text: {\n        title: \'Privacy Settings\',\n        description: \'{{lookup - silktide banner description}}\'\n      },\n      consentTypes: [\n        { id: \'analytics\', label: \'Analytics\', gtag: \'analytics_storage\' },\n        { id: \'advertising\', label: \'Marketing\', gtag: [\'ad_storage\',\'ad_user_data\',\'ad_personalization\'] }\n      ],\n      options: { expandedByDefault: a === \'strict-opt-in\' }\n    });\n  };\n  document.head.appendChild(s);\n})();\n</script>'

def consent(cv):
    return {'consentStatus': 'NEEDED', 'consentType': {'type': 'LIST', 'list': [{'type': 'TEMPLATE', 'value': cv}]}}

def tag(nm, tp, params, trigs, opt='ONCE_PER_EVENT'):
    return {'accountId': AID, 'containerId': CID, 'name': nm, 'type': tp,
            'parameter': params, 'firingTriggerId': trigs,
            'tagFiringOption': opt, 'monitoringMetadata': {'type': 'MAP'}}

new_tags = [
    tag('GA4 event-cta_click', 'gaawe', [
        boo('sendEcommerceData', 'false'),
        tpl('eventName', 'cta_click'),
        tpl('measurementIdOverride', '{{GA-measurement id}}'),
        {'type': 'LIST', 'key': 'eventSettingsTable', 'list': [
            obj(('parameter', 'cta_name'), ('parameterValue', '{{dlv-cta_name}}'))
        ]}
    ], ['30']),

    tag('GA4 event-inquiry_click', 'gaawe', [
        boo('sendEcommerceData', 'false'),
        tpl('eventName', 'inquiry_click'),
        tpl('measurementIdOverride', '{{GA-measurement id}}'),
        {'type': 'LIST', 'key': 'eventSettingsTable', 'list': [
            obj(('parameter', 'product_name'), ('parameterValue', '{{dlv-product_name}}'))
        ]}
    ], ['31']),

    tag('google ads-form_submit', 'awct', [
        tpl('conversionId', '18122392881'),
        tpl('conversionLabel', '3U3NCP7Ik9AcELGKt8FD'),
        boo('enableConversionLinker', 'true'),
        boo('enableNewCustomerReporting', 'false'),
        boo('enableProductReporting', 'false'),
        boo('enableShippingData', 'false'),
        boo('rdp', 'false')
    ], ['16']),

    tag('google ads-whatsapp_click', 'awct', [
        tpl('conversionId', '18122392881'),
        tpl('conversionLabel', 'Ug_iCPTZk9AcELGKt8FD'),
        boo('enableConversionLinker', 'true'),
        boo('enableNewCustomerReporting', 'false'),
        boo('enableProductReporting', 'false'),
        boo('enableShippingData', 'false'),
        boo('rdp', 'false')
    ], ['18']),

    tag('Consent - Silktide Initialization', 'html', [
        tpl('html', html_v), boo('supportDocumentWrite', 'true')
    ], ['2147479573'], opt='ONCE_PER_LOAD')
]

cv['tag'] = cv['tag'] + new_tags

# ── Consent for ALL tracking tags. Trigger 32 ONLY for googtag (config) ──
for tag in cv['tag']:
    ttype = tag.get('type', '')
    name = tag.get('name', '')
    if ttype in ('gclidw', 'html'):
        continue
    elif ttype in ('awct',) or 'ads' in name.lower() or 'AW' in name:
        cval = 'ad_storage'
    elif ttype in ('googtag', 'gaawe'):
        cval = 'analytics_storage'
    else:
        continue

    tag['consentSettings'] = consent(cval)

    # Only googtag config tags need trigger 32 (consent update)
    if ttype == 'googtag':
        ft = tag.get('firingTriggerId', [])
        if '32' not in ft:
            ft.append('32')
            tag['firingTriggerId'] = ft
        print(f'  +consent({cval}) +t32: {name}')
    else:
        print(f'  +consent({cval}): {name}')

# ── Save ──
out_path = r'C:\Users\huhu\Desktop\json\GTM_complete.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print(f'\nSaved: {out_path}')
print(f'  Vars: {len(cv["variable"])} (+6)')
print(f'  Triggers: {len(cv["trigger"])} (+3)')
print(f'  Tags: {len(cv["tag"])} (+5)')
print()
print('Import with: Merge + Overwrite conflicting')
