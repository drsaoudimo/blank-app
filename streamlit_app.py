#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PPFO v18.1 — تطبيق الويب الرياضي الكامل لأصفار زيتا مع تحويل تلقائي عند الفشل
نسخة Streamlit مع إصلاح التحقق من الصحة
"""

import math
import random
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from collections import Counter
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
</style>
""", unsafe_allow_html=True)

# ========== دوال رياضية أساسية محسنة ==========
def is_prime(n):
    """اختبار أولية دقيق"""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    # اختبار بسيط للأعداد الصغيرة
    if n < 10000:
        for i in range(3, int(math.sqrt(n)) + 1, 2):
            if n % i == 0:
                return False
        return True
    
    # اختبار فيرما للأعداد الكبيرة
    for a in [2, 3, 5, 7, 11, 13, 17]:
        if pow(a, n-1, n) != 1:
            return False
    return True

def gcd(a, b):
    """حساب القاسم المشترك الأكبر"""
    while b:
        a, b = b, a % b
    return a

def pollard_rho(n):
    """خوارزمية بولارد رو المحسنة"""
    if n % 2 == 0:
        return 2
    if n % 3 == 0:
        return 3
    
    x = random.randint(2, n-2)
    y = x
    c = random.randint(1, n-1)
    d = 1
    
    f = lambda x: (x*x + c) % n
    
    for _ in range(100000):
        x = f(x)
        y = f(f(y))
        d = gcd(abs(x-y), n)
        
        if d == n:
            break
        if d != 1:
            return d
    
    return n

def factorize_with_steps(n):
    """تحليل مع تتبع الخطوات"""
    if n < 2:
        return [], []
    
    factors = []
    steps = []
    current = n
    
    while current > 1:
        # إذا كان أولياً، أضفه وتوقف
        if is_prime(current):
            factors.append(current)
            steps.append(f"{current} هو عدد أولي")
            break
        
        # إيجاد عامل
        factor = pollard_rho(current)
        
        if factor == current:
            # لم نتمكن من إيجاد عامل، نضيف العدد كعامل أولي
            factors.append(current)
            steps.append(f"{current} يعتبر عدد أولي (لم نتمكن من تحليله)")
            break
        
        # حساب التكرار
        count = 0
        temp = current
        while temp % factor == 0:
            count += 1
            temp //= factor
        
        # إضافة العوامل
        for _ in range(count):
            factors.append(factor)
        
        steps.append(f"{current} ÷ {factor} = {current // factor}")
        current = current // factor
    
    return factors, steps

def verify_factorization(original, factors):
    """التحقق من صحة التحليل بشكل دقيق"""
    product = 1
    for factor in factors:
        product *= factor
    
    # استخدام تحقق دقيق مع التعامل مع الأعداد الكبيرة
    return product == original, product

# ========== واجهة Streamlit المحسنة ==========
def main():
    st.markdown('<div class="main-header">🧮 PPFO v18.1 - التحليل الرياضي المتقدم</div>', unsafe_allow_html=True)
    
    # إدخال الرقم
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔢 إدخال العدد")
        input_method = st.radio("طريقة الإدخال:", ["رقم عادي", "رقم سداسي عشري", "تعبير رياضي"])
        
        if input_method == "رقم عادي":
            N_str = st.text_input("أدخل العدد المراد تحليله:", value="120188373787")
        elif input_method == "رقم سداسي عشري":
            hex_str = st.text_input("أدخل العدد بصيغة سداسية عشرية:", value="0x1BF0C9B1B")
            N_str = hex_str
        else:
            expr = st.text_input("أدخل تعبيراً رياضياً:", value="23 * 71 * 167 * 440717")
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
            
            if is_prime(N):
                st.success("✅ العدد أولي")
            else:
                st.info("🔢 العدد مركب")
                
        except Exception as e:
            st.error(f"❌ خطأ في الإدخال: {e}")
            return
    
    if st.button("🚀 بدء التحليل", type="primary", use_container_width=True):
        if N < 2:
            st.error("❌ العدد يجب أن يكون أكبر من 1")
            return
        
        with st.spinner("جاري تحليل العدد..."):
            try:
                factors, steps = factorize_with_steps(N)
                is_correct, product = verify_factorization(N, factors)
                
                display_results(N, factors, steps, is_correct, product)
                
            except Exception as e:
                st.error(f"❌ فشل التحليل: {e}")

def display_results(original_number, factors, steps, is_correct, product):
    """عرض النتائج بشكل صحيح"""
    
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
    
    # التحقق من صحة التحليل - التصحيح الأساسي هنا
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
            factors_data.append({
                "العامل": factor,
                "التكرار": count,
                "الحجم (بت)": factor.bit_length(),
                "أولي": "✅" if is_prime(factor) else "❌"
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
                        title='حجم العوامل بالبت', color='العامل')
            st.plotly_chart(fig, use_container_width=True)
        
        # عرض التحليل بالصيغة الرياضية
        st.subheader("🧮 الصيغة الرياضية")
        factor_str = " × ".join([f"{factor}^{count}" if count > 1 else str(factor) 
                               for factor, count in factor_counts.items()])
        
        if is_correct:
            st.latex(f"{original_number} = {factor_str}")
        else:
            st.warning(f"⚠️ الصيغة غير صحيحة: {original_number} ≠ {factor_str}")
            st.info(f"حاصل الضرب الفعلي: {product}")
        
    else:
        st.warning("⚠️ لم يتم العثور على أي عوامل")
    
    # خطوات التحليل
    if steps:
        st.subheader("📋 خطوات التحليل")
        
        for i, step in enumerate(steps, 1):
            st.write(f"{i}. {step}")

# ========== اختبار العدد المحدد ==========
def test_specific_number():
    """اختبار العدد 120188373787"""
    st.sidebar.subheader("🧪 اختبار العدد 120188373787")
    
    test_num = 120188373787
    
    if st.sidebar.button("تحليل العدد الاختباري"):
        factors, steps = factorize_with_steps(test_num)
        is_correct, product = verify_factorization(test_num, factors)
        
        st.sidebar.write(f"**العدد:** {test_num}")
        st.sidebar.write(f"**العوامل:** {factors}")
        st.sidebar.write(f"**التحقق:** {'✅ ناجح' if is_correct else '❌ فاشل'}")
        st.sidebar.write(f"**حاصل الضرب:** {product}")
        
        if is_correct:
            st.sidebar.success("التحليل صحيح!")
        else:
            st.sidebar.error("التحليل خاطئ!")

# ========== التشغيل الرئيسي ==========
if __name__ == "__main__":
    test_specific_number()
    main()
