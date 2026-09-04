#!/usr/bin/env bash
# simpan.sh — simpan writeup ke GitHub dalam SATU perintah.
# Otomatis: git add -> commit -> git pull --rebase -> git push (retry kalau ketolak),
# jadi nggak perlu ngetik "git pull --rebase && git push" manual.
#
# Pakai:
#   ./simpan.sh <folder> ["pesan commit"]
#   ./simpan.sh nexsus404/Cinder "cinder solved"
#   ./simpan.sh                       # add SEMUA perubahan, pesan default
#
# Jalan dari mana pun (otomatis cd ke root repo tempat skrip ini berada).

cd "$(dirname "$0")" || exit 1

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
