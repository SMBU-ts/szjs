# -*- coding: utf-8 -*-
"""
云计算复习专栏构建脚本
- 读取「技术考试」目录里今晚生成的分章讲解 HTML
- 注入统一顶部章节导航 + 底部上/下章导航
- 输出：cloud/*.html 分章页、index.html 专栏首页、assets/nav.css
按《2025 湖南省数字技术应用能力考试 · 云计算基础知识及应用》考纲 1-7 章组织
"""
import os, re

SRC = r"C:\Users\16148\Desktop\技术考试"
OUT = os.path.dirname(os.path.abspath(__file__))

# (slug, 考纲编号, 标题, 简介)
chapters = [
    ("1",   "1",   "云计算概述",       "概念与发展 · 服务模式(IaaS/PaaS/SaaS) · 部署模式 · 特点优势"),
    ("2-1", "2.1", "虚拟化技术",       "基本概念 · 常见虚拟化技术 · 容器 · 与虚拟机区别 · 安全"),
    ("2-2", "2.2", "分布式技术",       "概念 · 在云中的应用 · 常见分布式技术 · 集群技术"),
    ("2-3", "2.3", "SDN 与 NFV",      "软件定义网络 · 网络功能虚拟化 · 应用场景 · VPC 与网络隔离"),
    ("3-1", "3.1", "Google 云计算",    "背景与场景 · 核心技术(GFS/MapReduce/BigTable等)"),
    ("3-3", "3.3", "华为云",           "核心技术与服务 · 各领域应用场景"),
    ("3-5", "3.5", "云平台选择比较",   "各平台特点 · 针对需求选型方法"),
    ("4-2", "4.2", "Web 服务与协议",  "核心组件 · SOAP · RESTful 原理与对比"),
    ("4-3", "4.3", "面向服务架构 SOA", "概念 · 核心组件 · 在分布式计算中的优势"),
    ("4-4", "4.4", "微服务架构",       "特性与架构 · 分布式数据管理 · 灵活扩展"),
    ("5-1", "5.1", "数据中心概念特征", "概念 · 核心组件 · 分类与分级 · 协同原理"),
    ("5-2", "5.2", "数据中心关键服务", "DCaaS · 总体架构 · 设计与构建需求"),
    ("5-3", "5.3", "绿色节能技术",     "配电/空调节能 · 典型绿色数据中心"),
    ("6",   "6",   "云安全",           "概念与威胁 · 分层安全(IaaS/PaaS/SaaS) · 身份访问管理"),
    ("7",   "7",   "产业应用与发展",   "产业现状 · 行业应用 · 挑战与趋势"),
]

SRC_FILE = {
    "1":   "1.云计算概述_详细讲解.html",
    "2-1": "2.1虚拟化技术_详细讲解.html",
    "2-2": "2.2分布式技术_详细讲解.html",
    "2-3": "2.3软件定义网络和网络功能虚拟化_详细讲解.html",
    "3-1": "3.1Google云计算_详解.html",
    "3-3": "3.3华为云_详细讲解.html",
    "3-5": "3.5典型云平台的选择与比较_详解.html",
    "4-2": "4.2 Web服务与协议_详细讲解.html",
    "4-3": "4.3面向服务的体系结构_详细讲解.html",
    "4-4": "4.4微服务架构_详细讲解.html",
    "5-1": "5.1云计算数据中心的概念及特征_详细讲解.html",
    "5-2": "5.2数据中心提供的关键服务和技术_详细讲解.html",
    "5-3": "5.3绿色节能技术_详细讲解.html",
    "6":   "6_云安全_详细讲解.html",
    "7":   "7.云计算产业应用与发展_详细讲解.html",
}

NAV_CSS = """/* 云计算复习专栏 — 共享导航样式 */
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

def nav_html(active, link_prefix, home_href, assets_href):
    chips = []
    for slug, num, title, _ in chapters:
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
        parts.append('<span></span>')
    parts.append(f'<a class="home" href="{home_href}">☁ 返回专栏首页</a>')
    if nxt:
        parts.append(f'<a class="next" href="{link_prefix}{nxt[0]}.html"><div class="lab">下一章</div><div class="ttl">{nxt[2]}</div></a>')
    else:
        parts.append('<span></span>')
    return '<div class="colfoot">' + "".join(parts) + "</div>"

def build_chapter_pages():
    os.makedirs(os.path.join(OUT, "cloud"), exist_ok=True)
    for slug, num, title, _ in chapters:
        src_path = os.path.join(SRC, SRC_FILE[slug])
        with open(src_path, "r", encoding="utf-8") as f:
            html = f.read()
        # 仅取 nav_html 里的 <nav> 段（<link> 单独注入 head）
        nav_full = nav_html(slug, "", "../index.html", "../assets/nav.css")
        nav_bar = nav_full.split("\n", 1)[1] if nav_full.startswith("<link") else nav_full
        bottom_bar = bottom_html(slug, "", "../index.html")
        html = re.sub(r"</head>", '  <link rel="stylesheet" href="../assets/nav.css">\n</head>', html, count=1)
        html = re.sub(r"<body[^>]*>", lambda m: m.group(0) + "\n" + nav_bar, html, count=1)
        html = re.sub(r"</body>", bottom_bar + "\n</body>", html, count=1)
        out_path = os.path.join(OUT, "cloud", f"{slug}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[ok] cloud/{slug}.html  ({title})")

def build_home():
    nav = nav_html("home", "cloud/", "index.html", "assets/nav.css")
    # 考纲大纲
    outline = [
        ("1", "云计算概述", [("1.1 概念及发展","1"),("1.2 服务模式","1"),("1.3 部署模式","1"),("1.4 特点及优势","1")]),
        ("2", "云计算关键技术", [("2.1 虚拟化技术","2-1"),("2.2 分布式技术","2-2"),("2.3 SDN 与 NFV","2-3")]),
        ("3", "典型云计算平台", [("3.1 Google 云计算","3-1"),("3.2 亚马逊 AWS","__"),("3.3 华为云","3-3"),("3.5 平台选择与比较","3-5")]),
        ("4", "面向服务的分布式计算", [("4.2 Web 服务与协议","4-2"),("4.3 面向服务架构 SOA","4-3"),("4.4 微服务架构","4-4")]),
        ("5", "云计算数据中心", [("5.1 概念及特征","5-1"),("5.2 关键服务技术","5-2"),("5.3 绿色节能技术","5-3")]),
        ("6", "云计算安全", [("6 云安全（6.1/6.2/6.3）","6")]),
        ("7", "云计算发展", [("7 产业应用与发展","7")]),
    ]
    outline_html = []
    for part, ptitle, items in outline:
        lis = []
        for it, slug in items:
            if slug == "__":
                lis.append(f'<li><span class="miss">\u25cb {it}（待补充）</span></li>')
            else:
                lis.append(f'<li><a href="cloud/{slug}.html">{it}</a></li>')
        outline_html.append(
            f'<div class="oline"><div class="opart">第 {part} 部分 · {ptitle}</div><ul class="oitems">'
            + "".join(lis) + "</ul></div>"
        )
    outline_html = "\n".join(outline_html)

    cards = []
    for slug, num, title, desc in chapters:
        cards.append(
            f'<a class="card" href="cloud/{slug}.html"><div class="cnum">{num}</div>'
            f'<div class="ctitle">{title}</div><div class="cdesc">{desc}</div></a>'
        )
    cards_html = "\n".join(cards)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>云计算复习专栏 · 2025 考纲</title>
{nav}
<style>
:root{{--bg:#f4f6fb;--card:#fff;--ink:#1f2937;--sub:#52606d;--brand:#2563eb;--line:#e5e7eb}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--ink);line-height:1.75;font-size:15px}}
.hero{{max-width:1120px;margin:26px auto 0;padding:34px 30px;border-radius:18px;color:#fff;
  background:linear-gradient(135deg,#1e3a8a,#2563eb 55%,#0ea5e9);box-shadow:0 12px 34px rgba(37,99,235,.28)}}
.hero h1{{margin:0 0 8px;font-size:30px;letter-spacing:.5px}}
.hero p{{margin:4px 0;opacity:.94;font-size:14.5px}}
.hero .badge{{display:inline-block;margin-top:12px;background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.4);padding:3px 12px;border-radius:999px;font-size:12.5px}}
.wrap{{max-width:1120px;margin:0 auto;padding:24px 18px 70px}}
.sec{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px 24px;margin-top:22px;box-shadow:0 2px 8px rgba(15,23,42,.04)}}
.sec h2{{font-size:19px;margin:0 0 14px;color:var(--brand);display:flex;align-items:center;gap:9px}}
.sec h2 .dot{{width:9px;height:9px;border-radius:3px;background:var(--brand);display:inline-block}}
.note{{background:#fffbeb;border:1px solid #fde68a;border-radius:10px;padding:11px 16px;margin-top:16px;font-size:13.5px;color:#92400e}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:14px;margin-top:6px}}
.card{{display:block;text-decoration:none;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 18px;color:var(--ink);box-shadow:0 2px 8px rgba(15,23,42,.04);transition:.15s;border-top:4px solid var(--brand)}}
.card:hover{{transform:translateY(-3px);box-shadow:0 10px 24px rgba(37,99,235,.18);border-color:#bfdbfe}}
.card .cnum{{display:inline-block;font-weight:800;color:#fff;background:var(--brand);border-radius:8px;padding:1px 9px;font-size:13px}}
.card .ctitle{{font-size:16px;font-weight:700;margin:9px 0 5px}}
.card .cdesc{{font-size:12.8px;color:var(--sub);line-height:1.55}}
.oline{{display:flex;gap:14px;padding:11px 0;border-bottom:1px dashed var(--line);flex-wrap:wrap}}
.oline:last-child{{border-bottom:none}}
.opart{{flex:0 0 180px;font-weight:700;color:#0f172a;font-size:14.5px}}
.oitems{{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:8px 16px}}
.oitems li a{{color:var(--brand);text-decoration:none;font-size:13.5px}}
.oitems li a:hover{{text-decoration:underline}}
.oitems .miss{{color:#94a3b8;font-size:13px}}
footer{{text-align:center;color:#94a3b8;font-size:12.5px;margin-top:30px}}
</style>
</head>
<body>
<header class="hero">
  <h1>\u2601 云计算复习专栏</h1>
  <p>依据《2025 湖南省数字技术应用能力考试 · 云计算基础知识及应用》考纲整理</p>
  <p>整理自今晚的云计算讲解，按考纲第 1–7 章分篇，每章一篇，可顺序复习或按需跳转。</p>
  <span class="badge">覆盖：概述 · 关键技术 · 典型平台 · 面向服务计算 · 数据中心 · 安全 · 产业发展</span>
</header>

<div class="wrap">
  <section class="sec">
    <h2><span class="dot"></span>考纲导航（点击直达对应章节）</h2>
    {outline_html}
    <div class="note">\u26a0 说明：考纲中的 <b>3.2 亚马逊 AWS</b> 等少数小节本次未单独生成讲解，已在上方标注「待补充」，后续可补充后加入。</div>
  </section>

  <section class="sec">
    <h2><span class="dot"></span>分章讲解（共 {len(chapters)} 篇）</h2>
    <div class="grid">
      {cards_html}
    </div>
  </section>

  <footer>云计算复习专栏 · 备考专用 · 配合《2025考纲》与《核心知识点详解》使用</footer>
</div>
</body>
</html>
"""
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("[ok] index.html (专栏首页)")

def main():
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    with open(os.path.join(OUT, "assets", "nav.css"), "w", encoding="utf-8") as f:
        f.write(NAV_CSS)
    print("[ok] assets/nav.css")
    build_chapter_pages()
    build_home()
    print("\n全部生成完成。")

if __name__ == "__main__":
    main()
