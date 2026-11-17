#!/usr/bin/env python3
"""
小红书（RedNote）全规则双模式合规审计脚本。
严格对齐《社区公约2.0》、广告法、三品一械/美妆/食品/财经/虚假种草/导流规范，
以及个人店（电子资源）经营权限边界与海外 AI 敏感词拦截机制。

支持模式：
  - post : 社区帖子（笔记）审查 —— 含 AI 味检测、虚假种草/对比图提醒、行业合规词、导流词、极限词
  - shop : 个人店商品上架审查 —— 额外严查个人店禁售类目（三品一械/奶粉/无授权美妆/活体/烟草）及超范围劳务服务词
  - all  : 同时执行上述全部最严校验（默认）
"""

import argparse
import json
import re
import sys
from pathlib import Path

COMMON_CRITICAL_RULES = [
    # 1. 广告法绝对化/极限用语
    (r"全网最|最(?:好|佳|优|强|快|低|便宜|省钱|全|实用|新|高|稳|牛|靠谱|有效)|极致|独家|第一|NO\.?\s*1|TOP\s*1|唯一|绝对|100%|永久|万能|史无前例|顶配|首选",
     "广告法极限/绝对化用语", "改为客观平和表达，如: 实用 / 个人整理 / 辅助提升"),
    # 2. 诱导消费与虚假效果/收益承诺
    (r"秒杀|抢爆|错过拍断腿|点击有惊喜|一键三连|免费领|立即获取|闭眼入|万人疯抢",
     "诱导互动/刺激抢购敏感词", "去掉强迫促单话术，改为自然引导"),
    (r"包过|包学会|稳赚|保本|躺赚|抄底必涨|牛股|内幕消息|荐股|月入过万|零基础暴富|无风险高收益|翻倍收益|商业变现|暴降\s*\d+%|省下\s*\d+%|翻倍|远超这份资料|彻底解决|彻底改变|无效退款",
     "虚假效果/财经违规/未证实量化承诺词", "去掉绝对收益或百分比保证，财经内容严禁荐股及收益承诺"),
    # 3. 站外导流全路径红线
    (r"微信|威信|(?<![A-Za-z0-9])vx(?![A-Za-z0-9])|(?<![A-Za-z0-9])v我|\+v|加v|扣扣|(?<![A-Za-z0-9])qq(?![A-Za-z0-9])|手机号|网盘|百度云|夸克|发卡网|二维码|扫码|戳链接|私信发|闲鱼|淘宝|某宝|拼多多|看主页简介|好评返现|返现卡",
     "站外导流/好评返现封号红线词", "删除所有外部联系方式、平台名、网盘及包裹返现卡引导，统一留在本平台小店卡片或客服窗内"),
    # 4. “三品一械”、医美与食品美妆非法宣称红线
    (r"械字号|医用冷敷贴|隐形眼镜|美瞳|护理液|处方药|抗生素|注射器|呼吸机|制氧机|自制中药|蓝帽子|特医食品|婴幼儿奶粉",
     "三品一械/特医/奶粉高危禁限售词", "普通个人号与个人店严禁发布药品、二三类医疗器械、蓝帽子保健品及婴幼儿奶粉"),
    (r"根治|治愈|药到病除|消炎|激素脸|降三高|抗癌|防癌|祛斑美白",
     "医疗/特殊功效违规宣称词", "普通化妆品与普通食品严禁宣称医疗治病或特证功效"),
    # 5. 仿品、违禁品及灰产红线
    (r"高仿|精仿|A货|超A|复刻|原单|尾单|厂货|渠道货|1[:：]1|剪标|水货|电子烟|烟弹|香烟|活体宠物|管制刀具|情趣内衣|计生用品",
     "仿品侵权/平台绝对禁售品词", "禁止销售仿品及烟草、活体、情趣计生、管制器具等平台禁售物"),
    # 6. 海外 AI 敏感与非法网络红线
    (r"(?<![A-Za-z0-9])codex(?![A-Za-z0-9])|c0dex", "海外AI高危拦截词(Codex)", "替换为: O社 CLI / O家代码助手"),
    (r"(?<![A-Za-z0-9])claude(?:\s*code)?(?![A-Za-z0-9])|c\*aude", "海外AI高危拦截词(Claude)", "替换为: CC / CC代码终端 / 小克"),
    (r"(?<![A-Za-z0-9])gemini(?![A-Za-z0-9])", "海外AI高危拦截词(Gemini)", "替换为: 哈基米 / 双子星"),
    (r"(?<![A-Za-z0-9])openai(?![A-Za-z0-9])|chatgpt|(?<![A-Za-z0-9])gpt[-\s]*[345o]?(?![A-Za-z0-9])|g-p-t", "海外AI高危拦截词(OpenAI/GPT)", "替换为: O社 / O家工具"),
    (r"(?<![A-Za-z0-9])anthropic(?![A-Za-z0-9])", "海外AI高危拦截词(Anthropic)", "替换为: A社"),
    (r"(?<![A-Za-z0-9])antigravity(?![A-Za-z0-9])", "跨境AI工具风险词(Antigravity)", "替换为: 反重力 / 反重力IDE"),
    (r"科学上网|(?<![A-Za-z0-9])vpn(?![A-Za-z0-9])|梯子|节点搭建|翻墙|纯净ip|魔法上网",
     "网络监管绝对红线词", "彻底回避，仅写: 需自行准备合规基础网络环境"),
    # 7. 版权/账号/远控/接口黑产词（否定句中亦不可出现）
    (r"远程(?:安装|协助|控制|调试|操作|配置)?|可远程|代安装|代装|向日葵|todesk|teamviewer",
     "高危远控/软件代装词", "严禁提远程/代装！个人店请包装为电子手册+模板包，笔记请写踩坑自查分享"),
    (r"破解|盗版|激活码|注册机|全家桶|外挂|群控|代写|代考|刷单|账号|独享号|合租|车位|代充|额度",
     "版权/账号/灰产高危词(切勿在否定句中出现)", "彻底删去该词，改为正面合规声明: 仅提供原创电子学习资料与模板"),
    (r"(?<![A-Za-z0-9])api(?![A-Za-z0-9])|api\s*接入|api\s*转发|token\s*售卖|key\s*售卖|中转站",
     "非法接口/API倒卖风险词", "替换为: 官方合规模型参数配置 / 模板格式说明"),
]

SHOP_EXTRA_CRITICAL_RULES = [
    (r"1对1.{0,6}(?:服务|调试|安装|配置|支持|排查)|技术劳务|有偿.{0,4}(?:调试|咨询|服务)|部署到.{0,4}服务器",
     "个人店无资质超范围经营词(个人店严禁直接售卖有偿技术服务/代调试)",
     "改为【电子资源】定位：主卖《配置图文手册(PDF)+模板包》，把排错指导写为‘购买资料后附带的店铺客服售后答疑’"),
    (r"全球购|海外直邮|保税仓直发|医美项目|医学美容",
     "个人店无权限准入类目词", "全球购及医美等强资质类目不对个人店开放，严禁上架"),
]

POST_AI_FLAVOR_WARNINGS = [
    (r"(?:总而言之|综上所述|不仅如此|话不多说|干货满满|建议收藏|强烈建议|赋能|闭环|一站式搞定|颠覆|痛点直击)",
     "AI味过重/营销腔套话", "改为自然口语，如: 说实话 / 后来折腾了一阵发现 / 整理了几条经验"),
    (r"1️⃣|2️⃣|3️⃣|4️⃣", "机械序号Emoji(浓重AI/营销排版痕迹)", "改用普通数字 1. 2. 3. 或短横线 -"),
    (r"前后对比|对比图|原相机", "对比图虚假种草核查提醒", "若发布效果前后对比图，务必标明“原相机、无修图、拍摄时间与光源条件”，避免误导限流"),
    (r"克劳德", "音译敏感词提示", "推荐替换为更隐蔽安全的: CC / CC终端"),
]

SHOP_WARNINGS = [
    (r"0\.01元|1分钱|1元拍", "疑似低价引流标价", "请标真实资料价格并配置虚拟自动发货"),
    (r"内参|内部资料|内部工作流", "虚假权威风险词", "改为: 个人实操整理笔记 / 实操手册"),
    (r"分装小样|无盒简装", "无资质美妆/来源不明商品警示", "个人店缺少品牌授权与质检备案极易被下架，确认资质齐全后再发"),
]


def audit_text(text: str, mode: str) -> dict:
    critical_hits = []
    warning_hits = []

    active_critical = list(COMMON_CRITICAL_RULES)
    if mode in ("shop", "all"):
        active_critical.extend(SHOP_EXTRA_CRITICAL_RULES)

    active_warnings = []
    if mode in ("post", "all"):
        active_warnings.extend(POST_AI_FLAVOR_WARNINGS)
    if mode in ("shop", "all"):
        active_warnings.extend(SHOP_WARNINGS)

    lines = text.splitlines()
    for line_no, line in enumerate(lines, start=1):
        for pattern, category, suggestion in active_critical:
            for match in re.finditer(pattern, line, flags=re.IGNORECASE):
                critical_hits.append({
                    "level": "CRITICAL",
                    "line": line_no,
                    "matched": match.group(0),
                    "category": category,
                    "suggestion": suggestion,
                    "context": line.strip(),
                })
        for pattern, category, suggestion in active_warnings:
            for match in re.finditer(pattern, line, flags=re.IGNORECASE):
                warning_hits.append({
                    "level": "WARNING",
                    "line": line_no,
                    "matched": match.group(0),
                    "category": category,
                    "suggestion": suggestion,
                    "context": line.strip(),
                })

    if mode in ("post", "all"):
        marketing_emojis = re.findall(r"[🔥🚀✅📦💡⚡️🎯💰🤖🛠️]", text)
        if len(marketing_emojis) >= 6:
            warning_hits.append({
                "level": "WARNING",
                "line": 0,
                "matched": f"营销类Emoji数量={len(marketing_emojis)}",
                "category": "AI营销排版痕迹过重",
                "suggestion": "减少 🔥✅📦💡 等列表Emoji，最多保留 1~2 个日常表情（如 😭🙏📝），更像真人分享",
                "context": "全文统计",
            })

    passed = len(critical_hits) == 0
    return {
        "platform": "rednote",
        "mode": mode,
        "status": "PASS" if passed else "BLOCKED",
        "critical_count": len(critical_hits),
        "warning_count": len(warning_hits),
        "critical_hits": critical_hits,
        "warning_hits": warning_hits,
    }


def main():
    parser = argparse.ArgumentParser(description="小红书全平台规则与双模式（帖子/个人店）合规审计工具")
    parser.add_argument("--mode", choices=["post", "shop", "all"], default="all",
                        help="检查模式: post(帖子笔记) / shop(个人店商品) / all(双模式全查)")
    parser.add_argument("--file", type=str, help="待检查的文本文件路径")
    parser.add_argument("--text", type=str, help="直接传入待检查的文本")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式报告")
    args = parser.parse_args()

    if args.file:
        content = Path(args.file).read_text(encoding="utf-8")
    elif args.text:
        content = args.text
    else:
        content = sys.stdin.read()

    result = audit_text(content, args.mode)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"=== 小红书合规检测结果 [{result['mode']}模式]: {result['status']} ===")
        print(f"高危阻断项: {result['critical_count']} 个 | 优化建议项(含AI味检测): {result['warning_count']} 个\n")
        for hit in result["critical_hits"]:
            loc = f"第 {hit['line']} 行" if hit["line"] else "全文"
            print(f"[🔴 高危阻断] {loc}命中 「{hit['matched']}」 -> {hit['category']}")
            print(f"    建议替换: {hit['suggestion']}")
            print(f"    所在行内容: {hit['context']}\n")
        for hit in result["warning_hits"]:
            loc = f"第 {hit['line']} 行" if hit["line"] else "全文"
            print(f"[🟡 建议优化] {loc}命中 「{hit['matched']}」 -> {hit['category']}")
            print(f"    建议替换: {hit['suggestion']}")
            print(f"    所在行内容: {hit['context']}\n")

    sys.exit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
