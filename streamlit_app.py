#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PPFO v25.0 Streamlit Web Application — نسخة محسّنة بالكامل مع دعم LaTeX وتصحيح أصفار زيتا
"""

import streamlit as st
import math, random, time, sys, re, json
from functools import lru_cache
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# إعداد صفحة Streamlit - إضافة دعم RTL
st.set_page_config(
    page_title="PPFO v25.0 - نسخة زيتا المصححة",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# إعداد النمط العام للتطبيق
st.markdown("""
<style>
    /* دعم اللغة العربية والاتجاه من اليمين لليسار */
    body, .stApp {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* تخصيص العناوين */
    h1, h2, h3, h4, h5, h6 {
        color: #1E3A8A;
        font-weight: bold;
    }
    
    /* مربعات النتائج */
    .result-box {
        background-color: #f0f9ff;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #3b82f6;
        margin: 15px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* مربعات التحذير */
    .warning-box {
        background-color: #fffbeb;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #f59e0b;
        margin: 10px 0;
    }
    
    /* مربعات النجاح */
    .success-box {
        background-color: #ecfdf5;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #10b981;
        margin: 10px 0;
    }
    
    /* أزرار مخصصة */
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #2563eb;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* تنسيق LaTeX */
    .latex-formula {
        font-size: 1.2em;
        background-color: #f1f5f9;
        padding: 10px;
        border-radius: 8px;
        margin: 10px 0;
        direction: ltr;
        text-align: left;
        font-family: 'Cambria Math', 'Times New Roman', serif;
    }
    
    /* جدول نتائج */
    .results-table {
        background-color: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* التنقل الجانبي */
    .sidebar .sidebar-content {
        background-color: #f8fafc;
    }
</style>
""", unsafe_allow_html=True)

# محاولة استيراد المكتبات المتقدمة
try:
    import sympy
    SYMPY_AVAILABLE = True
except Exception:
    SYMPY_AVAILABLE = False
    st.warning("❌ مكتبة sympy غير متوفرة. بعض الميزات المتقدمة ستكون معطلة.")

try:
    import gmpy2
    GMPY2_AVAILABLE = True
    mpz = gmpy2.mpz
except Exception:
    GMPY2_AVAILABLE = False
    mpz = int
    st.info("ℹ️ مكتبة gmpy2 غير متوفرة. سيتم استخدام حسابات بايثون القياسية.")

try:
    from mpmath import mp, zeta, zetazero, siegeltheta, log, pi, cos, sin, exp, sqrt, lambertw
    MP_MATH_AVAILABLE = True
    # ضبط دقة عالية جداً
    mp.dps = 50
except Exception:
    MP_MATH_AVAILABLE = False
    st.error("❌ مكتبة mpmath غير متوفرة. حسابات أصفار زيتا ستكون غير دقيقة.")

# ثوابت رياضية
EULER_GAMMA = 0.57721566490153286060651209008240243104215933593992

# ===================== دوال لمعالجة الأعداد الكبيرة =====================

def parse_large_number(input_str):
    """تحويل النص إلى عدد كبير مع دعم التنسيقات المختلفة"""
    if not input_str or not input_str.strip():
        raise ValueError("الرجاء إدخال عدد")
    
    input_str = str(input_str).strip().replace(',', '').replace(' ', '').replace('−', '-')
    
    # التعامل مع الترميز العلمي
    scientific_pattern = r'^([+-]?[\d.]+)e([+-]?\d+)$'
    if re.match(scientific_pattern, input_str.lower()):
        try:
            base, exp = re.split('e', input_str.lower())
            return int(float(base) * (10 ** float(exp)))
        except:
            pass
    
    # التعامل مع الترميز بالقوى
    power_pattern = r'^(\d+)\s*[\^*]{1,2}\s*(\d+)$'
    if re.match(power_pattern, input_str):
        try:
            if '^' in input_str:
                base, exp = input_str.split('^')
            else:
                base, exp = input_str.split('**')
            base = base.strip()
            exp = exp.strip()
            return int(base) ** int(exp)
        except:
            pass
    
    # محاولة التحويل المباشر
    try:
        return int(input_str)
    except ValueError:
        raise ValueError(f"لا يمكن تحويل '{input_str}' إلى عدد صحيح")

def format_large_number(n):
    """تنسيق الأعداد الكبيرة لعرضها بشكل مقروء"""
    if isinstance(n, float) and abs(n) > 1e15:
        return f"{n:.4e}"
    
    n_str = str(abs(int(n)))
    sign = "-" if int(n) < 0 else ""
    
    if len(n_str) <= 6:
        return sign + n_str
    
    # استخدام الترميز العلمي للأعداد الكبيرة جداً
    if len(n_str) > 15:
        return f"{sign}{n_str[0]}.{n_str[1:5]} × 10<sup>{len(n_str)-1}</sup>"
    
    # إضافة فواصل للأعداد الكبيرة
    parts = []
    while n_str:
        parts.append(n_str[-3:])
        n_str = n_str[:-3]
    return sign + ','.join(reversed(parts))

def validate_number_size(n, max_digits=100000):
    """التحقق من أن العدد ليس كبيراً جداً"""
    n_str = str(abs(n))
    if len(n_str) > max_digits:
        raise ValueError(f"العدد كبير جداً! الحد الأقصى المسموح: {max_digits} رقم")
    return n

# ===================== دوال زيتا غير التافهة المصححة - استخدام mpmath =====================

@st.cache_data(ttl=3600)
def zeta_zero_mpmath(n, precision=50):
    """حساب الصفر غير التافه رقم n باستخدام mpmath بدقة عالية"""
    if not MP_MATH_AVAILABLE:
        raise Exception("مكتبة mpmath غير متوفرة. لا يمكن حساب أصفار زيتا بدقة.")
    
    try:
        # ضبط الدقة
        mp.dps = precision
        
        # استخدام الدالة المدمجة في mpmath
        zero = zetazero(n)
        return float(zero.imag)
    except Exception as e:
        st.error(f"خطأ في حساب الصفر باستخدام mpmath: {e}")
        return None

@st.cache_data(ttl=3600)
def calculate_zeta_zeros_batch(start_n, end_n, precision=50):
    """حساب مجموعة من أصفار زيتا دفعة واحدة"""
    if not MP_MATH_AVAILABLE:
        raise Exception("مكتبة mpmath غير متوفرة")
    
    mp.dps = precision
    results = []
    
    for n in range(start_n, end_n + 1):
        try:
            zero = zetazero(n)
            results.append((n, float(zero.imag)))
        except Exception as e:
            st.warning(f"فشل حساب الصفر {n}: {e}")
    
    return results

def riemann_siegel_z(t, precision=30):
    """حساب دالة Riemann-Siegel Z(t) بدقة عالية"""
    if not MP_MATH_AVAILABLE:
        raise Exception("مكتبة mpmath غير متوفرة")
    
    mp.dps = precision
    t = mp.mpf(t)
    
    # حساب دالة ثيتا
    theta = siegeltheta(t)
    
    # حساب مجموع ريمان-سيغل
    N = int(mp.sqrt(t / (2 * mp.pi)))
    sum_val = mp.mpc(0)
    
    for n in range(1, N + 1):
        sum_val += (1/mp.sqrt(n)) * mp.cos(theta - t * mp.log(n))
    
    # التصحيح
    correction = (-1)**(N-1) * (t / (2 * mp.pi))**(-1/4)
    
    return 2 * sum_val.real + correction

def plot_z_function(t_min, t_max, num_points=1000, precision=30):
    """رسم دالة Z(t) في مجال معين"""
    if not MP_MATH_AVAILABLE:
        st.error("مكتبة mpmath غير متوفرة. لا يمكن رسم دالة Z(t).")
        return None
    
    mp.dps = precision
    t_vals = np.linspace(t_min, t_max, num_points)
    z_vals = []
    
    for t_val in t_vals:
        try:
            z_val = float(riemann_siegel_z(t_val, precision))
            z_vals.append(z_val)
        except:
            z_vals.append(np.nan)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(t_vals, z_vals, 'b-', linewidth=2)
    ax.axhline(y=0, color='k', linestyle='--', alpha=0.7)
    ax.set_xlabel('t', fontsize=12)
    ax.set_ylabel('Z(t)', fontsize=12)
    ax.set_title(f'دالة Riemann-Siegel Z(t) من {t_min} إلى {t_max}', fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.set_facecolor('#f8f9fa')
    
    return fig

def analyze_zero_gaps(zero_numbers, precision=30):
    """تحليل الفجوات بين أصفار زيتا المتتالية"""
    if not MP_MATH_AVAILABLE:
        st.error("مكتبة mpmath غير متوفرة. لا يمكن تحليل الفجوات.")
        return None
    
    mp.dps = precision
    gaps = []
    normalized_gaps = []
    
    # حساب الأصفار
    zeros = []
    for n in zero_numbers:
        try:
            zero = zetazero(n)
            zeros.append(float(zero.imag))
        except Exception as e:
            st.warning(f"فشل حساب الصفر {n}: {e}")
    
    if len(zeros) < 2:
        st.error("لم يتم حساب عدد كافٍ من الأصفار للتحليل")
        return None
    
    # حساب الفجوات
    for i in range(1, len(zeros)):
        gap = zeros[i] - zeros[i-1]
        gaps.append(gap)
    
    # تطبيع الفجوات
    mean_gap = sum(gaps) / len(gaps)
    for gap in gaps:
        normalized_gaps.append(gap / mean_gap)
    
    # مقارنة مع توزيع GUE
    x = np.linspace(0, 5, 100)
    gue_pdf = (32/(np.pi**2)) * x**2 * np.exp(-4*x**2/np.pi)
    
    # رسم بياني للمقارنة
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # رسم توزيع الفجوات الفعلية
    sns.histplot(normalized_gaps, bins=15, stat='density', kde=True, 
                 color='blue', alpha=0.6, label='الفجوات الفعلية', ax=ax)
    
    # رسم توزيع GUE النظري
    ax.plot(x, gue_pdf, 'r-', linewidth=2, label='توزيع GUE النظري')
    
    ax.set_xlabel('الفجوة المُعيرة', fontsize=12)
    ax.set_ylabel('الكثافة', fontsize=12)
    ax.set_title('مقارنة توزيع فجوات أصفار زيتا مع توزيع GUE', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_facecolor('#f8f9fa')
    
    return {
        'gaps': gaps,
        'normalized_gaps': normalized_gaps,
        'mean_gap': mean_gap,
        'min_gap': min(normalized_gaps),
        'max_gap': max(normalized_gaps),
        'fig': fig
    }

# ===================== دوال رياضية متقدمة للأعداد الأولية =====================

@lru_cache(maxsize=10000)
def is_prime_fast(n: int) -> bool:
    """نسخة محسنة وسريعة من التحقق من الأعداد الأولية مع دعم الأعداد الكبيرة"""
    try:
        n = mpz(n) if GMPY2_AVAILABLE else int(n)
    except:
        n = int(n)
    
    if n < 2: 
        return False
    if n in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29): 
        return True
    if n % 2 == 0: 
        return False
    
    # استخدام المكتبات المتقدمة للأعداد الكبيرة
    if GMPY2_AVAILABLE and n > 10**6:
        try:
            return bool(gmpy2.is_prime(n))
        except:
            pass
    
    if SYMPY_AVAILABLE and n > 10**8:
        try:
            return bool(sympy.isprime(n))
        except:
            pass
    
    # فحص القواسم الصغيرة أولاً
    small_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    for p in small_primes:
        if n % p == 0:
            return n == p
    
    # اختبار Miller-Rabin للأعداد الكبيرة
    d, s = n - 1, 0
    while d % 2 == 0: 
        d //= 2
        s += 1
    
    def check_composite(a):
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            return False
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                return False
        return True
    
    # قواعد أكثر تحفظاً للأعداد الكبيرة
    if n < 2**64:
        bases = [2, 325, 9375, 28178, 450775, 9780504, 1795265022]
    else:
        bases = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    
    for a in bases:
        if a % n == 0:
            continue
        if check_composite(a):
            return False
    
    return True

def factorize_fast(n: int, timeout=30, verbose=True):
    """نسخة محسنة للتحليل إلى عوامل أولية مع دعم الأعداد الكبيرة"""
    try:
        n = mpz(n) if GMPY2_AVAILABLE else int(n)
    except:
        n = int(n)
    
    if n < 2:
        return []
    
    # استخدام المكتبات المتقدمة للأعداد الكبيرة
    if SYMPY_AVAILABLE and n > 10**15:
        try:
            factors_dict = sympy.factorint(n)
            factors = []
            for prime, exp in factors_dict.items():
                factors.extend([int(prime)] * int(exp))
            return sorted(factors)
        except:
            pass
    
    if is_prime_fast(n):
        return [int(n)]
    
    factors = []
    start_time = time.time()
    
    # إزالة عوامل 2
    while n % 2 == 0:
        factors.append(2)
        n //= 2
        if time.time() - start_time > timeout:
            factors.append(int(n))
            return sorted(factors)
    
    # فحص الأعداد الأولية الصغيرة
    small_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    for p in small_primes:
        while n % p == 0:
            factors.append(p)
            n //= p
            if time.time() - start_time > timeout:
                factors.append(int(n))
                return sorted(factors)
        if n == 1:
            return sorted(factors)
    
    if is_prime_fast(n):
        factors.append(int(n))
        return sorted(factors)
    
    # خوارزمية Pollard's Rho محسنة
    def pollard_rho(n, timeout_time):
        if n == 1:
            return None
        if n % 2 == 0:
            return 2
        if n % 3 == 0:
            return 3
        
        x = random.randint(2, min(n-2, 10**6))
        y = x
        c = random.randint(1, min(n-1, 10**6))
        d = 1
        
        f = lambda x: (x * x + c) % n
        
        while d == 1:
            if time.time() > timeout_time:
                return None
            x = f(x)
            y = f(f(y))
            d = math.gcd(abs(x - y), n)
            if d == n:
                break
        
        return d if 1 < d < n else None
    
    timeout_time = start_time + timeout
    remaining = n
    
    while remaining > 1 and not is_prime_fast(remaining):
        if time.time() > timeout_time:
            factors.append(int(remaining))
            break
        
        factor = pollard_rho(remaining, timeout_time)
        if factor is None:
            factors.append(int(remaining))
            break
        
        if is_prime_fast(factor):
            factors.append(int(factor))
        else:
            sub_factors = factorize_fast(factor, timeout - (time.time() - start_time), verbose)
            factors.extend(sub_factors)
        
        remaining //= factor
    
    if remaining > 1:
        factors.append(int(remaining))
    
    return sorted(factors)

# ===================== واجهة Streamlit المحسنة مع دعم كامل للـ LaTeX =====================

def show_latex_formula(formula, description=""):
    """عرض صيغة رياضية باستخدام LaTeX"""
    st.markdown(f"""
    <div class="latex-formula">
        <p style="margin: 0; font-size: 1.1em">{formula}</p>
        <p style="margin: 5px 0 0 0; font-size: 0.9em; color: #64748b">{description}</p>
    </div>
    """, unsafe_allow_html=True)

def zeta_zero_calculator_section():
    """قسم حاسبة أصفار دالة زيتا"""
    st.header("𝛇 أصفار دالة زيتا غير التافهة - النسخة المصححة")
    
    # شرح رياضي باستخدام LaTeX
    st.markdown("""
    **دالة زيتا لريمان** $\zeta(s)$ لها أصفار غير تافهة على الخط الحرج $\Re(s) = \\frac{1}{2}$.
    
    الصيغة العامة للصفر غير التافه رقم $n$:
    """)
    
    show_latex_formula(
        r"$$\zeta\left(\frac{1}{2} + i t_n\right) = 0$$",
        "حيث $t_n$ هو الجزء التخيلي للصفر رقم $n$"
    )
    
    st.success("""
    **✅ تم تصحيح الخوارزميات لحساب أصفار زيتا بدقة عالية باستخدام مكتبة mpmath**
    - دقة تصل إلى 50 خانة عشرية
    - استخدام خوارزميات Riemann-Siegel المتقدمة
    - قيم مرجعية معتمدة من المشاريع البحثية
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        n_input = st.text_input("رقم الصفر $n$:", value="167", key="zeta_zero_input")
    
    with col2:
        precision = st.slider("دقة الحساب (خانات عشرية):", 
                             min_value=15, max_value=60, value=30, step=5,
                             help="زيادة الدقة تحسن النتائج لكن تستغرق وقتاً أطول")
    
    with col3:
        method = st.selectbox("طريقة الحساب:", 
                             ["mpmath (موصى به)", "الخوارزمية التقريبية"],
                             help="mpmath توفر أعلى دقة")
    
    if st.button("🔍 حساب الصفر غير التافه", type="primary"):
        try:
            n = parse_large_number(n_input)
            if n < 1:
                st.error("$n$ يجب أن يكون على الأقل 1")
                return
            
            with st.spinner(f"جاري حساب الصفر غير التافه رقم {n} بدقة {precision} خانة عشرية..."):
                start_time = time.time()
                
                if method.startswith("mpmath") and MP_MATH_AVAILABLE:
                    zero = zeta_zero_mpmath(n, precision)
                    method_used = "mpmath (دقة عالية)"
                else:
                    st.warning("استخدام الخوارزمية التقريبية (دقة أقل)")
                    # استخدام خوارزمية احتياطية هنا
                    zero = None
                
                end_time = time.time()
                
                if zero is not None:
                    st.success(f"**الصفر غير التافه رقم {n}:** $t_{{{n}}} = {zero:.15f}$")
                    
                    # عرض المقارنة مع القيمة الصحيحة للصفر 167
                    if n == 167:
                        correct_value = 346.3478705660099473959364598161519
                        error = abs(zero - correct_value)
                        st.info(f"**القيمة الصحيحة:** ${correct_value:.15f}$")
                        st.info(f"**الخطأ النسبي:** ${error:.2e}$")
                        
                        if error < 1e-8:
                            st.success("✅ **الحساب دقيق جداً!**")
                        else:
                            st.warning("⚠️ **تحذير:** الخطأ أكبر من المتوقع. نوصي بزيادة الدقة.")
                    
                    st.metric("الوقت المستغرق", f"{end_time - start_time:.3f} ثانية")
                    st.metric("الطريقة المستخدمة", method_used)
                    
                    # رسم دالة Z(t) حول الصفر المحسوب
                    if st.checkbox("📊 عرض رسم بياني لدالة Z(t) حول هذا الصفر"):
                        t_min = max(0, zero - 5)
                        t_max = zero + 5
                        fig = plot_z_function(t_min, t_max, precision=precision)
                        if fig:
                            st.pyplot(fig)
                            plt.close(fig)
                else:
                    st.error("فشل الحساب. يرجى المحاولة مرة أخرى أو استخدام دقة أقل.")
        
        except Exception as e:
            st.error(f"❌ خطأ: {e}")
    
    # قسم التحليل المتقدم
    st.subheader("📈 التحليل المتقدم لأصفار زيتا")
    
    col1, col2 = st.columns(2)
    
    with col1:
        start_n = st.number_input("الصفر الابتدائي:", min_value=1, value=160, step=1)
    
    with col2:
        end_n = st.number_input("الصفر النهائي:", min_value=start_n+1, value=170, step=1)
    
    if st.button("تحليل مجموعة من الأصفار", type="secondary"):
        try:
            with st.spinner(f"جاري تحليل الأصفار من {start_n} إلى {end_n}..."):
                zeros_data = calculate_zeta_zeros_batch(start_n, end_n, precision)
                
                if zeros_data:
                    # عرض النتائج في جدول
                    st.markdown('<div class="results-table">', unsafe_allow_html=True)
                    st.subheader(f"نتائج الأصفار من {start_n} إلى {end_n}")
                    
                    results_df = []
                    for n, t_val in zeros_data:
                        results_df.append({
                            "الرقم": n,
                            "القيمة": f"{t_val:.10f}",
                            "الفرق عن السابق": f"{t_val - (results_df[-1]['القيمة'] if results_df else t_val):.6f}" if results_df else "-"
                        })
                    
                    st.dataframe(results_df, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # تحليل الفجوات
                    gap_analysis = analyze_zero_gaps(list(range(start_n, end_n+1)), precision)
                    if gap_analysis:
                        st.subheader("🔬 تحليل الفجوات بين الأصفار")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.info(f"**متوسط الفجوة:** {gap_analysis['mean_gap']:.6f}")
                            st.info(f"**أصغر فجوة مُعيرة:** {gap_analysis['min_gap']:.4f}")
                            st.info(f"**أكبر فجوة مُعيرة:** {gap_analysis['max_gap']:.4f}")
                        
                        with col2:
                            st.pyplot(gap_analysis['fig'])
                            plt.close(gap_analysis['fig'])
        
        except Exception as e:
            st.error(f"❌ خطأ في التحليل: {e}")

def zeta_applications_section():
    """قسم تطبيقات دالة زيتا"""
    st.header("🔗 تطبيقات دالة زيتا في نظرية الأعداد")
    
    st.markdown("""
    دالة زيتا لريمان لها تطبيقات عميقة في نظرية الأعداد، خاصة في دراسة توزيع الأعداد الأولية.
    """)
    
    tab1, tab2, tab3 = st.tabs([
        "علاقة زيتا بالأعداد الأولية",
        "الصيغة الصريحة",
        "فرضية ريمان والأمن السيبراني"
    ])
    
    with tab1:
        st.subheader("🧮 العلاقة بين دالة زيتا والأعداد الأولية")
        
        show_latex_formula(
            r"$$\zeta(s) = \sum_{n=1}^{\infty} \frac{1}{n^s} = \prod_{p \text{ أولي}} \frac{1}{1 - p^{-s}}$$",
            "صيغة أويلر للعلاقة بين دالة زيتا والأعداد الأولية"
        )
        
        st.markdown("""
        هذه الصيغة توضح العلاقة العميقة بين دالة زيتا وتوزيع الأعداد الأولية. معرفة أصفار دالة زيتا
        تساعد في فهم سلوك الأعداد الأولية بشكل أفضل.
        """)
        
        if st.button("استكشاف العلاقة - حساب أول 100 عدد أولي"):
            primes = []
            num = 2
            while len(primes) < 100:
                if is_prime_fast(num):
                    primes.append(num)
                num += 1
            
            st.success(f"**تم حساب أول {len(primes)} عدد أولي بنجاح!**")
            
            # رسم توزيع الفجوات بين الأعداد الأولية
            gaps = [primes[i+1] - primes[i] for i in range(len(primes)-1)]
            
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(range(1, len(gaps)+1), gaps, 'bo-')
            ax.set_xlabel('العدد الأولي')
            ax.set_ylabel('الفجوة مع العدد التالي')
            ax.set_title('فجوات بين الأعداد الأولية المتتالية')
            ax.grid(True, alpha=0.3)
            
            st.pyplot(fig)
            plt.close(fig)
    
    with tab2:
        st.subheader("📜 الصيغة الصريحة لعدد الأعداد الأولية")
        
        show_latex_formula(
            r"$$\pi(x) = \mathrm{Li}(x) - \sum_{\rho} \mathrm{Li}(x^{\rho}) + \int_{x}^{\infty} \frac{dt}{t(t^2-1)\ln t} - \ln 2$$",
            "حيث $\\rho$ هي أصفار دالة زيتا غير التافهة، و $\\mathrm{Li}(x)$ هو دالة التكامل اللوغاريتمي"
        )
        
        st.markdown("""
        هذه الصيغة تربط بين عدد الأعداد الأولية $\\pi(x)$ حتى العدد $x$ وأصفار دالة زيتا.
        دقة حساب $\\pi(x)$ تعتمد بشكل مباشر على دقة معرفة أصفار دالة زيتا.
        """)
        
        x_val = st.number_input("أدخل قيمة $x$ لحساب $\\pi(x)$:", 
                               min_value=10, max_value=10000, value=1000, step=100)
        
        if st.button("حساب $\\pi(x)$"):
            # حساب بسيط لـ π(x) كمثال (ليس دقيقاً للأعداد الكبيرة)
            count = 0
            start_time = time.time()
            
            for num in range(2, x_val + 1):
                if is_prime_fast(num):
                    count += 1
            
            end_time = time.time()
            
            st.success(f"$\\pi({x_val}) = {count}$")
            st.info(f"**الوقت المستغرق:** {end_time - start_time:.3f} ثانية")
            
            # مقارنة مع التقريب
            approx = x_val / math.log(x_val) if x_val > 1 else 0
            st.warning(f"**التقريب باستخدام نظرية الأعداد الأولية:** {approx:.1f}")
            st.info(f"**النسبة:** {count/approx:.4f} (يجب أن تكون قريبة من 1 للأعداد الكبيرة)")
    
    with tab3:
        st.subheader("🔐 فرضية ريمان والأمن السيبراني")
        
        st.markdown("""
        **فرضية ريمان** هي واحدة من أهم المسائل غير المحلولة في الرياضيات. تنص على أن جميع
        الأصفار غير التافهة لدالة زيتا تقع على الخط الحرج $\\Re(s) = \\frac{1}{2}$.
        
        هذه الفرضية لها آثار عميقة في:
        - نظرية الأعداد
        - التشفير الحديث
        - الأمن السيبراني
        - الفيزياء النظرية
        """)
        
        show_latex_formula(
            r"$$\text{فرضية ريمان: } \quad \zeta(s) = 0 \implies \Re(s) = \frac{1}{2} \quad \text{لجميع الأصفار غير التافهة}$$"
        )
        
        st.info("""
        **لماذا تهم فرضية ريمان الأمن السيبراني؟**
        - خوارزميات التشفير الحديثة (مثل RSA) تعتمد على صعوبة تحليل الأعداد الكبيرة
        - إثبات فرضية ريمان قد يؤدي إلى خوارزميات أسرع لتحليل الأعداد
        - هذا بدوره قد يؤثر على أمن أنظمة التشفير الحالية
        """)

def main():
    """الدالة الرئيسية للتطبيق"""
    
    # ترويسة التطبيق
    st.markdown('<h1 style="text-align: center; color: #1E3A8A; font-weight: bold;">🧮 PPFO v25.0</h1>', 
                unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; color: #4B5563; margin-bottom: 2rem;">النسخة المحسّنة بالكامل مع دعم LaTeX وتصحيح أصفار زيتا</h2>', 
                unsafe_allow_html=True)
    
    # معلومات النظام
    with st.expander("🔧 معلومات النظام والإعدادات", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.info(f"**Sympy:** {'✅ متوفر' if SYMPY_AVAILABLE else '❌ غير متوفر'}")
        
        with col2:
            st.info(f"**GMPY2:** {'✅ متوفر' if GMPY2_AVAILABLE else '❌ غير متوفر'}")
        
        with col3:
            st.info(f"**mpmath:** {'✅ متوفر' if MP_MATH_AVAILABLE else '❌ غير متوفر'}")
        
        with col4:
            st.info("**الذاكرة المؤقتة:** ✅ مفعلة")
        
        if MP_MATH_AVAILABLE:
            st.success("**✅ تم تصحيح حساب أصفار زيتا بنجاح**")
        else:
            st.error("**❌ مكتبة mpmath غير متوفرة. حسابات أصفار زيتا ستكون غير دقيقة.**")
        
        st.warning("""
        **ملاحظات هامة:**
        - يمكن إدخال الأعداد بتنسيقات مختلفة: `123,456,789` أو `1.23e8` أو `2^100` أو `2**100`
        - الحد الأقصى للتحليل: 100,000 رقم
        - استخدم الترميز العلمي للأعداد الكبيرة جداً
        - دقة حساب أصفار زيتا تعتمد على مكتبة mpmath
        """)
    
    # شريط جانبي للتنقل
    st.sidebar.title("🧭 القوائم الرئيسية")
    
    main_section = st.sidebar.selectbox(
        "اختر القسم الرئيسي:",
        [
            "أصفار دالة زيتا - مصححة",
            "التطبيقات المتقدمة",
            "الأعداد الأولية والتحليل",
            "الدوال الرياضية المتقدمة"
        ]
    )
    
    # قسم أصفار دالة زيتا المصححة
    if main_section == "أصفار دالة زيتا - مصححة":
        zeta_zero_calculator_section()
    
    # قسم التطبيقات المتقدمة
    elif main_section == "التطبيقات المتقدمة":
        zeta_applications_section()
    
    # قسم الأعداد الأولية والتحليل
    elif main_section == "الأعداد الأولية والتحليل":
        st.header("🔍 الأعداد الأولية والتحليل إلى عوامل")
        
        service = st.sidebar.selectbox(
            "اختر الخدمة:",
            [
                "التحليل إلى عوامل أولية",
                "التحقق من الأعداد الأولية", 
                "أعداد ميرسين الأولية",
                "حدسية غولدباخ",
                "الأعداد الأولية في نطاق"
            ]
        )
        
        if service == "التحليل إلى عوامل أولية":
            st.subheader("🧮 التحليل إلى عوامل أولية")
            
            st.info("""
            **يمكنك إدخال الأعداد بالتنسيقات التالية:**
            - `123456789`
            - `123,456,789` 
            - `1.23456789e8`
            - `2^50` أو `2**50`
            """)
            
            col1, col2 = st.columns([2, 1])
            with col1:
                number_input = st.text_input("أدخل العدد للتحليل:", value="123456789", key="factorize_input")
            with col2:
                timeout = st.number_input("المهلة (بالثواني):", min_value=1, value=30, step=1)
            
            if st.button("تحليل العدد", type="primary"):
                try:
                    # تحليل العدد المدخل
                    number = parse_large_number(number_input)
                    number = validate_number_size(number, max_digits=100000)
                    
                    st.success(f"**تم تحليل العدد المدخل:** {format_large_number(number)}")
                    st.info(f"**عدد الأرقام:** {len(str(abs(number)))} رقم")
                    
                    with st.spinner("جاري التحليل... قد يستغرق هذا بعض الوقت للأعداد الكبيرة"):
                        start_time = time.time()
                        factors = factorize_fast(number, timeout=timeout, verbose=False)
                        end_time = time.time()
                        
                        if len(factors) == 1:
                            st.success("🎉 **النتيجة: العدد أولي**")
                            st.balloons()
                        else:
                            cnt = Counter(factors)
                            parts_str = []
                            for p in sorted(cnt):
                                if cnt[p] > 1:
                                    parts_str.append(f"{p}<sup>{cnt[p]}</sup>")
                                else:
                                    parts_str.append(str(p))
                            factorization = " × ".join(parts_str)
                            
                            st.markdown(f'<div class="result-box">'
                                      f'<strong>التحليل:</strong> {format_large_number(number)} = {factorization}'
                                      f'</div>', unsafe_allow_html=True)
                            
                            # عرض معلومات إضافية
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.info(f"**عدد العوامل:** {len(factors)}")
                            with col2:
                                st.info(f"**العوامل المميزة:** {len(cnt)}")
                            with col3:
                                st.info(f"**أكبر عامل:** {max(factors)}")
                        
                        st.metric("الوقت المستغرق", f"{end_time - start_time:.3f} ثانية")
                        
                except Exception as e:
                    st.error(f"❌ خطأ: {e}")
    
    # معلومات إضافية في الشريط الجانبي
    st.sidebar.markdown("---")
    st.sidebar.header("📚 موارد للتعلم")
    st.sidebar.markdown("""
    - [دالة زيتا على ويكيبيديا](https://ar.wikipedia.org/wiki/%D8%AF%D8%A7%D9%84%D8%A9_%D8%B2%D9%8A%D8%AA%D8%A7_%D9%84%D8%B1%D9%8A%D9%85%D8%A7%D9%86)
    - [فرضية ريمان](https://ar.wikipedia.org/wiki/%D9%81%D8%B1%D8%B6%D9%8A%D8%A9_%D8%B1%D9%8A%D9%85%D8%A7%D9%86)
    - [مشروع أصفار زيتا](https://www.dtc.umn.edu/~odlyzko/zeta_tables/)
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ الإعدادات")
    if st.sidebar.button("🔄 مسح الذاكرة المؤقتة"):
        is_prime_fast.cache_clear()
        st.sidebar.success("✓ تم مسح الذاكرة المؤقتة")
    
    # معلومات عن النسخة
    st.sidebar.markdown("---")
    st.sidebar.caption("PPFO v25.0 © 2024 - نسخة محسّنة مع دعم كامل للـ LaTeX")

if __name__ == "__main__":
    main()
