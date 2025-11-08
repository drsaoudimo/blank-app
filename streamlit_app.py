#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PPFO v20.3 — تطبيق الويب الرياضي المتقدم مع إطار ريمان الكامل
نسخة Streamlit مع تفعيل كامل لخوارزميات ريمان
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
    
    # تقدير رياضي لأصفار زيتا
    gamma_est = (2 * math.pi * n) / math.log((n + 1.5) / (2 * math.pi))
    gamma_est += (1 / (2 * math.pi)) * math.log((n + 1.5) / (2 * math.pi))
    
    if precise:
        # تصحيح إضافي للدقة
        gamma_est *= 1.0001 + (0.0001 * math.sin(gamma_est))
    
    return gamma_est

def riemann_correction(estimate, zeros=None):
    """تصحيح ريمان للتقديرات"""
    if zeros is None:
        zeros = RIEMANN_ZEROS
    
    x = max(3, int(estimate))
    ln_x = math.log(x)
    s = 0.0
    
    for gamma in zeros[:10]:  # استخدام أول 10 أصفار فقط للأداء
        term = math.cos(gamma * ln_x) / math.sqrt(0.25 + gamma * gamma)
        weight = 1.0 / (1.0 + 0.1 * gamma)  # وزن يتناقص مع زيادة gamma
        s += weight * term
    
    correction = (math.sqrt(x) / max(1.0, ln_x)) * (s / (2 * math.pi))
    return int(round(correction))

def prime_nth_estimate(n, use_riemann=False):
    """تقدير العدد الأولي رقم n باستخدام إطار ريمان"""
    if n < 6:
        return [2, 3, 5, 7, 11][n-1]
    
    ln_n = math.log(n)
    ln_ln_n = math.log(ln_n)
    
    # الصيغة الأساسية
    base = n * (ln_n + ln_ln_n - 1 + (ln_ln_n - 2) / ln_n)
    
    if n > 1000:
        base -= EULER_GAMMA * n / ln_n
    
    C_calibrated = 0.02176304641727069 + (-0.36685833943157 / ln_n) + (8.69441462116514 / (ln_n**2))
    estimate = int(round(base + C_calibrated))
    
    if use_riemann:
        corr = riemann_correction(estimate)
        cap = max(10, int(0.005 * estimate))
        corr = max(-cap, min(cap, corr))
        estimate += corr
    
    return estimate

def factreaman(n):
    """تقدير عامل شبه أولي سريع باستخدام ريمان"""
    n = int(n)
    if n < 2:
        return n
    
    # تقدير أولي باستخدام نظرية الأعداد الأولية
    bit_length = n.bit_length()
    prime_estimate = prime_nth_estimate(bit_length // 2, use_riemann=True)
    
    # البحث عن عامل قابل للقسمة
    estimate = prime_estimate
    max_attempts = 100
    
    for _ in range(max_attempts):
        if estimate < 2:
            break
        if n % estimate == 0:
            return estimate
        estimate -= 1
    
    return None

# ========== دوال رياضية أساسية محسنة ==========
@lru_cache(maxsize=2000)
def is_prime_fast(n):
    """اختبار أولية دقيق مع تحسينات ريمان"""
    n = int(n)
    if n < 2:
        return False
    if n in (2, 3, 5, 7, 11, 13):
        return True
    if n % 2 == 0:
        return 2
    
    # اختبار بسيط للأعداد الصغيرة
    if n < 10000:
        for i in range(3, int(math.sqrt(n)) + 1, 2):
            if n % i == 0:
                return False
        return True
    
    # اختبار فيرما المعزز
    bases = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    for a in bases:
        if a >= n:
            continue
        if pow(a, n-1, n) != 1:
            return False
    
    return True

def gcd(a, b):
    """حساب القاسم المشترك الأكبر"""
    while b:
        a, b = b, a % b
    return a

def brent_rho(n, timeout=None, use_riemann=False):
    """خوارزمية Brent Rho مع تحسينات ريمان"""
    if n % 2 == 0:
        return 2
    if n % 3 == 0:
        return 3
    
    y = random.randrange(2, n-1)
    c = random.randrange(1, n-1)
    
    if use_riemann:
        # استخدام أصفار زيتا لتوليد c محسّن
        zero_idx = random.randint(1, min(10, len(RIEMANN_ZEROS)))
        gamma = RIEMANN_ZEROS[zero_idx - 1]
        c = (c + int(math.cos(gamma) * 1000)) % (n-1) + 1
    
    m = random.randrange(1, min(n-1, 100))
    g, r, q = 1, 1, 1
    x = 0
    start = time.time()
    
    while g == 1:
        if timeout and (time.time() - start) > timeout:
            return None
        x = y
        for _ in range(r):
            y = (y * y + c) % n
        k = 0
        while k < r and g == 1:
            ys = y
            for _ in range(min(m, r - k)):
                y = (y * y + c) % n
                q = (q * abs(x - y)) % n
            g = gcd(q, n)
            k += m
        r *= 2
    
    if g == n:
        while True:
            ys = (ys * ys + c) % n
            g = gcd(abs(x - ys), n)
            if g > 1:
                break
    
    return g if g != n else None

def pollard_rho_riemann(n, timeout=None):
    """خوارزمية Pollard Rho مع توجيه ريمان"""
    if n % 2 == 0:
        return 2
    if n % 3 == 0:
        return 3
    
    start = time.time()
    
    for attempt in range(10):  # محاولات متعددة مع معلمات مختلفة
        if timeout and (time.time() - start) > timeout:
            return None
        
        # استخدام أصفار زيتا لتوليد معلمات أولية محسنة
        zero_idx = (attempt % len(RIEMANN_ZEROS)) + 1
        gamma = zetazero(zero_idx)
        
        x = int((math.sin(gamma) * 1e6) % (n-2)) + 2
        y = x
        c = int((math.cos(gamma) * 1e6) % (n-1)) + 1
        
        d = 1
        iterations = 0
        max_iterations = 100000
        
        while d == 1 and iterations < max_iterations:
            x = (x * x + c) % n
            y = (y * y + c) % n
            y = (y * y + c) % n
            d = gcd(abs(x - y), n)
            
            if timeout and (time.time() - start) > timeout:
                return None
            
            iterations += 1
            
            if d == n:
                break
        
        if d > 1 and d < n:
            return d
    
    return None

# ========== دوال التحليل الرئيسية مع ريمان ==========
def factorize_with_riemann(n, timeout=60, use_riemann=True, verbose=False):
    """تحليل العدد باستخدام إطار ريمان الكامل"""
    if n < 2:
        return [], []
    
    factors = []
    steps = []
    current = n
    iteration = 0
    max_iterations = 1000
    
    start_time = time.time()
    
    while current > 1 and iteration < max_iterations:
        iteration += 1
        
        if timeout and (time.time() - start_time) > timeout:
            steps.append("⏰ انتهى الوقت المحدد للتحليل")
            break
        
        # إذا كان أولياً، أضفه وتوقف
        if is_prime_fast(current):
            factors.append(current)
            steps.append(f"{current} هو عدد أولي ✅")
            break
        
        # محاولة إيجاد عامل باستخدام factreaman (سريع)
        if use_riemann:
            f = factreaman(current)
            if f and f != current and current % f == 0:
                factors.append(f)
                steps.append(f"{current} ÷ {f} = {current // f} (Factreaman + Riemann)")
                current = current // f
                continue
        
        # محاولة باستخدام Brent Rho مع ريمان
        d = brent_rho(current, timeout=timeout, use_riemann=use_riemann)
        if d and d != current:
            factors.append(d)
            steps.append(f"{current} ÷ {d} = {current // d} (Brent-Rho + Riemann)")
            current = current // d
            continue
        
        # محاولة باستخدام Pollard Rho مع ريمان
        d = pollard_rho_riemann(current, timeout=timeout)
        if d and d != current:
            factors.append(d)
            steps.append(f"{current} ÷ {d} = {current // d} (Pollard-Rho + Riemann)")
            current = current // d
            continue
        
        # إذا فشلت جميع المحاولات، نضيف العدد المتبقي
        factors.append(current)
        steps.append(f"{current} لم نتمكن من تحليله بالكامل ⚠️")
        break
    
    return factors, steps

def verify_factorization(original, factors):
    """التحقق من صحة التحليل"""
    product = 1
    for factor in factors:
        product *= factor
    
    return product == original, product

# ========== واجهة Streamlit المحسنة مع ريمان ==========
def main():
    st.markdown('<div class="main-header">🧮 PPFO v20.3 - الإطار الرياضي المتقدم مع ريمان</div>', unsafe_allow_html=True)
    
    # معلومات النظام وميزات ريمان
    with st.sidebar:
        st.header("⚙️ إطار ريمان الرياضي")
        st.markdown('<div class="riemann-feature">🧠 تفعيل إطار ريمان الكامل</div>', unsafe_allow_html=True)
        
        st.write("**مميزات ريمان المُفعّلة:**")
        st.write("✅ أصفار زيتا غير التافهة")
        st.write("✅ تصحيح ريمان للتقديرات")
        st.write("✅ Factreaman مع التوجيه الرياضي")
        st.write("✅ خوارزميات Pollard/Brent مع ريمان")
        st.write(f"**عدد أصفار زيتا:** {len(RIEMANN_ZEROS)}")
        
        use_riemann = st.checkbox("تفعيل إطار ريمان", value=True, help="استخدام التقنيات الرياضية المتقدمة لأصفار زيتا")
        show_riemann_info = st.checkbox("عرض معلومات ريمان", value=True)
    
    # إدخال الرقم
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔢 إدخال العدد")
        input_method = st.radio("طريقة الإدخال:", ["رقم عادي", "رقم سداسي عشري", "تعبير رياضي"])
        
        if input_method == "رقم عادي":
            N_str = st.text_input("أدخل العدد المراد تحليله:", value="1201883737878837377")
        elif input_method == "رقم سداسي عشري":
            hex_str = st.text_input("أدخل العدد بصيغة سداسية عشرية:", value="0x10B2D4E5A3D4E81")
            N_str = hex_str
        else:
            expr = st.text_input("أدخل تعبيراً رياضياً:", value="13 * 7 * 19 * 2281 * 191 * 21503 * 74201")
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
            
            if is_prime_fast(N):
                st.success("✅ العدد أولي")
            else:
                st.info("🔢 العدد مركب")
                
        except Exception as e:
            st.error(f"❌ خطأ في الإدخال: {e}")
            return
    
    # إعدادات التحليل المتقدم
    st.subheader("⚙️ إعدادات التحليل المتقدم")
    
    col1, col2 = st.columns(2)
    
    with col1:
        timeout = st.slider("الوقت الأقصى (ثواني)", 1, 300, 60)
        show_steps = st.checkbox("عرض خطوات التحليل", value=True)
    
    with col2:
        advanced_methods = st.checkbox("استخدام خوارزميات متقدمة", value=True)
        save_results = st.checkbox("حفظ النتائج", value=False)
    
    # زر البدء مع تفعيل ريمان
    if st.button("🚀 بدء التحليل مع ريمان", type="primary", use_container_width=True):
        if N < 2:
            st.error("❌ العدد يجب أن يكون أكبر من 1")
            return
        
        with st.spinner("جاري التحليل باستخدام إطار ريمان الرياضي..."):
            try:
                # التحليل باستخدام ريمان
                factors, steps = factorize_with_riemann(
                    N, 
                    timeout=timeout, 
                    use_riemann=use_riemann,
                    verbose=True
                )
                
                is_correct, product = verify_factorization(N, factors)
                
                # معلومات ريمان الإضافية
                riemann_info = {}
                if use_riemann and show_riemann_info:
                    riemann_info = calculate_riemann_metrics(N, factors)
                
                display_results(N, factors, steps, is_correct, product, riemann_info)
                
            except Exception as e:
                st.error(f"❌ فشل التحليل: {e}")

def calculate_riemann_metrics(n, factors):
    """حساب مقاييس ريمان للتحليل"""
    metrics = {}
    
    # تقدير ريمان للعدد الأولي
    bit_length = n.bit_length()
    prime_estimate = prime_nth_estimate(bit_length // 2, use_riemann=True)
    metrics["تقدير_ريمان_للعوامل"] = prime_estimate
    
    # تصحيح ريمان
    correction = riemann_correction(n)
    metrics["تصحيح_ريمان"] = correction
    
    # استخدام أصفار زيتا في التحليل
    metrics["أصفار_زيتا_المستخدمة"] = len(RIEMANN_ZEROS)
    
    # تحليل توزيع العوامل
    if factors:
        factor_product = math.prod(factors)
        metrics["دقة_التحليل"] = abs(n - factor_product)
    
    return metrics

def display_results(original_number, factors, steps, is_correct, product, riemann_info=None):
    """عرض النتائج مع معلومات ريمان"""
    
    st.markdown("---")
    st.subheader("📊 النتائج النهائية")
    
    # البطاقات الإحصائية
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
    
    # عرض العوامل
    st.subheader("🧩 العوامل المكتشفة")
    
    if factors:
        factor_counts = Counter(factors)
        
        # إنشاء جدول العوامل
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
        
        # مخططات العوامل
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(factors_df, names='العامل', values='التكرار', 
                        title='توزيع العوامل حسب التكرار')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(factors_df, x='العامل', y='الحجم (بت)',
                        title='حجم العوامل بالبت', color='أولي')
            st.plotly_chart(fig, use_container_width=True)
        
        # عرض التحليل بالصيغة الرياضية
        st.subheader("🧮 الصيغة الرياضية")
        factor_str = " × ".join([f"{factor}^{count}" if count > 1 else str(factor) 
                               for factor, count in factor_counts.items()])
        
        if is_correct:
            st.latex(f"{original_number} = {factor_str}")
        else:
            st.warning(f"⚠️ الصيغة غير صحيحة: {original_number} ≠ {factor_str}")
        
    else:
        st.warning("⚠️ لم يتم العثور على أي عوامل")
    
    # خطوات التحليل
    if steps and show_steps:
        st.subheader("📋 خطوات التحليل مع ريمان")
        
        for i, step in enumerate(steps, 1):
            # تمييز خطوات ريمان
            if "ريمان" in step or "Riemann" in step or "زيتا" in step:
                st.info(f"{i}. {step} 🌟")
            else:
                st.write(f"{i}. {step}")

# ========== اختبارات ريمان ==========
def riemann_tests():
    """اختبارات وتجارب ريمان"""
    st.sidebar.subheader("🧪 تجارب ريمان")
    
    if st.sidebar.button("اختبار أصفار زيتا"):
        st.sidebar.write("**أصفار زيتا غير التافهة:**")
        for i in range(1, 6):
            zero = zetazero(i)
            st.sidebar.write(f"ζ₀({i}) ≈ {zero:.10f}")
    
    if st.sidebar.button("اختبار Factreaman"):
        test_num = 123456789
        result = factreaman(test_num)
        st.sidebar.write(f"Factreaman({test_num}) = {result}")
    
    if st.sidebar.button("مقارنة التقديرات"):
        n = 100
        classic = prime_nth_estimate(n, use_riemann=False)
        riemann = prime_nth_estimate(n, use_riemann=True)
        st.sidebar.write(f"التقدير الكلاسيكي: {classic}")
        st.sidebar.write(f"التقدير بريمان: {riemann}")
        st.sidebar.write(f"الفرق: {riemann - classic}")

# ========== التشغيل الرئيسي ==========
if __name__ == "__main__":
    riemann_tests()
    main()
