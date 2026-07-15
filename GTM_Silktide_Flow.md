# GTM + Silktide Consent 整体逻辑与验证流程

## 一、组件关系

```
┌──────────────┐     ┌─────────────────┐     ┌──────────┐
│  b2b 网站     │────▶│  GTM 容器        │────▶│  GA4     │
│  页面埋点     │     │  GTM-PPLVHVWR   │     │  events  │
└──────────────┘     │                  │     └──────────┘
       │             │  ┌─变量(9个)────┐│     ┌──────────┐
       ▼             │  │ dlv-* (3)   ││     │ Google   │
┌──────────────┐     │  │ regex (1)   ││────▶│ Ads      │
│  Silktide    │────▶│  │ lookup (2)  ││     │ conv.    │
│  Consent     │     │  │ GA-id (1)   ││     └──────────┘
│  Manager     │     │  │ dlv-ecom(2) ││
└──────────────┘     │  └─────────────┘│
       │             │                 │
       │  stcm_      │  ┌─触发(7个)────┐│
       │  consent_   │  │ 13 nav-link ││
       │  update     │  │ 16 form_sub ││
       └─────────────▶  │ 18 whatsapp ││
                        │ 23 purchase ││
                        │ 30 cta_click││
                        │ 31 inquiry  ││
                        │ 32 consent▲ ││
                        └─────────────┘│
                        ┌─代码(12个)───┐│
                        │ GA4-config  ││
                        │ GA4 event×4 ││
                        │ GTAG AW     ││
                        │ AW conv ×3  ││
                        │ Silktide    ││
                        │ ConvLinker  ││
                        └─────────────┘│
                        └──────────────┘
```

---

## 二、页面加载流程

```
用户访问页面
    │
    ▼
1. 浏览器加载 HTML
    │
    ▼
2. Consent 默认值设定（页面源码，GTM 之前）
    ├─ GDPR 国家（DE,FR,GB...）: 全部 denied
    └─ 其他国家: 全部 granted
    │
    ▼
3. GTM 容器加载
    │
    ▼
4. Silktide Init 代码触发（All Pages, ONCE_PER_LOAD）
    │
    ├─ 读取 {{dlv - user_country}}（由页面 js 推入 dataLayer）
    ├─ {{regex - legal region archetype}} 匹配:
    │   ├─ GDPR 国家 → "strict-opt-in"
    │   ├─ US/CA      → "notice-opt-out"
    │   └─ 其他       → "none"
    │
    ├─ {{lookup - silktide mode}}:
    │   ├─ strict-opt-in → "opt-in"   ← 必须先同意
    │   ├─ notice-opt-out→ "opt-out"  ← 默认同意，可拒绝
    │   └─ none          → "opt-out"
    │
    ├─ {{lookup - silktide banner description}}:
    │   ├─ strict-opt-in → "We require your active consent..."
    │   └─ notice-opt-out→ "We use cookies for optimization..."
    │
    └─ regex = "none" → 跳过，不弹窗
    │
    ▼
5. 用户与 Consent Banner 交互
    ├─ 点"同意全部" → stcm 更新 → stcm_consent_update 事件
    ├─ 点"拒绝"     → stcm 更新 → stcm_consent_update 事件
    └─ 不操作       → 保持默认值
```

---

## 三、用户行为追踪流程

```
用户行为                  dataLayer 事件         GTM 触发      代码触发          Consent 检查
───────                  ─────────────         ───────       ────────          ────────────
点击导航链接      ──▶    （内置 click）    ──▶  trigger 13  ──▶ GA4 menue_link    analytics_storage
                                                        _click
                                                       
点击 CTA          ──▶    cta_click         ──▶  trigger 30  ──▶ GA4 event-        analytics_storage
                                                        cta_click

点击 WhatsApp     ──▶    inquiry_click     ──▶  trigger 31  ──▶ GA4 event-        analytics_storage
                                                        inquiry_click

点击 WhatsApp     ──▶    （内置 click）    ──▶  trigger 18  ──▶ ads-              ad_storage
（LINK_CLICK）                                          whatsapp_click

提交表单          ──▶    form_submit       ──▶  trigger 16  ──▶ GA4 event-        analytics_storage
                                                        form submit
                                                                   ──▶ ads-              ad_storage
                                                                   form_submit

购买              ──▶    purchase          ──▶  trigger 23  ──▶ ads-              ad_storage
                                                        purchase
```

---

## 四、Consent 控制逻辑

```
代码类型           Consent 要求        拒绝时行为
────────          ─────────────        ──────────
googtag (GA4)     analytics_storage    代码不触发，GA4 不接收
googtag (AW)      ad_storage           代码不触发，Ads 不接收
gaawe (事件)      analytics_storage    代码不触发
awct (转化)       ad_storage           代码不触发
gclidw (链接器)   （无）               始终触发
html (Silktide)   （无）               始终触发
```

---

## 五、验证清单

### 第1步：GTM 容器确认

| # | 检查项 | GTM 路径 |
|---|--------|---------|
| 1 | 9 个变量都存在 | 变量 > 用户定义的变量 |
| 2 | 7 个触发都存在 | 触发 > 列表 |
| 3 | 12 个代码都存在 | 代码 > 列表 |
| 4 | 6 个追踪代码有 consent | 逐个代码 > 高级设置 > 同意设置 |
| 5 | 10 个追踪代码有 trigger 32 | 逐个代码 > 触发条件 |

### 第2步：Consent Banner 验证

| # | 测试 | 操作 | 预期 |
|---|------|------|------|
| 6 | GDPR 国家 | VPN 到德国，打开网站 | 弹出 opt-in 横幅，默认全部拒绝 |
| 7 | US | VPN 到美国，打开网站 | 弹出 opt-out 横幅，默认全部同意 |
| 8 | 非监管国 | VPN 到新加坡（不在 GDPR 列表），打开网站 | 不弹窗，默认识别为 none |
| 9 | 同意全部 | 在 GDPR 模式点"同意全部" | 横幅关闭，stcm_consent_update 触发 |

### 第3步：GA4 事件验证

用 GTM 预览模式 + GA4 实时报告：

| # | 操作 | 预览模式检查 | GA4 实时检查 |
|---|------|------------|------------|
| 10 | 点击导航链接 | GA4 menue_link_click 触发 | 事件出现 |
| 11 | 点击 CTA 按钮 | GA4 event-cta_click 触发 | 事件出现 |
| 12 | 点击 WhatsApp | GA4 event-inquiry_click 触发 | 事件出现 |
| 13 | 提交表单 | GA4 event-form submit 触发 | generate_lead 出现 |

### 第4步：Google Ads 转化验证

| # | 操作 | GTM 预览检查 | Ads 后台 |
|---|------|------------|---------|
| 14 | 提交表单 | ads-form_submit 触发 | 等 24-48h 看转化 |
| 15 | 点击 WhatsApp | ads-whatsapp_click 触发 | 等 24-48h 看转化 |
| 16 | 完成购买 | ads-purchase 触发 | 等 24-48h 看转化 |

### 第5步：Consent 拒绝验证

| # | 操作 | 预期 |
|---|------|------|
| 17 | GDPR 模式下拒绝 consent，点 CTA | GA4 事件不触发 |
| 18 | GDPR 模式下拒绝 consent，提交表单 | GA4 + Ads 都不触发 |
| 19 | 拒绝后再同意，点 CTA | 后续事件正常触发 |

---

## 六、验证顺序（推荐）

```
第1步（GTM 容器）──▶ 第2步（Banner VPN）──▶ 第3步（GA4 预览）
                                                    │
                                                    ▼
                              第5步（拒绝验证）◀── 第4步（Ads 转化）
```
