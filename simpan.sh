#!/usr/bin/env bash
# simpan.sh — simpan writeup ke GitHub.
#
#   ./simpan.sh                      -> add SEMUA perubahan, commit+pull-rebase+push (sekali)
#   ./simpan.sh <folder> ["pesan"]   -> cuma folder itu (sekali)
#   ./simpan.sh --watch [interval]   -> NONGKRONG: taruh/edit writeup di folder -> otomatis
#                                       ke-commit + push tiap ada perubahan. Ctrl+C berhenti.
#
# Semua otomatis pull --rebase dulu, jadi nggak kena "fetch first".

cd "$(dirname "$0")" || exit 1

# ---------------- mode watch (auto-push tiap ada perubahan) ----------------
if [ "$1" = "--watch" ]; then
  interval="${2:-15}"
  echo "[*] AUTO-SIMPAN aktif, cek tiap ${interval}s."
  echo "    Taruh/edit writeup di folder kamu -> otomatis ke-push. Ctrl+C untuk berhenti."
  while true; do
    git pull --rebase --autostash >/dev/null 2>&1 || true
    if [ -n "$(git status --porcelain)" ]; then
      git add -A
      git commit -m "auto-simpan $(date +%H:%M:%S)" >/dev/null 2>&1
      ok=""
      for i in 1 2 3; do
        if git push >/dev/null 2>&1; then ok=1; break; fi
        git pull --rebase --autostash >/dev/null 2>&1 || true
      done
      if [ -n "$ok" ]; then
        echo "[+] $(date +%H:%M:%S) perubahan disimpan & di-push"
      else
        echo "[-] $(date +%H:%M:%S) push gagal, dicoba lagi siklus berikut"
      fi
    else
      printf "."
    fi
    sleep "$interval"
  done
  exit 0
fi

# ---------------- mode sekali ----------------
target="${1:-.}"
msg="${2:-update writeup}"

echo "[*] git add $target"
git add "$target" || { echo "[-] git add gagal (folder ada?)"; exit 1; }

if git diff --cached --quiet; then
  echo "[*] tidak ada perubahan baru untuk di-commit (lanjut sinkron + push commit lama)."
else
  git commit -m "$msg" >/dev/null && echo "[+] commit: $msg"
fi

for i in 1 2 3; do
  git pull --rebase --autostash >/dev/null 2>&1 || true
  if git push 2>/dev/null; then
    echo "[+] tersimpan & ter-push ke GitHub."
    exit 0
  fi
  echo "[*] origin barusan berubah, sinkron ulang & coba lagi ($i/3)..."
  sleep 1
done

echo "[-] gagal push setelah 3x. Coba manual: git pull --rebase && git push"
exit 1
