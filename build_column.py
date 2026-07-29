# -*- coding: utf-8 -*-
"""
云计算复习专栏构建脚本
- 读取「技术考试」目录里分章讲解 HTML（含 3.2 亚马逊AWS / 3.4 百度云 / 4.1 Web文档服务 / 5.4 容灾备份）
- 生成：
    cloud/index.html  —— 左右分栏单页应用（左侧分组目录 + 右侧内容区，点击动态切换，选中高亮，移动端抽屉）
    cloud/*.html      —— 各章独立页（保留，供直接分享/深链）
    cloud/assets/nav.css
按《2025 湖南省数字技术应用能力考试 · 云计算基础知识及应用》考纲 1-7 章组织
"""
import os, re

SRC = r"C:\Users\16148\Desktop\技术考试"
OUT = os.path.dirname(os.path.abspath(__file__))

# (slug, 考纲编号, 标题, 简介, 所属分组)
chapters = [
    ("1",   "1",   "云计算概述",       "概念与发展 · 服务模式(IaaS/PaaS/SaaS) · 部署模式 · 特点优势",  "一、云计算概述"),
    ("2-1", "2.1", "虚拟化技术",       "基本概念 · 常见虚拟化技术 · 容器 · 与虚拟机区别 · 安全",        "二、云计算关键技术"),
    ("2-2", "2.2", "分布式技术",       "概念 · 在云中的应用 · 常见分布式技术 · 集群技术",              "二、云计算关键技术"),
    ("2-3", "2.3", "SDN 与 NFV",      "软件定义网络 · 网络功能虚拟化 · 应用场景 · VPC 与网络隔离",    "二、云计算关键技术"),
    ("3-1", "3.1", "Google 云计算",    "背景与场景 · 核心技术(GFS/MapReduce/BigTable等)",             "三、典型云计算平台"),
    ("3-2", "3.2", "亚马逊 AWS",       "核心服务(EC2/S3/RDS等) · 应用场景",                           "三、典型云计算平台"),
    ("3-3", "3.3", "华为云",           "核心技术与服务 · 各领域应用场景",                             "三、典型云计算平台"),
    ("3-4", "3.4", "百度云",           "核心服务 · AI 与行业应用",                                   "三、典型云计算平台"),
    ("3-5", "3.5", "云平台选择比较",   "各平台特点 · 针对需求选型方法",                               "三、典型云计算平台"),
    ("4-1", "4.1", "Web 文档服务",    "定义 · 核心组件 · 与 Web 服务的区别",                         "四、面向服务的分布式计算"),
    ("4-2", "4.2", "Web 服务与协议",  "核心组件 · SOAP · RESTful 原理与对比",                        "四、面向服务的分布式计算"),
    ("4-3", "4.3", "面向服务架构 SOA", "概念 · 核心组件 · 在分布式计算中的优势",                      "四、面向服务的分布式计算"),
    ("4-4", "4.4", "微服务架构",       "特性与架构 · 分布式数据管理 · 灵活扩展",                      "四、面向服务的分布式计算"),
    ("5-1", "5.1", "数据中心概念特征", "概念 · 核心组件 · 分类与分级 · 协同原理",                     "五、云计算数据中心"),
    ("5-2", "5.2", "数据中心关键服务", "DCaaS · 总体架构 · 设计与构建需求",                           "五、云计算数据中心"),
    ("5-3", "5.3", "绿色节能技术",     "配电/空调节能 · 典型绿色数据中心",                            "五、云计算数据中心"),
    ("5-4", "5.4", "容灾备份",         "容灾概念 · 备份策略 · RPO/RTO",                               "五、云计算数据中心"),
    ("6",   "6",   "云安全",           "概念与威胁 · 分层安全(IaaS/PaaS/SaaS) · 身份访问管理",        "六、云计算安全"),
    ("7",   "7",   "产业应用与发展",   "产业现状 · 行业应用 · 挑战与趋势",                            "七、云计算产业发展"),
]

SRC_FILE = {
    "1":   "1.云计算概述_详细讲解.html",
    "2-1": "2.1虚拟化技术_详细讲解.html",
    "2-2": "2.2分布式技术_详细讲解.html",
    "2-3": "2.3软件定义网络和网络功能虚拟化_详细讲解.html",
    "3-1": "3.1Google云计算_详解.html",
    "3-2": "3.2亚马逊AWS_详细讲解.html",
    "3-3": "3.3华为云_详细讲解.html",
    "3-4": "3.4百度云_复习.html",
    "3-5": "3.5典型云平台的选择与比较_详解.html",
    "4-1": "4.1_Web文档服务_复习.html",
    "4-2": "4.2 Web服务与协议_详细讲解.html",
    "4-3": "4.3面向服务的体系结构_详细讲解.html",
    "4-4": "4.4微服务架构_详细讲解.html",
    "5-1": "5.1云计算数据中心的概念及特征_详细讲解.html",
    "5-2": "5.2数据中心提供的关键服务和技术_详细讲解.html",
    "5-3": "5.3绿色节能技术_详细讲解.html",
    "5-4": "5.4容灾备份_复习卡片.html",
    "6":   "6_云安全_详细讲解.html",
    "7":   "7.云计算产业应用与发展_详细讲解.html",
}

NAV_CSS = """/* 云计算复习专栏 — 共享导航样式（独立分章页用） */
.colnav{position:sticky;top:0;z-index:100;background:linear-gradient(120deg,#1d4ed8,#3b82f6 60%,#0ea5e9);box-shadow:0 2px 10px rgba(20,40,80,.20)}
.colnav .inner{max-width:1120px;margin:0 auto;display:flex;align-items:center;gap:10px;padding:7px 14px}
.colnav .brand{font-weight:800;font-size:15px;white-space:nowrap;text-decoration:none;color:#fff;display:flex;align-items:center;gap:5px;flex:0 0 auto}
.colnav .brand small{font-weight:500;opacity:.8;font-size:11px}
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

# ---------- 抽取与样式作用域隔离 ----------
def extract_style(html):
    return "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S))

def extract_wrap(html):
    """返回 <div class="wrap"> 内部 HTML（按 div 层级平衡截取）"""
    m = re.search(r'<div class="wrap">', html)
    if not m:
        mb = re.search(r"<body[^>]*>(.*)</body>", html, re.S)
        return mb.group(1) if mb else html
    start = m.end()
    depth = 0
    for t in re.finditer(r"<(/?)div\b[^>]*>", html[start:]):
        if t.group(1) == "/":
            depth -= 1
            if depth == -1:
                return html[start:start + t.start()]
        else:
            depth += 1
    return html[start:]

GLOBAL_SELECTORS = {":root", "*", "html", "body"}
def scope_css(css, scope):
    """把一段 CSS 的所有选择器加上 #scope 前缀；:root/*/html/body 保持全局。"""
    prefix = "#" + scope + " "
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
            idx = s.index("{")
            head, body = s[:idx], s[idx + 1:s.rindex("}")]
            out.append(head + "{" + scope_css(body, scope) + "}")
        else:
            idx = s.index("{")
            sel, body = s[:idx], s[idx + 1:s.rindex("}")]
            sels = []
            for part in sel.split(","):
                p = part.strip()
                if not p:
                    continue
                sels.append(p if p in GLOBAL_SELECTORS else prefix + p)
            out.append(",".join(sels) + "{" + body + "}")
    return "".join(out)

# ---------- 独立分章页（保留，供深链/分享） ----------
def nav_html(active, link_prefix, home_href, assets_href):
    chips = []
    for slug, num, title, _, _ in chapters:
        cls = "chip active" if slug == active else "chip"
        chips.append(f'<a class="{cls}" href="{link_prefix}{slug}.html"><span class="num">{num}</span> {title}</a>')
    home_cls = "chip active" if active == "home" else "chip"
    return (
        f'<link rel="stylesheet" href="{assets_href}">\n'
        f'<nav class="colnav"><div class="inner">\n'
        f'<a class="{home_cls}" href="{home_href}"><span class="num">☁</span> 云计算复习专栏</a>\n'
        f'<div class="chips">\n' + "\n".join(chips) + "\n</div>\n</div></nav>"
    )

def bottom_html(active, link_prefix, home_href):
    idx = [c[0] for c in chapters].index(active)
    prev = chapters[idx - 1] if idx > 0 else None
    nxt = chapters[idx + 1] if idx < len(chapters) - 1 else None
    parts = []
    if prev:
        parts.append(f'<a class="prev" href="{link_prefix}{prev[0]}.html"><div class="lab">上一章</div><div class="ttl">{prev[2]}</div></a>')
    else:
        parts.append("<span></span>")
    parts.append(f'<a class="home" href="{home_href}">☁ 返回专栏首页</a>')
    if nxt:
        parts.append(f'<a class="next" href="{link_prefix}{nxt[0]}.html"><div class="lab">下一章</div><div class="ttl">{nxt[2]}</div></a>')
    else:
        parts.append("<span></span>")
    return '<div class="colfoot">' + "".join(parts) + "</div>"

def build_chapter_pages():
    os.makedirs(os.path.join(OUT, "cloud"), exist_ok=True)
    for slug, num, title, _, _ in chapters:
        src_path = os.path.join(SRC, SRC_FILE[slug])
        with open(src_path, "r", encoding="utf-8") as f:
            html = f.read()
        nav_full = nav_html(slug, "", "index.html", "assets/nav.css")
        nav_bar = nav_full.split("\n", 1)[1] if nav_full.startswith("<link") else nav_full
        bottom_bar = bottom_html(slug, "", "index.html")
        html = re.sub(r"</head>", '  <link rel="stylesheet" href="assets/nav.css">\n</head>', html, count=1)
        html = re.sub(r"<body[^>]*>", lambda m: m.group(0) + "\n" + nav_bar, html, count=1)
        html = re.sub(r"</body>", bottom_bar + "\n</body>", html, count=1)
        out_path = os.path.join(OUT, "cloud", f"{slug}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[ok] cloud/{slug}.html  ({title})")

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
.chapter{max-width:940px;margin:0 auto;display:none;font-size:15px;line-height:1.75;color:#1f2937}
.chapter.active{display:block;animation:fade .25s ease}
@keyframes fade{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
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
/* ===== 各章节样式（已按章节作用域隔离，互不干扰） ===== */
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

def build_home():
    # 左侧分组目录
    groups, cur_label, cur_items = [], None, []
    for slug, num, title, _, grp in chapters:
        if grp != cur_label:
            if cur_items:
                groups.append((cur_label, cur_items))
            cur_label, cur_items = grp, []
        cur_items.append((slug, num, title))
    if cur_items:
        groups.append((cur_label, cur_items))

    side_parts, first = [], True
    for label, items in groups:
        lis = []
        for i, (slug, num, title) in enumerate(items):
            act = " active" if first else ""
            lis.append(f'<a class="nav-item{act}" data-target="{slug}"><span class="nav-num">{num}</span><span class="nav-ttl">{title}</span></a>')
            first = False
        side_parts.append('<div class="group"><div class="group-label">' + label + "</div>" + "".join(lis) + "</div>")
    sidebar_html = "\n".join(side_parts)

    # 右侧各章内容（内嵌 + 作用域隔离样式）
    chap_parts, chap_css, first = [], [], True
    for slug, num, title, _, _ in chapters:
        with open(os.path.join(SRC, SRC_FILE[slug]), "r", encoding="utf-8") as f:
            html = f.read()
        style = extract_style(html)
        wrap = extract_wrap(html)
        wrap = re.sub(r"<script.*?</script>", "", wrap, flags=re.S)
        scoped = scope_css(style, "ch-" + slug)
        chap_css.append("/* === " + slug + " " + title + " === */\n" + scoped)
        act = " active" if first else ""
        chap_parts.append(f'<section class="chapter{act}" id="ch-{slug}">\n{wrap}\n</section>')
        first = False
    chapters_html = "\n".join(chap_parts)
    chapter_css = "\n".join(chap_css)

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
    os.makedirs(os.path.join(OUT, "cloud", "assets"), exist_ok=True)
    with open(os.path.join(OUT, "cloud", "assets", "nav.css"), "w", encoding="utf-8") as f:
        f.write(NAV_CSS)
    print("[ok] cloud/assets/nav.css")
    build_chapter_pages()
    build_home()
    print("\n全部生成完成。")

if __name__ == "__main__":
    main()
