#!/usr/bin/env python3
"""
build_writeup.py — gabungkan semua writeup per anggota jadi satu WRITEUP.md,
mengikuti gaya template (banner + tabel Team + Daftar Isi Challenge + tiap soal).

Struktur repo yang diharapkan (tiap anggota punya folder sendiri):

    <anggota>/<challenge>/WRITEUP.md          <- writeup (wajib)
    <anggota>/<challenge>/img/*.png           <- screenshot (opsional, ditulis "img/xxx.png")
    <anggota>/<challenge>/<solver, file soal> <- opsional

Contoh:
    nexsus404/BMN/WRITEUP.md
    nexsus404/BMN/img/01-soal.png
    sanzxcte/Ecliprime/WRITEUP.md

Header dokumen diambil dari _template/header.md (judul + banner + tabel Team).
Edit file itu tiap event. Kalau tidak ada, dipakai judul default (--event).

Metadata opsional di baris paling atas WRITEUP.md (biar tabel Daftar Isi rapi):
    <!-- category: web | points: 498 -->

Pemakaian:
    python3 build_writeup.py                 # rakit folder saat ini -> WRITEUP.md
    python3 build_writeup.py --pull          # git pull dulu, baru rakit
    python3 build_writeup.py --push          # rakit lalu commit + push
    python3 build_writeup.py --pull --push   # sinkron penuh
    python3 build_writeup.py -o GABUNGAN.md  # nama output lain
    python3 build_writeup.py --event "Techtonic-2026"        # judul kalau tak ada header.md
    python3 build_writeup.py --members sanzxcte nexsus404 x0r # atur urutan anggota
    python3 build_writeup.py --no-pagebreak                   # tanpa page-break PDF

Clone dari nol lalu rakit:
    python3 build_writeup.py --repo https://github.com/USER/REPO.git --into REPO
"""
import argparse
import os
import re
import subprocess
import sys

IMG_MD = re.compile(r"(!\[[^\]]*\]\()\s*([^)\s]+)([^)]*\))")
IMG_HTML = re.compile(r"""(<img\b[^>]*?\bsrc=["'])([^"']+)(["'])""", re.I)

SKIP_DIRS = {".git", ".github", "img", "images", "assets", "node_modules",
             "__pycache__", "_template"}
DEFAULT_EVENT = "Techtonic-2026"
HEADER_FILE = os.path.join("_template", "header.md")
PAGEBREAK = '<div style="page-break-after: always;"></div>'


def sh(args, cwd=None, check=True):
    return subprocess.run(args, cwd=cwd, check=check, text=True, capture_output=True)


def is_external(p):
    return p.startswith(("http://", "https://", "//", "#", "mailto:", "data:", "/"))


def rewrite_paths(text, prefix):
    """Tambahkan prefix (folder writeup) ke path gambar relatif."""
    def fix(m):
        pre, path, post = m.group(1), m.group(2), m.group(3)
        p = path.strip()
        if is_external(p):
            return m.group(0)
        if p.startswith("./"):
            p = p[2:]
        return f"{pre}{prefix}/{p}{post}"
    return IMG_HTML.sub(fix, IMG_MD.sub(fix, text))


def github_slug(s):
    s = s.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    return s.replace(" ", "-")


def parse_meta(text, fallback_title):
    category, points = "", ""
    m = re.search(r"<!--(.*?)-->", text, re.S)
    if m:
        for kv in re.split(r"[|,\n]", m.group(1)):
            if ":" in kv:
                k, v = kv.split(":", 1)
                k, v = k.strip().lower(), v.strip()
                if k in ("category", "kategori"):
                    category = v
                elif k in ("points", "poin", "point"):
                    points = v
    title = fallback_title
    h = re.search(r"^\s{0,3}#{1,6}\s+(.+?)\s*$", text, re.M)
    if h:
        title = re.sub(r"[`*]", "", h.group(1)).strip()
    return title, category, points


def strip_body(text):
    """Buang komentar metadata + heading judul pertama (diganti heading rakitan)."""
    text = re.sub(r"<!--.*?-->", "", text, count=1, flags=re.S)
    out, dropped = [], False
    for ln in text.splitlines():
        if not dropped and re.match(r"^\s{0,3}#{1,6}\s+", ln):
            dropped = True
            continue
        out.append(ln)
    return "\n".join(out).strip("\n")


def detect_members(root, explicit):
    if explicit:
        return explicit
    members = []
    for name in sorted(os.listdir(root)):
        d = os.path.join(root, name)
        if not os.path.isdir(d) or name in SKIP_DIRS or name.startswith("."):
            continue
        for chal in os.listdir(d):
            cd = os.path.join(d, chal)
            if os.path.isdir(cd) and any(
                os.path.isfile(os.path.join(cd, f))
                for f in ("WRITEUP.md", "writeup.md", "README.md")
            ):
                members.append(name)
                break
    return members


def find_writeups(root, members):
    items = []
    for member in members:
        mdir = os.path.join(root, member)
        if not os.path.isdir(mdir):
            continue
        for chal in sorted(os.listdir(mdir)):
            cdir = os.path.join(mdir, chal)
            if not os.path.isdir(cdir):
                continue
            for cand in ("WRITEUP.md", "writeup.md", "README.md"):
                fp = os.path.join(cdir, cand)
                if os.path.isfile(fp):
                    items.append({
                        "member": member, "chal": chal, "path": fp,
                        "reldir": os.path.relpath(cdir, root).replace(os.sep, "/"),
                    })
                    break
    return items


def build(root, out_name, members, event, pagebreak=True):
    items = find_writeups(root, members)
    if not items:
        print("[-] Tidak ada writeup ditemukan. Pastikan struktur "
              "<anggota>/<challenge>/WRITEUP.md", file=sys.stderr)
        return False

    entries = []
    for i, it in enumerate(items, 1):
        with open(it["path"], encoding="utf-8") as f:
            raw = f.read()
        title, cat, pts = parse_meta(raw, it["chal"])
        head = f"{i}. `{title}` — {cat}" if cat else f"{i}. `{title}`"
        entries.append({**it, "n": i, "title": title, "cat": cat, "pts": pts,
                        "head": head, "anchor": github_slug(head),
                        "body": rewrite_paths(strip_body(raw), it["reldir"])})

    pb = ("\n" + PAGEBREAK + "\n") if pagebreak else ""
    out = []

    # --- header dari template, atau default ---
    hpath = os.path.join(root, HEADER_FILE)
    if os.path.isfile(hpath):
        with open(hpath, encoding="utf-8") as f:
            out.append(re.sub(r"<!--.*?-->", "", f.read(), flags=re.S).strip())
    else:
        out.append(f"# Writeup {event}")
    out.append(pb)

    # --- Daftar Isi Challenge ---
    out.append("## Daftar Isi Challenge\n")
    out.append("| #   | Challenge | Kategori | Points | Solver |")
    out.append("| --- | --------- | -------- | ------ | ------ |")
    for e in entries:
        out.append(f"| {e['n']} | [`{e['title']}`](#{e['anchor']}) | "
                   f"`{e['cat'] or '-'}` | `{e['pts'] or '-'}` | {e['member']} |")
    out.append(pb)

    # --- tiap challenge ---
    for e in entries:
        out.append(f"# {e['head']}")
        meta = " · ".join(x for x in (
            f"solved by **{e['member']}**",
            f"{e['pts']} poin" if e['pts'] else "",
        ) if x)
        out.append(f"\n> {meta}\n" if meta else "")
        out.append("---\n")
        out.append(e["body"])
        out.append(pb)

    text = "\n".join(p for p in out if p is not None)
    text = re.sub(r"\n{3,}", "\n\n", text).rstrip() + "\n"
    with open(os.path.join(root, out_name), "w", encoding="utf-8") as f:
        f.write(text)

    print(f"[+] {out_name} dibuat — {len(entries)} challenge:")
    for e in entries:
        print(f"    {e['n']:>2}. {e['title']:<28} [{e['member']}]")
    return True


def main():
    ap = argparse.ArgumentParser(description="Gabungkan writeup per anggota jadi satu file.")
    ap.add_argument("-o", "--output", default="WRITEUP.md")
    ap.add_argument("--members", nargs="*")
    ap.add_argument("--dir", default=".")
    ap.add_argument("--event", default=DEFAULT_EVENT, help="judul kalau _template/header.md tak ada")
    ap.add_argument("--repo")
    ap.add_argument("--into")
    ap.add_argument("--pull", action="store_true")
    ap.add_argument("--push", action="store_true")
    ap.add_argument("--no-pagebreak", action="store_true", help="tanpa page-break PDF")
    args = ap.parse_args()

    root = args.dir
    if args.repo:
        root = args.into or os.path.splitext(os.path.basename(args.repo.rstrip("/")))[0]
        if os.path.isdir(os.path.join(root, ".git")):
            print(f"[*] {root} sudah ada, git pull...")
            sh(["git", "pull", "--ff-only"], cwd=root, check=False)
        else:
            print(f"[*] clone {args.repo} -> {root}")
            sh(["git", "clone", args.repo, root])
    elif args.pull:
        print("[*] git pull...")
        sh(["git", "pull", "--ff-only"], cwd=root, check=False)

    members = detect_members(root, args.members)
    if not members:
        print("[-] Tidak ada folder anggota terdeteksi.", file=sys.stderr)
        sys.exit(1)
    print(f"[*] Anggota: {', '.join(members)}")

    if not build(root, args.output, members, args.event, not args.no_pagebreak):
        sys.exit(1)

    if args.push:
        sh(["git", "add", args.output], cwd=root)
        if not sh(["git", "status", "--porcelain", args.output], cwd=root).stdout.strip():
            print("[*] Tidak ada perubahan, skip commit.")
            return
        sh(["git", "commit", "-m", f"build: rakit {args.output} otomatis"], cwd=root)
        r = sh(["git", "push"], cwd=root, check=False)
        msg = (r.stderr or r.stdout).strip().splitlines()
        print("[+] push:", msg[-1] if msg else "ok")


if __name__ == "__main__":
    main()
