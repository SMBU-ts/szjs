# szjs · 云计算复习专栏

湖南省数字技术应用能力水平考试（2025 考纲）·《云计算基础知识及应用》复习专栏。

> 内容整理自备考对话，按考纲第 1–7 章分篇，每章一篇，配统一章节导航。

## 访问地址
- 专栏首页（GitHub Pages 主站）：`https://smbu-ts.github.io/szjs/`
- 分章讲解：`/cloud/1.html`、`/cloud/2-1.html` ……（见首页考纲导航）
- 旧版完整备考手册（含 AI / 物联网）：`/archive/完整备考手册.html`

## 考纲覆盖（云计算 1–7 章）
1. 云计算概述（概念·服务模式·部署模式·特点优势）
2. 云计算关键技术（虚拟化·分布式·SDN/NFV）
3. 典型云计算平台（Google·华为云·平台选型；亚马逊 AWS 待补充）
4. 面向服务的分布式计算（Web 服务与协议·SOA·微服务）
5. 云计算数据中心（概念特征·关键服务·绿色节能）
6. 云计算安全
7. 云计算产业应用与发展

## 本地构建
分章讲解由 `build_column.py` 从「技术考试」目录的讲解 HTML 注入统一导航生成：

```bash
python build_column.py
```

## 部署
推送到 `main` 分支即由 `.github/workflows/deploy-pages.yml` 自动部署到 GitHub Pages（源：main / 路径 `/`）。
