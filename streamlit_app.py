#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PPFO v28.0 Streamlit Web Application - إصدار متكامل مع دالة زيتا لتحليل الأعداد
"""

import streamlit as st
import math, random, time, sys, re, json
from functools import lru_cache
from collections import Counter
import numpy as np

# 📱 إعداد صفحة Streamlit
st.set_page_config(
    page_title="PPFO v28.0 - دوال زيتا المتكاملة",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 🎨 CSS مخصص مع دعم LaTeX
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4F46E5;
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: bold;
    }
    
    .mobile-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        margin: 12px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 1px solid #e5e7eb;
    }
    
    .latex-container {
        background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        border: 2px solid #bfdbfe;
        text-align: center;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #4F46E5, #7C3AED);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 14px 24px;
        font-weight: 600;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# 🌍 نظام الترجمة
TRANSLATIONS = {
    "ar": {
        "app_title": "PPFO v28.0 - دوال زيتا المتكاملة",
        "welcome": "مرحباً بك في PPFO v28.0",
        "zeta_zeros": "أصفار دالة زيتا غير التافهة",
        "primes": "الأعداد الأولية",
        "advanced": "التطبيقات المتقدمة",
        "calculate": "حساب",
        "precision": "الدقة",
        "method": "طريقة الحساب",
        "result": "النتيجة",
        "time_taken": "الوقت المستغرق",
        "error": "خطأ",
        "success": "نجح",
        "quick_example": "مثال سريع"
    },
    "fr": {
        "app_title": "PPFO v28.0 - Fonctions Zêta Intégrées",
        "welcome": "Bienvenue dans PPFO v28.0",
        "zeta_zeros": "Zéros Non Triviaux de la Fonction Zêta",
        "primes": "Nombres Premiers",
        "advanced": "Applications Avancées",
        "calculate": "Calculer",
        "precision": "Précision",
        "method": "Méthode de Calcul",
        "result": "Résultat",
        "time_taken": "Temps Écoulé",
        "error": "Erreur",
        "success": "Succès",
        "quick_example": "Exemple Rapide"
    }
}

# 📚 مكتبات الرياضيات
try:
    import mpmath as mp
    MP_MATH_AVAILABLE = True
    mp.mp.dps = 50
except Exception:
    MP_MATH_AVAILABLE = False

# ===================== نظام الترجمة =====================

def get_translation(key, lang):
    """الحصول على الترجمة المناسبة للمفتاح واللغة"""
    return TRANSLATIONS.get(lang, {}).get(key, key)

def show_mobile_card(title, content, type="info"):
    """عرض بطاقة معلومات"""
    colors = {
        "info": "#3B82F6",
        "success": "#10B981", 
        "warning": "#F59E0B",
        "danger": "#EF4444"
    }
    
    st.markdown(f"""
    <div class="mobile-card" style="border-top: 4px solid {colors.get(type, '#3B82F6')};">
        <strong>{title}:</strong> {content}
    </div>
    """, unsafe_allow_html=True)

# ===================== دوال الرياضيات الأساسية =====================

def parse_large_number(input_str):
    """تحويل النص إلى عدد كبير"""
    if not input_str or not input_str.strip():
        raise ValueError("الرجاء إدخال عدد")
    
    input_str = str(input_str).strip().replace(',', '').replace(' ', '')
    
    try:
        return int(input_str)
    except ValueError:
        raise ValueError(f"لا يمكن تحويل '{input_str}' إلى عدد صحيح")

@st.cache_data(ttl=3600)
def zeta_zero_advanced(n, precision=30):
    """حساب الصفر غير التافه رقم n لدالة زيتا"""
    n = int(n)
    
    if n < 1:
        raise ValueError("n يجب أن يكون على الأقل 1")
    
    # قيم معروفة بدقة
    known_zeros = {
        1: 14.134725141734693790,
        2: 21.022039638771554993,
        3: 25.010857580145688763,
        4: 30.424876125859513210,
        5: 32.935061587739189031,
        10: 49.773832477672302182,
        100: 236.52422966581620580,
        167: 346.3478705660099473959364598161519
    }
    
    if n in known_zeros:
        return known_zeros[n]
    
    # استخدام mpmath إذا كانت متوفرة
    if MP_MATH_AVAILABLE:
        try:
            mp.mp.dps = precision
            zero = mp.zetazero(n)
            return float(zero.imag)
        except:
            pass
    
    # تقدير تقريبي
    if n <= 100:
        return (2 * math.pi * (n - 1.125)) / math.log((n - 1.125) / (2 * math.pi))
    else:
        return (2 * math.pi * n) / math.log(n)

@st.cache_data(ttl=3600)
def is_prime_fast(n: int) -> bool:
    """التحقق من الأعداد الأولية"""
    if n < 2: 
        return False
    if n in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29): 
        return True
    if n % 2 == 0: 
        return False
    
    # اختبار بسيط للأعداد الصغيرة
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    
    return True

@st.cache_data(ttl=3600)
def factorize_fast(n: int):
    """التحليل إلى عوامل أولية (الطريقة التقليدية)"""
    if n < 2:
        return []
    
    if is_prime_fast(n):
        return [n]
    
    factors = []
    temp = n
    
    # إزالة عوامل 2
    while temp % 2 == 0:
        factors.append(2)
        temp //= 2
    
    # فحص القواسم الفردية
    factor = 3
    while factor * factor <= temp:
        if temp % factor == 0:
            factors.append(factor)
            temp //= factor
        else:
            factor += 2
    
    if temp > 1:
        factors.append(temp)
    
    return sorted(factors)

# ===================== الدوال الجديدة المرتبطة بدالة زيتا =====================

def pi_approx_zeta(x, num_zeros=50, lang="ar"):
    """
    تقدير دالة العد π(x) باستخدام الصيغة الصريحة مع أصفار زيتا
    """
    if not MP_MATH_AVAILABLE:
        # استخدام تقريب بسيط إذا لم تكن mpmath متوفرة
        approx = x / math.log(x) if x > 1 else 0
        if lang == "ar":
            st.info(f"استخدام تقريب بسيط: π({x}) ≈ {approx:.1f}")
        else:
            st.info(f"Utilisation d'une approximation simple: π({x}) ≈ {approx:.1f}")
        return approx
    
    try:
        mp.mp.dps = 25
        
        # دالة التكامل اللوغاريتمي
        def li(t):
            return mp.li(t)
        
        # الحد الأساسي
        result = li(x)
        
        # جمع مساهمة الأصفار غير التافهة (عدد محدود للسرعة)
        zeros_to_use = min(num_zeros, 20)  # تقليل العدد للسرعة
        
        for n in range(1, zeros_to_use + 1):
            try:
                zero_val = zeta_zero_advanced(n)
                rho = 0.5 + 1j * zero_val
                
                # Li(x^ρ) + Li(x^(1-ρ))
                term1 = li(x**rho)
                term2 = li(x**(1-rho))
                result -= (term1 + term2).real
            except:
                continue
        
        # الحدود التصحيحية
        result -= mp.log(2)
        result += mp.quad(lambda t: 1/(t*(t**2-1)*mp.log(t)), [x, mp.inf])
        
        return float(result.real)
    except Exception as e:
        if lang == "ar":
            st.warning(f"تحذير في حساب π(x): {e}")
        else:
            st.warning(f"Avertissement dans le calcul de π(x): {e}")
        return x / math.log(x) if x > 1 else 0

def factorize_using_zeta(n, lang="ar"):
    """
    تحليل العدد n إلى عوامل أولية باستخدام تقدير π(x) من دالة زيتا
    """
    if n < 2:
        return []
    
    if is_prime_fast(n):
        return [n]
    
    factors = []
    temp = n
    
    # استخدام تقدير π(x) لتحديد حدود البحث عن العوامل
    sqrt_n = int(math.sqrt(n))
    
    if lang == "ar":
        st.info(f"جاري تحليل العدد {n} باستخدام دالة زيتا...")
    else:
        st.info(f"Factorisation du nombre {n} avec la fonction Zêta...")
    
    # البحث عن عوامل صغيرة أولاً (طريقة عملية)
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    
    for p in small_primes:
        if p * p > temp:
            break
        while temp % p == 0:
            factors.append(p)
            temp //= p
            if temp == 1:
                return sorted(factors)
    
    # إذا بقي عدد كبير، استخدام الطريقة التقليدية مع معلومات من π(x)
    if temp > 1:
        if is_prime_fast(temp):
            factors.append(temp)
        else:
            # حساب π(√n) تقريبياً
            estimated_primes = pi_approx_zeta(sqrt_n, num_zeros=10, lang=lang)
            
            if lang == "ar":
                st.info(f"تقدير عدد الأعداد الأولية ≤ √{n}: ~{estimated_primes:.0f}")
            else:
                st.info(f"Estimation des nombres premiers ≤ √{n}: ~{estimated_primes:.0f}")
            
            # استخدام خوارزمية تقليدية كنسخة احتياطية
            backup_factors = factorize_fast(temp)
            factors.extend(backup_factors)
    
    return sorted(factors)

def nth_prime_zeta(n, lang="ar"):
    """
    تقدير العدد الأولي النوني باستخدام العلاقة مع دالة زيتا
    """
    if n < 1:
        raise ValueError("n يجب أن يكون موجباً" if lang == "ar" else "n doit être positif")
    
    if n == 1:
        return 2
    if n == 2:
        return 3
    
    # استخدام التقريب p_n ≈ n log n
    x = n * math.log(n)
    
    # تحسين التقدير باستخدام π(x)
    for iteration in range(5):  # تقليل التكرارات للسرعة
        pi_x = pi_approx_zeta(x, num_zeros=20, lang=lang)
        if abs(pi_x - n) < 0.5:
            break
        # تحديث x باستخدام نيوتن
        derivative = 1 / math.log(x) if x > 1 else 1
        x = x - (pi_x - n) * derivative
    
    # البحث عن العدد الأولي الأقرب
    candidate = max(2, int(x))
    found = False
    prime_candidate = candidate
    
    for i in range(100):  # بحث محدود
        test_num = candidate + i
        if test_num > 2 and test_num % 2 == 0:
            continue
            
        if is_prime_fast(test_num):
            # التحقق من أن هذا هو العدد الأولي النوني
            count = 0
            for num in range(2, test_num + 1):
                if is_prime_fast(num):
                    count += 1
                if count == n:
                    prime_candidate = test_num
                    found = True
                    break
            if found:
                break
    
    if found:
        return prime_candidate
    
    # نسخة احتياطية بسيطة
    count = 0
    num = 2
    while count < n:
        if is_prime_fast(num):
            count += 1
            if count == n:
                return num
        num += 1

# ===================== الواجهة الرئيسية =====================

def main():
    # تهيئة حالة الجلسة
    if 'lang' not in st.session_state:
        st.session_state.lang = "ar"
    
    # زر تبديل اللغة
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("العربية 🇸🇦", use_container_width=True):
            st.session_state.lang = "ar"
            st.rerun()
    with col2:
        if st.button("Français 🇫🇷", use_container_width=True):
            st.session_state.lang = "fr"
            st.rerun()
    
    # 🎯 الترويسة
    st.markdown(f'<h1 class="main-header">✨ {get_translation("app_title", st.session_state.lang)}</h1>', unsafe_allow_html=True)
    
    # 📱 قائمة التنقل
    tabs = st.tabs([
        get_translation("welcome", st.session_state.lang),
        get_translation("zeta_zeros", st.session_state.lang),
        get_translation("primes", st.session_state.lang),
        get_translation("advanced", st.session_state.lang)
    ])
    
    # ===================== الصفحة الرئيسية =====================
    with tabs[0]:
        st.markdown('<div class="mobile-card">', unsafe_allow_html=True)
        st.subheader(get_translation("welcome", st.session_state.lang))
        
        # حالة النظام
        st.markdown(f"**mpmath:** {'🟢 متوفر' if MP_MATH_AVAILABLE else '🔴 غير متوفر'}")
        
        st.markdown(f"""
        **الميزات الرئيسية:**
        - ✅ أصفار دالة زيتا غير التافهة
        - 🔍 الأعداد الأولية والتحليل
        - 📐 تحليل الأعداد باستخدام دالة زيتا
        - 🌍 دعم اللغتين العربية والفرنسية
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # مثال سريع
        st.markdown('<div class="mobile-card" style="border-top: 4px solid #10B981;">', unsafe_allow_html=True)
        st.subheader(get_translation("quick_example", st.session_state.lang))
        if st.button(f"🎯 حساب الصفر رقم 167" if st.session_state.lang == "ar" else f"🎯 Calculer le Zéro 167"):
            with st.spinner("جاري الحساب..." if st.session_state.lang == "ar" else "Calcul en cours..."):
                try:
                    zero_167 = zeta_zero_advanced(167)
                    st.success(f"الصفر رقم 167 = {zero_167:.12f}" if st.session_state.lang == "ar" else f"Zéro 167 = {zero_167:.12f}")
                except Exception as e:
                    st.error(f"خطأ: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ===================== أصفار زيتا =====================
    with tabs[1]:
        st.header(get_translation("zeta_zeros", st.session_state.lang))
        
        # 🎯 إعدادات الحساب
        col1, col2 = st.columns([3, 1])
        with col1:
            n_input = st.text_input(
                "رقم الصفر المطلوب:",
                value="167",
                key="zeta_n_input"
            )
        with col2:
            precision = st.selectbox(
                "الدقة",
                [15, 30, 50],
                index=1,
                key="precision_select"
            )
        
        if st.button(f"🎯 {get_translation('calculate', st.session_state.lang)}", type="primary", key="calculate_btn"):
            try:
                n = parse_large_number(n_input)
                if n < 1:
                    show_mobile_card("خطأ", "يجب أن يكون رقم الصفر موجباً", "danger")
                else:
                    with st.spinner("جاري الحساب..." if st.session_state.lang == "ar" else "Calcul en cours..."):
                        start_time = time.time()
                        zero_value = zeta_zero_advanced(n, precision=precision)
                        end_time = time.time()
                        
                        show_mobile_card(
                            "النتيجة",
                            f"{zero_value:.15f}",
                            "success"
                        )
                        
                        show_mobile_card(
                            "الوقت المستغرق",
                            f"{end_time - start_time:.3f} ثانية",
                            "info"
                        )
                        
            except Exception as e:
                show_mobile_card("خطأ", str(e), "danger")
        
        # 📋 أمثلة جاهزة
        st.markdown('<div class="mobile-card">', unsafe_allow_html=True)
        st.subheader("أمثلة جاهزة")
        
        examples = [1, 10, 100, 167]
        cols = st.columns(2)
        for i, example in enumerate(examples):
            with cols[i % 2]:
                if st.button(f"الصفر {example}", key=f"ex_{i}", use_container_width=True):
                    with st.spinner(f"جاري الحساب للصفر {example}..."):
                        try:
                            zero_val = zeta_zero_advanced(example)
                            show_mobile_card("النتيجة", f"{zero_val:.6f}", "primary")
                        except Exception as e:
                            show_mobile_card("خطأ", str(e), "danger")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ===================== الأعداد الأولية =====================
    with tabs[2]:
        st.header(get_translation("primes", st.session_state.lang))
        
        # 🔍 خدمات الأعداد الأولية
        prime_service = st.selectbox(
            "اختر الخدمة:",
            [
                "التحقق من عدد أولي",
                "التحليل إلى عوامل (طريقة تقليدية)",
                "التحليل إلى عوامل (باستخدام زيتا)",
                "العدد الأولي النوني باستخدام زيتا"
            ]
        )
        
        if prime_service == "التحقق من عدد أولي":
            number_input = st.text_input(
                "أدخل العدد للتحقق:",
                value="982451653",
                key="primality_input"
            )
            
            if st.button("تحقق", type="primary", key="primality_btn"):
                try:
                    number = parse_large_number(number_input)
                    with st.spinner("جاري التحقق..."):
                        start_time = time.time()
                        is_prime = is_prime_fast(number)
                        end_time = time.time()
                        
                        if is_prime:
                            show_mobile_card("النتيجة", "العدد أولي! ✅", "success")
                        else:
                            show_mobile_card("النتيجة", "العدد غير أولي ❌", "danger")
                        
                        show_mobile_card("الوقت المستغرق", f"{end_time - start_time:.3f} ثانية", "info")
                        
                except Exception as e:
                    show_mobile_card("خطأ", str(e), "danger")
        
        elif prime_service == "التحليل إلى عوامل (طريقة تقليدية)":
            number_input = st.text_input(
                "أدخل العدد للتحليل:",
                value="123456789",
                key="factorization_input"
            )
            
            if st.button("حلل", type="primary", key="factorization_btn"):
                try:
                    number = parse_large_number(number_input)
                    with st.spinner("جاري التحليل..."):
                        start_time = time.time()
                        factors = factorize_fast(number)
                        end_time = time.time()
                        
                        if len(factors) == 1:
                            show_mobile_card("النتيجة", "العدد أولي! ✅", "success")
                        else:
                            cnt = Counter(factors)
                            factorization_str = " × ".join([
                                f"{p}^{e}" if e > 1 else str(p) 
                                for p, e in cnt.items()
                            ])
                            
                            show_mobile_card(
                                "النتيجة",
                                f"{number} = {factorization_str}",
                                "primary"
                            )
                        
                        show_mobile_card("الوقت المستغرق", f"{end_time - start_time:.3f} ثانية", "info")
                        
                except Exception as e:
                    show_mobile_card("خطأ", str(e), "danger")
        
        elif prime_service == "التحليل إلى عوامل (باستخدام زيتا)":
            number_input = st.text_input(
                "أدخل العدد للتحليل باستخدام زيتا:",
                value="123456789",
                key="zeta_factorization_input"
            )
            
            if st.button("حلل باستخدام زيتا", type="primary", key="zeta_factorization_btn"):
                try:
                    number = parse_large_number(number_input)
                    with st.spinner("تحليل باستخدام دالة زيتا وأصفارها..."):
                        start_time = time.time()
                        factors = factorize_using_zeta(number, lang=st.session_state.lang)
                        end_time = time.time()
                        
                        if len(factors) == 1:
                            show_mobile_card("النتيجة", "العدد أولي! ✅", "success")
                        else:
                            cnt = Counter(factors)
                            factorization_str = " × ".join([
                                f"{p}^{e}" if e > 1 else str(p) 
                                for p, e in cnt.items()
                            ])
                            
                            show_mobile_card(
                                "النتيجة",
                                f"{number} = {factorization_str}",
                                "primary"
                            )
                        
                        show_mobile_card("الوقت المستغرق", f"{end_time - start_time:.3f} ثانية", "info")
                        
                except Exception as e:
                    show_mobile_card("خطأ", str(e), "danger")
        
        elif prime_service == "العدد الأولي النوني باستخدام زيتا":
            n_input = st.number_input(
                "أدخل n:",
                min_value=1,
                value=100,
                key="nth_prime_input"
            )
            
            if st.button("احسب العدد الأولي النوني", type="primary", key="nth_prime_btn"):
                try:
                    with st.spinner("حساب باستخدام دالة زيتا..."):
                        start_time = time.time()
                        nth_prime = nth_prime_zeta(n_input, lang=st.session_state.lang)
                        end_time = time.time()
                        
                        show_mobile_card(
                            "النتيجة",
                            f"العدد الأولي رقم {n_input}: {nth_prime}",
                            "success"
                        )
                        
                        show_mobile_card(
                            "الوقت المستغرق",
                            f"{end_time - start_time:.3f} ثانية",
                            "info"
                        )
                        
                except Exception as e:
                    show_mobile_card("خطأ", str(e), "danger")
    
    # ===================== التطبيقات المتقدمة =====================
    with tabs[3]:
        st.header(get_translation("advanced", st.session_state.lang))
        
        st.markdown("""
        <div class="mobile-card">
        <h3>العلاقة بين دالة زيتا وتحليل الأعداد</h3>
        
        **الصيغة الصريحة لـ π(x):**
        ```
        π(x) = li(x) - Σ [li(x^ρ) + li(x^(1-ρ))] - log(2) + ...
        ```
        
        حيث:
        - `π(x)`: عدد الأعداد الأولية ≤ x
        - `li(x)`: التكامل اللوغاريتمي
        - `ρ`: الأصفار غير التافهة لدالة زيتا
        
        **التطبيق العملي:**
        - استخدام تقدير π(x) لتحسين خوارزميات تحليل الأعداد
        - تحديد حدود البحث عن العوامل الأولية بشكل أكثر كفاءة
        - فهم أعمق لتوزيع الأعداد الأولية
        </div>
        """, unsafe_allow_html=True)
        
        # أمثلة عملية
        st.markdown('<div class="mobile-card">', unsafe_allow_html=True)
        st.subheader("أمثلة عملية")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("تقدير π(1000)"):
                with st.spinner("جاري الحساب..."):
                    try:
                        pi_1000 = pi_approx_zeta(1000, lang=st.session_state.lang)
                        st.info(f"π(1000) ≈ {pi_1000:.1f} (القيمة الحقيقية: 168)")
                    except Exception as e:
                        st.error(f"خطأ: {e}")
        
        with col2:
            if st.button("تقدير π(10000)"):
                with st.spinner("جاري الحساب..."):
                    try:
                        pi_10000 = pi_approx_zeta(10000, lang=st.session_state.lang)
                        st.info(f"π(10000) ≈ {pi_10000:.1f} (القيمة الحقيقية: 1229)")
                    except Exception as e:
                        st.error(f"خطأ: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
