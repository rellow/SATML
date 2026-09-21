#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""render_evidence_png.py — 把真实复现日志片段渲染成终端风格 PNG（内容全部来自实机日志，未做内容改写）。"""
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "evidence")

FONT_CANDIDATES = [
    ("C:/Windows/Fonts/msjh.ttc", 17),
    ("C:/Windows/Fonts/msyh.ttc", 17),
    ("C:/Windows/Fonts/Deng.ttf", 17),
    ("C:/Windows/Fonts/consola.ttf", 17),
]


def load_font():
    for path, size in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def render(title, text, outname, max_width=100):
    font = load_font()
    lines = []
    for ln in (title, *text.splitlines()):
        if len(ln) <= max_width:
            lines.append(ln)
        else:
            lines.extend(textwrap.wrap(ln, max_width, replace_whitespace=False) or [""])
    pad, lh = 24, 26
    w = 1400
    h = pad * 2 + lh * (len(lines) + 1)
    img = Image.new("RGB", (w, h), (30, 30, 30))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, pad + lh // 2 + 18], fill=(45, 45, 48))
    d.ellipse([16, 16, 28, 28], fill=(255, 95, 86))
    d.ellipse([36, 16, 48, 28], fill=(255, 189, 46))
    d.ellipse([56, 16, 68, 28], fill=(39, 201, 63))
    d.text((90, 12), title.splitlines()[0], font=font, fill=(200, 200, 200))
    y = pad + lh // 2 + 26
    for ln in lines[1:]:
        color = (204, 204, 204)
        if ln.startswith("$") or ln.startswith("[+]"):
            color = (120, 220, 120)
        elif ln.startswith("[-]") or "FAIL" in ln:
            color = (255, 120, 120)
        elif ln.startswith("[*]") or ln.startswith("[i]"):
            color = (120, 180, 255)
        d.text((pad, y), ln, font=font, fill=color)
        y += lh
    path = os.path.join(OUT, outname)
    img.save(path)
    print("saved", path)


def read_excerpt(path, start_pat, n_lines):
    """从真实日志中截取片段（原文引用，不改写）。"""
    lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    for i, ln in enumerate(lines):
        if start_pat in ln:
            return "\n".join(lines[i:i + n_lines])
    return "\n".join(lines[:n_lines])


if __name__ == "__main__":
    main_log = os.path.join(OUT, "exploit_run.log")
    root_log = os.path.join(OUT, "2026-07-29_提权root证据.log")
    render("exploit — mDNS 发现与零凭据握手（U-03）",
           read_excerpt(main_log, "阶段 0", 16), "01_发现与握手.png")
    render("exploit — cmd 365 Lua 注入 → system 反连 shell（U-30）",
           read_excerpt(main_log, "阶段 3 取证 A", 20), "02_system身份shell.png")
    render("exploit — mtk-su CVE-2020-0069 提权 root（U-20）",
           read_excerpt(root_log, "mtk-su -c id", 16), "03_提权root.png")
