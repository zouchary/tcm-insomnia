#!/usr/bin/env python3
"""生成 cases/00_index.md：既有 01~06 证型案 + 李可医案 li_*。"""
import re, glob, os, json

rows = []
for f in sorted(glob.glob("cases/[0-9][0-9]_*.md")):
    t = open(f, encoding="utf-8").read()
    title = re.search(r"^#\s+(.+)$", t, re.M)
    title = title.group(1).strip() if title else os.path.basename(f)
    src = re.search(r"来源[:：]\s*(.+)", t)
    src = src.group(1).strip().strip("《》") if src else "（未标注）"
    n = len(re.findall(r"^##\s*医案", t, re.M))
    rows.append((title, f"证型篇（{n} 则）", src, "—", os.path.basename(f), "既有"))

for f in sorted(glob.glob("cases/li_*.md")):
    t = open(f, encoding="utf-8").read()
    title = re.search(r"^#\s+医案：(.+)$", t, re.M)
    title = title.group(1).strip() if title else os.path.basename(f)
    pat = re.search(r"\*\*患者\*\*：(.+)", t)
    pat = pat.group(1).strip() if pat else "—"
    src = re.search(r"\*\*出处\*\*：(.+)", t)
    src = src.group(1).strip() if src else "—"
    ln = re.search(r"（第 (\d+) 行）", t)
    ln = "L" + ln.group(1) if ln else "—"
    rows.append((title, pat, src, ln, os.path.basename(f), "新增"))

with open("cases/00_index.md", "w", encoding="utf-8") as f:
    f.write("# 医案库索引\n\n")
    f.write(f"> 共 {len(rows)} 篇医案文件（新增 {sum(1 for r in rows if r[5]=='新增')} · 既有 {sum(1 for r in rows if r[5]=='既有')}）。\n")
    f.write("> 四段链内容逐字取自原文；原文未载者显式标注，未作推理补全。\n\n")
    f.write("| 医案 | 患者 | 出处 | 溯源行 | 文件 | 批次 |\n")
    f.write("|------|------|------|--------|------|------|\n")
    for r in rows:
        f.write(f"| {r[0][:30]} | {r[1][:26]} | {r[2][:24]} | {r[3]} | `{r[4]}` | {r[5]} |\n")
    f.write("\n> 检索：失眠/心悸/多梦等主诉 → 查本表定位证型 → Read 对应医案文件。\n")
print("index rows =", len(rows))
