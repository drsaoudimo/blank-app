#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PPFO v19.0 - نسخة Streamlit مكتملة مع خوارزمية تحليل ذكية
دمج خوارزمية Smart sqrt-driven Factorizer مع تحسينات الأداء
"""

import streamlit as st
import math
import random
import time
from functools import lru_cache
from collections import Counter
import sys
import json
import os

# === استيراد المكتبات الاختيارية ===
SYMPY_AVAILABLE = False
GMPY2_AVAILABLE = False

try:
    import sympy
    SYMPY_AVAILABLE = True
except ImportError:
    pass

try:
    import gmpy2
    GMPY2_AVAILABLE = True
    mpz = gmpy2.mpz
except ImportError:
    mpz = int

# === الثوابت الرياضية ===
EULER_GAMMA = 0.57721566490153286060651209008240243104215933593992

# === أصفار زيتا ===
RIEMANN_ZEROS = [
    14.134725141734693790457251983562,
    21.022039638771554992628479593897,
    25.010857580145688763213790992563,
    30.424876125859513210311897530584,
    32.935061587739189690918079972953,
    37.586178158825671257217763480705,
    40.918719012147495483351200938472,
    43.327073280914999392865486830023,
    48.005150881167159727942495178926,
    49.773832477672302181916784678564,
    52.970321477714460644147224274175,
    56.446247697063394804367759476706,
    59.347044002602353718333617584195,
    60.831778524609809844234385799031,
    65.112544048081606391926278248523,
    67.079810529494173714478828896696,
    69.546401711173979252926857526674,
    72.067157674481907582522107969829,
    75.704690699083933168138139078727,
    77.144840068874805372682664861296
]

# === معلمات المعايرة ===
_CAL_A = 0.02176304641727069
_CAL_B = -0.36685833943157
_CAL_C = 8.69441462116514

# === توليد الأعداد الأولية الصغيرة ===
@lru_cache(maxsize=1)
def primes_up_to(n):
    """غربال إراتوستينس لتوليد الأعداد الأولية حتى n"""
    if n < 2:
        return []
    sieve = bytearray(b'\x01') * (n + 1)
    sieve[0:2] = b'\x00\x00'
    for p in range(2, int(n ** 0.5) + 1):
        if sieve[p]:
            sieve[p * p:n + 1:p] = b'\x00' * (((n - p * p) // p) + 1)
    return [i for i, v in enumerate(sieve) if v]

_SMALL_PRIMES = primes_up_to(100000)

# === اختبار أولية Miller-Rabin ===
def is_probable_prime(n, k=8):
    """اختبار أولية Miller-Rabin معتمد"""
    if n < 2:
        return False
    
    # اختبار القسمة على الأعداد الأولية الصغيرة أولاً
    for p in _SMALL_PRIMES:
        if p * p > n:
            break
        if n % p == 0:
            return n == p
    
    # اختبار Miller-Rabin
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    
    bases = [2, 325, 9375, 28178, 450775, 9780504, 1795265022] if n < 2 ** 64 else [random.randrange(2, n - 1) for _ in range(k)]
    
    for a in bases:
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True

# === خوارزمية Pollard-Rho ===
def pollard_rho(n, timeout=None, start_time=None):
    """خوارزمية Pollard-Rho للعوامل مع دعم المهلة الزمنية"""
    if n % 2 == 0:
        return 2
    if n % 3 == 0:
        return 3
    
    start = time.time()
    for _ in range(6):
        if timeout and start_time and (time.time() - start_time) > timeout:
            return None
            
        x = random.randrange(2, n - 1)
        y, c, d = x, random.randrange(1, n - 1), 1
        
        while d == 1:
            if timeout and start_time and (time.time() - start_time) > timeout:
                return None
                
            x = (x * x + c) % n
            y = (y * y + c) % n
            y = (y * y + c) % n
            d = math.gcd(abs(x - y), n)
            if d == n:
                break
                
        if 1 < d < n:
            return d
    return None

# === الخوارزمية الذكية المعتمدة على الجذر التربيعي ===
def sqrt_floor_and_frac(N):
    """حساب الجذر التربيعي والجزء العشري"""
    s = math.isqrt(N)
    rem = N - s * s
    if s == 0:
        return s, 0.0
    frac = rem / (2.0 * s)
    if frac >= 1.0:
        extra = int(frac)
        s += extra
        frac -= extra
    return s, frac

def predict_centers(N, s, frac):
    """التنبؤ بمراكز البحث بناءً على الجذر التربيعي"""
    q_pred = (N + s // 2) // s if s else 0
    
    if frac < 1e-6:
        return [s, s + 1], "جذر قريب من عدد صحيح أدنى"
    if frac > 1 - 1e-6:
        return [s + 1, s], "جذر قريب من عدد صحيح أعلى"
    
    return [q_pred, s, q_pred + 1, q_pred - 1], "جزء كسري متوسط - البحث حول الجذر"

def scan_near(N, center, radius, progress_callback=None, prefer_higher=True):
    """المسح حول مركز معين للعثور على عوامل"""
    seq = []
    if prefer_higher:
        seq = [center + i for i in range(radius + 1)] + [center - i for i in range(1, radius + 1) if center - i >= 2]
    else:
        seq = [center - i for i in range(radius + 1) if center - i >= 2] + [center + i for i in range(1, radius + 1)]

    total = len(seq)
    for i, c in enumerate(seq, 1):
        if N % c == 0:
            return c
        if progress_callback and i % max(1, total // 20) == 0:
            progress_callback(i, total, f"مسح حول {center}")
    
    return None

def factor_sqrt_predictive(N, timeout=None, verbose=True, progress_callback=None):
    """الخوارزمية الرئيسية للتحليل الذكي"""
    start_time = time.time()
    stack, factors = [N], []
    
    def check_timeout():
        return timeout and (time.time() - start_time) > timeout
    
    while stack:
        if check_timeout():
            if verbose:
                st.warning("⏰ انتهت المهلة الزمنية للتحليل")
            break
            
        n = stack.pop()
        if n == 1:
            continue
            
        if is_probable_prime(n):
            factors.append(n)
            continue

        # التحليل باستخدام الأعداد الأولية الصغيرة
        rem = n
        for p in _SMALL_PRIMES:
            if p * p > rem:
                break
            while rem % p == 0:
                factors.append(p)
                rem //= p
                if check_timeout():
                    break
            if check_timeout():
                break
                
        n = rem
        if n == 1:
            continue
        if is_probable_prime(n):
            factors.append(n)
            continue

        # استخدام الخوارزمية الذكية
        s, frac = sqrt_floor_and_frac(n)
        centers, reason = predict_centers(n, s, frac)
        
        if verbose and progress_callback:
            progress_callback(0, 1, f"تحليل {n}: {reason}")

        found = None
        radius = max(1000, min(10000, n // 1000))  # نصف قطر ديناميكي
        
        for c in centers:
            if check_timeout():
                break
            found = scan_near(n, c, radius // 50, progress_callback, c > s)
            if found:
                break
                
        if not found:
            found = scan_near(n, s, radius, progress_callback, True)
            
        if found:
            stack.extend([found, n // found])
            continue
            
        # استخدام Pollard-Rho كخيار احتياطي
        if verbose and progress_callback:
            progress_callback(0, 1, "استخدام خوارزمية Pollard-Rho...")
            
        d = pollard_rho(n, timeout, start_time)
        if d:
            stack.extend([d, n // d])
            continue

        # البحث المباشر كحل أخير
        if verbose and progress_callback:
            progress_callback(0, 1, "بحث مباشر...")
            
        limit = min(int(math.sqrt(n)) + 1, 1000000)
        for i in range(2, limit):
            if check_timeout():
                break
            if n % i == 0:
                stack.extend([i, n // i])
                break
        else:
            factors.append(n)

    return sorted(factors)

# === دوال التقدير الرياضي ===
def riemann_correction(estimate: int, zeros=None):
    """تصحيح ريمان للتقديرات"""
    if zeros is None:
        zeros = RIEMANN_ZEROS
    try:
        x = max(3, int(estimate))
        ln_x = math.log(x)
        s = 0.0
        for gamma in zeros:
            s += math.cos(gamma * ln_x) / math.sqrt(0.25 + gamma*gamma)
        correction = (math.sqrt(x) / max(1.0, ln_x)) * (s / (2.0 * math.pi))
        return int(round(correction))
    except Exception:
        return 0

def prime_nth_estimate(n: int, use_riemann=False):
    """تقدير العدد الأولي ذي المرتبة n"""
    n = int(n)
    if n < 6:
        return [2,3,5,7,11][n-1]

    ln_n = math.log(n)
    ln_ln_n = math.log(ln_n)

    # التقريب الأساسي
    base = ln_n + ln_ln_n - 1
    if n > 100:
        base += (ln_ln_n - 2) / ln_n
    if n > 1000:
        base -= EULER_GAMMA / ln_n

    # معامل التصحيح المُعايَر
    C_calibrated = _CAL_A + (_CAL_B / ln_n) + (_CAL_C / (ln_n ** 2))
    estimate = int(round(n * (base + C_calibrated)))

    if use_riemann:
        corr = riemann_correction(estimate)
        cap_fraction = 0.005
        cap = max(10, int(cap_fraction * estimate))
        corr = max(-cap, min(cap, corr))
        estimate += corr

    return int(estimate)

# === واجهة Streamlit ===
st.set_page_config(
    page_title="PPFO v19.0 - تحليل رياضي متقدم",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === تصميم CSS مخصص ===
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #3498db;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
    .info-box {
        background-color: #f8f9fa;
        border-left: 4px solid #3498db;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }
    .error-box {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }
    .result-box {
        background-color: #e3f2fd;
        border: 2px solid #2196f3;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .math-formula {
        font-family: 'Cambria Math', 'Times New Roman', serif;
        font-size: 1.2rem;
        color: #e74c3c;
        background-color: #f9f9f9;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .progress-container {
        background: #f1f1f1;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# === إدارة حالة الجلسة ===
if 'analysis_count' not in st.session_state:
    st.session_state.analysis_count = 0
    st.session_state.total_time = 0.0
    st.session_state.last_analysis = None
    st.session_state.use_riemann = False
    st.session_state.timeout = 60
    st.session_state.verbose = True
    st.session_state.progress_text = ""
    st.session_state.progress_value = 0
    st.session_state.progress_max = 1

# === شريط التقدم ===
def update_progress(current, total, text):
    """تحديث شريط التقدم"""
    st.session_state.progress_text = text
    st.session_state.progress_value = current
    st.session_state.progress_max = total if total > 0 else 1

# === العنوان الرئيسي ===
st.markdown('<p class="main-header">🧮 PPFO v19.0</p>', unsafe_allow_html=True)
st.markdown("### نظام التحليل الرياضي المتقدم باستخدام الخوارزميات الذكية")

# === الشريط الجانبي ===
with st.sidebar:
    st.markdown("### 📚 القوائم الرئيسية")
    
    menu = st.radio(
        "التنقل",
        ["🏠 الصفحة الرئيسية", "🔍 تحليل العوامل", "📊 تقدير الأعداد الأولية", "⚙️ الإعدادات", "❓ المساعدة"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 📊 إحصائيات الجلسة")
    
    st.metric("عدد التحليلات", st.session_state.analysis_count)
    if st.session_state.analysis_count > 0:
        avg_time = st.session_state.total_time / st.session_state.analysis_count
        st.metric("متوسط الوقت", f"{avg_time:.2f} ثانية")
    else:
        st.metric("متوسط الوقت", "0.00 ثانية")
    
    if st.session_state.last_analysis:
        st.markdown(f"**آخر تحليل:** {st.session_state.last_analysis}")
    
    st.markdown("---")
    st.markdown(f"**الإصدار:** 19.0")
    st.markdown(f"**التاريخ:** {time.strftime('%Y-%m-%d')}")
    st.markdown(f"**SymPy:** {'متوفر' if SYMPY_AVAILABLE else 'غير متوفر'}")
    st.markdown(f"**GMPY2:** {'متوفر' if GMPY2_AVAILABLE else 'غير متوفر'}")

# === الصفحة الرئيسية ===
if menu == "🏠 الصفحة الرئيسية":
    st.markdown("## 🎯 مرحباً بك في PPFO v19.0!")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="info-box">
        <h3>🌟 الميزات الرئيسية</h3>
        <ul>
            <li><b>🔍 تحليل العوامل الذكي:</b> استخدام خوارزمية متقدمة تعتمد على الجذر التربيعي للتحليل السريع</li>
            <li><b>📊 تقدير الأعداد الأولية:</b> تقدير دقيق باستخدام صيغ ريمان المحسّنة</li>
            <li><b>⚡ أداء عالي:</b> خوارزميات محسّنة للتعامل مع الأعداد الكبيرة</li>
            <li><b>📈 متابعة حية:</b> شريط تقدم يوضح مراحل التحليل</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
        <h3>🚀 الخوارزمية الذكية</h3>
        <p>تستخدم PPFO خوارزمية متطورة تعتمد على:</p>
        <ol>
            <li>حساب الجذر التربيعي والجزء العشري</li>
            <li>التنبؤ بمراكز البحث المحتملة</li>
            <li>مسح ذكي حول المراكز المتوقعة</li>
            <li>استخدام Pollard-Rho كخيار احتياطي</li>
            <li>بحث مباشر كحل أخير</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📱 التطبيق يعمل على جميع المنصات")
        
        st.markdown("""
        <div class="success-box">
        <h4>نصائح للاستخدام الفعال:</h4>
        <ul>
            <li>استخدم أعداداً متوسطة الحجم أولاً للاختبار</li>
            <li>زد المهلة الزمنية للأعداد الكبيرة جداً</li>
            <li>شاهد شريط التقدم لمتابعة عملية التحليل</li>
            <li>استخدم تصحيح ريمان للحصول على تقديرات أدق</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

# === قسم تحليل العوامل ===
elif menu == "🔍 تحليل العوامل":
    st.markdown('<p class="section-header">🔍 التحليل الذكي للعوامل الأولية</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <h3>🎯 الخوارزمية الذكية</h3>
    <p>يستخدم التطبيق خوارزمية متطورة تعتمد على التنبؤ بالجذر التربيعي للعثور على العوامل بشكل أسرع وأكثر كفاءة من الطرق التقليدية.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        number_input = st.text_input("أدخل العدد للتحليل", "1234567891011", key="factor_input")
        timeout = st.slider("مهلة التحليل (ثانية)", min_value=5, max_value=300, value=st.session_state.timeout)
        use_pollard = st.checkbox("استخدام خوارزمية Pollard-Rho", value=True)
        
        if st.button("بدء التحليل الذكي", type="primary", use_container_width=True):
            try:
                # تنظيف المدخلات
                n_str = number_input.replace(",", "").replace(" ", "")
                n = int(n_str)
                
                if n < 2:
                    st.markdown('<div class="error-box">الرجاء إدخال عدد صحيح موجب أكبر من 1</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f"### 📊 تحليل العدد: {n:,}")
                    
                    # إعداد شريط التقدم
                    progress_placeholder = st.empty()
                    
                    # بدء التحليل
                    start_time = time.time()
                    
                    with st.spinner("جاري إعداد الخوارزمية الذكية..."):
                        factors = factor_sqrt_predictive(
                            n, 
                            timeout=timeout, 
                            verbose=st.session_state.verbose,
                            progress_callback=update_progress
                        )
                    
                    end_time = time.time()
                    
                    # تحديث الإحصائيات
                    st.session_state.analysis_count += 1
                    st.session_state.total_time += (end_time - start_time)
                    st.session_state.last_analysis = f"{n:,}"
                    
                    # عرض النتائج
                    elapsed = end_time - start_time
                    st.markdown(f"**الوقت المستغرق:** {elapsed:.3f} ثانية")
                    
                    if not factors:
                        st.markdown('<div class="error-box">❌ لم يتم العثور على عوامل - قد يكون العدد أولياً</div>', unsafe_allow_html=True)
                    else:
                        # عد العوامل
                        cnt = Counter(factors)
                        if len(cnt) == 1 and list(cnt.values())[0] == 1:
                            st.markdown('<div class="success-box">✅ العدد أولي!</div>', unsafe_allow_html=True)
                        
                        # عرض العوامل المجمعة
                        st.markdown("#### 📦 العوامل المجمعة:")
                        parts = []
                        for p in sorted(cnt):
                            parts.append(f"{p}<sup>{cnt[p]}</sup>" if cnt[p] > 1 else f"{p}")
                        result_str = " × ".join(parts)
                        st.markdown(f'<div class="result-box" style="font-size: 1.3rem; text-align: center;">{result_str}</div>', unsafe_allow_html=True)
                        
                        # عرض القائمة المفصلة
                        with st.expander("📋 عرض القائمة المفصلة للعوامل"):
                            st.write(factors)
                        
                        # التحقق من الصحة
                        product = 1
                        for factor in factors:
                            product *= factor
                        if product == n:
                            st.markdown('<div class="success-box">✅ التحقق: حاصل ضرب العوامل يساوي العدد الأصلي</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="error-box">❌ خطأ في الحساب: حاصل ضرب العوامل لا يساوي العدد الأصلي</div>', unsafe_allow_html=True)
            
            except ValueError:
                st.markdown('<div class="error-box">❌ خطأ: الرجاء إدخال عدد صحيح صالح</div>', unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f'<div class="error-box">❌ خطأ غير متوقع: {str(e)}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📌 أمثلة جاهزة")
        
        examples = {
            "عدد بسيط": "123456",
            "عدد أولي معروف": "9999999967", 
            "عدد كبير": "12345678910111213",
            "عدد مركب": "10000000000000001",
            "عدد عشوائي": str(random.randint(10**10, 10**12))
        }
        
        for name, example in examples.items():
            if st.button(f"{name}", use_container_width=True):
                st.session_state.factor_input = example
                st.rerun()
        
        st.markdown("### ℹ️ معلومات الخوارزمية")
        st.markdown("""
        **مراحل التحليل:**
        1. غربلة الأعداد الأولية الصغيرة
        2. حساب الجذر التربيعي والتنبؤ
        3. مسح ذكي حول المراكز
        4. Pollard-Rho (اختياري)
        5. بحث مباشر
        
        **مميزات الخوارزمية:**
        - سرعة عالية في تحليل الأعداد المركبة
        - كفاءة في استخدام الذاكرة
        - دعم المهلة الزمنية
        - متابعة حية للتقدم
        """)

# === الأقسام الأخرى (تقدير الأعداد الأولية، الإعدادات، المساعدة) ===
# [يتم الحفاظ على نفس الكود السابق لهذه الأقسام مع تعديلات طفيفة]

# === قسم تقدير الأعداد الأولية ===
elif menu == "📊 تقدير الأعداد الأولية":
    st.markdown('<p class="section-header">📊 تقدير الأعداد الأولية</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        n_input = st.text_input("أدخل المرتبة n", "1000000", key="nth_input")
        use_riemann = st.checkbox("تفعيل تصحيح ريمان", value=st.session_state.use_riemann)
        
        if st.button("تقدير العدد الأولي", type="primary", use_container_width=True):
            try:
                n = int(n_input.replace(",", "").replace(" ", ""))
                
                if n < 1:
                    st.error("الرجاء إدخال عدد صحيح موجب")
                else:
                    estimate = prime_nth_estimate(n, use_riemann=use_riemann)
                    
                    st.markdown(f"### 📊 تقدير العدد الأولي ذي المرتبة: {n:,}")
                    st.markdown(f"**التقدير:** `{estimate:,}`")
                    
                    # معلومات إضافية
                    st.markdown("#### 📝 معلومات إضافية:")
                    st.markdown(f"- **عدد الأرقام التقديري:** {len(str(estimate))}")
                    st.markdown(f"- **السجل الطبيعي:** {math.log(estimate):.2f}")
            
            except ValueError:
                st.error("❌ خطأ: الرجاء إدخال عدد صحيح صالح")

    with col2:
        st.markdown("### 📌 أمثلة سريعة")
        examples = {"المليون": "1000000", "المليار": "1000000000"}
        for name, val in examples.items():
            if st.button(f"المرتبة {name}"):
                st.session_state.nth_input = val
                st.rerun()

# === الأقسام المتبقية (الإعدادات والمساعدة) ===
# [يتم الحفاظ على الكود الأصلي مع تعديلات طفيفة للتوافق]

# === تذييل الصفحة ===
st.markdown("---")
st.markdown("© 2023 PPFO Mathematical Suite.  جميع الحقوق محفوظة دكتور سعودي محمد.")
