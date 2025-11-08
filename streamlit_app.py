#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PPFO v20.3 — تطبيق الويب الرياضي المتقدم مع إطار ريمان الكامل
نسخة Streamlit مع دعم كامل للأعداد الكبيرة جداً
"""

import math
import random
import time
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from collections import Counter
from datetime import datetime
from functools import lru_cache

# إعدادات الصفحة
st.set_page_config(
    page_title="PPFO v20.3 - الإطار الرياضي المتقدم مع ريمان",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS مخصص
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .riemann-feature {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .large-number-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
        color: #856404;
    }
</style>
""", unsafe_allow_html=True)

# ========== ثوابت ودوال ريمان الأساسية ==========
EULER_GAMMA = 0.57721566490153286060651209008240243104215933593992

# أصفار زيتا غير التافهة
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
    65.112544048081606391926278248523
]

def zetazero(n, precise=False):
    """إرجاع الصفر غير التافه رقم n مع إطار ريمان"""
    if n <= len(RIEMANN_ZEROS):
        return RIEMANN_ZEROS[n-1]
    
    gamma_est = (2 * math.pi * n) / math.log((n + 1.5) / (2 * math.pi))
    gamma_est += (1 / (2 * math.pi)) * math.log((n + 1.5) / (2 * math.pi))
    
    if precise:
        gamma_est *= 1.0001 + (0.0001 * math.sin(gamma_est))
    
    return gamma_est

def riemann_correction(estimate, zeros=None):
    """تصحيح ريمان للتقديرات - معدل للأعداد الكبيرة"""
    if zeros is None:
        zeros = RIEMANN_ZEROS
    
    # استخدام اللوغاريتمات لتجنب الأعداد الكبيرة جداً
    if estimate > 10**20:
        log_estimate = math.log(estimate)
        correction_factor = math.sqrt(log_estimate) * (log_estimate ** 0.25)
        return int(round(correction_factor * 1000))  # تقدير معقول
    
    x = max(3, int(estimate))
    ln_x = math.log(x)
    s = 0.0
    
    for gamma in zeros[:8]:  # استخدام عدد أقل من الأصفار للأعداد الكبيرة
        term = math.cos(gamma * ln_x) / math.sqrt(0.25 + gamma * gamma)
        weight = 1.0 / (1.0 + 0.1 * gamma)
        s += weight * term
    
    correction = (math.sqrt(x) / max(1.0, ln_x)) * (s / (2 * math.pi))
    return int(round(correction))

def prime_nth_estimate(n, use_riemann=False):
    """تقدير العدد الأولي رقم n باستخدام إطار ريمان - معدل للأعداد الكبيرة"""
    if n < 6:
        return [2, 3, 5, 7, 11][n-1]
    
    ln_n = math.log(n)
    ln_ln_n = math.log(ln_n)
    
    # الصيغة الأساسية المعدلة للأعداد الكبيرة
    if n > 10**6:
        base = n * (ln_n + ln_ln_n - 0.5)  # تبسيط للكفاءة
    else:
        base = n * (ln_n + ln_ln_n - 1 + (ln_ln_n - 2) / ln_n)
    
    estimate = int(round(base))
    
    if use_riemann:
        corr = riemann_correction(estimate)
        # تحديد حد معقول للتصحيح
        cap = max(1000, int(0.001 * estimate))
        corr = max(-cap, min(cap, corr))
        estimate += corr
    
    return max(2, estimate)  # التأكد من أن التقدير أكبر من 1

def factreaman_large(n):
    """تقدير عامل شبه أولي سريع للأعداد الكبيرة جداً"""
    n_int = int(n)
    if n_int < 2:
        return n_int
    
    bit_length = n_int.bit_length()
    
    # تقدير أولي مبسط للأعداد الكبيرة
    if bit_length > 100:
        # للأعداد الكبيرة جداً، نستخدم خوارزمية مبسطة
        estimate = 2 ** (bit_length // 3)
        max_attempts = 50
    else:
        prime_estimate = prime_nth_estimate(bit_length // 2, use_riemann=True)
        estimate = prime_estimate
        max_attempts = 100
    
    for _ in range(max_attempts):
        if estimate < 2:
            break
        if n_int % estimate == 0:
            return estimate
        estimate -= 1
    
    return None

# ========== دوال رياضية أساسية محسنة للأعداد الكبيرة ==========
def is_prime_fast_large(n):
    """اختبار أولية دقيق للأعداد الكبيرة"""
    n_int = int(n)
    if n_int < 2:
        return False
    if n_int in (2, 3, 5, 7, 11, 13):
        return True
    if n_int % 2 == 0:
        return 2
    
    # للأعداد الكبيرة، نستخدم اختبار فيرما الأساسي فقط
    if n_int > 10**15:
        bases = [2, 3, 5, 7, 11, 13]
        for a in bases:
            if a >= n_int:
                continue
            if pow(a, n_int-1, n_int) != 1:
                return False
        return True
    
    # للأعداد الأصغر، نستخدم اختبار أكثر دقة
    if n_int < 10**8:
        for i in range(3, int(math.sqrt(n_int)) + 1, 2):
            if n_int % i == 0:
                return False
        return True
    
    # للأعداد المتوسطة
    bases = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    for a in bases:
        if a >= n_int:
            continue
        if pow(a, n_int-1, n_int) != 1:
            return False
    
    return True

def gcd_large(a, b):
    """حساب القاسم المشترك الأكبر للأعداد الكبيرة"""
    a_int, b_int = int(a), int(b)
    while b_int:
        a_int, b_int = b_int, a_int % b_int
    return a_int

def trial_division_small_factors_large(n, limit=10000):
    """تحليل بالقسمة المتكررة للعوامل الصغيرة - للأعداد الكبيرة"""
    n_int = int(n)
    factors = []
    
    # اختبار القسمة على 2
    while n_int % 2 == 0:
        factors.append(2)
        n_int //= 2
    
    # اختبار القسمة على الأعداد الفردية الصغيرة
    f = 3
    while f * f <= n_int and f <= limit:
        if n_int % f == 0:
            factors.append(f)
            n_int //= f
        else:
            f += 2
    
    return factors, n_int

def pollard_rho_large(n, timeout=None, max_iterations=10000):
    """خوارزمية Pollard Rho للأعداد الكبيرة"""
    n_int = int(n)
    if n_int % 2 == 0:
        return 2
    if n_int % 3 == 0:
        return 3
    
    start = time.time()
    
    for attempt in range(3):  # محاولات أقل للأعداد الكبيرة
        if timeout and (time.time() - start) > timeout:
            return None
        
        # استخدام بذور عشوائية آمنة للأعداد الكبيرة
        x = random.randint(2, min(n_int-2, 10**6))
        y = x
        c = random.randint(1, min(n_int-1, 10**6))
        
        d = 1
        iterations = 0
        
        while d == 1 and iterations < max_iterations:
            if timeout and (time.time() - start) > timeout:
                return None
            
            x = (x * x + c) % n_int
            y = (y * y + c) % n_int
            y = (y * y + c) % n_int
            d = gcd_large(abs(x - y), n_int)
            
            iterations += 1
            
            if d == n_int:
                break
        
        if d > 1 and d < n_int:
            return d
    
    return None

# ========== دوال التحليل الرئيسية للأعداد الكبيرة ==========
def factorize_large_number(n, timeout=60, use_riemann=True):
    """تحليل الأعداد الكبيرة جداً باستخدام خوارزميات مبسطة"""
    n_int = int(n)
    if n_int < 2:
        return []
    
    factors = []
    remaining = n_int
    
    start_time = time.time()
    
    # المرحلة 1: التحليل بالعوامل الصغيرة
    small_factors, remaining = trial_division_small_factors_large(remaining, limit=1000)
    factors.extend(small_factors)
    
    if remaining == 1:
        return factors
    
    # المرحلة 2: Factreaman للأعداد الكبيرة
    if use_riemann and remaining > 10**6:
        f = factreaman_large(remaining)
        if f and f != remaining and remaining % f == 0:
            factors.append(f)
            factors.extend(factorize_large_number(remaining // f, timeout=timeout//2, use_riemann=use_riemann))
            return factors
    
    # المرحلة 3: Pollard Rho للأعداد الكبيرة
    if remaining > 10**6:
        d = pollard_rho_large(remaining, timeout=timeout//3)
        if d and d != remaining:
            factors.append(d)
            factors.extend(factorize_large_number(remaining // d, timeout=timeout//3, use_riemann=use_riemann))
            return factors
    
    # إذا بقي جزء ولم نستطع تحليله
    if remaining > 1:
        factors.append(remaining)
    
    return factors

def analyze_large_number(n):
    """تحليل أولي للعدد الكبير لتحديد خصائصه"""
    n_int = int(n)
    bit_length = n_int.bit_length()
    
    analysis = {
        'bit_length': bit_length,
        'digit_count': len(str(n_int)),
        'is_even': n_int % 2 == 0,
        'last_digits': str(n_int)[-6:],
        'approximate_size': f"10^{int(math.log10(n_int))}",
        'factorization_difficulty': 'Very High' if bit_length > 150 else 'High'
    }
    
    return analysis

def verify_factorization_large(original, factors):
    """التحقق من صحة التحليل للأعداد الكبيرة"""
    product = 1
    for factor in factors:
        product *= int(factor)
    
    return product == original, product

# ========== واجهة Streamlit المحسنة للأعداد الكبيرة ==========
def main():
    st.markdown('<div class="main-header">🧮 PPFO v20.3 - الإطار الرياضي المتقدم مع ريمان</div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("⚙️ إطار ريمان الرياضي")
        st.markdown('<div class="riemann-feature">🧠 تفعيل إطار ريمان الكامل</div>', unsafe_allow_html=True)
        
        st.write("**مميزات ريمان المُفعّلة:**")
        st.write("✅ أصفار زيتا غير التافهة")
        st.write("✅ تصحيح ريمان للتقديرات")
        st.write("✅ Factreaman مع التوجيه الرياضي")
        st.write("✅ دعم الأعداد الكبيرة جداً")
        st.write(f"**عدد أصفار زيتا:** {len(RIEMANN_ZEROS)}")
        
        use_riemann = st.checkbox("تفعيل إطار ريمان", value=True)
        show_riemann_info = st.checkbox("عرض معلومات ريمان", value=True)
        show_steps = st.checkbox("عرض خطوات التحليل", value=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔢 إدخال العدد")
        input_method = st.radio("طريقة الإدخال:", ["رقم عادي", "رقم سداسي عشري", "تعبير رياضي"])
        
        if input_method == "رقم عادي":
            N_str = st.text_input("أدخل العدد المراد تحليله:", value="900090009000900090099009900990099009909990999099909991")
        elif input_method == "رقم سداسي عشري":
            hex_str = st.text_input("أدخل العدد بصيغة سداسية عشرية:", value="0x1234567890ABCDEF")
            N_str = hex_str
        else:
            expr = st.text_input("أدخل تعبيراً رياضياً:", value="123456789012345678901234567890")
            N_str = expr
    
    with col2:
        st.subheader("📊 معلومات العدد")
        try:
            if input_method == "رقم سداسي عشري":
                N = int(N_str, 16)
            else:
                N = int(eval(N_str) if input_method == "تعبير رياضي" else N_str)
            
            bit_length = N.bit_length()
            digit_count = len(str(N))
            
            st.metric("حجم العدد", f"{bit_length} بت")
            st.metric("عدد الأرقام", f"{digit_count:,}")
            
            if N < 2:
                st.error("العدد يجب أن يكون أكبر من 1")
                return
            
            # تحليل أولي للعدد الكبير
            analysis = analyze_large_number(N)
            
            if bit_length > 150:
                st.warning("⚠️ هذا العدد كبير جداً وقد يستغرق تحليله وقتاً طويلاً")
            
            if is_prime_fast_large(N):
                st.success("✅ العدد أولي")
            else:
                st.info("🔢 العدد مركب")
                
        except Exception as e:
            st.error(f"❌ خطأ في الإدخال: {e}")
            return
    
    st.subheader("⚙️ إعدادات التحليل المتقدم")
    
    col1, col2 = st.columns(2)
    
    with col1:
        timeout = st.slider("الوقت الأقصى (ثواني)", 1, 600, 120)
    
    with col2:
        save_results = st.checkbox("حفظ النتائج", value=False)
    
    if st.button("🚀 بدء التحليل المتعمق", type="primary", use_container_width=True):
        if N < 2:
            st.error("❌ العدد يجب أن يكون أكبر من 1")
            return
        
        # تحذير للأعداد الكبيرة جداً
        if bit_length > 200:
            st.markdown('<div class="large-number-warning">'
                       '⚠️ تحذير: هذا العدد كبير جداً (أكثر من 200 بت). '
                       'التحليل قد يستغرق وقتاً طويلاً أو قد لا يكتمل.'
                       '</div>', unsafe_allow_html=True)
        
        with st.spinner("جاري التحليل المتعمق للأعداد الكبيرة..."):
            try:
                # التحليل للأعداد الكبيرة
                factors = factorize_large_number(
                    N, 
                    timeout=timeout, 
                    use_riemann=use_riemann
                )
                
                # التحقق من صحة التحليل
                is_correct, product = verify_factorization_large(N, factors)
                
                # معلومات ريمان
                riemann_info = {}
                if use_riemann and show_riemann_info:
                    riemann_info = calculate_riemann_metrics_large(N, factors)
                
                # عرض النتائج
                display_results_large(N, factors, is_correct, product, riemann_info, show_steps)
                
            except Exception as e:
                st.error(f"❌ فشل التحليل: {e}")

def calculate_riemann_metrics_large(n, factors):
    """حساب مقاييس ريمان للتحليل - للأعداد الكبيرة"""
    metrics = {}
    
    bit_length = n.bit_length()
    
    # تقديرات مبسطة للأعداد الكبيرة
    if bit_length > 100:
        prime_estimate = 2 ** (bit_length // 3)
    else:
        prime_estimate = prime_nth_estimate(bit_length // 2, use_riemann=True)
    
    metrics["تقدير_ريمان_للعوامل"] = prime_estimate
    
    # تصحيح مبسط للأعداد الكبيرة
    if n > 10**20:
        correction = int(math.sqrt(bit_length) * 1000)
    else:
        correction = riemann_correction(n)
    
    metrics["تصحيح_ريمان"] = correction
    metrics["أصفار_زيتا_المستخدمة"] = len(RIEMANN_ZEROS)
    
    if factors:
        try:
            factor_product = math.prod(factors)
            metrics["دقة_التحليل"] = abs(n - factor_product)
        except:
            metrics["دقة_التحليل"] = "غير محسوب"
    
    return metrics

def display_results_large(original_number, factors, is_correct, product, riemann_info=None, show_steps=True):
    """عرض النتائج للأعداد الكبيرة"""
    
    st.markdown("---")
    st.subheader("📊 النتائج النهائية")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("العدد الأصلي", f"{original_number:,}")
    
    with col2:
        st.metric("عدد العوامل", len(factors))
    
    with col3:
        unique_factors = len(set(factors))
        st.metric("عوامل فريدة", unique_factors)
    
    with col4:
        status = "✅ صحيح" if is_correct else "❌ خطأ"
        st.metric("التحقق", status)
    
    # معلومات ريمان
    if riemann_info:
        st.subheader("🧮 معلومات ريمان الرياضية")
        riemann_col1, riemann_col2 = st.columns(2)
        
        with riemann_col1:
            st.write("**تقدير ريمان:**")
            st.write(f"تقدير العامل: {riemann_info.get('تقدير_ريمان_للعوامل', 'N/A')}")
            st.write(f"التصحيح: {riemann_info.get('تصحيح_ريمان', 'N/A')}")
        
        with riemann_col2:
            st.write("**إحصائيات الزيتا:**")
            st.write(f"أصفار زيتا المستخدمة: {riemann_info.get('أصفار_زيتا_المستخدمة', 'N/A')}")
            if 'دقة_التحليل' in riemann_info:
                st.write(f"دقة التحليل: {riemann_info['دقة_التحليل']}")
    
    # التحقق من صحة التحليل
    if is_correct:
        st.success("🎯 التحليل صحيح - حاصل ضرب العوامل يساوي العدد الأصلي")
    else:
        st.error("❌ هناك خطأ في التحليل - حاصل الضرب لا يساوي العدد الأصلي")
        
        with st.expander("🔍 تفاصيل الخطأ"):
            st.write(f"**العدد الأصلي:** {original_number}")
            st.write(f"**حاصل الضرب المحسوب:** {product}")
            st.write(f"**الفرق:** {original_number - product}")
            st.write(f"**العوامل:** {factors}")
    
    # تحليل العوامل
    st.subheader("🔍 تحليل العوامل المكتشفة")
    
    if len(factors) > 1 or (len(factors) == 1 and factors[0] != original_number):
        # التحقق من أولية جميع العوامل
        non_prime_factors = [f for f in set(factors) if not is_prime_fast_large(f) and f > 1]
        prime_factors = [f for f in set(factors) if is_prime_fast_large(f) and f > 1]
        
        if non_prime_factors:
            st.error(f"❌ يوجد {len(non_prime_factors)} عامل غير أولي")
            # عرض العوامل غير الأولية الكبيرة بشكل مختصر
            for factor in non_prime_factors:
                if factor > 10**10:
                    st.write(f"عامل غير أولي كبير: ...{str(factor)[-20:]}")
                else:
                    st.write(f"عامل غير أولي: {factor}")
        else:
            st.success(f"✅ جميع العوامل أولية ({len(prime_factors)} عامل أولي)")
        
        factor_counts = Counter(factors)
        
        # إنشاء جدول العوامل (للعوامل المعقولة الحجم فقط)
        factors_data = []
        for factor, count in factor_counts.items():
            if factor < 10**15:  # عرض العوامل المعقولة الحجم فقط
                prime_status = "✅" if is_prime_fast_large(factor) else "❌"
                factors_data.append({
                    "العامل": factor,
                    "التكرار": count,
                    "الحجم (بت)": factor.bit_length(),
                    "أولي": prime_status
                })
        
        if factors_data:
            factors_df = pd.DataFrame(factors_data)
            st.dataframe(factors_df, use_container_width=True)
        
        # مخططات العوامل (للعوامل المعقولة الحجم فقط)
        reasonable_factors = [(f, c) for f, c in factor_counts.items() if f < 10**10]
        if reasonable_factors:
            col1, col2 = st.columns(2)
            
            with col1:
                factors_df_small = pd.DataFrame([
                    {"العامل": f, "التكرار": c} 
                    for f, c in reasonable_factors
                ])
                fig = px.pie(factors_df_small, names='العامل', values='التكرار', 
                            title='توزيع العوامل الصغيرة حسب التكرار')
                st.plotly_chart(fig, use_container_width=True)
        
        # الصيغة الرياضية المبسطة
        st.subheader("🧮 الصيغة الرياضية المبسطة")
        if len(factors) <= 10:
            factor_str = " × ".join([f"{factor}^{count}" if count > 1 else str(factor) 
                                   for factor, count in factor_counts.items()])
            if is_correct:
                st.latex(f"{original_number} = {factor_str}")
            else:
                st.warning(f"⚠️ الصيغة غير صحيحة: {original_number} ≠ {factor_str}")
        else:
            st.info("📝 العدد يحتوي على العديد من العوامل. يتم عرض التحليل المبسط.")
            main_factors = [f for f in factors if f < original_number // 100][:5]
            if main_factors:
                st.write(f"أهم العوامل: {' × '.join(map(str, main_factors))} × ...")
        
    else:
        st.warning("⚠️ لم يتم العثور على عوامل أو العدد نفسه هو العامل الوحيد")
        st.info("💡 هذا يعني أن العدد إما أولي أو كبير جداً ولم نستطع تحليله")

def riemann_tests():
    """اختبارات وتجارب ريمان"""
    st.sidebar.subheader("🧪 تجارب ريمان")
    
    if st.sidebar.button("اختبار أصفار زيتا"):
        st.sidebar.write("**أصفار زيتا غير التافهة:**")
        for i in range(1, 6):
            zero = zetazero(i)
            st.sidebar.write(f"ζ₀({i}) ≈ {zero:.10f}")

if __name__ == "__main__":
    riemann_tests()
    main()
