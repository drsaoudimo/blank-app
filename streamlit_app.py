#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PPFO v18.1 — تطبيق الويب الرياضي الكامل لأصفار زيتا مع تحويل تلقائي عند الفشل
نسخة Streamlit مع التحليل الفعلي
"""

import math
import random
import threading
import time
import re
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from collections import Counter, defaultdict
from functools import lru_cache
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(
    page_title="PPFO v18.1 - التحليل الرياضي المتقدم",
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
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ========== دوال رياضية أساسية محسنة ==========
def is_prime_fast(n):
    """اختبار أولية محسن"""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return 2
    
    # اختبار بسيط للأعداد الصغيرة
    if n < 10000:
        for i in range(3, int(math.sqrt(n)) + 1, 2):
            if n % i == 0:
                return i
        return True
    
    # اختبار فيرما للأعداد الكبيرة
    for a in [2, 3, 5, 7, 11]:
        if pow(a, n-1, n) != 1:
            return False
    return True

def gcd(a, b):
    """حساب القاسم المشترك الأكبر"""
    while b:
        a, b = b, a % b
    return a

def trial_division(n, limit=None):
    """تحليل بالقسمة المتكررة"""
    if limit is None:
        limit = int(math.sqrt(n)) + 1
    
    factors = []
    # اختبار القسمة على 2
    while n % 2 == 0:
        factors.append(2)
        n //= 2
    
    # اختبار القسمة على الأعداد الفردية
    f = 3
    while f * f <= n and f <= limit:
        if n % f == 0:
            factors.append(f)
            n //= f
        else:
            f += 2
    
    if n > 1:
        factors.append(n)
    
    return factors

def pollard_rho(n):
    """خوارزمية بولارد رو الأساسية"""
    if n % 2 == 0:
        return 2
    if n % 3 == 0:
        return 3
    
    x = random.randint(2, n-2)
    y = x
    c = random.randint(1, n-1)
    d = 1
    
    f = lambda x: (x*x + c) % n
    
    while d == 1:
        x = f(x)
        y = f(f(y))
        d = gcd(abs(x-y), n)
        
        if d == n:
            return pollard_rho(n)
    
    return d

def factorize_optimized(n):
    """دالة تحليل محسنة تعمل بشكل صحيح"""
    if n < 2:
        return []
    
    factors = []
    
    # التحليل بالعوامل الصغيرة أولاً
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    for p in small_primes:
        while n % p == 0:
            factors.append(p)
            n //= p
        if n == 1:
            break
    
    if n == 1:
        return factors
    
    # إذا كان العدد أولي بعد إزالة العوامل الصغيرة
    if is_prime_fast(n) == True:
        factors.append(n)
        return factors
    
    # استخدام بولارد رو للباقي
    remaining = n
    attempts = 0
    while remaining > 1 and attempts < 10:
        if is_prime_fast(remaining) == True:
            factors.append(remaining)
            break
        
        factor = pollard_rho(remaining)
        if factor != remaining:
            factors.extend(factorize_optimized(factor))
            remaining //= factor
        else:
            attempts += 1
    
    if remaining > 1:
        factors.append(remaining)
    
    return factors

# ========== إدارة الحالة المحسنة ==========
class FactorizationState:
    def __init__(self, N):
        self.N = N
        self.factors = []
        self.methods_used = []
        self.start_time = time.time()
        self.completed = False
    
    def add_factor(self, factor, method):
        self.factors.append(factor)
        self.methods_used.append(method)
    
    def get_elapsed_time(self):
        return time.time() - self.start_time
    
    def verify_factorization(self):
        """التحقق من صحة التحليل"""
        product = 1
        for factor in self.factors:
            product *= factor
        return product == self.N
    
    def get_factorization_dict(self):
        """الحصول على العوامل مع تكراراتها"""
        return dict(Counter(self.factors))

# ========== واجهة Streamlit المحسنة ==========
def main():
    st.markdown('<div class="main-header">🧮 PPFO v18.1 - التحليل الرياضي المتقدم</div>', unsafe_allow_html=True)
    
    # معلومات النظام
    with st.sidebar:
        st.header("⚙️ معلومات النظام")
        st.info("""
        **ℹ️ حول الخوارزميات:**
        - القسمة المتكررة للعوامل الصغيرة
        - بولارد رو للعوامل المتوسطة
        - اختبار أولية محسن
        """)
    
    # إدخال الرقم
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔢 إدخال العدد")
        input_method = st.radio("طريقة الإدخال:", ["رقم عادي", "رقم سداسي عشري", "تعبير رياضي"])
        
        if input_method == "رقم عادي":
            default_num = "123456789012345678901234567890"
            N_str = st.text_input("أدخل العدد المراد تحليله:", value=default_num)
        elif input_method == "رقم سداسي عشري":
            default_hex = "0x1234567890ABCDEF"
            hex_str = st.text_input("أدخل العدد بصيغة سداسية عشرية:", value=default_hex)
            N_str = hex_str
        else:
            default_expr = "2**128 + 1"
            expr = st.text_input("أدخل تعبيراً رياضياً:", value=default_expr)
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
            
            # تحليل أولي
            prime_check = is_prime_fast(N)
            if prime_check == True:
                st.success("✅ العدد أولي")
            elif isinstance(prime_check, int):
                st.info(f"🔢 العدد مركب - قابل للقسمة على {prime_check}")
            else:
                st.info("🔢 العدد مركب")
                
        except Exception as e:
            st.error(f"❌ خطأ في الإدخال: {e}")
            return
    
    # إعدادات التحليل
    st.subheader("⚙️ إعدادات التحليل")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_time = st.number_input("الوقت الأقصى (ثواني)", 1, 3600, 60)
        show_steps = st.checkbox("عرض خطوات التحليل", value=True)
    
    with col2:
        use_advanced = st.checkbox("استخدام خوارزميات متقدمة", value=True)
        save_results = st.checkbox("حفظ النتائج", value=False)
    
    # زر البدء
    if st.button("🚀 بدء التحليل", type="primary", use_container_width=True):
        if N < 2:
            st.error("❌ العدد يجب أن يكون أكبر من 1")
            return
        
        # إعداد شريط التقدم
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # بدء التحليل
        with st.spinner("جاري تحليل العدد..."):
            state = FactorizationState(N)
            
            # تحديث الحالة الأولية
            status_text.text("بدء التحليل...")
            progress_bar.progress(10)
            
            try:
                # التحليل الفعلي
                factors = factorize_optimized(N)
                state.factors = factors
                
                # تحديث الحالة النهائية
                progress_bar.progress(100)
                status_text.success("✅ اكتمل التحليل")
                
                # عرض النتائج
                display_results(state, show_steps, save_results)
                
            except Exception as e:
                progress_bar.progress(0)
                status_text.error(f"❌ فشل التحليل: {e}")

def display_results(state, show_steps=True, save_results=False):
    """عرض النتائج بشكل صحيح"""
    
    st.markdown("---")
    st.subheader("📊 النتائج النهائية")
    
    # البطاقات الإحصائية
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        elapsed = state.get_elapsed_time()
        st.metric("⏱️ الوقت الإجمالي", f"{elapsed:.3f} ثانية")
    
    with col2:
        total_factors = len(state.factors)
        st.metric("🔢 عدد العوامل", total_factors)
    
    with col3:
        unique_factors = len(set(state.factors))
        st.metric("🔍 عوامل فريدة", unique_factors)
    
    with col4:
        # التحقق من صحة النتيجة
        is_correct = state.verify_factorization()
        status = "✅ صحيح" if is_correct else "❌ خطأ"
        st.metric("✓ التحقق", status)
    
    # التحقق من صحة التحليل
    if state.verify_factorization():
        st.success("🎯 التحليل صحيح - حاصل ضرب العوامل يساوي العدد الأصلي")
    else:
        st.error("❌ هناك خطأ في التحليل - حاصل الضرب لا يساوي العدد الأصلي")
        
        # حساب الفرق
        product = 1
        for factor in state.factors:
            product *= factor
        difference = state.N - product
        
        with st.expander("🔍 تفاصيل الخطأ"):
            st.write(f"**العدد الأصلي:** {state.N}")
            st.write(f"**حاصل الضرب:** {product}")
            st.write(f"**الفرق:** {difference}")
            st.write(f"**العوامل:** {state.factors}")
    
    # عرض العوامل
    st.subheader("🧩 العوامل المكتشفة")
    
    if state.factors:
        factor_counts = Counter(state.factors)
        
        # إنشاء جدول العوامل
        factors_data = []
        for factor, count in factor_counts.items():
            factors_data.append({
                "العامل": factor,
                "التكرار": count,
                "الحجم (بت)": factor.bit_length(),
                "نسبة الحجم %": (factor.bit_length() * count / state.N.bit_length()) * 100
            })
        
        factors_df = pd.DataFrame(factors_data)
        st.dataframe(factors_df, use_container_width=True)
        
        # مخططات العوامل
        col1, col2 = st.columns(2)
        
        with col1:
            if len(factors_df) > 0:
                fig = px.pie(factors_df, names='العامل', values='التكرار', 
                            title='توزيع العوامل حسب التكرار')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if len(factors_df) > 0:
                fig = px.bar(factors_df, x='العامل', y='الحجم (بت)',
                            title='حجم العوامل بالبت', color='العامل')
                st.plotly_chart(fig, use_container_width=True)
        
        # عرض التحليل بالصيغة الرياضية
        st.subheader("🧮 الصيغة الرياضية")
        factor_str = " × ".join([f"{factor}^{count}" if count > 1 else str(factor) 
                               for factor, count in factor_counts.items()])
        st.latex(f"{state.N} = {factor_str}")
        
    else:
        st.warning("⚠️ لم يتم العثور على أي عوامل")
    
    # خطوات التحليل
    if show_steps and state.factors:
        st.subheader("📋 خطوات التحليل")
        
        steps = []
        temp_n = state.N
        
        for factor in state.factors:
            steps.append(f"{temp_n} ÷ {factor} = {temp_n // factor}")
            temp_n //= factor
        
        for i, step in enumerate(steps, 1):
            st.write(f"{i}. {step}")
    
    # خيارات التصدير
    if save_results:
        st.subheader("💾 حفظ النتائج")
        
        # إنشاء تقرير
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        factor_counts = Counter(state.factors)
        
        report = f"""
        تقرير تحليل PPFO v18.1
        =====================
        التاريخ: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        العدد المدخل: {state.N}
        الحجم: {state.N.bit_length()} بت
        الوقت الإجمالي: {state.get_elapsed_time():.3f} ثانية
        عدد العوامل: {len(state.factors)}
        العوامل الفريدة: {len(set(state.factors))}
        التحقق: {'ناجح' if state.verify_factorization() else 'فاشل'}
        
        العوامل:
        {chr(10).join(f'- {factor} (تكرار: {count})' for factor, count in factor_counts.items())}
        
        الصيغة الرياضية:
        {state.N} = {" × ".join([f"{factor}^{count}" if count > 1 else str(factor) for factor, count in factor_counts.items()])}
        """
        
        st.download_button(
            label="📥 تحميل التقرير",
            data=report,
            file_name=f"ppfo_analysis_{timestamp}.txt",
            mime="text/plain"
        )

# ========== اختبار الدوال ==========
def test_factorization():
    """دالة لاختبار التحليل"""
    test_numbers = [
        123456789,
        123456789012345,
        123456789012345678901234567890
    ]
    
    for num in test_numbers:
        st.write(f"تحليل {num}:")
        factors = factorize_optimized(num)
        st.write(f"العوامل: {factors}")
        
        # التحقق
        product = 1
        for f in factors:
            product *= f
        st.write(f"التحقق: {product == num}")
        st.write("---")

# ========== التشغيل الرئيسي ==========
if __name__ == "__main__":
    # إضافة زر اختبار في الشريط الجانبي
    with st.sidebar:
        if st.button("🧪 اختبار التحليل", use_container_width=True):
            test_factorization()
    
    main()
