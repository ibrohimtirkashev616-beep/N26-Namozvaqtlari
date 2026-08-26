"""
Kalkulyator modulini avtomatik tekshirish testlari.
Barcha arifmetik amallar, funksiyalar, o'zbekcha belgilar va xatolik holatlarini sinaydi.
"""

import os
import sys

# Windows konsolida emoji va unicode to'g'ri chiqishi uchun
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Script joylashgan papkani import yo'liga qo'shish
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from calculator import evaluate_math
from bot import looks_like_math_expression


def test_calculations():
    test_cases = [
        # 1. Asosiy arifmetik amallar
        ("2 + 2", True, "4"),
        ("100 - 35", True, "65"),
        ("12 * 12", True, "144"),
        ("100 / 4", True, "25"),
        ("15 // 4", True, "3"),
        ("15 % 4", True, "3"),
        ("2 ** 5", True, "32"),
        
        # 2. O'zbekcha va muqobil belgilar (x, ×, ✕, ·, ÷, :, ^, vergul)
        ("10 × 5", True, "50"),
        ("10 x 5", True, "50"),
        ("10 X 5", True, "50"),
        ("10 ✕ 5", True, "50"),
        ("10 · 5", True, "50"),
        ("100 ÷ 5", True, "20"),
        ("100 : 4", True, "25"),
        ("2 ^ 4", True, "16"),
        ("2,5 + 3,5", True, "6"),
        ("1,5 * 4", True, "6"),
        ("5 + 5 =", True, "10"),
        ("5 + 5 = ?", True, "10"),
        ("[10 + 5] * 2", True, "30"),
        
        # 3. Yashirin ko'paytirish (Implicit multiplication)
        ("2(3 + 4)", True, "14"),
        ("(2 + 3)(4 + 5)", True, "45"),
        ("2pi", True, "6.2831853072"),
        ("3e", True, "8.1548454854"),
        ("2sqrt(16)", True, "8"),
        
        # 4. Foiz va Faktorial
        ("10%", True, "0.1"),
        ("200 * 15%", True, "30"),
        ("500 + 500 * 20%", True, "600"),
        ("5!", True, "120"),
        ("0!", True, "1"),
        ("3! + 4!", True, "30"),
        
        # 5. Qavsli va murakkab ifodalar
        ("(10 + 5) * 2", True, "30"),
        ("((5 + 5) * (10 - 2)) / 4", True, "20"),
        ("-10 + 5", True, "-5"),
        ("-(10 + 5) * 2", True, "-30"),
        
        # 6. Matematik funksiyalar va doimiylar
        ("sqrt(144)", True, "12"),
        ("√144", True, "12"),
        ("√16 + √9", True, "7"),
        ("cbrt(27)", True, "3"),
        ("abs(-50)", True, "50"),
        ("round(3.7)", True, "4"),
        ("round(3.14159, 2)", True, "3.14"),
        ("pi * 2", True, "6.2831853072"),
        ("π * 2", True, "6.2831853072"),
        ("sin(pi/2)", True, "1"),
        ("sind(90)", True, "1"),
        ("cosd(60)", True, "0.5"),
        ("tand(45)", True, "1"),
        ("log(100, 10)", True, "2"),
        ("ln(e)", True, "1"),
        ("lg(1000)", True, "3"),
        ("exp(2)", True, "7.3890560989"),
        ("gcd(24, 36)", True, "12"),
        ("max(10, 25)", True, "25"),
        ("min(10, 25)", True, "10"),
        
        # 7. Xatolik holatlari
        ("10 / 0", False, "Nolga bo'lish"),
        ("sqrt(-4)", False, "Matematik xatolik"),
        ("log(-10)", False, "Matematik xatolik"),
        ("+++---", False, "Sintaktik"),
        ("__import__('os').system('dir')", False, "Ruxsat berilmagan"),
    ]

    print("🧪 Matematik kalkulyator testlari boshlandi...\n")
    passed = 0
    total = len(test_cases)

    for expr, expected_success, expected_substr in test_cases:
        success, result = evaluate_math(expr)
        is_ok = (success == expected_success) and (expected_substr in result)
        
        if is_ok:
            passed += 1
            print(f"✅ PASSED: '{expr}' ➡️ {result}")
        else:
            print(f"❌ FAILED: '{expr}' ➡️ Kutilgan: (success={expected_success}, '{expected_substr}'), Olingan: (success={success}, '{result}')")

    print(f"\n📊 Natija: {passed}/{total} ta test muvaffaqiyatli o'tdi!")
    assert passed == total, f"Ba'zi testlar o'tmadi: {passed}/{total}"


def test_bot_recognition():
    """Botning matematik ifodalarni to'g'ri ajratib olishini tekshirish."""
    test_inputs = [
        ("2 + 2", True),
        ("10 x 5", True),
        ("100 : 4", True),
        ("pi + pi", True),
        ("sin(pi/2)", True),
        ("5+5=", True),
        ("5+5=?", True),
        ("sqrt(144)", True),
        ("√144", True),
        ("5!", True),
        ("2,5 + 3,5", True),
        ("200 * 15%", True),
        ("Salom, bot qalaysan?", False),
        ("Qanday yordam bera olasan", False),
        ("test 123 abc", False),
    ]

    print("\n🔍 Bot ifodalarni aniqlash (looks_like_math_expression) testlari...\n")
    passed = 0
    total = len(test_inputs)

    for text, expected in test_inputs:
        actual = looks_like_math_expression(text)
        if actual == expected:
            passed += 1
            print(f"✅ PASSED: '{text}' ➡️ {actual}")
        else:
            print(f"❌ FAILED: '{text}' ➡️ Kutilgan: {expected}, Olingan: {actual}")

    print(f"\n📊 Bot aniqlash natijasi: {passed}/{total} ta test muvaffaqiyatli o'tdi!")
    assert passed == total, f"Aniqlash testlari o'tmadi: {passed}/{total}"


if __name__ == "__main__":
    test_calculations()
    test_bot_recognition()
