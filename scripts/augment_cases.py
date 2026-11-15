#!/usr/bin/env python3
"""失眠库：为既有 01~06 证型案中的每个医案块补 证-机-方-效 四段链标准段头 + 溯源。
原则：内容逐字取自该块既有正文，不新增任何推理；溯源标注可核对出处。
"""
import re, glob, os

def parse_block(b):
    """返回 [(标签, 内容)]，保留原标签"""
    fields = []
    cur = None
    for l in b:
        st = l.strip()
        m = re.match(r"^\*\*([^*]+)\*\*[：:]?\s*(.*)$", st)
        if m:
            cur = [m.group(1).strip(), [m.group(2)] if m.group(2) else []]
            fields.append(cur)
        elif cur and st:
            cur[1].append(st)
    return [(k, "\n".join(x for x in v if x.strip())) for k, v in fields]

def get(fs, *names):
    out = []
    for k, v in fs:
        if any(k.startswith(n) for n in names):
            if v.strip(): out.append((k, v))
    return out

def render(fs, names):
    out = []
    for k, v in get(fs, *names):
        out.append(f"**{k}**：\n{v}")
    return "\n\n".join(out)

for f in sorted(glob.glob("cases/[0-9][0-9]_*.md")):
    t = open(f, encoding="utf-8").read()
    if re.search(r"^## 证\s*$", t, re.M):
        continue
    srcm = re.search(r"来源[:：]\s*(.+)", t)
    src = srcm.group(1).strip() if srcm else "（未标注）"
    src = src.strip("《》")
    lines = t.split("\n")
    idxs = [i for i, l in enumerate(lines) if re.match(r"^##\s*医案[一二三四五六七八九十\d]", l.strip())]
    if not idxs: continue
    out, prev = [], 0
    for k, st in enumerate(idxs):
        en = idxs[k+1] if k+1 < len(idxs) else len(lines)
        blk = lines[st:en]
        title = blk[0].strip()
        fs = parse_block(blk[1:])
        # 证：主诉 + 舌脉 + 辨证
        zheng = render(fs, ["主诉", "舌脉", "辨证"]) or "原文未载证候描述。"
        # 机：辨证块中含病机推演的部分 → 辨证块第二行起
        ji_parts = []
        for kk, v in fs:
            if kk.startswith("辨证"):
                linesv = v.split("\n")
                if len(linesv) > 1:
                    ji_parts.append("\n".join(linesv[1:]))
        ji = "\n\n".join(p for p in ji_parts if p.strip()) or "原文未单独论述病机。"
        fang = render(fs, ["治法", "方药", "加味", "用法"]) or "原文未载处方。"
        xiao = render(fs, ["疗效", "后续"]) or "未见疗效记录。"
        prov = (f"**溯源**：本篇整理自《{src}》，该书原文未随本仓库收录，"
                f"故无法给出行号；请回《{src}》对应篇目核对。")
        newblk = [title, "",
                  "## 证", "", zheng, "",
                  "## 机", "", ji, "",
                  "## 方", "", fang, "",
                  "## 效", "", xiao, "",
                  prov, "", "---", ""]
        out.extend(lines[prev:st]); out.extend(newblk); prev = en
    out.extend(lines[prev:])
    open(f, "w", encoding="utf-8").write("\n".join(out))
    print("改造:", os.path.basename(f))
