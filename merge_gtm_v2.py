import json, shutil

# Read v4 export
src = r'C:\Users\huhu\b2b-test-site\GTM-PPLVHVWR_v4.json'
with open(src, 'r', encoding='utf-8') as f:
    d = json.load(f)

cv = d['containerVersion']
AID, CID = '6355959832', '252791019'

# ── Variables (4) ──
new_vars = [
    {
        'accountId':AID,'containerId':CID,
        'name':'dlv - user_country','type':'v',
        'parameter':[
            {'type':'INTEGER','key':'dataLayerVersion','value':'2'},
            {'type':'BOOLEAN','key':'setDefaultValue','value':'false'},
            {'type':'TEMPLATE','key':'name','value':'user_country'}
        ]
    },
    {
        'accountId':AID,'containerId':CID,
        'name':'regex - legal region archetype','type':'REM',
        'parameter':[
            {'type':'TEMPLATE','key':'input','value':'{{dlv - user_country}}'},
            {'type':'LIST','key':'map','list':[
                {'type':'MAP','map':[
                    {'type':'TEMPLATE','key':'pattern','value':'^(BY|SG|KR|GB|DE|FR|IT|ES|PL|NL|BE|IE|AT|PT|SE|DK|FI|CZ|RO)$'},
                    {'type':'TEMPLATE','key':'output','value':'strict-opt-in'}
                ]},
                {'type':'MAP','map':[
                    {'type':'TEMPLATE','key':'pattern','value':'^(US|CA)$'},
                    {'type':'TEMPLATE','key':'output','value':'notice-opt-out'}
                ]}
            ]},
            {'type':'BOOLEAN','key':'fullMatch','value':'true'},
            {'type':'BOOLEAN','key':'ignoreCase','value':'true'},
            {'type':'TEMPLATE','key':'defaultValue','value':'none'}
        ]
    },
    {
        'accountId':AID,'containerId':CID,
        'name':'lookup - silktide mode','type':'SML',
        'parameter':[
            {'type':'TEMPLATE','key':'input','value':'{{regex - legal region archetype}}'},
            {'type':'LIST','key':'map','list':[
                {'type':'MAP','map':[{'type':'TEMPLATE','key':'key','value':'strict-opt-in'},{'type':'TEMPLATE','key':'val','value':'opt-in'}]},
                {'type':'MAP','map':[{'type':'TEMPLATE','key':'key','value':'notice-opt-out'},{'type':'TEMPLATE','key':'val','value':'opt-out'}]},
                {'type':'MAP','map':[{'type':'TEMPLATE','key':'key','value':'none'},{'type':'TEMPLATE','key':'val','value':'opt-out'}]}
            ]},
            {'type':'TEMPLATE','key':'defaultValue','value':'opt-out'}
        ]
    },
    {
        'accountId':AID,'containerId':CID,
        'name':'lookup - silktide banner description','type':'SML',
        'parameter':[
            {'type':'TEMPLATE','key':'input','value':'{{regex - legal region archetype}}'},
            {'type':'LIST','key':'map','list':[
                {'type':'MAP','map':[{'type':'TEMPLATE','key':'key','value':'strict-opt-in'},{'type':'TEMPLATE','key':'val','value':'We require your active consent to use cookies for advertising and analytics.'}]},
                {'type':'MAP','map':[{'type':'TEMPLATE','key':'key','value':'notice-opt-out'},{'type':'TEMPLATE','key':'val','value':'We use cookies for optimization. You have the right to opt-out of the sale or sharing of data.'}]}
            ]},
            {'type':'TEMPLATE','key':'defaultValue','value':''}
        ]
    }
]

# ── Trigger (1) ──
new_trigger = {
    'accountId':AID,'containerId':CID,
    'name':'Custom Event - stcm_consent_update','type':'CUSTOM_EVENT',
    'customEventFilter':[{
        'type':'EQUALS',
        'parameter':[
            {'type':'TEMPLATE','key':'arg0','value':'{{_event}}'},
            {'type':'TEMPLATE','key':'arg1','value':'stcm_consent_update'}
        ]
    }]
}

# ── Tag (1) ──
html_val = '<script>\n(function(){\n  var a = \'{{regex - legal region archetype}}\';\n  if(a === \'none\') return;\n\n  silktideConsentManager.init({\n    mode: \'{{lookup - silktide mode}}\',\n    text: {\n      title: \'Privacy Settings\',\n      description: \'{{lookup - silktide banner description}}\'\n    },\n    consentTypes: [\n      { id: \'analytics\', label: \'Analytics\', gtag: \'analytics_storage\' },\n      { id: \'advertising\', label: \'Marketing\', gtag: [\'ad_storage\',\'ad_user_data\',\'ad_personalization\'] }\n    ],\n    options: { expandedByDefault: a === \'strict-opt-in\' }\n  });\n})();\n</script>'

new_tag = {
    'accountId':AID,'containerId':CID,
    'name':'Consent - Silktide Initialization','type':'html',
    'parameter':[
        {'type':'TEMPLATE','key':'html','value':html_val},
        {'type':'BOOLEAN','key':'supportDocumentWrite','value':'true'}
    ],
    'firingTriggerId':['2147479571'],
    'tagFiringOption':'ONCE_PER_PAGE'
}

# ── Merge ──
cv['variable'] = cv.get('variable',[]) + new_vars
cv['trigger'].append(new_trigger)
cv['tag'].append(new_tag)

# ── Add consent to all GA4 + Google Ads tags ──
print('Consent updates:')
for tag in cv['tag']:
    name = tag['name']
    ttype = tag['type']

    # GA4 tags
    if (ttype == 'googtag' and 'AW' not in name) or ttype == 'gaawe':
        tag['consentSettings'] = {
            'consentStatus':'REQUIRE_ADDITIONAL_CONSENT',
            'consentRequireType':'ANY',
            'additionalConsent':[{'type':'TEMPLATE','key':'consentType','value':'analytics_storage'}]
        }
        if 'firingTriggerId' in tag:
            tag['firingTriggerId'].append('5')
        print(f'  analytics_storage: {name}')

    # Google Ads tags (AW- prefix or ads keywords)
    if ttype == 'awct' or (ttype == 'googtag' and 'AW' in name):
        tag['consentSettings'] = {
            'consentStatus':'REQUIRE_ADDITIONAL_CONSENT',
            'consentRequireType':'ANY',
            'additionalConsent':[
                {'type':'TEMPLATE','key':'consentType','value':'ad_storage'},
                {'type':'TEMPLATE','key':'consentType','value':'ad_user_data'},
                {'type':'TEMPLATE','key':'consentType','value':'ad_personalization'}
            ]
        }
        if 'firingTriggerId' in tag:
            tag['firingTriggerId'].append('5')
        print(f'  ad_storage+ad_user_data+ad_personalization: {name}')

# ── Write ──
out = r'C:\Users\huhu\b2b-test-site\GTM-PPLVHVWR_consent_v2.json'
with open(out, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print(f'\nDone: GTM-PPLVHVWR_consent_v2.json')
print(f'  +{len(new_vars)} variables, +1 trigger, +1 tag')
