import json

src = r'C:\Users\huhu\b2b-test-site\GTM-PPLVHVWR_v4.json'
with open(src, 'r', encoding='utf-8') as f:
    d = json.load(f)

cv = d['containerVersion']
AID, CID = '6355959832', '252791019'

# ═══════════════════════════════════════
# 1. NEW TRIGGERS
# ═══════════════════════════════════════

new_triggers = [
    {
        'accountId':AID,'containerId':CID,
        'name':'cta_click trigger','type':'CUSTOM_EVENT',
        'customEventFilter':[{
            'type':'EQUALS',
            'parameter':[
                {'type':'TEMPLATE','key':'arg0','value':'{{_event}}'},
                {'type':'TEMPLATE','key':'arg1','value':'cta_click'}
            ]
        }]
    },
    {
        'accountId':AID,'containerId':CID,
        'name':'inquiry_click trigger','type':'CUSTOM_EVENT',
        'customEventFilter':[{
            'type':'EQUALS',
            'parameter':[
                {'type':'TEMPLATE','key':'arg0','value':'{{_event}}'},
                {'type':'TEMPLATE','key':'arg1','value':'inquiry_click'}
            ]
        }]
    }
]

# ═══════════════════════════════════════
# 2. GA4 EVENT TAGS
# ═══════════════════════════════════════

ga4_tags = [
    {
        'accountId':AID,'containerId':CID,
        'name':'GA4 event-cta_click','type':'gaawe',
        'parameter':[
            {'type':'TEMPLATE','key':'eventName','value':'cta_click'},
            {'type':'TEMPLATE','key':'measurementId','value':'G-50PJHKG2M5'},
            {'type':'LIST','key':'eventParameters','list':[
                {'type':'MAP','map':[
                    {'type':'TEMPLATE','key':'parameterName','value':'cta_name'},
                    {'type':'TEMPLATE','key':'parameterValue','value':'{{dlv-cta_name}}'}
                ]}
            ]}
        ],
        'firingTriggerId':['6'],  # will be new trigger index
        'tagFiringOption':'ONCE_PER_EVENT'
    },
    {
        'accountId':AID,'containerId':CID,
        'name':'GA4 event-inquiry_click','type':'gaawe',
        'parameter':[
            {'type':'TEMPLATE','key':'eventName','value':'inquiry_click'},
            {'type':'TEMPLATE','key':'measurementId','value':'G-50PJHKG2M5'},
            {'type':'LIST','key':'eventParameters','list':[
                {'type':'MAP','map':[
                    {'type':'TEMPLATE','key':'parameterName','value':'product_name'},
                    {'type':'TEMPLATE','key':'parameterValue','value':'{{dlv-product_name}}'}
                ]}
            ]}
        ],
        'firingTriggerId':['7'],  # will be new trigger index
        'tagFiringOption':'ONCE_PER_EVENT'
    }
]

# ═══════════════════════════════════════
# 3. GOOGLE ADS CONVERSION TAGS
# ═══════════════════════════════════════

ads_tags = [
    {
        'accountId':AID,'containerId':CID,
        'name':'google ads-form_submit','type':'awct',
        'parameter':[
            {'type':'TEMPLATE','key':'conversionId','value':'18122392881'},
            {'type':'TEMPLATE','key':'conversionLabel','value':'FORM_SUBMIT_LABEL'},
            {'type':'BOOLEAN','key':'enableConversionLinker','value':'true'},
            {'type':'BOOLEAN','key':'enableNewCustomerReporting','value':'false'},
            {'type':'BOOLEAN','key':'enableProductReporting','value':'false'},
            {'type':'BOOLEAN','key':'enableShippingData','value':'false'},
            {'type':'BOOLEAN','key':'rdp','value':'false'}
        ],
        'firingTriggerId':['16'],
        'tagFiringOption':'ONCE_PER_EVENT'
    },
    {
        'accountId':AID,'containerId':CID,
        'name':'google ads-whatsapp_click','type':'awct',
        'parameter':[
            {'type':'TEMPLATE','key':'conversionId','value':'18122392881'},
            {'type':'TEMPLATE','key':'conversionLabel','value':'WHATSAPP_CLICK_LABEL'},
            {'type':'BOOLEAN','key':'enableConversionLinker','value':'true'},
            {'type':'BOOLEAN','key':'enableNewCustomerReporting','value':'false'},
            {'type':'BOOLEAN','key':'enableProductReporting','value':'false'},
            {'type':'BOOLEAN','key':'enableShippingData','value':'false'},
            {'type':'BOOLEAN','key':'rdp','value':'false'}
        ],
        'firingTriggerId':['18'],
        'tagFiringOption':'ONCE_PER_EVENT'
    }
]

# ═══════════════════════════════════════
# MERGE
# ═══════════════════════════════════════

# Add triggers
trigger_start = len(cv['trigger'])
cv['trigger'].extend(new_triggers)
print(f'Triggers: {len(cv["trigger"])} (+2)')
for i, t in enumerate(new_triggers):
    idx = trigger_start + i
    print(f'  [{idx}] {t["name"]}')

# Fix GA4 tag trigger IDs (they reference new trigger indices as strings)
# After adding 2 triggers: old triggers 0,1,2,3 → new triggers 4,5
# form_submit trigger was index 1 → now referenced as "16" (its triggerId)
# whatsapp trigger was index 2 → "18"
# New cta_click trigger = index 4 → need to use its triggerId or position
# New inquiry_click trigger = index 5

# The new triggers don't have triggerIds yet. In GTM import, triggers without
# explicit triggerId get auto-assigned. Tags reference triggers by triggerId string.
# Since we're adding to a workspace export, let's use position-based references.
# After adding 2 triggers AFTER the 4 existing ones:
#   existing: [13, 16, 18, 23]
#   new cta_click → position 4 in array
#   new inquiry_click → position 5 in array

# In GTM export format, firingTriggerId uses triggerId values (strings).
# New triggers won't have IDs yet. The simplest fix: use triggerId values.
# We'll set temporary triggerIds that GTM will remap on import.
# Actually, GTM import uses these triggerIds for matching. Let's use
# unique high numbers that won't conflict.

new_triggers[0]['triggerId'] = '50'
new_triggers[1]['triggerId'] = '51'

# Update tag references
ga4_tags[0]['firingTriggerId'] = ['50']
ga4_tags[1]['firingTriggerId'] = ['51']

# Add GA4 tags
for tag in ga4_tags:
    tag['consentSettings'] = {
        'consentStatus':'REQUIRE_ADDITIONAL_CONSENT',
        'consentRequireType':'ANY',
        'additionalConsent':[{'type':'TEMPLATE','key':'consentType','value':'analytics_storage'}]
    }
cv['tag'].extend(ga4_tags)
print(f'\nGA4 tags: +2 (cta_click, inquiry_click)')

# Add Google Ads tags
for tag in ads_tags:
    tag['consentSettings'] = {
        'consentStatus':'REQUIRE_ADDITIONAL_CONSENT',
        'consentRequireType':'ANY',
        'additionalConsent':[
            {'type':'TEMPLATE','key':'consentType','value':'ad_storage'},
            {'type':'TEMPLATE','key':'consentType','value':'ad_user_data'},
            {'type':'TEMPLATE','key':'consentType','value':'ad_personalization'}
        ]
    }
cv['tag'].extend(ads_tags)
print(f'Ads tags: +2 (form_submit, whatsapp_click)')

# ═══════════════════════════════════════
# ALSO: Add 4 Silktide consent variables + trigger + tag
# (reusing logic from merge_gtm_v2.py)
# ═══════════════════════════════════════

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

stcm_trigger = {
    'accountId':AID,'containerId':CID,
    'triggerId':'52',
    'name':'Custom Event - stcm_consent_update','type':'CUSTOM_EVENT',
    'customEventFilter':[{
        'type':'EQUALS',
        'parameter':[
            {'type':'TEMPLATE','key':'arg0','value':'{{_event}}'},
            {'type':'TEMPLATE','key':'arg1','value':'stcm_consent_update'}
        ]
    }]
}

html_val = '<script>\n(function(){\n  var a = \'{{regex - legal region archetype}}\';\n  if(a === \'none\') return;\n\n  silktideConsentManager.init({\n    mode: \'{{lookup - silktide mode}}\',\n    text: {\n      title: \'Privacy Settings\',\n      description: \'{{lookup - silktide banner description}}\'\n    },\n    consentTypes: [\n      { id: \'analytics\', label: \'Analytics\', gtag: \'analytics_storage\' },\n      { id: \'advertising\', label: \'Marketing\', gtag: [\'ad_storage\',\'ad_user_data\',\'ad_personalization\'] }\n    ],\n    options: { expandedByDefault: a === \'strict-opt-in\' }\n  });\n})();\n</script>'

stcm_tag = {
    'accountId':AID,'containerId':CID,
    'name':'Consent - Silktide Initialization','type':'html',
    'parameter':[
        {'type':'TEMPLATE','key':'html','value':html_val},
        {'type':'BOOLEAN','key':'supportDocumentWrite','value':'true'}
    ],
    'firingTriggerId':['2147479571'],
    'tagFiringOption':'ONCE_PER_PAGE'
}

# Add Silktide vars
cv['variable'] = cv.get('variable',[]) + new_vars
cv['trigger'].append(stcm_trigger)

# Add stcm trigger to all existing tracking tags
for tag in cv['tag']:
    if 'firingTriggerId' in tag:
        if tag['type'] in ('googtag','gaawe','awct'):
            if '52' not in tag['firingTriggerId']:
                tag['firingTriggerId'].append('52')

cv['tag'].append(stcm_tag)

print(f'\nSilktide: +4 variables, +1 trigger, +1 tag')

# ── Write ──
out = r'C:\Users\huhu\b2b-test-site\GTM_complete.json'
with open(out, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print(f'\nDone: GTM_complete.json')
print(f'  Variables: {len(cv["variable"])}')
print(f'  Triggers:  {len(cv["trigger"])}')
print(f'  Tags:      {len(cv["tag"])}')
print()
print('⚠️  Google Ads 转化标签的 conversionLabel 是占位符:')
print('   google ads-form_submit → FORM_SUBMIT_LABEL')
print('   google ads-whatsapp_click → WHATSAPP_CLICK_LABEL')
print('   去 Google Ads 创建转化操作后，把真实 Label 替换掉')
