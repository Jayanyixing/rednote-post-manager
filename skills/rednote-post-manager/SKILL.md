---
name: rednote-post-manager
description: >-
  Comprehensive Xiaohongshu (小红书 / RedNote) compliance and operations skill
  strictly aligned with Community Convention 2.0, AIGC labeling rules, CQS/fake-seeding
  enforcement, and Personal Shop (个人店) full-category prohibitions ("三品一械",
  cosmetics/food claims, finance, virtual/digital resources). Use whenever the
  user wants to draft natural non-AI posts, publish or fix Personal Shop listings,
  design 3:4/1:1 covers, or audit copy against all Xiaohongshu risk rules.
---

# 小红书全规则帖子与个人售卖合规管家 (`rednote-post-manager`)

严格遵循《小红书社区公约2.0》、AIGC 内容标识规定、广告法及个人店全品类准入/禁售规则，同时深耕**① 社区帖子（笔记）**与**② 个人售卖（个人店）**两大独立规则体系。

## 核心工作流

### 1. 读取平台全规则参考文档（按需加载）
在编写或排查任何小红书内容前，先明确场景并加载对应完整规则：
- **帖子（笔记）全规则**：必读 [community_post_rules.md](./references/community_post_rules.md)（《社区公约2.0》、CQS 内容质量分、AI 辅助创作主动标识红线、虚假种草与蒲公英报备、医疗科普与财经金融八大禁区、全路径站外导流防封及惩罚梯度）。
- **个人售卖（个人店）全规则**：必读 [personal_shop_rules.md](./references/personal_shop_rules.md)（个人店 vs 企业店边界、**“三品一械”/奶粉/无授权美妆全球购/普通食品功效/烟草活体全面禁售清单**、个人店禁售技术劳务与《电子资源》合规换壳策略、虚拟自动发货闭环及快递包裹卡避雷）。
- **全行业违禁词库与 AI 工具代号**：必读 [banned_words_and_aliases.md](./references/banned_words_and_aliases.md)（广告法极限词、诱导词、三品一械与医疗美容词、财经荐股词、仿品词、导流词、否定句正则陷阱及海外 AI 安全代号）。
- **视觉与去 AI 味双模板**：参考 [copy_and_cover_templates.md](./references/copy_and_cover_templates.md)（3:4 笔记封面与 1:1 个人店商品主图规范）。

### 2. 双轨执行硬性规范

1. **社区帖子（笔记）轨道**：
   - **去 AI 味“活人感”**：禁用套路排比、`总而言之/不仅如此/赋能/一站式` 等营销腔及 `1️⃣ ✅ 💡` 列表刷屏；写成真实个人踩坑与具体经验分享。
   - **严守行业内容禁区**：医疗/医美/普通食品/普通化妆品不得做疗效或特证功效宣称；财经内容禁止荐股及收益承诺；前后对比图必须注明原相机及拍摄条件；软广须走蒲公英报备，不得伪装素人虚假种草。
   - **AIGC 主动标识**：凡配图、视频或主体使用 AI 辅助生成，**必须明确提醒用户在发布页手动勾选“AI辅助创作”标识**，严禁抹除隐式元数据。
   - **全链路防导流**：正文、图上、评论、置顶、私信均禁提微信/VX/QQ/网盘/外部平台。

2. **个人售卖（个人店）轨道**：
   - **先判品类准入**：若用户试图用个人店上架药品、二三类医疗器械（美瞳/隐形眼镜/护理液/械字号面膜/呼吸机）、蓝帽子保健品、婴幼儿奶粉、全球购或无授权大牌美妆、电子烟、活体宠物等，**必须立即劝阻并说明违反个人店禁限售规范**。
   - **技能/软件配置类个人店唯一合规路径**：个人店无企业资质禁售“远程安装/代装/有偿技术调试”，必须包装为 **`电子资源` 类目下的《图文配置手册(PDF) + 模板包》**，千帆后台开启虚拟自动发货并真正上传数字文档，将排错协助包装为“购后店铺客服附带答疑”。
   - **履约底线**：如实描述交付规格，禁发空包、禁标 0.01/1 元低价引流、**严禁在发货包裹里塞任何引导加微或好评返现的售后卡**。

### 3. 强制自动化脚本校验（交付前必跑）
交付任何文案或封面图文字前，**必须**按对应场景运行全规则审计脚本：

- **查社区帖子 / 3:4 笔记封面文字**：
  ```bash
  python3 ./scripts/audit_rednote_content.py --mode post --text "<文案内容>"
  ```
- **查个人店商品标题 / 详情 / 1:1 主图文字**：
  ```bash
  python3 ./scripts/audit_rednote_content.py --mode shop --text "<商品文案内容>"
  ```
- **同时检查（默认最严模式）**：
  ```bash
  python3 ./scripts/audit_rednote_content.py --mode all --file "<文件路径>"
  ```

只有高危阻断项为 `0`（`PASS`）且确认 AI 味/行业合规警示无误后，方可交付给用户。
