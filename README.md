# rednote-post-manager

小红书（RedNote）社区帖子（笔记）与个人售卖（个人店）全规则合规管家 Skill / Antigravity Plugin。

## 双轨核心能力
1. **社区帖子（笔记）规则深耕**：
   - 对齐《社区公约2.0》、CQS 内容质量分及搜索权重逻辑，强制“去 AI 味”活人感表达。
   - 覆盖 AIGC 内容主动标识义务、虚假种草与前后对比图拍摄条件标注、商业软广蒲公英报备、医疗科普认证门槛、财经《社区金融生态公约》八大禁区及全路径站外导流防封。
2. **个人售卖（个人店）全品类规则**：
   - 严格界定个人店（身份证）与企业店权限红线，涵盖“三品一械”（药品、二三类医疗器械如美瞳/护理液/械字号面膜、蓝帽子保健品、特医与婴幼儿奶粉）、无授权美妆与全球购、普通食品功效宣称、烟草活体等禁限售清单。
   - 针对个人店禁售“远程代装/有偿技术服务”，提供合规的【`电子资源`类目（手册+模板包）+ 购后客服答疑】换壳策略及千帆虚拟自动发货闭环。
3. **双模式自动化合规审计 (`audit_rednote_content.py`)**：
   - 支持 `--mode post`（帖子与 AI 味检测）、`--mode shop`（个人店超范围与禁售品检测）及 `--mode all`。

## 目录结构
```text
rednote-post-manager/
├── plugin.json
├── LICENSE
├── README.md
├── assets/logo.svg
└── skills/rednote-post-manager/
    ├── SKILL.md
    ├── references/
    │   ├── community_post_rules.md
    │   ├── personal_shop_rules.md
    │   ├── banned_words_and_aliases.md
    │   └── copy_and_cover_templates.md
    └── scripts/
        └── audit_rednote_content.py
```

## 快速安装（Antigravity）
```bash
git clone https://github.com/Jayanyixing/rednote-post-manager.git
ln -sfn "$(pwd)/rednote-post-manager" ~/.gemini/config/plugins/rednote-post-manager
```

## 脚本独立用法
```bash
# 检查帖子/笔记文案
python3 skills/rednote-post-manager/scripts/audit_rednote_content.py --mode post --text "待检测笔记文案"

# 检查个人店商品标题与详情
python3 skills/rednote-post-manager/scripts/audit_rednote_content.py --mode shop --text "待检测个人店商品文案"
```

## License
MIT License
