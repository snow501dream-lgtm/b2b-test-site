import json

with open(r'C:\Users\huhu\b2b-test-site\GTM-PPLVHVWR_v3.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

cv = d['containerVersion']
AID = '6355959832'
CID = '252791019'

# ── 4 new variables ──
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
        'accountId': AID, 'containerId': CID,
        'name': 'lookup - silktide mode', 'type': 'SML',
        'parameter': [
            {'type': 'TEMPLATE', 'key': 'input', 'value': '{{regex - legal region archetype}}'},
            {'type': 'LIST', 'key': 'map', 'list': [
                {'type': 'MAP', 'map': [
                    {'type': 'TEMPLATE', 'key': 'key', 'value': 'strict-opt-in'},
                    {'type': 'TEMPLATE', 'key': 'val', 'value': 'opt-in'}
                ]},
                {'type': 'MAP', 'map': [
                    {'type': 'TEMPLATE', 'key': 'key', 'value': 'notice-opt-out'},
                    {'type': 'TEMPLATE', 'key': 'val', 'value': 'opt-out'}
                ]},
                {'type': 'MAP', 'map': [
                    {'type': 'TEMPLATE', 'key': 'key', 'value': 'none'},
                    {'type': 'TEMPLATE', 'key': 'val', 'value': 'opt-out'}
                ]}
            ]},
            {'type': 'TEMPLATE', 'key': 'defaultValue', 'value': 'opt-out'}
        ]
    },
    {
        'accountId': AID, 'containerId': CID,
        'name': 'lookup - silktide banner description', 'type': 'SML',
        'parameter': [
            {'type': 'TEMPLATE', 'key': 'input', 'value': '{{regex - legal region archetype}}'},
            {'type': 'LIST', 'key': 'map', 'list': [
                {'type': 'MAP', 'map': [
                    {'type': 'TEMPLATE', 'key': 'key', 'value': 'strict-opt-in'},
                    {'type': 'TEMPLATE', 'key': 'val', 'value': 'We require your active consent to use cookies for advertising and analytics.'}
                ]},
                {'type': 'MAP', 'map': [
                    {'type': 'TEMPLATE', 'key': 'key', 'value': 'notice-opt-out'},
                    {'type': 'TEMPLATE', 'key': 'val', 'value': 'We use cookies for optimization. You have the right to opt-out of the sale or sharing of data.'}
                ]}
            ]},
            {'type': 'TEMPLATE', 'key': 'defaultValue', 'value': ''}
        ]
    }
]

# ── 1 new trigger ──
new_trigger = {
    'accountId': AID, 'containerId': CID,
    'name': 'Custom Event - stcm_consent_update', 'type': 'CUSTOM_EVENT',
    'customEventFilter': [{
        'type': 'EQUALS',
        'parameter': [
            {'type': 'TEMPLATE', 'key': 'arg0', 'value': '{{_event}}'},
            {'type': 'TEMPLATE', 'key': 'arg1', 'value': 'stcm_consent_update'}
        ]
    }]
}

# ── 1 new tag ──
consent_html = """<script>
(function(){
  var a = '{{regex - legal region archetype}}';
  if(a === 'none') return;

  silktideConsentManager.init({
    mode: '{{lookup - silktide mode}}',
    text: {
      title: 'Privacy Settings',
      description: '{{lookup - silktide banner description}}'
    },
    consentTypes: [
      { id: 'analytics', label: 'Analytics', gtag: 'analytics_storage' },
      { id: 'advertising', label: 'Marketing', gtag: ['ad_storage','ad_user_data','ad_personalization'] }
    ],
    options: { expandedByDefault: a === 'strict-opt-in' }
  });
})();
</script>"""

new_tag = {
    'accountId': AID, 'containerId': CID,
    'name': 'Consent - Silktide Initialization', 'type': 'html',
    'parameter': [
        {'type': 'TEMPLATE', 'key': 'html', 'value': consent_html},
        {'type': 'BOOLEAN', 'key': 'supportDocumentWrite', 'value': 'true'}
    ],
    'firingTriggerId': ['2147479571'],
    'tagFiringOption': 'ONCE_PER_PAGE'
}

# ── Merge ──
cv['variable'] = cv.get('variable', []) + new_vars
cv['trigger'].append(new_trigger)
cv['tag'].append(new_tag)

# ── Update GA4 tags: consent + stcm trigger ──
for tag in cv['tag']:
    if tag['type'] in ('googtag', 'gaawe'):
        # Add consent requirement
        tag['consentSettings'] = {
            'consentStatus': 'REQUIRE_ADDITIONAL_CONSENT',
            'consentRequireType': 'ANY',
            'additionalConsent': [
                {'type': 'TEMPLATE', 'key': 'consentType', 'value': 'analytics_storage'}
            ]
        }
        # Add stcm_consent_update trigger
        if 'firingTriggerId' in tag:
            tag['firingTriggerId'].append('5')

# ── Write ──
out_path = r'C:\Users\huhu\b2b-test-site\GTM-PPLVHVWR_consent_ready.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print(f'Done: {out_path}')
print(f'  Variables: {len(cv["variable"])} (added 4)')
print(f'  Triggers:  {len(cv["trigger"])} (added 1)')
print(f'  Tags:      {len(cv["tag"])} (added 1)')
