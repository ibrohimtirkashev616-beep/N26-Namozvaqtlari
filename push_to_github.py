"""
GitHub Repozitoriyasiga Loyihani Yuklash (Push) Skripti
"""

import sys
import os
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from dulwich import porcelain
from dulwich.repo import Repo

REPO_PATH = Path(__file__).resolve().parent
DEFAULT_REMOTE_URL = "https://github.com/ibrohimtirkashev616-beep/N26.git"


def push_project(token: str, remote_url: str = DEFAULT_REMOTE_URL):
    """GitHub repozitoriyasiga loyihani yuklaydi."""
    token = token.strip()
    if not token:
        print("❌ Token kiritilmadi!")
        return False

    auth_url = f"https://oauth2:{token}@github.com/ibrohimtirkashev616-beep/N26.git"

    print("📦 Fayllar tekshirilmoqda...")
    try:
        repo = Repo(str(REPO_PATH))
        
        # Barcha yangi o'zgarishlarni qo'shish
        porcelain.add(str(REPO_PATH))
        
        # Status tekshirish
        status = porcelain.status(str(REPO_PATH))
        if status.staged.get("add") or status.staged.get("modify") or status.staged.get("delete"):
            print("📝 Yangi o'zgarishlar commit qilinmoqda...")
            porcelain.commit(
                str(REPO_PATH),
                message="Update: AI HR Agent Telegram Bot files",
                author="Ibrohim <ibrohim@example.com>"
            )
            print("✅ O'zgarishlar commit qilindi.")
        else:
            print("ℹ️ Barcha fayllar allaqachon commit qilingan.")

        print(f"🚀 GitHub ga yuklanmoqda ({remote_url})...")
        
        # Push qilish
        ref = repo.head()
        print(f"Boshlang'ich commit: {ref}")
        
        try:
            porcelain.push(
                str(REPO_PATH),
                remote_location=auth_url,
                refspecs=[b"refs/heads/master:refs/heads/main"],
                force=True
            )
        except Exception as err1:
            print(f"Master->Main urinishi: {err1}, Main->Main sinab ko'rilmoqda...")
            porcelain.push(
                str(REPO_PATH),
                remote_location=auth_url,
                refspecs=[b"HEAD:refs/heads/main"],
                force=True
            )
            
        print("🎉 MUVAFFAQIYATLI YUKLANDI! (Push Success)")
        print(f"🔗 Repozitoriy: https://github.com/ibrohimtirkashev616-beep/N26")
        return True

    except Exception as e:
        print(f"❌ Yuklashda xatolik yuz berdi: {type(e)} - {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 GITHUB GA YUKLASH YORDAMCHISI")
    print(f"📌 Repozitoriy: {DEFAULT_REMOTE_URL}")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        github_token = sys.argv[1]
    else:
        github_token = input("Token: ").strip()

    push_project(github_token)
