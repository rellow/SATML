# -*- coding: utf-8 -*-
# make_screenshot.py — 把文本日志渲染成终端风格 PNG 截图
# 用法: python make_screenshot.py <输入文本> <输出png> [标题]
import sys
from PIL import Image, ImageDraw, ImageFont

FONT_CJK = "C:/Windows/Fonts/msyh.ttc"
FONT_MONO = "C:/Windows/Fonts/consola.ttf"

def load_font(size):
    for p in (FONT_CJK, FONT_MONO):
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()

def render(text, out, title="Terminal — evidence"):
    lines = text.replace("\t", "    ").splitlines() or [""]
    pad_x, pad_y, title_h = 26, 22, 46
    fs = 20
    font = load_font(fs)
    tmp = Image.new("RGB", (10, 10))
    d = ImageDraw.Draw(tmp)
    max_w = max((d.textlength(l, font=font) for l in lines), default=400)
    w = int(max_w + pad_x * 2) + 4
    h = title_h + pad_y + len(lines) * (fs + 8) + pad_y
    img = Image.new("RGB", (w, h), (30, 34, 42))
    dr = ImageDraw.Draw(img)
    # 标题栏
    dr.rectangle([0, 0, w, title_h], fill=(22, 25, 31))
    for i, c in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
        dr.ellipse([18 + i * 26, 15, 34 + i * 26, 31], fill=c)
    tf = load_font(17)
    tw = dr.textlength(title, font=tf)
    dr.text(((w - tw) / 2, 13), title, font=tf, fill=(160, 168, 180))
    # 正文
    y = title_h + pad_y
    for l in lines:
        color = (220, 225, 232)
        if l.lstrip().startswith(("[+]", "[!!!]", "[结论]")):
            color = (80, 220, 130)
        elif l.lstrip().startswith(("[-]", "[!]")):
            color = (255, 120, 110)
        elif l.lstrip().startswith(("[步骤", "[证据", "[i]", "[*]")):
            color = (120, 180, 255)
        dr.text((pad_x, y), l, font=font, fill=color)
        y += fs + 8
    img.save(out)
    print("[+]", out)

if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    title = sys.argv[3] if len(sys.argv) > 3 else "Terminal — evidence"
    render(open(src, encoding="utf-8").read(), out, title)
