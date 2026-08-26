"""
Xavfsiz matematik ifodalarni hisoblash moduli.
Python'ning `ast` (Abstract Syntax Tree) moduli yordamida ishlaydi,
bu esa xavfli buyruqlar (masalan: os.system, __import__) bajarilishining oldini oladi.
"""

import ast
import operator
import math
import re
from typing import Tuple, Union


# Ruxsat etilgan matematik amallar
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# Ruxsat etilgan matematik funksiyalar
MATH_FUNCTIONS = {
    'sqrt': math.sqrt,
    'cbrt': getattr(math, 'cbrt', lambda x: x ** (1/3)),
    'abs': abs,
    'round': round,
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'sind': lambda x: math.sin(math.radians(x)),
    'cosd': lambda x: math.cos(math.radians(x)),
    'tand': lambda x: math.tan(math.radians(x)),
    'asin': math.asin,
    'acos': math.acos,
    'atan': math.atan,
    'sinh': math.sinh,
    'cosh': math.cosh,
    'tanh': math.tanh,
    'log': math.log,
    'ln': math.log,
    'log10': math.log10,
    'lg': math.log10,
    'log2': math.log2,
    'exp': math.exp,
    'ceil': math.ceil,
    'floor': math.floor,
    'factorial': math.factorial,
    'fact': math.factorial,
    'gcd': math.gcd,
    'lcm': getattr(math, 'lcm', lambda a, b: abs(int(a * b)) // math.gcd(int(a), int(b))),
    'pow': pow,
    'min': min,
    'max': max,
    'rad': math.radians,
    'radians': math.radians,
    'deg': math.degrees,
    'degrees': math.degrees,
}

CONSTANTS = {
    'pi': math.pi,
    'e': math.e,
    'tau': getattr(math, 'tau', math.pi * 2),
}


class SafeCalculator:
    """Xavfsiz matematik ifoda baholovchi sinf."""

    def preprocess_expression(self, expr: str) -> str:
        """Kiritilgan ifodani tozalash va to'g'ri Python sintaksisiga keltirish."""
        s = expr.strip()
        
        # Oxiridagi '=' yoki '?' belgilarini olib tashlash (masalan: "5 + 5 = " -> "5 + 5")
        s = re.sub(r'[\s=\?]+$', '', s).strip()

        # Kvadrat qavslarni yumaloq qavslarga almashtirish: [10 + 5] -> (10 + 5)
        s = s.replace('[', '(').replace(']', ')')
        s = s.replace('{', '(').replace('}', ')')

        # Maxsus belgilar
        s = s.replace('π', 'pi')
        # √144 -> sqrt(144), √(16) -> sqrt(16)
        s = re.sub(r'√\s*(\d+(?:\.\d+)?)', r'sqrt(\1)', s)
        s = re.sub(r'√\s*(\([^\(\)]+\))', r'sqrt\1', s)
        s = s.replace('√', 'sqrt')

        # Ko'paytirish va bo'lish belgilari
        s = s.replace('×', '*').replace('✕', '*').replace('·', '*')
        s = s.replace('÷', '/').replace(':', '/')
        s = s.replace('^', '**')

        # 'x' yoki 'X' harflarini faqat ko'paytirish amali bo'lganda '*' ga almashtirish (exp, max, min buzilmaydi)
        s = re.sub(r'(\d+|\))\s*[xX]\s*(\d+|\(|\bpi\b|\be\b|[a-zA-Z])', r'\1 * \2', s)
        s = re.sub(r'(\bpi\b|\be\b)\s*[xX]\s*(\d+|\(|\bpi\b|\be\b|[a-zA-Z])', r'\1 * \2', s)

        # O'nlik kasr vergulini nuqtaga almashtirish (2,5 -> 2.5)
        s = re.sub(r'(\d+),(\d+)', r'\1.\2', s)

        # Foiz hisoblash: "200 * 15%" -> "200 * (15/100)", "50%" -> "(50/100)"
        s = re.sub(r'(\d+(?:\.\d+)?|\))\s*%(?!\s*\d)', r'(\1/100)', s)

        # Faktorial belgisi: "5!" -> "factorial(5)", "(2+3)!" -> "factorial(2+3)"
        while re.search(r'(\d+(?:\.\d+)?|\([^\(\)]+\))!', s):
            s = re.sub(r'(\d+(?:\.\d+)?|\([^\(\)]+\))!', r'factorial(\1)', s)

        # Yashirin ko'paytirish (Implicit multiplication):
        # 2(3) -> 2*(3)
        s = re.sub(r'(\d+)\s*\(', r'\1*(', s)
        # (3)2 -> (3)*2
        s = re.sub(r'\)\s*(\d+)', r')*\1', s)
        # (2)(3) -> (2)*(3)
        s = re.sub(r'\)\s*\(', r')*(', s)

        # 2pi -> 2*pi, 2sqrt(9) -> 2*sqrt(9), 2e -> 2*e
        func_and_consts = '|'.join(list(CONSTANTS.keys()) + list(MATH_FUNCTIONS.keys()))
        s = re.sub(rf'(\d+)\s*({func_and_consts})\b', r'\1*\2', s)
        s = re.sub(rf'\b(pi|e|tau)\b\s*(\d+|{func_and_consts})\b', r'\1*\2', s)
        s = re.sub(rf'\)\s*({func_and_consts})\b', r')*\1', s)

        return s

    def _eval_node(self, node: ast.AST) -> Union[int, float]:
        """AST tugunini rekursiv hisoblash."""
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Noto'g'ri qiymat: {node.value}")

        # Python 3.7 va undan oldingi versiyalar uchun
        elif hasattr(ast, 'Num') and isinstance(node, ast.Num):
            return node.n

        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op_type = type(node.op)
            
            if op_type in OPERATORS:
                if op_type in (ast.Div, ast.FloorDiv, ast.Mod) and right == 0:
                    raise ZeroDivisionError("Nolga bo'lish mumkin emas!")
                
                if op_type == ast.Pow:
                    if abs(right) > 1000 or (abs(left) > 1000 and right > 10):
                        raise OverflowError("Daraja qiymati juda katta!")
                
                return OPERATORS[op_type](left, right)
            raise ValueError(f"Qo'llab-quvvatlanmaydigan amal: {op_type.__name__}")

        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            op_type = type(node.op)
            if op_type in OPERATORS:
                return OPERATORS[op_type](operand)
            raise ValueError(f"Qo'llab-quvvatlanmaydigan belgi: {op_type.__name__}")

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in MATH_FUNCTIONS:
                func = MATH_FUNCTIONS[node.func.id]
                args = [self._eval_node(arg) for arg in node.args]
                return func(*args)
            raise ValueError("Ruxsat berilmagan funksiya chaqiruvi!")

        elif isinstance(node, ast.Name):
            if node.id in CONSTANTS:
                return CONSTANTS[node.id]
            raise ValueError(f"Noma'lum o'zgaruvchi: {node.id}")

        else:
            raise TypeError(f"Ruxsat berilmagan ifoda elementi: {type(node).__name__}")

    def calculate(self, expression: str) -> Tuple[bool, str]:
        """
        Matematik ifodani hisoblaydi.
        
        Qaytaradi:
            (success: bool, result_or_error: str)
        """
        if not expression or not expression.strip():
            return False, "Ifoda bo'sh bo'lishi mumkin emas!"

        try:
            clean_expr = self.preprocess_expression(expression)
            tree = ast.parse(clean_expr, mode='eval')
            raw_result = self._eval_node(tree.body)

            if isinstance(raw_result, (int, float)):
                if isinstance(raw_result, float):
                    if math.isnan(raw_result):
                        return False, "❌ Natija aniqlanmagan (NaN)!"
                    if math.isinf(raw_result):
                        return False, "❌ Natija cheksiz (Infinity)!"
                    
                    rounded = round(raw_result, 10)
                    if rounded.is_integer():
                        formatted = str(int(rounded))
                    else:
                        formatted = f"{rounded:.10f}".rstrip('0').rstrip('.')
                        if not formatted or formatted == "-0":
                            formatted = "0"
                else:
                    formatted = str(raw_result)

                # Natija uzunligini cheklash
                if len(formatted) > 500:
                    formatted = f"{float(raw_result):.8e}"

                return True, formatted
            else:
                return False, "❌ Noto'g'ri natija turi!"

        except ZeroDivisionError:
            return False, "❌ Nolga bo'lish mumkin emas!"
        except OverflowError:
            return False, "❌ Natija juda katta (cheksizlik)!"
        except ValueError as e:
            err_msg = str(e).lower()
            if "math domain error" in err_msg:
                return False, "❌ Matematik xatolik: Funksiya aniqlanish sohasidan tashqarida (masalan: manfiy sondan ildiz yoki manfiy/nol logarifmi)!"
            elif "factorial" in err_msg:
                return False, "❌ Faktorial faqat manfiy bo'lmagan butun sonlar uchun hisoblanadi!"
            return False, f"❌ Qiymat xatoligi: {str(e)}"
        except (SyntaxError, TypeError):
            return False, "❌ Sintaktik xatolik! Ifodani to'g'ri kiriting.\nMisol: `(15 + 5) * 2`"
        except Exception as e:
            return False, f"❌ Xatolik yuz berdi: {str(e)}"


# Yordamchi qulay ob'ekt va funksiya
calculator = SafeCalculator()

def evaluate_math(expr: str) -> Tuple[bool, str]:
    return calculator.calculate(expr)
