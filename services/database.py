"""
SQLite asosidagi ma'lumotlar bazasi boshqaruvi (aiosqlite)
"""

import aiosqlite
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import config

logger = logging.getLogger(__name__)


async def init_db():
    """Baza jadvallarini yaratish."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                full_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                vacancy_key TEXT NOT NULL,
                vacancy_title TEXT NOT NULL,
                experience_text TEXT,
                salary_expectation TEXT,
                portfolio_url TEXT,
                resume_file_id TEXT,
                resume_file_name TEXT,
                resume_text TEXT,
                ai_score INTEGER DEFAULT 0,
                ai_status TEXT,
                ai_summary TEXT,
                ai_report_json TEXT,
                hr_status TEXT DEFAULT 'NEW',
                hr_decision_by TEXT,
                hr_note TEXT,
                group_message_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await db.commit()
    logger.info("Ma'lumotlar bazasi muvaffaqiyatli ishga tushirildi.")


async def save_user(user_id: int, username: Optional[str], first_name: Optional[str], last_name: Optional[str]):
    """Foydalanuvchini bazaga saqlash yoki yangilash."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute("""
            INSERT INTO users (user_id, username, first_name, last_name, last_active)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                username=excluded.username,
                first_name=excluded.first_name,
                last_name=excluded.last_name,
                last_active=CURRENT_TIMESTAMP
        """, (user_id, username, first_name, last_name))
        await db.commit()


async def create_application(
    user_id: int,
    username: Optional[str],
    full_name: str,
    phone: str,
    vacancy_key: str,
    vacancy_title: str,
    experience_text: str,
    salary_expectation: str,
    portfolio_url: str,
    resume_file_id: Optional[str],
    resume_file_name: Optional[str],
    resume_text: str,
    ai_result: Dict[str, Any]
) -> int:
    """Yangi arizani bazaga saqlash va uning ID sini qaytarish."""
    ai_score = ai_result.get("match_score", 0)
    ai_status = ai_result.get("status", "QISMAN MOS")
    ai_summary = ai_result.get("summary", "")
    ai_report_json = json.dumps(ai_result, ensure_ascii=False)

    async with aiosqlite.connect(config.DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO applications (
                user_id, username, full_name, phone,
                vacancy_key, vacancy_title, experience_text,
                salary_expectation, portfolio_url,
                resume_file_id, resume_file_name, resume_text,
                ai_score, ai_status, ai_summary, ai_report_json,
                hr_status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'NEW', CURRENT_TIMESTAMP)
        """, (
            user_id, username, full_name, phone,
            vacancy_key, vacancy_title, experience_text,
            salary_expectation, portfolio_url,
            resume_file_id, resume_file_name, resume_text,
            ai_score, ai_status, ai_summary, ai_report_json
        ))
        await db.commit()
        return cursor.lastrowid


async def update_application_group_message(app_id: int, message_id: int):
    """Guruhdagi xabar ID sini saqlash."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute("""
            UPDATE applications
            SET group_message_id = ?
            WHERE id = ?
        """, (message_id, app_id))
        await db.commit()


async def get_application_by_id(app_id: int) -> Optional[Dict[str, Any]]:
    """Arizani ID bo'yicha olish."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM applications WHERE id = ?", (app_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                data = dict(row)
                if data.get("ai_report_json"):
                    try:
                        data["ai_report"] = json.loads(data["ai_report_json"])
                    except Exception:
                        data["ai_report"] = {}
                return data
            return None


async def get_user_applications(user_id: int) -> List[Dict[str, Any]]:
    """Foydalanuvchining barcha arizalarini olish."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM applications
            WHERE user_id = ?
            ORDER BY id DESC
        """, (user_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def update_application_status(
    app_id: int,
    status: str,
    decision_by: str,
    note: Optional[str] = None
) -> bool:
    """HR qarorini saqlash (INVITED, REJECTED, RESERVED)."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute("""
            UPDATE applications
            SET hr_status = ?, hr_decision_by = ?, hr_note = ?
            WHERE id = ?
        """, (status, decision_by, note, app_id))
        await db.commit()
        return True


async def get_statistics() -> Dict[str, Any]:
    """HR uchun umumiy statistika."""
    async with aiosqlite.connect(config.DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM applications") as c:
            total_apps = (await c.fetchone())[0]
            
        async with db.execute("SELECT COUNT(*) FROM applications WHERE ai_status = 'MOS KELDI'") as c:
            qualified = (await c.fetchone())[0]
            
        async with db.execute("SELECT COUNT(*) FROM applications WHERE ai_status = 'QISMAN MOS'") as c:
            partially_qualified = (await c.fetchone())[0]
            
        async with db.execute("SELECT COUNT(*) FROM applications WHERE ai_status = 'MOS KELMADI'") as c:
            rejected_ai = (await c.fetchone())[0]
            
        async with db.execute("SELECT COUNT(*) FROM applications WHERE hr_status = 'INVITED'") as c:
            invited = (await c.fetchone())[0]
            
        async with db.execute("SELECT COUNT(*) FROM applications WHERE hr_status = 'REJECTED'") as c:
            rejected_hr = (await c.fetchone())[0]

        async with db.execute("SELECT COUNT(*) FROM users") as c:
            total_users = (await c.fetchone())[0]
            
        return {
            "total_apps": total_apps,
            "qualified": qualified,
            "partially_qualified": partially_qualified,
            "rejected_ai": rejected_ai,
            "invited": invited,
            "rejected_hr": rejected_hr,
            "total_users": total_users
        }
