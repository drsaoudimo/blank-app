#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PPFO v24.0 — تطبيق الويب الرياضي المتقدم مع خوارزميات التحليل السريع
نسخة Streamlit مع دعم كامل للأعداد الكبيرة وتحسينات السرعة
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
    page_title="PPFO v24.0 - التحليل الرياضي المتقدم",
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
    .fast-analysis {
        background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .result-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ========== دوال رياضية أساسية محسنة ==========
@lru_cache(maxsize=10000)
def is_prime_fast(n: int) -> bool:
    """نسخة محسنة وسريعة من التحقق من الأعداد الأولية"""
    n = int(n)
    if n < 2: 
        return False
    if n in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29): 
        return True
    if n % 2 == 0: 
        return False
    
    # فحص القواسم الصغيرة أولاً
    small_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    for p in small_primes:
        if n % p == 0:
            return n == p
    
    # Miller-Rabin محسن
    d, s = n - 1, 0
    while d % 2 == 0: 
        d //= 2
        s += 1
    
    bases = [2, 325, 9375, 28178, 450775, 9780504, 1795265022] if n > 10**12 else [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    
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

def gcd(a, b):
    """حساب القاسم المشترك الأكبر"""
    while b:
        a, b = b, a % b
    return a

def pollard_rho_optimized(n, timeout_time=None):
    """خوارزمية Pollard's Rho محسنة وسريعة"""
    if n % 2 == 0: 
        return 2
    if n % 3 == 0: 
        return 3
    
    # استخدام بذور عشوائية محسنة
    x = random.randint(2, n-2)
    y = x
    c = random.randint(1, n-1)
    d = 1
    
    f = lambda x: (x * x + c) % n
    
    iterations = 0
    max_iterations = 100000
    
    while d == 1 and iterations < max_iterations:
        if timeout_time and time.time() > timeout_time:
            return None
            
        x = f(x)
        y = f(f(y))
        d = gcd(abs(x - y), n)
        
        iterations += 1
        
        if d == n:
            break
            
    return d if 1 < d < n else None

def trial_division_fast(n, limit=10000):
    """تحليل سريع بالقسمة المتكررة"""
    factors = []
    
    # اختبار القسمة على 2
    while n % 2 == 0:
        factors.append(2)
        n //= 2
    
    # اختبار القسمة على الأعداد الفردية الصغيرة
    f = 3
    while f * f <= n and f <= limit:
        if n % f == 0:
            factors.append(f)
            n //= f
        else:
            f += 2
    
    return factors, n

# ========== خوارزمية التحليل السريع الرئيسية ==========
def factorize_fast(n: int, timeout=60, verbose=True):
    """الخوارزمية الرئيسية للتحليل السريع - مستوحاة من PPFO v24.0"""
    n = int(n)
    if n < 2:
        return []
    if is_prime_fast(n):
        return [n]
    
    factors = []
    start_time = time.time()
    timeout_time = start_time + timeout if timeout else None
    
    # المرحلة 1: إزالة عوامل 2
    while n % 2 == 0:
        factors.append(2)
        n //= 2
    
    # المرحلة 2: فحص الأعداد الأولية الصغيرة
    small_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 
                   53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107,
                   109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167]
    
    for p in small_primes:
        while n % p == 0:
            factors.append(p)
            n //= p
        if n == 1:
            return sorted(factors)
        if timeout_time and time.time() > timeout_time:
            if verbose:
                st.warning("⏱️ تم الوصول إلى مهلة التحليل في المرحلة 2")
            factors.append(n)
            return sorted(factors)
    
    # إذا بقي العدد أولي
    if is_prime_fast(n):
        factors.append(n)
        return sorted(factors)
    
    # المرحلة 3: Pollard's Rho للعوامل المتوسطة
    remaining = n
    max_rho_attempts = 5
    
    for attempt in range(max_rho_attempts):
        if timeout_time and time.time() > timeout_time:
            if verbose:
                st.warning("⏱️ تم الوصول إلى مهلة التحليل في المرحلة 3")
            factors.append(remaining)
            break
            
        if remaining == 1:
            break
            
        if is_prime_fast(remaining):
            factors.append(remaining)
            break
        
        factor = pollard_rho_optimized(remaining, timeout_time)
        
        if factor is None:
            # إذا فشل Pollard Rho، نضيف العدد المتبقي
            factors.append(remaining)
            break
        
        # تحليل العامل المكتشف
        sub_factors = factorize_fast(factor, timeout=(timeout_time - time.time()) if timeout_time else None, verbose=verbose)
        factors.extend(sub_factors)
        remaining //= factor
    
    if remaining > 1 and remaining != n:
        factors.append(remaining)
    
    return sorted(factors)

def factorize_large_optimized(n, timeout=60):
    """خوارزمية متقدمة للتحليل السريع للأعداد الكبيرة"""
    n_int = int(n)
    
    # للعدد الكبير جداً، نستخدم خوارزمية مخصصة
    if n_int < 10**15:
        return factorize_fast(n_int, timeout, verbose=False)
    
    factors = []
    remaining = n_int
    start_time = time.time()
    
    # المرحلة 1: عوامل صغيرة سريعة
    small_factors, remaining = trial_division_fast(remaining, limit=1000)
    factors.extend(small_factors)
    
    if remaining == 1:
        return factors
    
    # المرحلة 2: Pollard's Rho مع تحسينات
    timeout_time = start_time + timeout
    
    while remaining > 1 and time.time() < timeout_time:
        if is_prime_fast(remaining):
            factors.append(remaining)
            break
            
        factor = pollard_rho_optimized(remaining, timeout_time)
        
        if factor is None:
            factors.append(remaining)
            break
            
        # تحليل سريع للعامل
        if factor < 10**10 or is_prime_fast(factor):
            factors.append(factor)
        else:
            sub_factors = factorize_fast(factor, timeout=5, verbose=False)
            factors.extend(sub_factors)
            
        remaining //= factor
    
    if remaining > 1:
        factors.append(remaining)
    
    return sorted(factors)

def verify_factorization(original, factors):
    """التحقق من صحة التحليل"""
    try:
        product = 1
        for factor in factors:
            product *= int(factor)
        return product == original, product
    except:
        return False, 0

# ========== واجهة Streamlit المحسنة ==========
def main():
    st.markdown('<div class="main-header">🧮 PPFO v24.0 - التحليل الرياضي المتقدم</div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("⚡ خوارزميات سريعة")
        st.markdown('<div class="fast-analysis">🚀 تحليل سريع للأعداد الكبيرة</div>', unsafe_allow_html=True)
        
        st.write("**المميزات:**")
        st.write("✅ تحليل سريع باستخدام Pollard's Rho")
        st.write("✅ فحص أولية محسن")
        st.write("✅ تحليل متعدد المراحل")
        st.write("✅ دعم الأعداد الكبيرة جداً")
        
        analysis_mode = st.selectbox(
            "وضع التحليل:",
            ["سريع", "متوازن", "شامل"],
            index=0,
            help="الوضع السريع مناسب للأعداد الكبيرة"
        )
        
        show_steps = st.checkbox("عرض تفاصيل التحليل", value=True)
        show_charts = st.checkbox("عرض المخططات", value=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔢 إدخال العدد")
        input_method = st.radio("طريقة الإدخال:", ["رقم عادي", "رقم سداسي عشري", "تعبير رياضي"])
        
        if input_method == "رقم عادي":
            N_str = st.text_input("أدخل العدد المراد تحليله:", value="900090009000900090099009900990099009909990999099909991")
        elif input_method == "رقم سداسي عشري":
            hex_str = st.text_input("أدخل العدد بصيغة سداسية عشرية:", value="0x10B2D4E5A3D4E81")
            N_str = hex_str
        else:
            expr = st.text_input("أدخل تعبيراً رياضياً:", value="722817036322379041 * 909090909090909091 * 1369778187490592461")
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
            
            if bit_length > 150:
                st.warning("⚠️ هذا العدد كبير جداً")
            elif bit_length > 100:
                st.info("🔍 العدد كبير - التحليل قد يستغرق بضع ثوان")
            
            if is_prime_fast(N):
                st.success("✅ العدد أولي")
            else:
                st.info("🔢 العدد مركب")
                
        except Exception as e:
            st.error(f"❌ خطأ في الإدخال: {e}")
            return
    
    st.subheader("⚙️ إعدادات التحليل")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if analysis_mode == "سريع":
            timeout = st.slider("الوقت الأقصى (ثواني)", 1, 300, 30)
        elif analysis_mode == "متوازن":
            timeout = st.slider("الوقت الأقصى (ثواني)", 1, 600, 60)
        else:
            timeout = st.slider("الوقت الأقصى (ثواني)", 1, 1200, 120)
    
    with col2:
        save_results = st.checkbox("حفظ النتائج", value=False)
    
    if st.button("🚀 بدء التحليل السريع", type="primary", use_container_width=True):
        if N < 2:
            st.error("❌ العدد يجب أن يكون أكبر من 1")
            return
        
        # تحذير للأعداد الكبيرة جداً
        if bit_length > 200:
            st.warning("🧠 العدد كبير جداً - قد يستغرق التحليل عدة دقائق")
        
        with st.spinner(f"جاري التحليل السريع باستخدام خوارزميات PPFO v24.0..."):
            try:
                start_time = time.time()
                
                # اختيار خوارزمية التحليل بناءً على الوضع
                if analysis_mode == "سريع":
                    factors = factorize_large_optimized(N, timeout=timeout)
                elif analysis_mode == "متوازن":
                    factors = factorize_fast(N, timeout=timeout, verbose=False)
                else:
                    # وضع شامل - محاولات متعددة
                    factors = factorize_large_optimized(N, timeout=timeout)
                    if len(factors) == 1 and factors[0] == N:
                        # إذا فشل التحليل الأولي، نجرب مرة أخرى
                        factors = factorize_fast(N, timeout=timeout, verbose=False)
                
                end_time = time.time()
                analysis_time = end_time - start_time
                
                # التحقق من صحة التحليل
                is_correct, product = verify_factorization(N, factors)
                
                # عرض النتائج
                display_advanced_results(N, factors, is_correct, product, analysis_time, show_steps, show_charts)
                
            except Exception as e:
                st.error(f"❌ فشل التحليل: {e}")

def display_advanced_results(original_number, factors, is_correct, product, analysis_time, show_steps=True, show_charts=True):
    """عرض النتائج المتقدمة"""
    
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
        st.metric("⏱️ الوقت", f"{analysis_time:.3f} ثانية")
    
    # التحقق من صحة التحليل
    if is_correct:
        st.success("🎯 التحليل صحيح - حاصل ضرب العوامل يساوي العدد الأصلي")
    else:
        st.error("❌ هناك خطأ في التحليل - حاصل الضرب لا يساوي العدد الأصلي")
        
        with st.expander("🔍 تفاصيل الخطأ"):
            st.write(f"**العدد الأصلي:** {original_number}")
            st.write(f"**حاصل الضرب المحسوب:** {product}")
            st.write(f"**الفرق:** {original_number - product}")
    
    # تحليل العوامل
    st.subheader("🔍 العوامل المكتشفة")
    
    if len(factors) > 1 or (len(factors) == 1 and factors[0] != original_number):
        # التحقق من أولية جميع العوامل
        non_prime_factors = [f for f in set(factors) if not is_prime_fast(f) and f > 1]
        prime_factors = [f for f in set(factors) if is_prime_fast(f) and f > 1]
        
        if non_prime_factors:
            st.error(f"❌ يوجد {len(non_prime_factors)} عامل غير أولي")
            # محاولة تحليل العوامل غير الأولية
            with st.spinner("جاري تحليل العوامل غير الأولية..."):
                all_prime_factors = []
                for factor in factors:
                    if is_prime_fast(factor):
                        all_prime_factors.append(factor)
                    else:
                        sub_factors = factorize_fast(factor, timeout=10, verbose=False)
                        all_prime_factors.extend(sub_factors)
                
                factors = all_prime_factors
                # التحقق مرة أخرى
                is_correct, product = verify_factorization(original_number, factors)
                
                if is_correct:
                    st.success("✅ تم تحليل جميع العوامل إلى عوامل أولية")
        
        factor_counts = Counter(factors)
        
        # عرض العوامل
        st.markdown("### 🧮 العوامل الأولية:")
        factor_str = " × ".join([f"**{factor}**" if count == 1 else f"**{factor}**^{count}" 
                               for factor, count in factor_counts.items()])
        st.markdown(f"<div class='result-card'>{factor_str}</div>", unsafe_allow_html=True)
        
        # جدول العوامل
        factors_data = []
        for factor, count in factor_counts.items():
            prime_status = "✅" if is_prime_fast(factor) else "❌"
            factors_data.append({
                "العامل": factor,
                "التكرار": count,
                "الحجم (بت)": factor.bit_length(),
                "أولي": prime_status
            })
        
        factors_df = pd.DataFrame(factors_data)
        st.dataframe(factors_df, use_container_width=True)
        
        # مخططات
        if show_charts and len(factors_df) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.pie(factors_df, names='العامل', values='التكرار', 
                            title='توزيع العوامل حسب التكرار')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(factors_df, x='العامل', y='الحجم (بت)',
                            title='حجم العوامل بالبت', color='أولي')
                st.plotly_chart(fig, use_container_width=True)
        
        # الصيغة الرياضية
        st.subheader("🧪 الصيغة الرياضية الكاملة")
        latex_str = " × ".join([f"{factor}^{{{count}}}" if count > 1 else f"{factor}" 
                              for factor, count in factor_counts.items()])
        
        if is_correct:
            st.latex(f"{original_number} = {latex_str}")
        else:
            st.warning(f"⚠️ الصيغة غير صحيحة: {original_number} \\neq {latex_str}")
        
    else:
        st.warning("⚠️ لم يتم العثور على عوامل - العدد قد يكون أولياً")
        if is_prime_fast(original_number):
            st.success(f"✅ {original_number} هو عدد أولي")
    
    # إحصائيات التحليل
    if show_steps:
        st.subheader("📈 إحصائيات التحليل")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("سرعة التحليل", f"{analysis_time:.3f} ثانية")
        
        with col2:
            efficiency = len(factors) / analysis_time if analysis_time > 0 else 0
            st.metric("كفاءة التحليل", f"{efficiency:.1f} عامل/ثانية")
        
        with col3:
            success_rate = "عالية" if is_correct else "منخفضة"
            st.metric("معدل النجاح", success_rate)

def performance_test():
    """اختبار أداء الخوارزمية"""
    st.sidebar.subheader("🧪 اختبار الأداء")
    
    test_numbers = [
        ("عدد صغير", 123456789),
        ("عدد متوسط", 123456789012345),
        ("عدد كبير", 900090009000900090099009900990099009909990999099909991)
    ]
    
    for name, number in test_numbers:
        if st.sidebar.button(f"اختبار {name}"):
            with st.sidebar:
                st.write(f"**اختبار {name}:**")
                start_time = time.time()
                factors = factorize_fast(number, timeout=30, verbose=False)
                end_time = time.time()
                st.write(f"الوقت: {end_time - start_time:.3f} ثانية")
                st.write(f"العوامل: {len(factors)}")
                if len(factors) <= 5:
                    st.write(factors)

if __name__ == "__main__":
    performance_test()
    main()
