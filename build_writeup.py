#!/usr/bin/env python3
"""
build_writeup.py — gabungkan semua writeup per anggota jadi satu WRITEUP.md,
mengikuti gaya template (banner + tabel Team + Daftar Isi Challenge + tiap soal).

Struktur repo yang diharapkan (tiap anggota punya folder sendiri):

    <anggota>/<challenge>/WRITEUP.md          <- writeup (wajib)
    <anggota>/<challenge>/img/*.png           <- screenshot (opsional, ditulis "img/xxx.png")
    <anggota>/<challenge>/<solver, file soal> <- opsional

Header dokumen diambil dari _template/header.md (judul + banner + tabel Team).
Metadata opsional di baris atas WRITEUP.md: <!-- category: web | points: 498 -->

Pemakaian:
    python3 build_writeup.py                 # rakit sekali -> WRITEUP.md
    python3 build_writeup.py --push          # rakit lalu commit + push
    python3 build_writeup.py --pull --push   # sinkron penuh sekali jalan

    # MODE WATCH: jalanin SEKALI, dia nongkrong; tiap ada push baru dari temen,
    # otomatis pull -> rakit ulang -> push. Ctrl+C untuk berhenti.
    python3 build_writeup.py --watch                 # cek tiap 20 detik
    python3 build_writeup.py --watch --interval 10   # cek tiap 10 detik

    # lain-lain
    python3 build_writeup.py -o GABUNGAN.md
    python3 build_writeup.py --event "Techtonic-2026"
    python3 build_writeup.py --members sanzxcte nexsus404 x0r
    python3 build_writeup.py --no-pagebreak
    python3 build_writeup.py --repo https://github.com/USER/REPO.git --into REPO --watch
"""
import argparse
import os
import re
import subprocess
import sys
import time

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
    text = re.sub(r"<!--.*?-->", "", text, count=1, flags=re.S)
    out, dropped = [], False
    for ln in text.splitlines():
        if not dropped and re.match(r"^\s{0,3}#{1,6}\s+", ln):
            dropped = True
            continue
        out.append(ln)
    return "\n".join(out).strip("\n")


PREFER = ("WRITEUP.md", "writeup.md", "Writeup.md", "README.md", "readme.md")


def writeup_in(cdir):
    """File writeup di folder soal: prioritas WRITEUP.md/README.md, kalau tidak
    ada pakai file .md apa pun (jadi nama bebas)."""
    for cand in PREFER:
        if os.path.isfile(os.path.join(cdir, cand)):
            return cand
    try:
        mds = sorted(f for f in os.listdir(cdir) if f.lower().endswith(".md"))
    except OSError:
        return None
    return mds[0] if mds else None


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
            if os.path.isdir(cd) and writeup_in(cd):
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
            wp = writeup_in(cdir)
            if wp:
                items.append({
                    "member": member, "chal": chal,
                    "path": os.path.join(cdir, wp),
                    "reldir": os.path.relpath(cdir, root).replace(os.sep, "/"),
                })
    return items


def build(root, out_name, members, event, pagebreak=True):
    items = find_writeups(root, members)
    if not items:
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
    hpath = os.path.join(root, HEADER_FILE)
    if os.path.isfile(hpath):
        with open(hpath, encoding="utf-8") as f:
            out.append(re.sub(r"<!--.*?-->", "", f.read(), flags=re.S).strip())
    else:
        out.append(f"# Writeup {event}")
    out.append(pb)

    out.append("## Daftar Isi Challenge\n")
    out.append("| #   | Challenge | Kategori | Points | Solver |")
    out.append("| --- | --------- | -------- | ------ | ------ |")
    for e in entries:
        out.append(f"| {e['n']} | [`{e['title']}`](#{e['anchor']}) | "
                   f"`{e['cat'] or '-'}` | `{e['pts'] or '-'}` | {e['member']} |")
    out.append(pb)

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

    text = re.sub(r"\n{3,}", "\n\n", "\n".join(out)).rstrip() + "\n"
    with open(os.path.join(root, out_name), "w", encoding="utf-8") as f:
        f.write(text)
    return entries


# ------------------------- git helpers -------------------------
def git_head(root, ref="HEAD"):
    return sh(["git", "rev-parse", ref], cwd=root, check=False).stdout.strip()


def current_branch(root):
    b = sh(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=root, check=False).stdout.strip()
    return b or "main"


def push_output(root, out_name):
    """commit + push out_name; return True kalau ada perubahan yang dipush."""
    sh(["git", "add", out_name], cwd=root)
    if not sh(["git", "status", "--porcelain", out_name], cwd=root).stdout.strip():
        return False
    sh(["git", "commit", "-m", f"build: rakit {out_name} otomatis"], cwd=root)
    r = sh(["git", "push"], cwd=root, check=False)
    if r.returncode != 0:                      # kalau ketolak, sinkron lalu coba lagi
        sh(["git", "pull", "--rebase"], cwd=root, check=False)
        r = sh(["git", "push"], cwd=root, check=False)
    return r.returncode == 0


def sync_once(root, args, quiet=False):
    """detect -> build -> (push). return jumlah challenge, atau -1 kalau kosong."""
    members = detect_members(root, args.members)
    if not members:
        if not quiet:
            print("[-] belum ada writeup di folder anggota manapun.")
        return -1
    entries = build(root, args.output, members, args.event, not args.no_pagebreak)
    if not entries:
        return -1
    print(f"[*] Anggota: {', '.join(members)}")
    print(f"[+] {args.output} — {len(entries)} challenge:")
    for e in entries:
        print(f"    {e['n']:>2}. {e['title']:<28} [{e['member']}]")
    if args.push or args.watch:
        if push_output(root, args.output):
            print("[+] pushed.")
        else:
            print("[*] tidak ada perubahan pada output, skip push.")
    return len(entries)


def commit_push_all(root, msg):
    """Stage SEMUA perubahan (writeup mentah + gambar + WRITEUP.md), commit, push
    dengan retry. return True kalau ada yang di-commit."""
    sh(["git", "add", "-A"], cwd=root, check=False)
    if sh(["git", "diff", "--cached", "--quiet"], cwd=root, check=False).returncode == 0:
        return False                              # tidak ada yang berubah
    sh(["git", "commit", "-m", msg], cwd=root, check=False)
    for _ in range(3):
        if sh(["git", "push"], cwd=root, check=False).returncode == 0:
            return True
        sh(["git", "pull", "--rebase", "--autostash"], cwd=root, check=False)
    return True


def watch_loop(root, args):
    br = current_branch(root)
    print(f"[*] MODE WATCH aktif di branch '{br}', cek tiap {args.interval}s. "
          f"Ctrl+C untuk berhenti.")
    print("    (taruh/edit file writeup di folder anggota -> otomatis push + rakit)")
    first = True
    while True:
        try:
            if not first:
                time.sleep(args.interval)
            first = False
            # 1) tarik update dari anggota lain (autostash lindungi kerjaan lokal)
            sh(["git", "fetch", "origin", br], cwd=root, check=False)
            sh(["git", "pull", "--rebase", "--autostash"], cwd=root, check=False)
            # 2) rakit ulang WRITEUP.md dari semua writeup yang ada
            members = detect_members(root, args.members)
            if members:
                build(root, args.output, members, args.event, not args.no_pagebreak)
            # 3) commit + push SEMUA (writeup mentah yang baru ditaruh + WRITEUP.md)
            if commit_push_all(root, "auto-sync: writeup + rakit WRITEUP.md"):
                n = len(find_writeups(root, members)) if members else 0
                print(f"\n[+] tersinkron & ter-push ({n} challenge di {args.output}).")
            else:
                print(".", end="", flush=True)  # heartbeat: tidak ada perubahan
        except KeyboardInterrupt:
            print("\n[*] watch dihentikan.")
            break


def main():
    ap = argparse.ArgumentParser(description="Gabungkan writeup per anggota jadi satu file.")
    ap.add_argument("-o", "--output", default="WRITEUP.md")
    ap.add_argument("--members", nargs="*")
    ap.add_argument("--dir", default=".")
    ap.add_argument("--event", default=DEFAULT_EVENT)
    ap.add_argument("--repo")
    ap.add_argument("--into")
    ap.add_argument("--pull", action="store_true")
    ap.add_argument("--push", action="store_true")
    ap.add_argument("--watch", action="store_true", help="nongkrong; auto rakit+push tiap ada push baru")
    ap.add_argument("--interval", type=int, default=20, help="detik antar cek di mode watch (default 20)")
    ap.add_argument("--no-pagebreak", action="store_true")
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

    if args.watch:
        watch_loop(root, args)
    else:
        n = sync_once(root, args)
        if n < 0:
            sys.exit(1)


if __name__ == "__main__":
    main()
