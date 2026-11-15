#!/usr/bin/env python3
"""失眠库：把 like-insomnia.md 的《李可医案处方集》医案实录落盘为独立医案文件（证-机-方-效四段链 + 溯源），
并为既有 01~06 证型案补标准四段链段头与溯源。
原则：内容逐字取自原文，不编造；溯源给出行号。
"""
import re, glob, os, json, hashlib

SRC = "like-insomnia.md"
lines = open(SRC, encoding="utf-8").read().split("\n")

# ---------- 1) 抽取李可医案 ----------
starts = []
for i, l in enumerate(lines, 1):
    if re.match(r"^##\s*医案\d+[：:]", l.strip()):
        starts.append((i, l.strip()))
cases = []
for idx, (i, title) in enumerate(starts):
    end = starts[idx+1][0] if idx+1 < len(starts) else len(lines)+1
    blk = lines[i-1:end-1]
    def g(key):
        for b in blk:
            m = re.match(r"^\*\*" + re.escape(key) + r"\*\*[：:]\s*(.*)$", b.strip())
            if m: return m.group(1).strip()
        return ""
    # 编按可能跨行
    bianan = ""
    for k, b in enumerate(blk):
        if b.strip().startswith("**编按**"):
            bianan = b.strip().replace("**编按**：", "").strip()
            break
    src = g("来源"); pat = g("患者"); sym = g("症状")
    zheng = g("辨证"); fang = g("处方"); dose = g("剂量"); eff = g("疗效")
    cases.append(dict(line=i, title=title.replace("## ", ""), src=src, pat=pat, sym=sym,
                      zheng=zheng, fang=fang, dose=dose, eff=eff, bianan=bianan,
                      bianan_line=next((i + k for k, b in enumerate(blk) if b.strip().startswith("**编按**")), i)))

os.makedirs("cases", exist_ok=True)
def seg(t, v, miss):
    return f"## {t}\n\n{v if v else miss}\n"

rows = []
for c in cases:
    d = hashlib.md5((c["title"] + c["pat"]).encode()).hexdigest()[:6]
    no = re.match(r"医案(\d+)", c["title"]).group(1)
    fn = f"li_{no}_{d}.md"
    md = f"""# 医案：{c['title']}

**患者**：{c['pat']}
**主诉/症状**：{c['sym']}
**出处**：《李可医案处方集》
**溯源**：`{SRC}` 搜"{c['title']}"（第 {c['line']} 行）

{seg("证", c["zheng"], "原文未载辨证。")}
{seg("机", c["bianan"] or "原文未单独论述病机。", "原文未单独论述病机。")}
{seg("方", (f"**处方**：{c['fang']}\n\n**剂量**：{c['dose']}" if c['fang'] or c['dose'] else ""), "原文未载处方。")}
{seg("效", c["eff"] if c["eff"] and c["eff"] != "未详述" else "未见疗效记录。", "未见疗效记录。")}

## 原文摘录

> **{c['title']}**
>
> 患者：{c['pat']}
>
> 症状：{c['sym']}
>
> 辨证：{c['zheng']}
>
> 处方：{c['fang']}
>
> 剂量：{c['dose']}
>
> 疗效：{c['eff']}
>
> 编按：{c['bianan']}
"""
    open(f"cases/{fn}", "w", encoding="utf-8").write(md)
    rows.append((c["title"], c["pat"], c["line"], fn))

print(f"李可医案落盘 {len(rows)} 篇", file=__import__("sys").stderr)
json.dump(rows, open("scripts/like_cases.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
