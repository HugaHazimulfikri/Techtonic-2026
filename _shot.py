#!/usr/bin/env python3
"""
Helper screenshot bersama untuk writeup nexsus404.

Dua mode, keduanya merekam hal yang SUNGGUHAN terjadi - tidak ada teks yang
diketik ulang atau tampilan yang direka:

  terminal(...)  menjalankan perintahnya, menangkap stdout/stderr apa adanya,
                 lalu menggambar keluaran itu ke PNG bergaya terminal (Pillow).
  web(...)       memotret halaman langsung dari server target pakai Chromium
                 headless.
  web_html(...)  memotret BODY RESPONSE ASLI dari server (mis. hasil POST yang
                 tidak bisa dilakukan Chromium lewat URL). HTML-nya utuh dari
                 server, cuma disisipi <base> supaya CSS-nya tetap termuat.
"""
import os, subprocess, tempfile, textwrap
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/TTF/JetBrainsMono-Regular.ttf"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0"
BG, FG, PROMPT, CMD, JUDUL = "#0d1117", "#c9d1d9", "#3fb950", "#d29922", "#58a6ff"
UK, PAD, SPASI = 15, 22, 6


def jalankan(perintah, timeout=300):
    """Jalankan perintah sungguhan; kembalikan stdout+stderr apa adanya."""
    h = subprocess.run(perintah, shell=True, capture_output=True, text=True, timeout=timeout)
    return (h.stdout + h.stderr).rstrip("\n")


def terminal(folder, nama, judul, blok, sorot=(), lebar_maks=132):
    """blok = [(perintah, keluaran)]. sorot = kata yang diwarnai merah."""
    f = ImageFont.truetype(FONT, UK)
    fb = ImageFont.truetype(FONT, UK + 3)
    baris = [(judul, JUDUL, fb), ("", FG, f)]
    for perintah, keluaran in blok:
        for i, p in enumerate(textwrap.wrap(perintah, lebar_maks) or [""]):
            baris.append((("$ " if i == 0 else "  ") + p, CMD, f))
        for k in keluaran.split("\n"):
            for w in (textwrap.wrap(k, lebar_maks) or [""]):
                baris.append((w, "#f85149" if any(s in w for s in sorot) else FG, f))
        baris.append(("", FG, f))

    th = UK + SPASI
    lebar = max(int(ft.getlength(t)) for t, _, ft in baris) + PAD * 2
    img = Image.new("RGB", (max(lebar, 720), len(baris) * th + PAD * 2), BG)
    d = ImageDraw.Draw(img)
    for i, (t, w, ft) in enumerate(baris):
        x = PAD
        if t.startswith("$ "):
            d.text((x, PAD + i * th), "$", font=ft, fill=PROMPT)
            x += ft.getlength("$ ")
            t = t[2:]
        d.text((x, PAD + i * th), t, font=ft, fill=w)
    return _simpan(img, folder, nama)


def _chromium(url, keluar, ukuran="1100,900"):
    subprocess.run(["chromium", "--headless", "--disable-gpu", "--no-sandbox",
                    "--hide-scrollbars", f"--window-size={ukuran}",
                    f"--user-agent={UA}", f"--screenshot={keluar}", url],
                   capture_output=True, timeout=120)


def web(folder, nama, url, ukuran="1100,900"):
    """Potret halaman langsung dari server target."""
    p = _jalur(folder, nama)
    _chromium(url, p, ukuran)
    return _lapor(p)


def web_html(folder, nama, html, base, ukuran="1100,700"):
    """Potret body response ASLI dari server (untuk hasil POST)."""
    html = html.replace("<head>", f'<head><base href="{base}">', 1)
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as t:
        t.write(html)
        tmp = t.name
    p = _jalur(folder, nama)
    _chromium("file://" + tmp, p, ukuran)
    os.unlink(tmp)
    return _lapor(p)


def _jalur(folder, nama):
    """img/ selalu relatif ke direktori kerja script pemanggil (tiap script
    sudah chdir ke foldernya sendiri), BUKAN ke lokasi _shot.py - supaya
    folder soal bisa dipindah-pindah tanpa gambar nyasar."""
    d = os.path.join(os.getcwd(), "img")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, nama + ".png")


def _simpan(img, folder, nama):
    p = _jalur(folder, nama)
    img.save(p)
    return _lapor(p)


def _lapor(p):
    if os.path.exists(p):
        w, h = Image.open(p).size
        print(f"  tersimpan: {os.path.relpath(p)}  ({w}x{h})")
    else:
        print(f"  GAGAL: {p}")
    return p
