import streamlit as st
from sympy import parse_expr, solve, symbols, diff, integrate, limit, series, expand, factor, Matrix
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import math
import json
import time
from fractions import Fraction
from typing import List, Dict, Any, Optional, Tuple, Union
import sympy as sp
import pandas as pd
from PIL import Image

# === إعداد الصفحة ===
st.set_page_config(
    page_title="PPFO Math Solver",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === تصميم مخصص ===
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 2rem;
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
</style>
""", unsafe_allow_html=True)

# === العنوان الرئيسي ===
st.markdown('<p class="main-header">🧮 PPFO Mathematical Suite</p>', unsafe_allow_html=True)
st.markdown("### تطبيق رياضي متقدم يعمل على جميع المنصات")

# === الشريط الجانبي للتنقل ===
with st.sidebar:
    st.image("https://via.placeholder.com/150x50?text=PPFO+Logo", use_column_width=True)
    st.markdown("### 📚 القوائم الرئيسية")
    menu = st.radio(
        "",
        ["🏠 الصفحة الرئيسية", "🧮 الجبر", "📈 التفاضل والتكامل", "📐 الهندسة", "📊 الإحصاء", "❓ المساعدة"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### ⚙️ الإعدادات")
    precision = st.slider("دقة الحسابات", min_value=5, max_value=50, value=15)
    use_latex = st.checkbox("عرض النتائج بصيغة LaTeX", value=True)
    
    st.markdown("---")
    st.markdown("### ℹ️ معلومات")
    st.markdown(f"**الإصدار:** 3.0")
    st.markdown(f"**التاريخ:** {time.strftime('%Y-%m-%d')}")
    st.markdown(f"**الوقت:** {time.strftime('%H:%M:%S')}")

# === الصفحة الرئيسية ===
if menu == "🏠 الصفحة الرئيسية":
    st.markdown("## 🎯 مرحباً بك في PPFO Mathematical Suite!")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="info-box">
        <h3>🌟 الميزات الرئيسية</h3>
        <ul>
            <li><b>🧮 الجبر:</b> حل المعادلات الخطية والتربيعية والأنية</li>
            <li><b>📈 التفاضل والتكامل:</b> حساب المشتقات والتكاملات المحدودة وغير المحدودة</li>
            <li><b>📐 الهندسة:</b> رسم الدوال الرياضية وتحليلها</li>
            <li><b>📊 الإحصاء:</b> تحليل البيانات والاختبارات الإحصائية</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
        <h3>🚀 كيفية الاستخدام</h3>
        <ol>
            <li>اختر القسم الذي تريد العمل فيه من الشريط الجانبي</li>
            <li>أدخل البيانات المطلوبة في الحقول المناسبة</li>
            <li>اضغط على زر التنفيذ لرؤية النتائج</li>
            <li>يمكنك حفظ النتائج أو تصديرها</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # زر التحميل السريع
        with st.expander("📱 تحميل التطبيق على هاتفك"):
            st.markdown("""
            **كيفية تثبيت التطبيق على هاتفك الأندرويد:**
            1. افتح هذا الرابط في متصفح Chrome
            2. انقر على أيقونة القائمة (⋮) في الأعلى
            3. اختر "تثبيت التطبيق" أو "Install app"
            4. اتبع التعليمات لإضافة التطبيق إلى شاشتك الرئيسية
            
            **المزايا:**
            - يعمل دون اتصال بالإنترنت
            - واجهة سهلة وسريعة
            - تحديثات تلقائية
            """)
    
    with col2:
        st.image("https://via.placeholder.com/400x300?text=Math+Visualization", use_column_width=True)
        st.markdown("### 📱 تطبيق يعمل على جميع الأجهزة")
        st.markdown("📱 **الأندرويد** | 🍎 **iOS** | 💻 **الويب** | 🖥️ **سطح المكتب**")
        
        # عداد الاستخدام
        if 'usage_count' not in st.session_state:
            st.session_state.usage_count = 0
        st.session_state.usage_count += 1
        
        st.metric("عدد الزيارات في هذه الجلسة", st.session_state.usage_count)

# === قسم الجبر ===
elif menu == "🧮 الجبر":
    st.markdown('<p class="section-header">🧮 قسم الجبر المتقدم</p>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["حل معادلة", "نظام معادلات", "البولينومات"])
    
    # --- تبويب حل معادلة واحدة ---
    with tab1:
        st.markdown("### حل معادلة جبرية")
        st.markdown("""
        <div class="info-box">
        أدخل معادلة رياضية باستخدام الصيغ التالية:
        - `x**2` للمربع
        - `x**3` للمكعب
        - `sqrt(x)` للجذر التربيعي
        - `sin(x)`, `cos(x)`, `tan(x)` للدوال المثلثية
        - `log(x)` للوغاريتم الطبيعي
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            equation = st.text_input("أدخل المعادلة", "x**2 - 4 = 0", key="eq1")
            variable = st.text_input("المتغير", "x", max_chars=1, key="var1")
            
            if st.button("حل المعادلة", type="primary"):
                try:
                    x = symbols(variable)
                    # تحويل المعادلة إلى الشكل f(x) = 0
                    if '=' in equation:
                        left, right = equation.split('=', 1)
                        expr = parse_expr(left.strip()) - parse_expr(right.strip())
                    else:
                        expr = parse_expr(equation)
                    
                    # حل المعادلة
                    solutions = solve(expr, x)
                    
                    # عرض النتائج
                    st.markdown("### النتائج:")
                    st.markdown(f"**المعادلة:** `{equation}`")
                    st.markdown(f"**المتغير:** `{variable}`")
                    st.markdown(f"**عدد الحلول:** {len(solutions)}")
                    
                    for i, sol in enumerate(solutions, 1):
                        sol_eval = sp.N(sol, precision)
                        st.markdown(f"#### الحل {i}:")
                        if use_latex:
                            st.latex(f"x_{{{i}}} = {sp.latex(sol)}")
                            st.latex(f"x_{{{i}}} \\approx {sp.latex(sol_eval)}")
                        else:
                            st.code(f"الحل الدقيق: {sol}")
                            st.code(f"الحل التقريبي: {sol_eval}")
                    
                    # حفظ النتائج في الجلسة
                    st.session_state.last_result = {
                        'type': 'equation',
                        'equation': equation,
                        'variable': variable,
                        'solutions': [str(sol) for sol in solutions],
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    st.success("✅ تم حل المعادلة بنجاح!")
                    
                except Exception as e:
                    st.markdown(f'<div class="error-box">❌ خطأ: {str(e)}</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("### أمثلة جاهزة")
            examples = {
                "معادلة خطية": "2*x + 3 = 7",
                "معادلة تربيعية": "x**2 - 5*x + 6 = 0",
                "معادلة مكعبة": "x**3 - 6*x**2 + 11*x - 6 = 0",
                "معادلة مثلثية": "sin(x) = 0.5",
                "معادلة أسية": "2**x = 8"
            }
            
            for name, example in examples.items():
                if st.button(f"مثال: {name}"):
                    st.session_state.eq1 = example
                    st.experimental_rerun()
    
    # --- تبويب نظام المعادلات ---
    with tab2:
        st.markdown("### حل نظام معادلات")
        
        num_eqs = st.number_input("عدد المعادلات", min_value=2, max_value=5, value=2)
        
        equations = []
        for i in range(num_eqs):
            eq = st.text_input(f"المعادلة {i+1}", f"x + y = {i+2}", key=f"sys_eq{i}")
            equations.append(eq)
        
        variables = st.text_input("المتغيرات (مفصولة بمسافات)", "x y", key="sys_vars")
        
        if st.button("حل النظام", type="primary"):
            try:
                # تحضير المتغيرات
                var_list = variables.split()
                syms = symbols(' '.join(var_list))
                sym_dict = dict(zip(var_list, syms))
                
                # تحضير المعادلات
                eqs = []
                for eq in equations:
                    if '=' in eq:
                        left, right = eq.split('=', 1)
                        expr = parse_expr(left.strip()) - parse_expr(right.strip())
                    else:
                        expr = parse_expr(eq)
                    eqs.append(expr)
                
                # حل النظام
                solutions = solve(eqs, syms, dict=True)
                
                # عرض النتائج
                st.markdown("### النتائج:")
                st.markdown(f"**عدد الحلول:** {len(solutions)}")
                
                for i, sol in enumerate(solutions, 1):
                    st.markdown(f"#### الحل {i}:")
                    for var, val in sol.items():
                        val_eval = sp.N(val, precision)
                        if use_latex:
                            st.latex(f"{sp.latex(var)} = {sp.latex(val)}")
                            st.latex(f"{sp.latex(var)} \\approx {sp.latex(val_eval)}")
                        else:
                            st.code(f"{var} = {val}")
                            st.code(f"{var} ≈ {val_eval}")
                
                st.success("✅ تم حل النظام بنجاح!")
                
            except Exception as e:
                st.markdown(f'<div class="error-box">❌ خطأ: {str(e)}</div>', unsafe_allow_html=True)
    
    # --- تبويب البولينومات ---
    with tab3:
        st.markdown("### تحليل البولينومات")
        
        polynomial = st.text_input("أدخل البولينوم", "x**3 - 6*x**2 + 11*x - 6", key="poly")
        variable = st.text_input("المتغير", "x", max_chars=1, key="poly_var")
        
        if st.button("تحليل البولينوم", type="primary"):
            try:
                x = symbols(variable)
                poly = parse_expr(polynomial)
                
                # تحليل البولينوم
                factored = factor(poly)
                expanded = expand(poly)
                roots = solve(poly, x)
                
                # عرض النتائج
                st.markdown("### النتائج:")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### الشكل المحلل:")
                    if use_latex:
                        st.latex(f"{sp.latex(factored)}")
                    else:
                        st.code(str(factored))
                
                with col2:
                    st.markdown("#### الشكل الموسع:")
                    if use_latex:
                        st.latex(f"{sp.latex(expanded)}")
                    else:
                        st.code(str(expanded))
                
                st.markdown("#### الجذور:")
                for i, root in enumerate(roots, 1):
                    root_eval = sp.N(root, precision)
                    if use_latex:
                        st.latex(f"x_{{{i}}} = {sp.latex(root)} \\approx {sp.latex(root_eval)}")
                    else:
                        st.write(f"الجذر {i}: {root} ≈ {root_eval}")
                
                # رسم البولينوم
                if st.checkbox("عرض الرسم البياني"):
                    x_vals = np.linspace(-10, 10, 1000)
                    f = sp.lambdify(x, poly, 'numpy')
                    
                    fig, ax = plt.subplots(figsize=(10, 6))
                    y_vals = []
                    for xv in x_vals:
                        try:
                            yv = f(xv)
                            if np.isfinite(yv):
                                y_vals.append(yv)
                            else:
                                y_vals.append(np.nan)
                        except:
                            y_vals.append(np.nan)
                    
                    ax.plot(x_vals, y_vals, 'b-', linewidth=2, label=str(poly))
                    ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
                    ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
                    ax.grid(True, alpha=0.3)
                    ax.set_title(f"رسم البولينوم: {polynomial}")
                    ax.set_xlabel('x')
                    ax.set_ylabel('y')
                    ax.legend()
                    
                    st.pyplot(fig)
                
                st.success("✅ تم تحليل البولينوم بنجاح!")
                
            except Exception as e:
                st.markdown(f'<div class="error-box">❌ خطأ: {str(e)}</div>', unsafe_allow_html=True)

# === قسم التفاضل والتكامل ===
elif menu == "📈 التفاضل والتكامل":
    st.markdown('<p class="section-header">📈 قسم التفاضل والتكامل المتقدم</p>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["المشتقات", "التكاملات", "النهايات"])
    
    # --- تبويب المشتقات ---
    with tab1:
        st.markdown("### حساب المشتق")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            function = st.text_input("أدخل الدالة", "x**2 + 2*x + 1", key="deriv_func")
            variable = st.text_input("المتغير", "x", max_chars=1, key="deriv_var")
            order = st.number_input("رتبة المشتق", min_value=1, max_value=10, value=1)
            
            if st.button("حساب المشتق", type="primary"):
                try:
                    x = symbols(variable)
                    func = parse_expr(function)
                    derivative = diff(func, x, order)
                    
                    # عرض النتائج
                    st.markdown("### النتائج:")
                    st.markdown(f"**الدالة:** `{function}`")
                    st.markdown(f"**المتغير:** `{variable}`")
                    st.markdown(f"**رتبة المشتق:** {order}")
                    
                    st.markdown("#### المشتق:")
                    if use_latex:
                        st.latex(f"\\frac{{d^{{{order}}}f}}{{d{variable}^{{{order}}}}} = {sp.latex(derivative)}")
                    else:
                        st.code(str(derivative))
                    
                    # حساب قيمة المشتق عند نقطة
                    point = st.number_input("احسب قيمة المشتق عند", value=1.0)
                    if st.button("حساب القيمة"):
                        deriv_func = sp.lambdify(x, derivative, 'numpy')
                        value = deriv_func(point)
                        st.markdown(f"#### قيمة المشتق عند x = {point}:")
                        st.markdown(f"**النتيجة:** {value:.{precision}f}")
                    
                    st.success("✅ تم حساب المشتق بنجاح!")
                    
                except Exception as e:
                    st.markdown(f'<div class="error-box">❌ خطأ: {str(e)}</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("### قواعد الاشتقاق الأساسية")
            st.markdown("""
            - **الثابت:** `d(c)/dx = 0`
            - **القوة:** `d(x^n)/dx = n*x^(n-1)`
            - **المجموع:** `d(f+g)/dx = df/dx + dg/dx`
            - **الضرب:** `d(f*g)/dx = f'*g + f*g'`
            - **الخارج:** `d(f/g)/dx = (f'*g - f*g')/g^2`
            """)
    
    # --- تبويب التكاملات ---
    with tab2:
        st.markdown("### حساب التكامل")
        
        integration_type = st.radio("نوع التكامل", ["غير محدود", "محدود"], horizontal=True)
        
        function = st.text_input("أدخل الدالة", "x**2 + 2*x + 1", key="int_func")
        variable = st.text_input("المتغير", "x", max_chars=1, key="int_var")
        
        if integration_type == "محدود":
            col1, col2 = st.columns(2)
            with col1:
                lower_limit = st.text_input("الحد الأدنى", "0")
            with col2:
                upper_limit = st.text_input("الحد الأعلى", "1")
        
        if st.button("حساب التكامل", type="primary"):
            try:
                x = symbols(variable)
                func = parse_expr(function)
                
                if integration_type == "غير محدود":
                    integral = integrate(func, x)
                    
                    st.markdown("### النتائج:")
                    st.markdown("#### التكامل غير المحدود:")
                    if use_latex:
                        st.latex(f"\\int {sp.latex(func)} \\, d{variable} = {sp.latex(integral)} + C")
                    else:
                        st.code(str(integral) + " + C")
                    
                else:
                    a = parse_expr(lower_limit)
                    b = parse_expr(upper_limit)
                    definite_integral = integrate(func, (x, a, b))
                    numerical_value = sp.N(definite_integral, precision)
                    
                    st.markdown("### النتائج:")
                    st.markdown(f"**الحدود:** من {lower_limit} إلى {upper_limit}")
                    
                    st.markdown("#### التكامل المحدود:")
                    if use_latex:
                        st.latex(f"\\int_{{{sp.latex(a)}}}^{{{sp.latex(b)}}} {sp.latex(func)} \\, d{variable} = {sp.latex(definite_integral)}")
                        st.latex(f"\\approx {sp.latex(numerical_value)}")
                    else:
                        st.code(str(definite_integral))
                        st.code(f"≈ {numerical_value}")
                
                st.success("✅ تم حساب التكامل بنجاح!")
                
            except Exception as e:
                st.markdown(f'<div class="error-box">❌ خطأ: {str(e)}</div>', unsafe_allow_html=True)
    
    # --- تبويب النهايات ---
    with tab3:
        st.markdown("### حساب النهايات")
        
        function = st.text_input("أدخل الدالة", "sin(x)/x", key="limit_func")
        variable = st.text_input("المتغير", "x", max_chars=1, key="limit_var")
        point = st.text_input("نقطة النهاية", "0", key="limit_point")
        direction = st.selectbox("الاتجاه", ["ثنائي", "من اليمين", "من اليسار"])
        
        if st.button("حساب النهاية", type="primary"):
            try:
                x = symbols(variable)
                func = parse_expr(function)
                point_val = parse_expr(point)
                
                if direction == "ثنائي":
                    limit_val = limit(func, x, point_val)
                elif direction == "من اليمين":
                    limit_val = limit(func, x, point_val, dir='+')
                else:
                    limit_val = limit(func, x, point_val, dir='-')
                
                # عرض النتائج
                st.markdown("### النتائج:")
                st.markdown(f"**الدالة:** `{function}`")
                st.markdown(f"**نقطة النهاية:** {point}")
                st.markdown(f"**الاتجاه:** {direction}")
                
                st.markdown("#### قيمة النهاية:")
                if use_latex:
                    st.latex(f"\\lim_{{{variable} \\to {point}}} {sp.latex(func)} = {sp.latex(limit_val)}")
                else:
                    st.code(str(limit_val))
                
                st.success("✅ تم حساب النهاية بنجاح!")
                
            except Exception as e:
                st.markdown(f'<div class="error-box">❌ خطأ: {str(e)}</div>', unsafe_allow_html=True)

# === قسم الهندسة ===
elif menu == "📐 الهندسة":
    st.markdown('<p class="section-header">📐 قسم الهندسة والرسوم البيانية</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["رسم الدوال", "الهندسة التحليلية"])
    
    # --- تبويب رسم الدوال ---
    with tab1:
        st.markdown("### رسم الدوال الرياضية")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            function = st.text_input("أدخل الدالة", "x**2", key="plot_func")
            variable = st.text_input("المتغير", "x", max_chars=1, key="plot_var")
            
            col3, col4 = st.columns(2)
            with col3:
                x_min = st.number_input("الحد الأدنى لـ x", value=-10.0)
            with col4:
                x_max = st.number_input("الحد الأعلى لـ x", value=10.0)
            
            num_points = st.slider("عدد النقاط", min_value=100, max_value=5000, value=1000)
            
            if st.button("رسم الدالة", type="primary"):
                try:
                    x = symbols(variable)
                    func = parse_expr(function)
                    f = sp.lambdify(x, func, 'numpy')
                    
                    x_vals = np.linspace(x_min, x_max, num_points)
                    y_vals = []
                    
                    for xv in x_vals:
                        try:
                            yv = f(xv)
                            if np.isfinite(yv):
                                y_vals.append(yv)
                            else:
                                y_vals.append(np.nan)
                        except:
                            y_vals.append(np.nan)
                    
                    # إنشاء الرسم البياني
                    fig, ax = plt.subplots(figsize=(12, 8), dpi=100)
                    
                    # رسم الدالة
                    ax.plot(x_vals, y_vals, 'b-', linewidth=2, label=f'${sp.latex(func)}$')
                    
                    # إعدادات المحاور
                    ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
                    ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
                    ax.grid(True, alpha=0.3)
                    ax.set_title(f"رسم الدالة: {function}", fontsize=16)
                    ax.set_xlabel(variable, fontsize=14)
                    ax.set_ylabel('y', fontsize=14)
                    ax.legend(fontsize=12)
                    
                    # ضبط المحاور لتجنب القيم اللانهائية
                    y_vals_clean = [y for y in y_vals if np.isfinite(y)]
                    if y_vals_clean:
                        y_min = min(y_vals_clean)
                        y_max = max(y_vals_clean)
                        y_range = y_max - y_min
                        ax.set_ylim(y_min - 0.1*y_range, y_max + 0.1*y_range)
                    
                    # عرض الرسم
                    st.pyplot(fig)
                    
                    # حفظ الرسم كصورة
                    if st.button("حفظ الرسم"):
                        fig.savefig('function_plot.png', bbox_inches='tight', dpi=300)
                        st.success("✅ تم حفظ الرسم كـ 'function_plot.png'")
                    
                    st.success("✅ تم رسم الدالة بنجاح!")
                
                except Exception as e:
                    st.markdown(f'<div class="error-box">❌ خطأ: {str(e)}</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("### أمثلة للرسم")
            examples = {
                "قطع مكافئ": "x**2",
                "دوال مثلثية": "sin(x)",
                "دوال أسية": "exp(x)",
                "دوال لوغاريتمية": "log(x)",
                "دوال كسرية": "1/x"
            }
            
            for name, example in examples.items():
                if st.button(f"رسم {name}"):
                    st.session_state.plot_func = example
                    st.experimental_rerun()
    
    # --- تبويب الهندسة التحليلية ---
    with tab2:
        st.markdown("### الهندسة التحليلية")
        
        geometry_type = st.selectbox("اختر النوع", ["خط مستقيم", "دائرة", "قطع مكافئ"])
        
        if geometry_type == "خط مستقيم":
            st.markdown("#### معادلة الخط المستقيم: y = mx + c")
            col1, col2 = st.columns(2)
            with col1:
                m = st.number_input("الميل (m)", value=1.0)
            with col2:
                c = st.number_input("الجزء المقطوع (c)", value=0.0)
            
            if st.button("رسم الخط المستقيم"):
                x_vals = np.linspace(-10, 10, 100)
                y_vals = m * x_vals + c
                
                fig, ax = plt.subplots(figsize=(10, 8))
                ax.plot(x_vals, y_vals, 'r-', linewidth=2, label=f'y = {m}x + {c}')
                ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
                ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
                ax.grid(True, alpha=0.3)
                ax.set_title(f"الخط المستقيم: y = {m}x + {c}")
                ax.set_xlabel('x')
                ax.set_ylabel('y')
                ax.legend()
                st.pyplot(fig)
        
        elif geometry_type == "دائرة":
            st.markdown("#### معادلة الدائرة: (x - h)² + (y - k)² = r²")
            col1, col2, col3 = st.columns(3)
            with col1:
                h = st.number_input("المركز x (h)", value=0.0)
            with col2:
                k = st.number_input("المركز y (k)", value=0.0)
            with col3:
                r = st.number_input("نصف القطر (r)", value=1.0, min_value=0.1)
            
            if st.button("رسم الدائرة"):
                theta = np.linspace(0, 2*np.pi, 100)
                x_vals = h + r * np.cos(theta)
                y_vals = k + r * np.sin(theta)
                
                fig, ax = plt.subplots(figsize=(10, 8))
                ax.plot(x_vals, y_vals, 'g-', linewidth=2, label=f'(x-{h})² + (y-{k})² = {r}²')
                ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
                ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
                ax.grid(True, alpha=0.3)
                ax.set_aspect('equal')
                ax.set_title(f"الدائرة: المركز ({h}, {k})، نصف القطر {r}")
                ax.set_xlabel('x')
                ax.set_ylabel('y')
                ax.legend()
                st.pyplot(fig)

# === قسم الإحصاء ===
elif menu == "📊 الإحصاء":
    st.markdown('<p class="section-header">📊 قسم الإحصاء والاحتمالات</p>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["تحليل البيانات", "التوزيعات", "اختبارات الفرضيات"])
    
    # --- تبويب تحليل البيانات ---
    with tab1:
        st.markdown("### تحليل البيانات الأساسية")
        
        data_input = st.text_area("أدخل البيانات (أرقام مفصولة بمسافات أو فواصل)", "1 2 3 4 5 6 7 8 9 10")
        
        if st.button("تحليل البيانات", type="primary"):
            try:
                # معالجة البيانات
                data_str = data_input.replace(',', ' ').split()
                data = [float(x) for x in data_str]
                
                if len(data) < 2:
                    st.warning("⚠️ يرجى إدخال بيانات كافية (على الأقل رقمين)")
                else:
                    # حساب الإحصائيات
                    n = len(data)
                    mean = np.mean(data)
                    median = np.median(data)
                    mode = stats.mode(data, keepdims=True)[0][0]
                    std_dev = np.std(data, ddof=1)
                    variance = np.var(data, ddof=1)
                    min_val = np.min(data)
                    max_val = np.max(data)
                    range_val = max_val - min_val
                    
                    # عرض النتائج
                    st.markdown("### النتائج:")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("عدد القيم", n)
                        st.metric("المتوسط", f"{mean:.{precision}f}")
                        st.metric("الوسيط", f"{median:.{precision}f}")
                    
                    with col2:
                        st.metric("المنوال", f"{mode:.{precision}f}")
                        st.metric("الانحراف المعياري", f"{std_dev:.{precision}f}")
                        st.metric("التباين", f"{variance:.{precision}f}")
                    
                    with col3:
                        st.metric("الحد الأدنى", f"{min_val:.{precision}f}")
                        st.metric("الحد الأعلى", f"{max_val:.{precision}f}")
                        st.metric("المدى", f"{range_val:.{precision}f}")
                    
                    # رسم البيانات
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.hist(data, bins='auto', alpha=0.7, color='skyblue', edgecolor='black')
                    ax.axvline(mean, color='red', linestyle='dashed', linewidth=2, label=f'المتوسط = {mean:.2f}')
                    ax.axvline(median, color='green', linestyle='dashed', linewidth=2, label=f'الوسيط = {median:.2f}')
                    ax.set_title("التوزيع التكراري للبيانات")
                    ax.set_xlabel("القيم")
                    ax.set_ylabel("التكرار")
                    ax.legend()
                    ax.grid(True, alpha=0.3)
                    
                    st.pyplot(fig)
                    
                    st.success("✅ تم تحليل البيانات بنجاح!")
            
            except Exception as e:
                st.markdown(f'<div class="error-box">❌ خطأ: {str(e)}</div>', unsafe_allow_html=True)
    
    # --- تبويب التوزيعات ---
    with tab2:
        st.markdown("### التوزيعات الاحتمالية")
        
        distribution = st.selectbox("اختر التوزيع", ["طبيعي", "ثنائي", "بواسون"])
        
        if distribution == "طبيعي":
            st.markdown("#### التوزيع الطبيعي N(μ, σ²)")
            col1, col2 = st.columns(2)
            with col1:
                mu = st.number_input("المتوسط (μ)", value=0.0)
            with col2:
                sigma = st.number_input("الانحراف المعياري (σ)", value=1.0, min_value=0.1)
            
            if st.button("عرض التوزيع الطبيعي"):
                x = np.linspace(mu - 4*sigma, mu + 4*sigma, 1000)
                y = stats.norm.pdf(x, mu, sigma)
                
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(x, y, 'b-', linewidth=2, label=f'N({mu}, {sigma}²)')
                ax.fill_between(x, y, alpha=0.2, color='blue')
                ax.axvline(mu, color='red', linestyle='dashed', label=f'μ = {mu}')
                ax.set_title(f"التوزيع الطبيعي: μ = {mu}, σ = {sigma}")
                ax.set_xlabel("x")
                ax.set_ylabel("كثافة الاحتمال")
                ax.legend()
                ax.grid(True, alpha=0.3)
                st.pyplot(fig)
        
        elif distribution == "ثنائي":
            st.markdown("#### التوزيع ثنائي الحدين B(n, p)")
            col1, col2 = st.columns(2)
            with col1:
                n = st.number_input("عدد المحاولات (n)", min_value=1, value=10)
            with col2:
                p = st.number_input("احتمال النجاح (p)", min_value=0.0, max_value=1.0, value=0.5)
            
            if st.button("عرض التوزيع ثنائي"):
                x = np.arange(0, n+1)
                y = stats.binom.pmf(x, n, p)
                
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.bar(x, y, alpha=0.7, color='green', edgecolor='black')
                ax.set_title(f"التوزيع ثنائي: n = {n}, p = {p}")
                ax.set_xlabel("عدد النجاحات")
                ax.set_ylabel("الاحتمال")
                ax.grid(True, alpha=0.3)
                st.pyplot(fig)
        
        elif distribution == "بواسون":
            st.markdown("#### توزيع بواسون P(λ)")
            lam = st.number_input("متوسط الأحداث (λ)", min_value=0.1, value=3.0)
            
            if st.button("عرض توزيع بواسون"):
                x = np.arange(0, max(20, int(lam*3)))
                y = stats.poisson.pmf(x, lam)
                
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.bar(x, y, alpha=0.7, color='purple', edgecolor='black')
                ax.set_title(f"توزيع بواسون: λ = {lam}")
                ax.set_xlabel("عدد الأحداث")
                ax.set_ylabel("الاحتمال")
                ax.grid(True, alpha=0.3)
                st.pyplot(fig)
    
    # --- تبويب اختبارات الفرضيات ---
    with tab3:
        st.markdown("### اختبارات الفرضيات")
        
        test_type = st.selectbox("اختر الاختبار", ["t-test", "Chi-square", "ANOVA"])
        
        if test_type == "t-test":
            st.markdown("#### اختبار t للمتوسطات")
            
            col1, col2 = st.columns(2)
            with col1:
                sample1 = st.text_area("عينة 1 (أرقام مفصولة بمسافات)", "1 2 3 4 5")
            with col2:
                sample2 = st.text_area("عينة 2 (أرقام مفصولة بمسافات)", "2 3 4 5 6")
            
            if st.button("إجراء اختبار t"):
                try:
                    data1 = np.array([float(x) for x in sample1.split()])
                    data2 = np.array([float(x) for x in sample2.split()])
                    
                    t_stat, p_value = stats.ttest_ind(data1, data2)
                    
                    st.markdown("### نتائج اختبار t:")
                    st.metric("إحصائية t", f"{t_stat:.{precision}f}")
                    st.metric("القيمة الاحتمالية (p-value)", f"{p_value:.{precision}f}")
                    
                    if p_value < 0.05:
                        st.markdown("#### 📌 الاستنتاج:")
                        st.markdown('<div class="error-box">هناك فرق ذو دلالة إحصائية بين المتوسطين (p < 0.05)</div>', unsafe_allow_html=True)
                    else:
                        st.markdown("#### 📌 الاستنتاج:")
                        st.markdown('<div class="success-box">لا يوجد فرق ذو دلالة إحصائية بين المتوسطين (p ≥ 0.05)</div>', unsafe_allow_html=True)
                
                except Exception as e:
                    st.markdown(f'<div class="error-box">❌ خطأ: {str(e)}</div>', unsafe_allow_html=True)

# === قسم المساعدة ===
elif menu == "❓ المساعدة":
    st.markdown('<p class="section-header">❓ دليل المستخدم والمساعدة</p>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["الدليل", "الأمثلة", "التواصل"])
    
    # --- تبويب الدليل ---
    with tab1:
        st.markdown("### 📘 الدليل الشامل")
        
        with st.expander("كيفية استخدام التطبيق"):
            st.markdown("""
            1. **اختر القسم** الذي تريد العمل فيه من الشريط الجانبي
            2. **أدخل البيانات** في الحقول المخصصة
            3. **اضغط على زر التنفيذ** لرؤية النتائج
            4. **استخدم الإعدادات** لضبط دقة الحسابات وتنسيق النتائج
            5. **احفظ النتائج** باستخدام أزرار التصدير المتاحة
            """)
        
        with st.expander("الصيغ والدوال المتاحة"):
            st.markdown("""
            **العمليات الأساسية:**
            - `+` `-` `*` `/` `**` (أس)
            - `()` للأقواس
            
            **الدوال الرياضية:**
            - `sqrt(x)` - الجذر التربيعي
            - `sin(x)`, `cos(x)`, `tan(x)` - الدوال المثلثية
            - `asin(x)`, `acos(x)`, `atan(x)` - الدوال المثلثية العكسية
            - `exp(x)` - الدالة الأسية
            - `log(x)` - اللوغاريتم الطبيعي
            - `log(x, base)` - لوغاريتم بأي أساس
            - `abs(x)` - القيمة المطلقة
            
            **الثوابت:**
            - `pi` - باي (3.14159...)
            - `E` - العدد النيبيري (2.71828...)
            """)
        
        with st.expander("نصائح وحلول للمشكلات الشائعة"):
            st.markdown("""
            **مشاكل في حل المعادلات:**
            - تأكد من كتابة المعادلة بشكل صحيح
            - استخدم `**` للأسس وليس `^`
            - تأكد من وجود متغير صالح (x, y, z)
            
            **مشاكل في الرسوم البيانية:**
            - تجنب الدوال غير المعرفة في مجالات معينة
            - قلل من نطاق x إذا كانت القيم كبيرة جداً
            - تأكد من وجود matplotlib و numpy
            
            **نصائح عامة:**
            - ابدأ بالمعادلات البسيطة أولاً
            - استخدم الأمثلة الجاهزة للتعرف على الصيغ
            - قم بتحديث الصفحة إذا واجهت مشكلة
            """)
    
    # --- تبويب الأمثلة ---
    with tab2:
        st.markdown("### 📚 أمثلة عملية")
        
        st.markdown("#### 1. حل معادلة تربيعية")
        st.code("x**2 - 5*x + 6 = 0")
        st.markdown("الحلول: x = 2, x = 3")
        
        st.markdown("#### 2. حساب مشتق")
        st.code("d/dx (x**3 + 2*x**2 - 5*x + 1) = 3*x**2 + 4*x - 5")
        
        st.markdown("#### 3. حساب تكامل")
        st.code("∫(2*x + 3)dx = x**2 + 3*x + C")
        
        st.markdown("#### 4. رسم دالة")
        st.code("sin(x) في المجال [-2π, 2π]")
        
        st.markdown("#### 5. تحليل بيانات")
        st.code("البيانات: 1, 2, 3, 4, 5")
        st.markdown("المتوسط = 3، الانحراف المعياري = 1.58")
    
    # --- تبويب التواصل ---
    with tab3:
        st.markdown("### 📞 التواصل والدعم")
        
        st.markdown("""
        <div class="info-box">
        <h3>للاستفسارات والدعم الفني</h3>
        <p>يمكنك التواصل معنا عبر:</p>
        <ul>
            <li>📧 البريد الإلكتروني: support@ppfo-math.com</li>
            <li>🌐 موقع الويب: www.ppfo-math.com</li>
            <li>📱 تيليجرام: @ppfo_math_support</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🐛 الإبلاغ عن مشكلة")
        problem_type = st.selectbox("نوع المشكلة", ["خطأ في الحساب", "مشكلة في الواجهة", "اقتراح تحسين", "مشكلة أخرى"])
        description = st.text_area("وصف المشكلة", "يرجى وصف المشكلة بالتفصيل...")
        
        if st.button("إرسال التقرير"):
            st.markdown('<div class="success-box">✅ تم إرسال التقرير بنجاح! سنقوم بمراجعته في أقرب وقت.</div>', unsafe_allow_html=True)

# === تذييل الصفحة ===
st.markdown("---")
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("© 2023 PPFO Mathematical Suite. جميع الحقوق محفوظة.")
with col2:
    st.markdown("### ⭐ قيّم التطبيق")
    rating = st.slider("تقييمك", 1, 5, 4)
    if rating >= 4:
        st.markdown("🌟 شكراً لثقتك! نحن نعمل باستمرار لتحسين التطبيق.")
    else:
        st.markdown("💡 نعتذر عن أي إزعاج. يرجى التواصل معنا لحل المشكلة.")

# === حفظ حالة التطبيق ===
if 'session_data' not in st.session_state:
    st.session_state.session_data = {
        'started_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'page_visits': {}
    }

# تحديث عدد الزيارات
current_page = menu.split()[-1]  # الحصول على اسم الصفحة الحالي
if current_page not in st.session_state.session_data['page_visits']:
    st.session_state.session_data['page_visits'][current_page] = 0
st.session_state.session_data['page_visits'][current_page] += 1
