#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PPFO v28.0 Streamlit - تطبيق ويب متكامل لتحليل الأعداد باستخدام دالة زيتا
"""

import streamlit as st
import math
import time
import random
from functools import lru_cache
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# محاولة استيراد مكتبات مساعدة
try:
    import sympy
    SYMPY_AVAILABLE = True
except Exception:
    SYMPY_AVAILABLE = False

try:
    import gmpy2
    GMPY2_AVAILABLE = True
    mpz = gmpy2.mpz
except Exception:
    GMPY2_AVAILABLE = False
    mpz = int

try:
    import mpmath as mp
    MP_MATH_AVAILABLE = True
    mp.mp.dps = 50
except Exception:
    MP_MATH_AVAILABLE = False

# ===================== إعدادات Streamlit =====================

st.set_page_config(
    page_title="PPFO v28.0 - تحليل الأعداد بدالة زيتا",
    page_icon="🔢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تنسيق CSS مخصص
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .section-header {
        font-size: 1.8rem;
        color: #2e86ab;
        margin: 1.5rem 0 1rem 0;
        border-bottom: 2px solid #2e86ab;
        padding-bottom: 0.5rem;
    }
    .result-box {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        border-left: 5px solid #1f77b4;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .factor-box {
        background: white;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid #dee2e6;
    }
    .zeta-zero {
        background: linear-gradient(135deg, #fff3cd, #ffeaa7);
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #ffc107;
    }
</style>
""", unsafe_allow_html=True)

# ===================== دوال زيتا المتقدمة =====================

@st.cache_data(ttl=3600)
def zeta_zero_advanced(n, method="auto", precise=True, precision=30):
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
        167: 346.3478705660099473959364598161519,
        1000: 1419.4224809459956865,
        10000: 9877.7826540055011428
    }
    
    if n in known_zeros:
        return known_zeros[n]
    
    # استخدام mpmath إذا كانت متوفرة
    if MP_MATH_AVAILABLE and (method == "auto" or method == "mpmath"):
        try:
            mp.mp.dps = precision
            zero = mp.zetazero(n)
            return float(zero.imag)
        except:
            pass
    
    # تقدير تقريبي باستخدام الصيغة التحليلية
    if n <= 100:
        t = (2 * math.pi * (n - 1.125)) / math.log((n - 1.125) / (2 * math.pi))
    else:
        t = (2 * math.pi * n) / math.log(n)
        
        # تصحيح دقيق أكثر للأعداد الكبيرة
        t -= (math.log(2*math.pi) - 1) / (2*math.pi) * math.log(n)
        t += (math.log(2*math.pi)**2 - 2*math.log(2*math.pi) - 1) / (8*math.pi*math.log(n))
    
    return t if precise else round(t, 4)

def riemann_siegel_theta(t):
    """دالة ثيتا لريمان-سيغل"""
    if t == 0:
        return -math.pi/8
    result = (t/2) * math.log(t/(2*math.pi)) - t/2 - math.pi/8
    result += 1/(48*t) + 7/(5760*t**3) + 31/(80640*t**5)
    return result

def zeta_on_critical_line(t, terms=100):
    """تقدير دالة زيتا على الخط الحرج"""
    result = 0
    for n in range(1, terms + 1):
        result += math.cos(t * math.log(n)) / math.sqrt(n)
    return 2 * result

# ===================== دوال التحليل باستخدام زيتا =====================

def pi_approx_zeta(x, num_zeros=50):
    """تقدير دالة العد π(x) باستخدام أصفار زيتا"""
    if x < 2:
        return 0
    
    if not MP_MATH_AVAILABLE:
        return x / math.log(x)  # تقدير بسيط
    
    try:
        # استخدام الصيغة الصريحة مع أصفار زيتا
        li_x = logarithmic_integral(x)
        result = li_x
        
        # جمع مساهمة الأصفار غير التافهة
        for n in range(1, min(num_zeros, 100) + 1):
            try:
                gamma_n = zeta_zero_advanced(n)
                rho = 0.5 + 1j * gamma_n
                
                # Li(x^ρ) + Li(x^(1-ρ))
                term1 = logarithmic_integral(x ** rho.real) * math.cos(gamma_n * math.log(x))
                term2 = logarithmic_integral(x ** (1 - rho.real)) * math.cos(gamma_n * math.log(x))
                
                result -= 2 * (term1 + term2)
            except:
                continue
        
        return max(0, result)
    except:
        return x / math.log(x)

def logarithmic_integral(x):
    """التكامل اللوغاريتمي Li(x)"""
    if x <= 1:
        return 0
    
    # استخدام تقريب متسلسلة
    result = 0
    term = 1
    factorial = 1
    for k in range(1, 50):
        factorial *= k
        term *= math.log(x)
        current_term = term / (k * factorial)
        if abs(current_term) < 1e-15:
            break
        result += current_term
    
    return 0.57721566490153286060 + math.log(abs(math.log(x))) + result

def factorize_using_zeta_insight(n, max_zeros=50):
    """
    تحليل العدد باستخدام رؤى من دالة زيتا
    تستخدم معلومات عن توزيع الأعداد الأولية
    """
    if n < 2:
        return []
    
    if is_prime_fast(n):
        return [n]
    
    factors = []
    temp = n
    
    # استخدام تقدير π(x) لتحديد استراتيجية التحليل
    sqrt_n = int(math.sqrt(n))
    estimated_primes = pi_approx_zeta(sqrt_n, max_zeros)
    
    st.info(f"📊 تقدير عدد الأعداد الأولية ≤ √{n}: ~{estimated_primes:.0f}")
    
    # استراتيجية ذكية بناءً على حجم العدد
    if n < 10**6:
        return factorize_fast(n)
    elif n < 10**12:
        return factorize_with_pollard_brent(n)
    else:
        # للأعداد الكبيرة، استخدام خوارزمية متقدمة مع معلومات زيتا
        return factorize_large_with_zeta_guidance(n, max_zeros)

def factorize_large_with_zeta_guidance(n, max_zeros):
    """تحليل الأعداد الكبيرة باستخدام توجيه من دالة زيتا"""
    factors = []
    temp = n
    
    # البحث عن عوامل صغيرة أولاً
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    for p in small_primes:
        while temp % p == 0:
            factors.append(p)
            temp //= p
        if temp == 1:
            return factors
    
    # إذا بقي عدد كبير، استخدام Pollard's Rho مع تحسينات
    if temp > 1:
        remaining_factors = factorize_with_pollard_brent(temp)
        factors.extend(remaining_factors)
    
    return sorted(factors)

# ===================== خوارزميات التحليل الأساسية =====================

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

def factorize_with_pollard_brent(n):
    """خوارزمية Pollard's Brent المحسنة"""
    if n == 1:
        return []
    if is_prime_fast(n):
        return [n]
    
    def brent(n):
        if n % 2 == 0:
            return 2
        y, c, m = random.randint(1, n-1), random.randint(1, n-1), random.randint(1, n-1)
        g, r, q = 1, 1, 1
        while g == 1:
            x = y
            for _ in range(r):
                y = (pow(y, 2, n) + c) % n
            k = 0
            while k < r and g == 1:
                ys = y
                for _ in range(min(m, r-k)):
                    y = (pow(y, 2, n) + c) % n
                    q = (q * abs(x - y)) % n
                g = math.gcd(q, n)
                k += m
            r *= 2
        if g == n:
            while True:
                ys = (pow(ys, 2, n) + c) % n
                g = math.gcd(abs(x - ys), n)
                if g > 1:
                    break
        return g
    
    factors = []
    stack = [n]
    
    while stack:
        current = stack.pop()
        if is_prime_fast(current):
            factors.append(current)
            continue
            
        factor = brent(current)
        if factor == current:
            factors.append(current)
        else:
            stack.append(factor)
            stack.append(current // factor)
    
    return sorted(factors)

# ===================== دوال رياضية مساعدة =====================

def mobius(n):
    """دالة موبيوس μ(n)"""
    if n == 1:
        return 1
    factors = factorize_fast(n)
    if len(factors) != len(set(factors)):
        return 0
    return (-1) ** len(factors)

def liouville_lambda(n):
    """دالة ليوڤيل λ(n)"""
    factors = factorize_fast(n)
    return (-1) ** len(factors)

def euler_totient(n):
    """دالة أويلر φ(n)"""
    if n == 1:
        return 1
    factors = set(factorize_fast(n))
    result = n
    for p in factors:
        result *= (1 - 1/p)
    return int(result)

# ===================== الواجهة الرئيسية =====================

def main():
    st.markdown('<h1 class="main-header">🔢 PPFO v28.0 - تحليل الأعداد باستخدام دالة زيتا</h1>', unsafe_allow_html=True)
    
    # شريط جانبي للإعدادات
    with st.sidebar:
        st.header("⚙️ الإعدادات")
        st.session_state.use_zeta = st.checkbox("استخدام رؤى دالة زيتا", value=True)
        st.session_state.max_zeros = st.slider("عدد أصفار زيتا المستخدمة", 10, 200, 50)
        st.session_state.precision = st.selectbox("دقة الحساب", [15, 30, 50, 100], index=1)
        
        st.header("📊 معلومات النظام")
        st.write(f"**SymPy:** {'🟢 متوفر' if SYMPY_AVAILABLE else '🔴 غير متوفر'}")
        st.write(f"**GMPY2:** {'🟢 متوفر' if GMPY2_AVAILABLE else '🔴 غير متوفر'}")
        st.write(f"**mpmath:** {'🟢 متوفر' if MP_MATH_AVAILABLE else '🔴 غير متوفر'}")
    
    # تبويبات رئيسية
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 تحليل الأعداد", "ζ دالة زيتا", "📈 إحصائيات أولية", "ℹ️ حول التطبيق"])
    
    with tab1:
        st.markdown('<div class="section-header">تحليل الأعداد إلى عوامل أولية</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            number_input = st.text_input("أدخل العدد للتحليل:", value="123456789")
            method = st.selectbox("طريقة التحليل:", [
                "تلقائي (باستخدام زيتا)", 
                "تقليدي", 
                "Pollard-Brent"
            ])
        
        with col2:
            st.write("**أمثلة سريعة:**")
            if st.button("عدد أولي كبير (982451653)"):
                number_input = "982451653"
            if st.button("عدد مركب كبير (1234567890123)"):
                number_input = "1234567890123"
            if st.button("قوة أولية (2^127 - 1)"):
                number_input = "170141183460469231731687303715884105727"
        
        if st.button("🔍 تحليل العدد", type="primary"):
            try:
                n = int(number_input.replace(',', ''))
                
                with st.spinner("جاري التحليل..."):
                    start_time = time.time()
                    
                    if method == "تلقائي (باستخدام زيتا)" and st.session_state.use_zeta:
                        factors = factorize_using_zeta_insight(n, st.session_state.max_zeros)
                    elif method == "Pollard-Brent":
                        factors = factorize_with_pollard_brent(n)
                    else:
                        factors = factorize_fast(n)
                    
                    end_time = time.time()
                    
                    # عرض النتائج
                    with st.container():
                        st.markdown('<div class="result-box">', unsafe_allow_html=True)
                        
                        if len(factors) == 1:
                            st.success(f"🎯 **العدد {n} هو عدد أولي!**")
                        else:
                            cnt = Counter(factors)
                            factorization_str = " × ".join([
                                f"{p}<sup>{e}</sup>" if e > 1 else str(p) 
                                for p, e in cnt.items()
                            ])
                            
                            st.success(f"**التحليل:** {n} = {factorization_str}")
                            
                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                st.metric("عدد العوامل", len(factors))
                            with col_b:
                                st.metric("العوامل المميزة", len(cnt))
                            with col_c:
                                st.metric("الوقت المستغرق", f"{end_time - start_time:.3f} ثانية")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # معلومات إضافية
                        if len(factors) > 1:
                            with st.expander("📊 تحليل مفصل للعوامل"):
                                for prime in sorted(cnt.keys()):
                                    exp = cnt[prime]
                                    st.write(f"- **{prime}**: أس {exp} (مساهمة: {prime**exp})")
                
            except Exception as e:
                st.error(f"❌ خطأ في التحليل: {e}")
    
    with tab2:
        st.markdown('<div class="section-header">دالة زيتا وأصفارها غير التافهة</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            zero_number = st.number_input("رقم الصفر غير التافه:", min_value=1, value=167, step=1)
            if st.button("حساب الصفر"):
                with st.spinner("جاري حساب الصفر..."):
                    try:
                        zero_value = zeta_zero_advanced(zero_number, precision=st.session_state.precision)
                        st.markdown('<div class="zeta-zero">', unsafe_allow_html=True)
                        st.success(f"**الصفر غير التافه رقم {zero_number}:**")
                        st.latex(f"\\rho_{{{zero_number}}} = \\frac{{1}}{{2}} + i \\cdot {zero_value:.10f}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"خطأ في الحساب: {e}")
        
        with col2:
            st.subheader("أمثلة على أصفار زيتا")
            example_zeros = [1, 10, 100, 167, 1000]
            for n in example_zeros:
                zero_val = zeta_zero_advanced(n, precision=15)
                st.write(f"**الصفر {n}:** {zero_val:.6f}")
        
        # رسم بياني لأصفار زيتا
        st.subheader("📈 توزيع أصفار زيتا على الخط الحرج")
        num_zeros_to_plot = st.slider("عدد الأصفار للرسم:", 10, 100, 50)
        
        if st.button("رسم الأصفار"):
            zeros = []
            with st.spinner("جاري حساب الأصفار..."):
                for i in range(1, num_zeros_to_plot + 1):
                    zeros.append(zeta_zero_advanced(i, precision=15))
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.scatter([0.5] * len(zeros), zeros, alpha=0.7, s=30)
            ax.set_xlabel('الجزء الحقيقي')
            ax.set_ylabel('الجزء التخيلي')
            ax.set_title('أصفار دالة زيتا غير التافهة على الخط الحرج')
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
    
    with tab3:
        st.markdown('<div class="section-header">إحصائيات الأعداد الأولية باستخدام زيتا</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            x_value = st.number_input("القيمة x لحساب π(x):", min_value=2, value=1000, step=100)
            if st.button("حساب π(x)"):
                with st.spinner("جاري الحساب..."):
                    actual_count = len([p for p in range(2, x_value + 1) if is_prime_fast(p)])
                    zeta_estimate = pi_approx_zeta(x_value, st.session_state.max_zeros)
                    
                    st.metric("π(x) الفعلي", actual_count)
                    st.metric("π(x) المقدر بزيتا", f"{zeta_estimate:.1f}")
                    st.metric("الفرق", f"{abs(actual_count - zeta_estimate):.1f}")
        
        with col2:
            st.subheader("دوال نظرية الأعداد")
            n_func = st.number_input("ادخل n لحساب الدوال:", min_value=1, value=100, step=1)
            
            if n_func > 0:
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("μ(n) - موبيوس", mobius(n_func))
                with col_b:
                    st.metric("λ(n) - ليوڤيل", liouville_lambda(n_func))
                with col_c:
                    st.metric("φ(n) - أويلر", euler_totient(n_func))
        
        # رسم بياني لتوزيع الأعداد الأولية
        st.subheader("مقارنة تقديرات دالة العد الأولي")
        max_x = st.slider("الحد الأقصى لـ x:", 100, 10000, 1000, step=100)
        
        if st.button("إنشاء الرسم البياني"):
            x_values = list(range(100, max_x + 1, 100))
            actual_counts = []
            zeta_estimates = []
            
            with st.spinner("جاري الحساب..."):
                for x in x_values:
                    actual_counts.append(len([p for p in range(2, x + 1) if is_prime_fast(p)]))
                    zeta_estimates.append(pi_approx_zeta(x, 30))
            
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(x_values, actual_counts, 'b-', label='π(x) الفعلي', linewidth=2)
            ax.plot(x_values, zeta_estimates, 'r--', label='π(x) المقدر بزيتا', linewidth=2)
            ax.set_xlabel('x')
            ax.set_ylabel('π(x)')
            ax.set_title('مقارنة دالة العد الأولي الفعلية مع التقدير باستخدام زيتا')
            ax.legend()
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
    
    with tab4:
        st.markdown('<div class="section-header">حول التطبيق والنظرية الرياضية</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 🧮 PPFO v28.0 - الإصدار المتكامل مع دالة زيتا -- برمجة د.محمد سعودي © 2025
        
        **العلاقة بين دالة زيتا وتحليل الأعداد:**
        
        دالة زيتا لريمان تعطينا معلومات عميقة عن توزيع الأعداد الأولية. من خلال الصيغة الصريحة:
        
        $$
        \\pi(x) = \\text{li}(x) - \\sum_{\\rho} \\text{li}(x^{\\rho}) - \\log 2 + \\int_x^{\\infty} \\frac{dt}{t(t^2-1)\\log t}
        $$
        
        حيث:
        - $\\pi(x)$: عدد الأعداد الأولية ≤ x
        - $\\text{li}(x)$: التكامل اللوغاريتمي
        - $\\rho$: الأصفار غير التافهة لدالة زيتا
        
        **التطبيق في تحليل الأعداد:**
        
        باستخدام معرفة توزيع الأعداد الأولية من دالة زيتا، يمكننا تحسين خوارزميات التحليل عن طريق:
        
        1. تحديد حدود البحث الأمثل للعوامل
        2. توقع كثافة الأعداد الأولية في نطاقات معينة
        3. تحسين استراتيجيات البحث عن العوامل
        
        **الميزات الرئيسية:**
        - تحليل الأعداد باستخدام رؤى من دالة زيتا
        - حساب أصفار زيتا غير التافهة بدقة عالية
        - تقدير دالة العد الأولي π(x)
        - خوارزميات تحليل متقدمة (Pollard-Brent)
        - تصورات بيانية للبيانات النظرية-العددية
        
        **الخوارزميات المدعومة:**
        - التحليل التقليدي
        - خوارزمية Pollard's Rho (Brent variant)
        - استخدام معلومات توزيع الأعداد الأولية من زيتا
        - دوال نظرية-عددية مساعدة (موبيوس، ليوڤيل، أويلر)
        """)
        
        st.info("""
        **ملاحظة:** هذا التطبيق يوضح العلاقة النظرية بين دالة زيتا وتحليل الأعداد. 
        في الممارسة العملية، الخوارزميات التقليدية غالباً ما تكون أكثر كفاءة، 
        لكن الفهم النظري يساعد في تطوير خوارزميات أفضل.
        """)

if __name__ == "__main__":
    main()
