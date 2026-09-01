"""
Media Downloader Module
Qo'llab-quvvatlanadigan platformalar: Instagram, TikTok, Pinterest, Facebook, YouTube va boshqalar.
Dasturchi: yt-dlp asosida (2GB gacha bo'lgan yuqori sifatli videolarni qo'llab-quvvatlaydi)
"""

import os
import re
import uuid
import asyncio
import logging
from typing import Optional, Dict, Any

try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except Exception:
    pass

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

logger = logging.getLogger(__name__)

# Yuklab olingan fayllar vaqtincha saqlanadigan papka
DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# URL larni aniqlash uchun regex and platformalar xaritasi
PLATFORM_PATTERNS = {
    "instagram": r"(https?://(?:www\.)?instagram\.com/(?:p|reel|tv|stories)/[a-zA-Z0-9_\-\.]+)",
    "tiktok": r"(https?://(?:(?:vt|vm|www|m)\.)?tiktok\.com/(?:@[\w\.-]+/video/\d+|[\w\.-]+|t/[\w\.-]+))",
    "pinterest": r"(https?://(?:[a-z]{2,3}\.)?pinterest\.(?:com|it|co\.uk|es|de|fr|ca|com\.au)/pin/[a-zA-Z0-9_\-\.]+|https?://pin\.it/[a-zA-Z0-9_\-\.]+)",
    "facebook": r"(https?://(?:www\.|m\.|web\.|fb\.)?(?:facebook\.com|fb\.watch)/(?:reel|videos|watch|share|[\w\.]+/videos)/[a-zA-Z0-9_\-\.\?=\&]+)",
    "youtube": r"(https?://(?:www\.|m\.)?(?:youtube\.com/(?:watch\?v=|shorts/|embed/)|youtu\.be/)[a-zA-Z0-9_\-]+)"
}

# Umumiy URL regex
URL_REGEX = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)'


def detect_platform(url: str) -> str:
    """URL qaysi platformaga tegishli ekanligini aniqlaydi."""
    for platform, pattern in PLATFORM_PATTERNS.items():
        if re.search(pattern, url, re.IGNORECASE):
            return platform
    return "other"


def extract_first_url(text: str) -> Optional[str]:
    """Matn ichidan birinchi uchragan URL manzilini ajratib oladi."""
    matches = re.findall(URL_REGEX, text)
    if matches:
        return matches[0]
    return None


def get_platform_badge(platform: str) -> str:
    """Platforma nomiga mos emoji va nom qaytaradi."""
    badges = {
        "instagram": "📸 Instagram",
        "tiktok": "🎵 TikTok",
        "pinterest": "📌 Pinterest",
        "facebook": "👥 Facebook",
        "youtube": "▶️ YouTube",
        "other": "🌐 Video Portal"
    }
    return badges.get(platform, "🌐 Video")


def _download_sync(url: str, output_template: str, max_filesize_mb: Optional[int] = None) -> Dict[str, Any]:
    """
    Sinxron ravishda yt-dlp orqali videoni yuklab oluvchi ichki funksiya.
    """
    if yt_dlp is None:
        raise RuntimeError("yt-dlp kutubxonasi o'rnatilmagan! Iltimos: pip install yt-dlp")

    if max_filesize_mb and max_filesize_mb <= 50:
        format_str = (
            f"best[filesize<{max_filesize_mb}M]/"
            f"bestvideo[filesize<{max_filesize_mb - 8}M]+bestaudio[filesize<8M]/"
            f"best[height<=720][filesize<{max_filesize_mb}M]/"
            f"best[height<=480][filesize<{max_filesize_mb}M]/"
            f"best[height<=360]/"
            f"best"
        )
    else:
        format_str = "bestvideo+bestaudio/best"

    ydl_opts = {
        'format': format_str,
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'web'],
            }
        },
        'http_headers': {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/124.0.0.0 Safari/537.36'
            ),
            'Accept-Language': 'en-US,en;q=0.9',
        },
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if info is None:
            raise ValueError("Video ma'lumotlarini olib bo'lmadi.")

        if 'entries' in info and info['entries']:
            info = info['entries'][0]

        filename = ydl.prepare_filename(info)
        
        # Fayl kengaytmasi o'zgargan bo'lsa (mp4, webm, mkv), qidirib topish
        if not os.path.exists(filename):
            base, _ = os.path.splitext(filename)
            for ext in ['.mp4', '.mkv', '.webm', '.mov', '.3gp', '.flv']:
                if os.path.exists(f"{base}{ext}"):
                    filename = f"{base}{ext}"
                    break

        return {
            "file_path": filename,
            "title": info.get("title", "Yuklangan video"),
            "duration": info.get("duration", 0),
            "width": info.get("width", None),
            "height": info.get("height", None),
            "thumbnail": info.get("thumbnail", None),
            "filesize": os.path.getsize(filename) if os.path.exists(filename) else 0,
        }


async def download_media(url: str, max_filesize_mb: Optional[int] = None) -> Dict[str, Any]:
    """
    Asinxron tarzda videoni yuklab oladi.
    """
    unique_id = uuid.uuid4().hex[:10]
    output_template = os.path.join(DOWNLOAD_DIR, f"video_{unique_id}.%(ext)s")
    
    result = await asyncio.to_thread(_download_sync, url, output_template, max_filesize_mb)
    return result
