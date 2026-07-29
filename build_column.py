# -*- coding: utf-8 -*-
"""
云计算复习专栏构建脚本（左右分栏单页应用 + 独立分章页）
- 读取「技术考试」目录里的分章讲解 HTML
- 抽取每章正文（优先 <main>，回退 .wrap / <body>），避免无 .wrap 章节把自身 header/内部目录/footer 一并塞进内容区
- 1、7、6 均使用独立源文件，不再使用 split_by_h2 切割（避免孤立标签导致渲染空白）
- 每章样式按作用域隔离后内嵌，章节间互不干扰；统一标题栏 + 统一基础排版
按《2025 湖南省数字技术应用能力考试 · 云计算基础知识及应用》考纲 1-7 章组织
"""
import os, re, glob

SRC = r"C:\Users\16148\Desktop\技术考试"
OUT = os.path.dirname(os.path.abspath(__file__))

GLOBAL_SELECTORS = {":root", "*", "html", "body"}

def read(rel):
    with open(os.path.join(SRC, rel), "r", encoding="utf-8") as f:
        return f.read()

# ---------- 抽取与样式作用域隔离 ----------
def extract_style(html):
    return "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S))

def extract_main(html):
    """取正文：优先 <main>，回退 .wrap（按 div 层级平衡），再回退 <body>；
    末尾统一剥离页面级 chrome（header.top / nav.toc / footer / 目录卡），避免套娃。"""
    m = re.search(r"<main[^>]*>(.*?)</main>", html, re.S)
    if m:
        raw = m.group(1)
    else:
        mw = re.search(r'<div class="wrap">', html)
        if mw:
            start = mw.end(); depth = 0
            raw = html[start:]
            for t in re.finditer(r"<(/?)div\b[^>]*>", html[start:]):
                if t.group(1) == "/":
                    depth -= 1
                    if depth == -1:
                        raw = html[start:start + t.start()]
                        break
                else:
                    depth += 1
        else:
            mb = re.search(r"<body[^>]*>(.*)</body>", html, re.S)
            raw = mb.group(1) if mb else html
    return strip_chrome(raw)

def _remove_tag_block(html, tag, cls_sub=None):
    """删除带指定 class 的整块标签（支持标签嵌套）；
    cls_sub 为 None 时删除任意该标签（如 footer）。"""
    if cls_sub is None:
        pat = re.compile(r"<%s\b[^>]*>" % tag, re.I)
    else:
        pat = re.compile(r"<%s\b[^>]*class=\"[^\"]*%s[^\"]*\"[^>]*>" % (tag, cls_sub), re.I)
    out, i, n = [], 0, len(html)
    close = "</%s>" % tag
    tl = len(tag) + 1
    while True:
        m = pat.search(html, i)
        if not m:
            out.append(html[i:]); break
        out.append(html[i:m.start()])
        depth, k, matched = 0, m.end(), False
        while k < n:
            # 找下一个同标签起始（排除 <tagX），优先于结束标签
            op, pos = -1, k
            while True:
                p = html.find("<%s" % tag, pos)
                if p == -1:
                    break
                nxt = html[p + tl] if p + tl < n else ">"
                if nxt in " \t\n>":
                    op = p; break
                pos = p + 1
            cl = html.find(close, k)
            if cl == -1:
                break
            if op != -1 and op < cl:
                depth += 1
                k = op + tl
            else:
                if depth == 0:
                    k = cl + len(close); matched = True; break
                depth -= 1
                k = cl + len(close)
        if matched:
            i = k
        else:
            out.append(html[m.start():]); break
    return "".join(out)

def strip_chrome(html):
    """剥离页面级 chrome：顶部 banner、目录导航、页脚。"""
    html = _remove_tag_block(html, "header", "top")
    html = _remove_tag_block(html, "div", "toc")
    html = _remove_tag_block(html, "nav", "toc")
    html = re.sub(r"<footer\b[^>]*>.*?</footer>", "", html, flags=re.S | re.I)
    return html

def split_by_h2(content):
    ms = list(re.finditer(r"<h2[^>]*>(.*?)</h2>", content, re.S))
    if not ms:
        return [("全文", content)]
    out = []
    for i, m in enumerate(ms):
        title = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        start = m.end()
        end = ms[i + 1].start() if i + 1 < len(ms) else len(content)
        out.append((title, content[start:end]))
    return out

def scope_css(css, scope):
    prefix = scope + " "
    blocks, buf, depth = [], "", 0
    for ch in css:
        buf += ch
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                blocks.append(buf); buf = ""
    out = []
    for blk in blocks:
        s = blk.strip()
        if not s:
            continue
        if s.startswith("@"):
            if s.startswith(("@keyframes", "@-webkit-keyframes", "@font-face")):
                out.append(blk); continue
            idx = s.index("{"); head = s[:idx]; body = s[idx + 1:s.rindex("}")]
            out.append(head + "{" + scope_css(body, scope) + "}")
        else:
            idx = s.index("{"); sel = s[:idx]; body = s[idx + 1:s.rindex("}")]
            sels = []
            for part in sel.split(","):
                p = part.strip()
                if not p:
                    continue
                sels.append(p if p in GLOBAL_SELECTORS else prefix + p)
            out.append(",".join(sels) + "{" + body + "}")
    return "".join(out)

# ---------- 构建章节条目（专栏导航的数据源） ----------
def build_entries():
    E = []
    def add_single(slug, num, title, src, group, scope=None):
        html = read(src)
        E.append({
            "slug": slug, "num": num, "title": title, "group": group,
            "style": extract_style(html), "content": extract_main(html),
            "scope": scope or ("#ch-" + slug), "wrap_based": ('class="wrap"' in html),
        })
    def add_split(base, chap_title, src, group, skip=None):
        skip = skip or []
        html = read(src)
        style = extract_style(html); content = extract_main(html)
        subs = [(t, b) for (t, b) in split_by_h2(content)
                if not any(k in t for k in skip)]
        for i, (t, b) in enumerate(subs):
            # 去除 h2 自带的前缀编号（如 "1.1" -> ""），避免 ch-head 重复显示 "1.1 1.1xxx"
            clean_t = re.sub(r'^\d+\.\d+\s*', '', t) or t
            E.append({
                "slug": f"{base}-{i+1}", "num": f"{base}.{i+1}", "title": clean_t,
                "group": group, "style": style, "content": b,
                "scope": f".ch{base}", "wrap_based": ('class="wrap"' in html),
            })

    # 一、云计算概述（拆分）
    add_split("1", "云计算概述", "1.云计算概述_详细讲解.html", "一、云计算概述")
    # 二、云计算关键技术
    add_single("2-1", "2.1", "虚拟化技术", "2.1虚拟化技术_详细讲解.html", "二、云计算关键技术")
    add_single("2-2", "2.2", "分布式技术", "2.2分布式技术_详细讲解.html", "二、云计算关键技术")
    add_single("2-3", "2.3", "SDN 与 NFV", "2.3软件定义网络和网络功能虚拟化_详细讲解.html", "二、云计算关键技术")
    # 三、典型云计算平台
    add_single("3-1", "3.1", "Google 云计算", "3.1Google云计算_详解.html", "三、典型云计算平台")
    add_single("3-2", "3.2", "亚马逊 AWS", "3.2亚马逊AWS_详细讲解.html", "三、典型云计算平台")
    add_single("3-3", "3.3", "华为云", "3.3华为云_详细讲解.html", "三、典型云计算平台")
    add_single("3-4", "3.4", "百度云", "3.4百度云_复习.html", "三、典型云计算平台")
    add_single("3-5", "3.5", "云平台选择比较", "3.5典型云平台的选择与比较_详解.html", "三、典型云计算平台")
    # 四、面向服务的分布式计算
    add_single("4-1", "4.1", "Web 文档服务", "4.1_Web文档服务_复习.html", "四、面向服务的分布式计算")
    add_single("4-2", "4.2", "Web 服务与协议", "4.2 Web服务与协议_详细讲解.html", "四、面向服务的分布式计算")
    add_single("4-3", "4.3", "面向服务架构 SOA", "4.3面向服务的体系结构_详细讲解.html", "四、面向服务的分布式计算")
    add_single("4-4", "4.4", "微服务架构", "4.4微服务架构_详细讲解.html", "四、面向服务的分布式计算")
    # 五、云计算数据中心
    add_single("5-1", "5.1", "数据中心概念特征", "5.1云计算数据中心的概念及特征_详细讲解.html", "五、云计算数据中心")
    add_single("5-2", "5.2", "数据中心关键服务", "5.2数据中心提供的关键服务和技术_详细讲解.html", "五、云计算数据中心")
    add_single("5-3", "5.3", "绿色节能技术", "5.3绿色节能技术_详细讲解.html", "五、云计算数据中心")
    add_single("5-4", "5.4", "容灾备份", "5.4容灾备份_复习卡片.html", "五、云计算数据中心")
    # 六、云计算安全（独立源文件，避免 split ��割导致孤立标签）
    add_single("6-1", "6.1", "云安全的概念及重要性", "6.1_云安全的概念及重要性_2025考纲.html", "六、云计算安全")
    add_single("6-2", "6.2", "安全防护与策略", "6.2_常见安全防护措施及相关安全策略_2025考纲.html", "六、云计算安全")
    add_single("6-3", "6.3", "身份授权与访问管理", "6.3_身份、授权和访问管理_2025考纲.html", "六、云计算安全")
    add_single("6-4", "6.4", "数据加密与密钥管理", "6.4_数据加密与密钥管理_2025考纲.html", "六、云计算安全")
    # 七、云计算产业发展（独立源文件）
    add_single("7-1", "7.1", "中国云计算产业发展现状", "7.1_中国云计算产业发展现状_复习考纲.html", "七、云计算产业发展")
    add_single("7-2", "7.2", "云计算的行业应用", "7.2_云计算的行业应用_复习考纲.html", "七、云计算产业发展")
    add_single("7-3", "7.3", "云计算发展及挑战", "7.3_云计算发展及挑战_复习考纲.html", "七、云计算产业发展")
    return E

ENTRIES = []

NAV_CSS = """/* 独立分章页顶部/底部导航（专栏 SPA 不使用） */
.colnav{position:sticky;top:0;z-index:100;background:linear-gradient(120deg,#1d4ed8,#3b82f6 60%,#0ea5e9);box-shadow:0 2px 10px rgba(20,40,80,.20)}
.colnav .inner{max-width:1120px;margin:0 auto;display:flex;align-items:center;gap:10px;padding:7px 14px}
.colnav .brand{font-weight:800;font-size:15px;white-space:nowrap;text-decoration:none;color:#fff;display:flex;align-items:center;gap:5px;flex:0 0 auto}
.colnav .chips{display:flex;gap:6px;overflow-x:auto;flex:1;padding:2px 0;scrollbar-width:thin}
.colnav .chips::-webkit-scrollbar{height:5px}
.colnav .chips::-webkit-scrollbar-thumb{background:rgba(255,255,255,.4);border-radius:4px}
.colnav .chip{flex:0 0 auto;text-decoration:none;color:#dbeafe;background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.18);padding:3px 9px;border-radius:999px;font-size:12px;white-space:nowrap;display:inline-flex;align-items:center;gap:5px;transition:.15s}
.colnav .chip:hover{background:rgba(255,255,255,.22);color:#fff}
.colnav .chip .num{font-weight:700;color:#fff}
.colnav .chip.active{background:#fff;color:#1d4ed8;border-color:#fff}
.colnav .chip.active .num{color:#1d4ed8}
.colfoot{max-width:980px;margin:28px auto 0;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
.colfoot a{text-decoration:none;flex:1 1 200px;border:1px solid #e5e7eb;background:#fff;border-radius:12px;padding:12px 16px;color:#1f2937;box-shadow:0 2px 8px rgba(15,23,42,.05);transition:.15s}
.colfoot a:hover{border-color:#2563eb;box-shadow:0 4px 14px rgba(37,99,235,.15)}
.colfoot a.home{text-align:center;background:#eff6ff;border-color:#bfdbfe;color:#1d4ed8;font-weight:700;flex:0 1 180px}
.colfoot .lab{font-size:12px;color:#94a3b8}
.colfoot .ttl{font-size:14.5px;font-weight:700;margin-top:2px}
.colfoot a.prev .ttl::before{content:"\\2190  "}
.colfoot a.next{text-align:right}
.colfoot a.next .ttl::after{content:"  \\2192"}
@media(max-width:560px){.colfoot a{flex:1 1 100%}.colfoot a.next{text-align:left}.colfoot a.home{flex:1 1 100%}}
"""

# 独立分章页：统一标题栏 + 基础排版（与 SPA 一致），同时兼容 .wrap / .content 两种容器
STANDALONE_CSS = """/* 独立分章页基础排版（与专栏 SPA 统一） */
.wrap,.content{font-size:15px;line-height:1.75;color:#1f2937}
.wrap h1,.content h1,.wrap h2,.content h2,.wrap h3,.content h3,.wrap h4,.content h4{color:#0f172a;line-height:1.35;margin:18px 0 10px}
.wrap h1,.content h1{font-size:24px}
.wrap h2,.content h2{font-size:20px;padding-bottom:6px;border-bottom:2px solid #e2e8f0}
.wrap h3,.content h3{font-size:17px}
.wrap h4,.content h4{font-size:15px}
.wrap p,.content p{margin:9px 0;line-height:1.85;color:#334155}
.wrap ul,.content ul,.wrap ol,.content ol{margin:9px 0;padding-left:22px;color:#334155}
.wrap li,.content li{margin:5px 0;line-height:1.8}
.wrap a,.content a{color:#2563eb;text-decoration:none}.wrap a:hover,.content a:hover{text-decoration:underline}
.wrap strong,.content strong,.wrap b,.content b{color:#0f172a}
.wrap table,.content table{border-collapse:collapse;width:100%;margin:12px 0;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 1px 4px rgba(15,23,42,.06)}
.wrap th,.content th,.wrap td,.content td{border:1px solid #e2e8f0;padding:9px 12px;text-align:left;vertical-align:top}
.wrap th,.content th{background:#eff6ff;color:#1e3a8a;font-weight:700}
.wrap code,.content code{background:#f1f5f9;padding:1px 6px;border-radius:5px;font-size:13px;color:#be123c}
.wrap pre,.content pre{background:#0f172a;color:#e2e8f0;padding:14px 16px;border-radius:10px;overflow:auto;font-size:13px}
.wrap blockquote,.content blockquote{border-left:4px solid #2563eb;background:#f8fafc;margin:12px 0;padding:10px 16px;color:#475569}
.wrap img,.content img{max-width:100%;border-radius:10px}
/* 统一标题栏（与 SPA 一致） */
.ch-head{display:flex;align-items:center;gap:12px;padding:14px 18px;border-radius:12px;background:linear-gradient(120deg,#1e3a8a,#2563eb 60%,#0ea5e9);color:#fff;box-shadow:0 6px 18px rgba(37,99,235,.22);margin-bottom:18px}
.ch-head .ch-num{background:rgba(255,255,255,.22);font-weight:800;font-size:15px;padding:3px 11px;border-radius:8px;flex:0 0 auto}
.ch-head .ch-ttl{font-size:18px;font-weight:700}"""

def nav_html(active, link_prefix, home_href, assets_href):
    chips = []
    for e in ENTRIES:
        cls = "chip active" if e["slug"] == active else "chip"
        chips.append(f'<a class="{cls}" href="{link_prefix}{e["slug"]}.html"><span class="num">{e["num"]}</span> {e["title"]}</a>')
    home_cls = "chip active" if active == "home" else "chip"
    return (
        f'<link rel="stylesheet" href="{assets_href}">\n'
        f'<nav class="colnav"><div class="inner">\n'
        f'<a class="{home_cls}" href="{home_href}"><span class="num">☁</span> 云计算复习专栏</a>\n'
        f'<div class="chips">\n' + "\n".join(chips) + "\n</div>\n</div></nav>"
    )

def bottom_html(active, link_prefix, home_href):
    idx = [e["slug"] for e in ENTRIES].index(active)
    prev = ENTRIES[idx - 1] if idx > 0 else None
    nxt = ENTRIES[idx + 1] if idx < len(ENTRIES) - 1 else None
    parts = []
    if prev:
        parts.append(f'<a class="prev" href="{link_prefix}{prev["slug"]}.html"><div class="lab">上一篇</div><div class="ttl">{prev["num"]} {prev["title"]}</div></a>')
    else:
        parts.append("<span></span>")
    parts.append(f'<a class="home" href="{home_href}">☁ 返回专栏首页</a>')
    if nxt:
        parts.append(f'<a class="next" href="{link_prefix}{nxt["slug"]}.html"><div class="lab">下一篇</div><div class="ttl">{nxt["num"]} {nxt["title"]}</div></a>')
    else:
        parts.append("<span></span>")
    return '<div class="colfoot">' + "".join(parts) + "</div>"

# ---------- 独立分章页（供深链/分享） ----------
def build_standalone(e):
    nav = nav_html(e["slug"], "", "index.html", "assets/nav.css")
    parts = nav.split("\n", 1)
    head_link = parts[0] if parts[0].startswith("<link") else ""
    nav_bar = parts[1] if len(parts) > 1 else parts[0]
    bottom = bottom_html(e["slug"], "", "index.html")
    cont_open = '<div class="wrap">' if e["wrap_based"] else "<main>"
    cont_close = "</div>" if e["wrap_based"] else "</main>"
    inner = e["content"]
    if e["scope"].startswith("."):  # 拆分出的小板块：补上被切掉的 h2 标题
        inner = f'<h2>{e["title"]}</h2>' + inner
    ch_head = f'<div class="ch-head"><span class="ch-num">{e["num"]}</span><span class="ch-ttl">{e["title"]}</span></div>'
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e['num']} {e['title']} · 云计算复习专栏</title>
<style>
{STANDALONE_CSS}
{e['style']}
</style>
{head_link}
</head>
<body>
{nav_bar}
{cont_open}
{ch_head}
{inner}
{cont_close}
{bottom}
</body>
</html>"""
    with open(os.path.join(OUT, "cloud", f"{e['slug']}.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[ok] cloud/{e['slug']}.html  ({e['num']} {e['title']})")

# ---------- 单页应用（左右分栏专栏） ----------
SPA_CSS = """*{box-sizing:border-box}
html,body{margin:0;padding:0;height:100%}
body{font-family:-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;background:#eef2f7;color:#1f2937;-webkit-font-smoothing:antialiased}
.topbar{height:56px;display:flex;align-items:center;gap:12px;padding:0 16px;background:linear-gradient(120deg,#1e3a8a,#2563eb 60%,#0ea5e9);color:#fff;position:sticky;top:0;z-index:30;box-shadow:0 2px 12px rgba(20,40,80,.2)}
.topbar .brand{font-weight:800;font-size:17px;flex:1;letter-spacing:.5px}
.topbar .menu-btn{display:none;border:none;background:rgba(255,255,255,.18);color:#fff;font-size:20px;width:38px;height:38px;border-radius:9px;cursor:pointer}
.topbar .home-link{color:#dbeafe;text-decoration:none;font-size:13px;border:1px solid rgba(255,255,255,.35);padding:5px 11px;border-radius:999px;white-space:nowrap}
.topbar .home-link:hover{background:rgba(255,255,255,.18);color:#fff}
.app{display:flex;height:calc(100vh - 56px)}
.sidebar{width:300px;flex:0 0 300px;background:#fff;border-right:1px solid #e5e7eb;overflow-y:auto;padding:16px 12px 40px}
.side-head{padding:4px 10px 14px;font-size:12px;font-weight:700;color:#94a3b8;letter-spacing:1px}
.toc{display:flex;flex-direction:column;gap:16px}
.group-label{font-size:12.5px;font-weight:800;color:#1e3a8a;padding:0 10px 6px;margin-bottom:2px;border-left:3px solid #2563eb;line-height:1.2}
.nav-item{display:flex;align-items:center;gap:10px;padding:9px 12px;border-radius:10px;color:#475569;text-decoration:none;font-size:14px;cursor:pointer;transition:.15s;border-left:3px solid transparent}
.nav-item:hover{background:#eef2ff;color:#1d4ed8}
.nav-item.active{background:linear-gradient(90deg,#2563eb,#3b82f6);color:#fff;font-weight:700;border-left-color:#1e3a8a;box-shadow:0 4px 12px rgba(37,99,235,.25)}
.nav-item .nav-num{flex:0 0 auto;min-width:30px;height:24px;padding:0 7px;border-radius:7px;background:#e2e8f0;color:#334155;font-size:12.5px;font-weight:700;display:inline-flex;align-items:center;justify-content:center}
.nav-item.active .nav-num{background:rgba(255,255,255,.28);color:#fff}
.nav-item .nav-ttl{line-height:1.3}
.content{flex:1;overflow-y:auto;background:#f1f5f9;padding:24px}
/* 用 main > section.chapter 仅匹配专栏自己的板块 section，避免误伤源文件里的 <div class="chapter"> */
main > section.chapter{max-width:940px;margin:0 auto;display:none;font-size:15px;line-height:1.75;color:#1f2937}
main > section.chapter.active{display:block;animation:fade .25s ease}
@keyframes fade{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
/* ===== 统一标题栏（每个板块一致） ===== */
.ch-head{display:flex;align-items:center;gap:12px;padding:14px 18px;border-radius:12px;background:linear-gradient(120deg,#1e3a8a,#2563eb 60%,#0ea5e9);color:#fff;box-shadow:0 6px 18px rgba(37,99,235,.22);margin-bottom:18px}
.ch-head .ch-num{background:rgba(255,255,255,.22);font-weight:800;font-size:15px;padding:3px 11px;border-radius:8px;flex:0 0 auto}
.ch-head .ch-ttl{font-size:18px;font-weight:700}
/* ===== 统一基础排版（富文本一致呈现） ===== */
.content h1,.content h2,.content h3,.content h4{color:#0f172a;line-height:1.35;margin:18px 0 10px}
.content h1{font-size:24px}.content h2{font-size:20px;padding-bottom:6px;border-bottom:2px solid #e2e8f0}
.content h3{font-size:17px}.content h4{font-size:15px}
.content p{margin:9px 0;line-height:1.85;color:#334155}
.content ul,.content ol{margin:9px 0;padding-left:22px;color:#334155}
.content li{margin:5px 0;line-height:1.8}
.content a{color:#2563eb;text-decoration:none}.content a:hover{text-decoration:underline}
.content strong,.content b{color:#0f172a}
.content table{border-collapse:collapse;width:100%;margin:12px 0;font-size:14px;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 1px 4px rgba(15,23,42,.06)}
.content th,.content td{border:1px solid #e2e8f0;padding:9px 12px;text-align:left;vertical-align:top}
.content th{background:#eff6ff;color:#1e3a8a;font-weight:700}
.content code{background:#f1f5f9;padding:1px 6px;border-radius:5px;font-size:13px;color:#be123c}
.content pre{background:#0f172a;color:#e2e8f0;padding:14px 16px;border-radius:10px;overflow:auto;font-size:13px}
.content blockquote{border-left:4px solid #2563eb;background:#f8fafc;margin:12px 0;padding:10px 16px;color:#475569}
.content img{max-width:100%;border-radius:10px}
.cf{text-align:center;color:#94a3b8;font-size:12.5px;margin-top:30px}
.overlay{display:none}
@media(max-width:820px){
  .topbar .menu-btn{display:block}
  .sidebar{position:fixed;top:56px;left:0;bottom:0;width:82%;max-width:330px;transform:translateX(-106%);transition:transform .25s ease;z-index:25;box-shadow:6px 0 28px rgba(0,0,0,.18)}
  .sidebar.open{transform:translateX(0)}
  .overlay{position:fixed;inset:56px 0 0 0;background:rgba(15,23,42,.45);z-index:20;display:none}
  .overlay.show{display:block}
  .content{padding:14px}
  .chapter{max-width:100%}
}"""

SPA_JS = """(function(){
  var items = Array.prototype.slice.call(document.querySelectorAll('.nav-item'));
  var sections = Array.prototype.slice.call(document.querySelectorAll('.chapter'));
  var sidebar = document.getElementById('sidebar');
  var overlay = document.getElementById('overlay');
  function show(target){
    sections.forEach(function(s){ s.classList.toggle('active', s.id === 'ch-' + target); });
    items.forEach(function(it){ it.classList.toggle('active', it.getAttribute('data-target') === target); });
    var c = document.getElementById('content'); if(c) c.scrollTop = 0;
    closeDrawer();
  }
  items.forEach(function(it){
    it.addEventListener('click', function(){ show(it.getAttribute('data-target')); });
  });
  function openDrawer(){ sidebar.classList.add('open'); overlay.classList.add('show'); }
  function closeDrawer(){ sidebar.classList.remove('open'); overlay.classList.remove('show'); }
  document.getElementById('menuBtn').addEventListener('click', openDrawer);
  overlay.addEventListener('click', closeDrawer);
  var h = location.hash ? location.hash.replace('#','') : '';
  if(h && document.getElementById('ch-'+h)){ show(h); }
  else { show(items.length ? items[0].getAttribute('data-target') : '1'); }
})();"""

SPA_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>云计算复习专栏 · 2025 考纲</title>
<style>
__BASECSS__
/* ===== 各章节样式（已按作用域隔离，互不干扰） ===== */
__CHAPTERCSS__
</style>
</head>
<body>
<header class="topbar">
  <button class="menu-btn" id="menuBtn" aria-label="打开目录">☰</button>
  <div class="brand">☁ 云计算复习专栏</div>
  <a class="home-link" href="../index.html">← 返回主页</a>
</header>
<div class="app">
  <aside class="sidebar" id="sidebar">
    <div class="side-head">复习目录 · 2025 考纲 1–7 章</div>
    <nav class="toc" id="toc">
__SIDEBAR__
    </nav>
  </aside>
  <div class="overlay" id="overlay"></div>
  <main class="content" id="content">
__CHAPTERS__
    <footer class="cf">云计算复习专栏 · 备考专用 · 配合《2025考纲》使用</footer>
  </main>
</div>
<script>
__JS__
</script>
</body>
</html>"""

def build_home(entries):
    groups, cur, items = [], None, []
    for e in entries:
        if e["group"] != cur:
            if items:
                groups.append((cur, items))
            cur, items = e["group"], []
        items.append(e)
    if items:
        groups.append((cur, items))

    side, first = [], True
    for label, items in groups:
        lis = []
        for e in items:
            act = " active" if first else ""
            lis.append(f'<a class="nav-item{act}" data-target="{e["slug"]}"><span class="nav-num">{e["num"]}</span><span class="nav-ttl">{e["title"]}</span></a>')
            first = False
        side.append('<div class="group"><div class="group-label">' + label + "</div>" + "".join(lis) + "</div>")
    sidebar_html = "\n".join(side)

    chap, cache, first = [], {}, True
    for e in entries:
        extra = (" " + e["scope"][1:]) if e["scope"].startswith(".") else ""
        act = " active" if first else ""
        tag = f'<section class="chapter{extra}{act}" id="ch-{e["slug"]}">'
        head = f'<div class="ch-head"><span class="ch-num">{e["num"]}</span><span class="ch-ttl">{e["title"]}</span></div>'
        chap.append(tag + head + e["content"] + "</section>")
        if e["scope"] not in cache:
            cache[e["scope"]] = scope_css(e["style"], e["scope"])
        first = False
    chapters_html = "\n".join(chap)
    chapter_css = "\n".join(cache.values())

    html = (SPA_TEMPLATE
            .replace("__BASECSS__", SPA_CSS)
            .replace("__CHAPTERCSS__", chapter_css)
            .replace("__SIDEBAR__", sidebar_html)
            .replace("__CHAPTERS__", chapters_html)
            .replace("__JS__", SPA_JS))
    with open(os.path.join(OUT, "cloud", "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("[ok] cloud/index.html (左右分栏单页应用)")

def main():
    # 清理旧的 cloud/*.html，避免残留旧 slug（如 1.html / 6.html）
    # 沙箱环境下 os.remove 可能被安全策略拦截，改为 best-effort，不因此中断构建
    for f in glob.glob(os.path.join(OUT, "cloud", "*.html")):
        try:
            os.remove(f)
        except Exception:
            pass
    os.makedirs(os.path.join(OUT, "cloud", "assets"), exist_ok=True)
    with open(os.path.join(OUT, "cloud", "assets", "nav.css"), "w", encoding="utf-8") as f:
        f.write(NAV_CSS)
    print("[ok] cloud/assets/nav.css")

    global ENTRIES
    ENTRIES = build_entries()
    for e in ENTRIES:
        build_standalone(e)
    build_home(ENTRIES)
    print(f"\n共 {len(ENTRIES)} 个板块，全部生成完成。")

if __name__ == "__main__":
    main()
