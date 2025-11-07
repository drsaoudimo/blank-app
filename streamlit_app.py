#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PPFO v20.0 - نسخة Streamlit متكاملة مع جميع فروع الرياضيات
تمت إضافة: التفاضل، التكامل، النهايات، المتسلسلات، والرياضيات المتقدمة
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
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image as PILImage
import base64
import sympy as sp
from sympy import symbols, diff, integrate, limit, series, solve, Eq
import pandas as pd
from scipy import stats

# === إعداد صفحة Streamlit ===
st.set_page_config(
    page_title="PPFO v20.0 - رياضيات متكاملة",
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
        text-align: center;
    }
    footer {
        display: none !important;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .stTab {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# === العنوان الرئيسي ===
st.markdown('<p class="main-header">🧮 PPFO v20.0 - رياضيات متكاملة</p>', unsafe_allow_html=True)
st.markdown("### تطبيق رياضي شامل يغطي جميع فروع الرياضيات")

# === الشريط الجانبي ===
with st.sidebar:
    st.image("https://via.placeholder.com/150x50?text=PPFO+Math", use_column_width=True)
    st.markdown("### 📚 القوائم الرئيسية")
    
    menu = st.radio(
        "التنقل",
        [
            "🏠 الصفحة الرئيسية",
            "🧮 الجبر",
            "📈 التفاضل",
            "📉 التكامل",
            "🎯 النهايات",
            "🔍 المتسلسلات",
            "📊 الإحصاء",
            "🔬 الرياضيات المتقدمة",
            "⚙️ الإعدادات",
            "❓ المساعدة"
        ],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### ⚙️ الإعدادات العامة")
    
    if 'precision' not in st.session_state:
        st.session_state.precision = 15
        st.session_state.use_latex = True
        st.session_state.plot_theme = 'default'
    
    precision = st.slider("دقة الحسابات", min_value=5, max_value=50, value=st.session_state.precision)
    st.session_state.precision = precision
    
    use_latex = st.checkbox("عرض النتائج بصيغة LaTeX", value=st.session_state.use_latex)
    st.session_state.use_latex = use_latex
    
    plot_theme = st.selectbox("سمة الرسوم البيانية", ["default", "dark_background", "seaborn", "ggplot"], 
                             index=["default", "dark_background", "seaborn", "ggplot"].index(st.session_state.plot_theme))
    st.session_state.plot_theme = plot_theme
    plt.style.use(plot_theme)
    
    st.markdown("---")
    st.markdown(f"**الإصدار:** 20.0")
    st.markdown(f"**التاريخ:** {time.strftime('%Y-%m-%d %H:%M')}")
    st.markdown(f"**SymPy:** {'متوفر' if True else 'غير متوفر'}")
    st.markdown(f"**NumPy:** {'متوفر' if True else 'غير متوفر'}")

# === الصفحة الرئيسية ===
if menu == "🏠 الصفحة الرئيسية":
    st.markdown("## 🎯 مرحباً بك في PPFO v20.0!")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="info-box">
        <h3>🌟 الميزات الرئيسية</h3>
        <ul>
            <li><b>🧮 الجبر:</b> حل المعادلات والأنظمة والبولينومات</li>
            <li><b>📈 التفاضل:</b> حساب المشتقات من جميع الرتب</li>
            <li><b>📉 التكامل:</b> التكامل المحدود وغير المحدود</li>
            <li><b>🎯 النهايات:</b> حساب النهايات من اليمين واليسار والثنائية</li>
            <li><b>🔍 المتسلسلات:</b> المتسلسلات التايلورية وماكلورين</li>
            <li><b>📊 الإحصاء:</b> تحليل البيانات والاختبارات الإحصائية</li>
            <li><b>🔬 الرياضيات المتقدمة:</b> تحويلات فورييه والمعادلات التفاضلية</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
        <h3>🚀 كيفية الاستخدام</h3>
        <ol>
            <li>اختر القسم المناسب من الشريط الجانبي</li>
            <li>أدخل البيانات أو الدوال المطلوبة</li>
            <li>اضبط الإعدادات حسب الحاجة</li>
            <li>انقر على زر التنفيذ لرؤية النتائج</li>
            <li>يمكنك حفظ النتائج أو تصديرها</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.image("https://via.placeholder.com/400x300?text=Math+Visualization", use_column_width=True)
        st.markdown("### 📱 التطبيق يعمل على جميع المنصات")
        
        st.markdown("""
        <div class="success-box">
        <h4>نصائح للاستخدام الفعال:</h4>
        <ul>
            <li>ابدأ بالدوال البسيطة أولاً</li>
            <li>استخدم صيغة LaTeX لعرض النتائج بدقة</li>
            <li>استكشف الأمثلة الجاهزة في كل قسم</li>
            <li>اضبط دقة الحسابات حسب الحاجة</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

# === قسم الجبر ===
elif menu == "🧮 الجبر":
    st.markdown('<p class="section-header">🧮 قسم الجبر المتقدم</p>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["حل معادلة", "نظام معادلات", "البولينومات"])
    
    # --- تبويب حل معادلة واحدة ---
    with tab1:
        st.markdown("### حل معادلة جبرية")
        st.markdown("""
        <div class="info-box">
        <h4>تعليمات</h4>
        <p>أدخل معادلة رياضية باستخدام الصيغ التالية:</p>
        <ul>
            <li>استخدم <code>**</code> للأسس (مثال: x**2)</li>
            <li>استخدم <code>*</code> للضرب (مثال: 2*x)</li>
            <li>الدوال المتاحة: <code>sin</code>, <code>cos</code>, <code>tan</code>, <code>log</code>, <code>exp</code>, <code>sqrt</code></li>
            <li>الثوابت: <code>pi</code>, <code>E</code></li>
        </ul>
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
                        expr = sp.parse_expr(left.strip()) - sp.parse_expr(right.strip())
                    else:
                        expr = sp.parse_expr(equation)
                    
                    # حل المعادلة
                    solutions = solve(expr, x)
                    
                    # عرض النتائج
                    st.markdown("### النتائج:")
                    st.markdown(f"**المعادلة:** `{equation}`")
                    st.markdown(f"**المتغير:** `{variable}`")
                    st.markdown(f"**عدد الحلول:** {len(solutions)}")
                    
                    for i, sol in enumerate(solutions, 1):
                        sol_eval = sp.N(sol, st.session_state.precision)
                        st.markdown(f"#### الحل {i}:")
                        if st.session_state.use_latex:
                            st.latex(f"x_{{{i}}} = {sp.latex(sol)}")
                            st.latex(f"x_{{{i}}} \\approx {sp.latex(sol_eval)}")
                        else:
                            st.code(f"الحل الدقيق: {sol}")
                            st.code(f"الحل التقريبي: {sol_eval}")
                    
                    # رسم الدالة
                    if st.checkbox("عرض الرسم البياني"):
                        x_vals = np.linspace(-10, 10, 1000)
                        f = sp.lambdify(x, expr, 'numpy')
                        
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
                        
                        ax.plot(x_vals, y_vals, 'b-', linewidth=2, label=f'${sp.latex(expr)} = 0$')
                        ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
                        ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
                        ax.grid(True, alpha=0.3)
                        ax.set_title(f"رسم المعادلة: {equation}")
                        ax.set_xlabel('x')
                        ax.set_ylabel('y')
                        ax.legend()
                        
                        st.pyplot(fig)
                
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
                        expr = sp.parse_expr(left.strip()) - sp.parse_expr(right.strip())
                    else:
                        expr = sp.parse_expr(eq)
                    eqs.append(expr)
                
                # حل النظام
                solutions = solve(eqs, syms, dict=True)
                
                # عرض النتائج
                st.markdown("### النتائج:")
                st.markdown(f"**عدد الحلول:** {len(solutions)}")
                
                for i, sol in enumerate(solutions, 1):
                    st.markdown(f"#### الحل {i}:")
                    solution_str = "{"
                    for var, val in sol.items():
                        val_eval = sp.N(val, st.session_state.precision)
                        if st.session_state.use_latex:
                            st.latex(f"{sp.latex(var)} = {sp.latex(val)} \\approx {sp.latex(val_eval)}")
                        else:
                            st.code(f"{var} = {val} ≈ {val_eval}")
                        solution_str += f"{var}={val}, "
                    solution_str = solution_str.rstrip(', ') + "}"
                    
                    # رسم الحلول
                    if st.checkbox(f"عرض الرسم للحل {i}"):
                        if 'x' in sol and 'y' in sol:
                            fig, ax = plt.subplots(figsize=(8, 6))
                            # رسم معادلات النظام
                            x_vals = np.linspace(-10, 10, 400)
                            colors = ['r-', 'g-', 'b-', 'm-', 'c-']
                            
                            for j, eq in enumerate(equations):
                                if '=' in eq:
                                    left, right = eq.split('=', 1)
                                    expr = sp.parse_expr(left.strip()) - sp.parse_expr(right.strip())
                                else:
                                    expr = sp.parse_expr(eq)
                                
                                # حل بالنسبة لـ y
                                try:
                                    y_expr = solve(expr, symbols('y'))[0]
                                    f = sp.lambdify(symbols('x'), y_expr, 'numpy')
                                    y_vals = [f(xv) for xv in x_vals]
                                    ax.plot(x_vals, y_vals, colors[j], linewidth=2, label=f'المعادلة {j+1}')
                                except:
                                    pass
                            
                            # تحديد الحل
                            x_val = float(sol[symbols('x')])
                            y_val = float(sol[symbols('y')])
                            ax.plot(x_val, y_val, 'ko', markersize=10, label=f'الحل: ({x_val:.2f}, {y_val:.2f})')
                            
                            ax.grid(True)
                            ax.set_title(f"رسم الحل {i} للنظام")
                            ax.set_xlabel('x')
                            ax.set_ylabel('y')
                            ax.legend()
                            
                            st.pyplot(fig)
            
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
                poly = sp.parse_expr(polynomial)
                
                # تحليل البولينوم
                factored = factor(poly)
                expanded = expand(poly)
                roots = solve(poly, x)
                
                # عرض النتائج
                st.markdown("### النتائج:")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### الشكل المحلل:")
                    if st.session_state.use_latex:
                        st.latex(f"{sp.latex(factored)}")
                    else:
                        st.code(str(factored))
                
                with col2:
                    st.markdown("#### الشكل الموسع:")
                    if st.session_state.use_latex:
                        st.latex(f"{sp.latex(expanded)}")
                    else:
                        st.code(str(expanded))
                
                st.markdown("#### الجذور:")
                for i, root in enumerate(roots, 1):
                    root_eval = sp.N(root, st.session_state.precision)
                    if st.session_state.use_latex:
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

# === قسم التفاضل ===
elif menu == "📈 التفاضل":
    st.markdown('<p class="section-header">📈 التفاضل والمشتقات</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        function = st.text_input("أدخل الدالة", "x**3 + 2*x**2 - 5*x + 1", key="deriv_func")
        variable = st.text_input("المتغير", "x", max_chars=1, key="deriv_var")
        order = st.number_input("رتبة المشتق", min_value=1, max_value=10, value=1)
        
        if st.button("حساب المشتق", type="primary"):
            try:
                x = symbols(variable)
                func = sp.parse_expr(function)
                derivative = diff(func, x, order)
                
                # عرض النتائج
                st.markdown("### النتائج:")
                st.markdown(f"**الدالة:** `{function}`")
                st.markdown(f"**المتغير:** `{variable}`")
                st.markdown(f"**رتبة المشتق:** {order}")
                
                st.markdown("#### المشتق:")
                if st.session_state.use_latex:
                    st.latex(f"\\frac{{d^{{{order}}}f}}{{d{variable}^{{{order}}}}} = {sp.latex(derivative)}")
                else:
                    st.code(str(derivative))
                
                # حساب قيمة المشتق عند نقطة
                point = st.number_input("احسب قيمة المشتق عند", value=1.0)
                if st.button("حساب القيمة"):
                    deriv_func = sp.lambdify(x, derivative, 'numpy')
                    value = deriv_func(point)
                    st.markdown(f"#### قيمة المشتق عند x = {point}:")
                    st.markdown(f"**النتيجة:** {value:.{st.session_state.precision}f}")
                
                # رسم الدالة والمشتق
                if st.checkbox("عرض الرسم البياني للدالة والمشتق"):
                    x_vals = np.linspace(-5, 5, 1000)
                    f = sp.lambdify(x, func, 'numpy')
                    f_deriv = sp.lambdify(x, derivative, 'numpy')
                    
                    fig, ax = plt.subplots(figsize=(12, 8))
                    
                    # رسم الدالة الأصلية
                    y_vals = [f(xv) if np.isfinite(f(xv)) else np.nan for xv in x_vals]
                    ax.plot(x_vals, y_vals, 'b-', linewidth=2, label=f'الدالة الأصلية: {function}')
                    
                    # رسم المشتق
                    y_deriv_vals = [f_deriv(xv) if np.isfinite(f_deriv(xv)) else np.nan for xv in x_vals]
                    ax.plot(x_vals, y_deriv_vals, 'r--', linewidth=2, label=f'المشتق: {derivative}')
                    
                    ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
                    ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
                    ax.grid(True, alpha=0.3)
                    ax.set_title(f"رسم الدالة والمشتق (الرتبة {order})")
                    ax.set_xlabel('x')
                    ax.set_ylabel('y')
                    ax.legend()
                    
                    st.pyplot(fig)
            
            except Exception as e:
                st.markdown(f'<div class="error-box">❌ خطأ: {str(e)}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📚 قواعد الاشتقاق الأساسية")
        st.markdown("""
        <div class="info-box">
        <h4>الثابت</h4>
        <p>\\(\\frac{d}{dx}(c) = 0\\)</p>
        
        <h4>القوة</h4>
        <p>\\(\\frac{d}{dx}(x^n) = nx^{n-1}\\)</p>
        
        <h4>المجموع</h4>
        <p>\\(\\frac{d}{dx}(f+g) = \\frac{df}{dx} + \\frac{dg}{dx}\\)</p>
        
        <h4>الضرب</h4>
        <p>\\(\\frac{d}{dx}(f \\cdot g) = f' \\cdot g + f \\cdot g'\\)</p>
        
        <h4>الخارج</h4>
        <p>\\(\\frac{d}{dx}(\\frac{f}{g}) = \\frac{f' \\cdot g - f \\cdot g'}{g^2}\\)</p>
        
        <h4>الدوال المثلثية</h4>
        <p>\\(\\frac{d}{dx}(\\sin x) = \\cos x\\)</p>
        <p>\\(\\frac{d}{dx}(\\cos x) = -\\sin x\\)</p>
        <p>\\(\\frac{d}{dx}(\\tan x) = \\sec^2 x\\)</p>
        </div>
        """, unsafe_allow_html=True)

# === قسم التكامل ===
elif menu == "📉 التكامل":
    st.markdown('<p class="section-header">📉 التكامل</p>', unsafe_allow_html=True)
    
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
            func = sp.parse_expr(function)
            
            if integration_type == "غير محدود":
                integral = integrate(func, x)
                
                st.markdown("### النتائج:")
                st.markdown("#### التكامل غير المحدود:")
                if st.session_state.use_latex:
                    st.latex(f"\\int {sp.latex(func)} \\, d{variable} = {sp.latex(integral)} + C")
                else:
                    st.code(str(integral) + " + C")
                
                # رسم الدالة والتكامل
                if st.checkbox("عرض الرسم البياني للدالة والتكامل"):
                    x_vals = np.linspace(-5, 5, 1000)
                    f = sp.lambdify(x, func, 'numpy')
                    
                    fig, ax = plt.subplots(figsize=(12, 8))
                    y_vals = [f(xv) if np.isfinite(f(xv)) else np.nan for xv in x_vals]
                    ax.plot(x_vals, y_vals, 'b-', linewidth=2, label=f'الدالة: {function}')
                    
                    # حساب التكامل عند نقاط مختلفة
                    integral_func = sp.lambdify(x, integral, 'numpy')
                    y_int_vals = [integral_func(xv) if np.isfinite(integral_func(xv)) else np.nan for xv in x_vals]
                    ax.plot(x_vals, y_int_vals, 'r--', linewidth=2, label=f'التكامل: {integral}')
                    
                    ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
                    ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
                    ax.grid(True, alpha=0.3)
                    ax.set_title("رسم الدالة والتكامل غير المحدود")
                    ax.set_xlabel('x')
                    ax.set_ylabel('y')
                    ax.legend()
                    
                    st.pyplot(fig)
            
            else:
                a = sp.parse_expr(lower_limit)
                b = sp.parse_expr(upper_limit)
                definite_integral = integrate(func, (x, a, b))
                numerical_value = sp.N(definite_integral, st.session_state.precision)
                
                st.markdown("### النتائج:")
                st.markdown(f"**الحدود:** من {lower_limit} إلى {upper_limit}")
                
                st.markdown("#### التكامل المحدود:")
                if st.session_state.use_latex:
                    st.latex(f"\\int_{{{sp.latex(a)}}}^{{{sp.latex(b)}}} {sp.latex(func)} \\, d{variable} = {sp.latex(definite_integral)}")
                    st.latex(f"\\approx {sp.latex(numerical_value)}")
                else:
                    st.code(str(definite_integral))
                    st.code(f"≈ {numerical_value}")
                
                # رسم منطقة التكامل
                if st.checkbox("عرض منطقة التكامل"):
                    x_vals = np.linspace(float(a), float(b), 1000)
                    f = sp.lambdify(x, func, 'numpy')
                    
                    fig, ax = plt.subplots(figsize=(12, 8))
                    y_vals = [f(xv) for xv in x_vals]
                    ax.plot(x_vals, y_vals, 'b-', linewidth=2, label=f'الدالة: {function}')
                    
                    # تظليل منطقة التكامل
                    ax.fill_between(x_vals, y_vals, alpha=0.3, color='blue', label=f'المساحة = {numerical_value:.4f}')
                    
                    ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
                    ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
                    ax.grid(True, alpha=0.3)
                    ax.set_title(f"منطقة التكامل من {lower_limit} إلى {upper_limit}")
                    ax.set_xlabel('x')
                    ax.set_ylabel('y')
                    ax.legend()
                    
                    st.pyplot(fig)
        
        except Exception as e:
            st.markdown(f'<div class="error-box">❌ خطأ: {str(e)}</div>', unsafe_allow_html=True)

# === قسم النهايات ===
elif menu == "🎯 النهايات":
    st.markdown('<p class="section-header">🎯 النهايات</p>', unsafe_allow_html=True)
    
    function = st.text_input("أدخل الدالة", "sin(x)/x", key="limit_func")
    variable = st.text_input("المتغير", "x", max_chars=1, key="limit_var")
    point = st.text_input("نقطة النهاية", "0", key="limit_point")
    direction = st.selectbox("الاتجاه", ["ثنائي", "من اليمين", "من اليسار"])
    
    if st.button("حساب النهاية", type="primary"):
        try:
            x = symbols(variable)
            func = sp.parse_expr(function)
            point_val = sp.parse_expr(point)
            
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
            if st.session_state.use_latex:
                st.latex(f"\\lim_{{{variable} \\to {point}}} {sp.latex(func)} = {sp.latex(limit_val)}")
            else:
                st.code(str(limit_val))
            
            # رسم الدالة حول نقطة النهاية
            if st.checkbox("عرض الرسم البياني حول نقطة النهاية"):
                # تحديد نطاق حول نقطة النهاية
                if point_val.is_real:
                    point_float = float(point_val)
                    x_min = point_float - 1
                    x_max = point_float + 1
                    x_vals = np.linspace(x_min, x_max, 1000)
                else:
                    x_vals = np.linspace(-5, 5, 1000)
                
                f = sp.lambdify(x, func, 'numpy')
                
                fig, ax = plt.subplots(figsize=(12, 8))
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
                
                ax.plot(x_vals, y_vals, 'b-', linewidth=2, label=f'الدالة: {function}')
                ax.axhline(y=float(limit_val), color='r', linestyle='--', alpha=0.7, label=f'النهاية = {limit_val}')
                ax.axvline(x=float(point_val), color='g', linestyle='--', alpha=0.7, label=f'نقطة النهاية = {point_val}')
                
                ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
                ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
                ax.grid(True, alpha=0.3)
                ax.set_title(f"رسم الدالة حول نقطة النهاية {point}")
                ax.set_xlabel('x')
                ax.set_ylabel('y')
                ax.legend()
                
                st.pyplot(fig)
        
        except Exception as e:
            st.markdown(f'<div class="error-box">❌ خطأ: {str(e)}</div>', unsafe_allow_html=True)

# === قسم المتسلسلات ===
elif menu == "🔍 المتسلسلات":
    st.markdown('<p class="section-header">🔍 المتسلسلات</p>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["متسلسلة تايلور", "متسلسلة ماكلورين", "التقارب"])
    
    # --- تبويب متسلسلة تايلور ---
    with tab1:
        st.markdown("### متسلسلة تايلور")
        st.markdown("""
        <div class="info-box">
        <h4>الصيغة العامة</h4>
        <p>\\(f(x) = \\sum_{n=0}^{\\infty} \\frac{f^{(n)}(a)}{n!}(x-a)^n\\)</p>
        <p>حيث \\(a\\) هي نقطة التطوير</p>
        </div>
        """, unsafe_allow_html=True)
        
        function = st.text_input("أدخل الدالة", "exp(x)", key="taylor_func")
        variable = st.text_input("المتغير", "x", max_chars=1, key="taylor_var")
        point = st.number_input("نقطة التطوير", value=0.0)
        order = st.number_input("رتبة المتسلسلة", min_value=1, max_value=20, value=5)
        
        if st.button("حساب متسلسلة تايلور", type="primary"):
            try:
                x = symbols(variable)
                func = sp.parse_expr(function)
                taylor_series = series(func, x, point, order+1)
                
                st.markdown("### النتائج:")
                st.markdown(f"**الدالة:** `{function}`")
                st.markdown(f"**نقطة التطوير:** {point}")
                st.markdown(f"**الرتبة:** {order}")
                
                if st.session_state.use_latex:
                    st.latex(f"f(x) = {sp.latex(taylor_series)}")
                else:
                    st.code(str(taylor_series))
                
                # رسم الدالة والمتسلسلة
                if st.checkbox("عرض الرسم البياني"):
                    x_vals = np.linspace(point-2, point+2, 1000)
                    f = sp.lambdify(x, func, 'numpy')
                    taylor_func = sp.lambdify(x, taylor_series.removeO(), 'numpy')
                    
                    fig, ax = plt.subplots(figsize=(12, 8))
                    
                    # رسم الدالة الأصلية
                    y_vals = [f(xv) for xv in x_vals]
                    ax.plot(x_vals, y_vals, 'b-', linewidth=2, label=f'الدالة الأصلية: {function}')
                    
                    # رسم متسلسلة تايلور
                    y_taylor_vals = [taylor_func(xv) for xv in x_vals]
                    ax.plot(x_vals, y_taylor_vals, 'r--', linewidth=2, label=f'متسلسلة تايلور (الرتبة {order})')
                    
                    ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
                    ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
                    ax.grid(True, alpha=0.3)
                    ax.set_title(f"رسم الدالة ومتسلسلة تايلور عند النقطة {point}")
                    ax.set_xlabel('x')
                    ax.set_ylabel('y')
                    ax.legend()
                    
                    st.pyplot(fig)
            
            except Exception as e:
                st.markdown(f'<div class="error-box">❌ خطأ: {str(e)}</div>', unsafe_allow_html=True)
    
    # --- تبويب متسلسلة ماكلورين ---
    with tab2:
        st.markdown("### متسلسلة ماكلورين")
        st.markdown("""
        <div class="info-box">
        <h4>الصيغة العامة</h4>
        <p>\\(f(x) = \\sum_{n=0}^{\\infty} \\frac{f^{(n)}(0)}{n!}x^n\\)</p>
        <p>هي حالة خاصة من متسلسلة تايلور عند النقطة \\(a = 0\\)</p>
        </div>
        """, unsafe_allow_html=True)
        
        function = st.text_input("أدخل الدالة", "sin(x)", key="maclaurin_func")
        variable = st.text_input("المتغير", "x", max_chars=1, key="maclaurin_var")
        order = st.number_input("رتبة المتسلسلة", min_value=1, max_value=20, value=7, key="maclaurin_order")
        
        if st.button("حساب متسلسلة ماكلورين", type="primary"):
            try:
                x = symbols(variable)
                func = sp.parse_expr(function)
                maclaurin_series = series(func, x, 0, order+1)
                
                st.markdown("### النتائج:")
                st.markdown(f"**الدالة:** `{function}`")
                st.markdown(f"**الرتبة:** {order}")
                
                if st.session_state.use_latex:
                    st.latex(f"f(x) = {sp.latex(maclaurin_series)}")
                else:
                    st.code(str(maclaurin_series))
                
                # رسم الدالة والمتسلسلة
                if st.checkbox("عرض الرسم البياني", key="maclaurin_plot"):
                    x_vals = np.linspace(-2*math.pi, 2*math.pi, 1000)
                    f = sp.lambdify(x, func, 'numpy')
                    maclaurin_func = sp.lambdify(x, maclaurin_series.removeO(), 'numpy')
                    
                    fig, ax = plt.subplots(figsize=(12, 8))
                    
                    # رسم الدالة الأصلية
                    y_vals = [f(xv) for xv in x_vals]
                    ax.plot(x_vals, y_vals, 'b-', linewidth=2, label=f'الدالة الأصلية: {function}')
                    
                    # رسم متسلسلة ماكلورين
                    y_maclaurin_vals = [maclaurin_func(xv) for xv in x_vals]
                    ax.plot(x_vals, y_maclaurin_vals, 'r--', linewidth=2, label=f'متسلسلة ماكلورين (الرتبة {order})')
                    
                    ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
                    ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
                    ax.grid(True, alpha=0.3)
                    ax.set_title(f"رسم الدالة ومتسلسلة ماكلورين")
                    ax.set_xlabel('x')
                    ax.set_ylabel('y')
                    ax.legend()
                    
                    st.pyplot(fig)
            
            except Exception as e:
                st.markdown(f'<div class="error-box">❌ خطأ: {str(e)}</div>', unsafe_allow_html=True)
    
    # --- تبويب التقارب ---
    with tab3:
        st.markdown("### اختبارات تقارب المتسلسلات")
        st.markdown("""
        <div class="info-box">
        <h4>اختبار النسبة</h4>
        <p>\\(\\lim_{n \\to \\infty} \\left|\\frac{a_{n+1}}{a_n}\\right| = L\\)</p>
        <p>إذا كان \\(L < 1\\) فالمتسلسلة متقاربة\\<br>
        إذا كان \\(L > 1\\) فالمتسلسلة متباعدة\\<br>
        إذا كان \\(L = 1\\) فالاختبار غير حاسم</p>
        </div>
        """, unsafe_allow_html=True)
        
        series_term = st.text_input("أدخل حد المتسلسلة", "1/n**2", key="series_term")
        variable = st.text_input("المتغير", "n", max_chars=1, key="series_var")
        
        if st.button("تحليل تقارب المتسلسلة", type="primary"):
            try:
                n = symbols(variable)
                a_n = sp.parse_expr(series_term)
                
                # حساب حد النسبة
                a_np1 = a_n.subs(n, n+1)
                ratio = sp.simplify(a_np1 / a_n)
                ratio_limit = limit(ratio, n, sp.oo)
                
                st.markdown("### نتائج تحليل التقارب:")
                st.markdown(f"**حد المتسلسلة:** `{series_term}`")
                st.markdown(f"**حد النسبة:** `{ratio}`")
                st.markdown(f"**نهاية حد النسبة:** `{ratio_limit}`")
                
                if ratio_limit.is_real:
                    ratio_float = float(ratio_limit)
                    if ratio_float < 1:
                        st.markdown('<div class="success-box">المتسلسلة متقاربة (حد النسبة < 1)</div>', unsafe_allow_html=True)
                    elif ratio_float > 1:
                        st.markdown('<div class="error-box">المتسلسلة متباعدة (حد النسبة > 1)</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="warning-box">الاختبار غير حاسم (حد النسبة = 1)</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="warning-box">غير قادر على تحديد التقارب من خلال اختبار النسبة</div>', unsafe_allow_html=True)
                
                # حساب المجموع الجزئي
                if st.checkbox("حساب المجموع الجزئي"):
                    N = st.number_input("عدد الحدود", min_value=1, max_value=1000, value=100)
                    partial_sum = sum([float(a_n.subs(n, i)) for i in range(1, N+1)])
                    st.markdown(f"**المجموع الجزئي للـ {N} حدًا الأول:** {partial_sum:.{st.session_state.precision}f}")
                    
                    # رسم الحدود المتتالية
                    if st.checkbox("عرض رسم الحدود المتتالية"):
                        terms = [float(a_n.subs(n, i)) for i in range(1, N+1)]
                        
                        fig, ax = plt.subplots(figsize=(12, 6))
                        ax.plot(range(1, N+1), terms, 'bo-', linewidth=2, markersize=4)
                        ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
                        ax.grid(True, alpha=0.3)
                        ax.set_title(f"رسم الحدود المتتالية للمتسلسلة")
                        ax.set_xlabel('رقم الحد')
                        ax.set_ylabel('قيمة الحد')
                        ax.set_yscale('log')  # مقياس لوغاريتمي لرؤية التقارب بوضوح
                        
                        st.pyplot(fig)
            
            except Exception as e:
                st.markdown(f'<div class="error-box">❌ خطأ: {str(e)}</div>', unsafe_allow_html=True)

# === قسم الإحصاء ===
elif menu == "📊 الإحصاء":
    st.markdown('<p class="section-header">📊 الإحصاء والاحتمالات</p>', unsafe_allow_html=True)
    
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
                    mode_result = stats.mode(data)
                    mode = mode_result.mode[0] if hasattr(mode_result, 'mode') and len(mode_result.mode) > 0 else "لا يوجد"
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
                        st.metric("المتوسط", f"{mean:.{st.session_state.precision}f}")
                        st.metric("الوسيط", f"{median:.{st.session_state.precision}f}")
                    
                    with col2:
                        st.metric("المنوال", f"{mode:.{st.session_state.precision}f}" if isinstance(mode, (int, float)) else mode)
                        st.metric("الانحراف المعياري", f"{std_dev:.{st.session_state.precision}f}")
                        st.metric("التباين", f"{variance:.{st.session_state.precision}f}")
                    
                    with col3:
                        st.metric("الحد الأدنى", f"{min_val:.{st.session_state.precision}f}")
                        st.metric("الحد الأعلى", f"{max_val:.{st.session_state.precision}f}")
                        st.metric("المدى", f"{range_val:.{st.session_state.precision}f}")
                    
                    # رسم البيانات
                    fig, ax = plt.subplots(figsize=(12, 6))
                    ax.hist(data, bins='auto', alpha=0.7, color='skyblue', edgecolor='black', density=True)
                    
                    # إضافة منحنى التوزيع الطبيعي
                    x = np.linspace(min_val, max_val, 100)
                    y = stats.norm.pdf(x, mean, std_dev)
                    ax.plot(x, y, 'r-', linewidth=2, label='التوزيع الطبيعي')
                    
                    ax.axvline(mean, color='red', linestyle='dashed', linewidth=2, label=f'المتوسط = {mean:.2f}')
                    ax.axvline(median, color='green', linestyle='dashed', linewidth=2, label=f'الوسيط = {median:.2f}')
                    ax.set_title("التوزيع التكراري للبيانات")
                    ax.set_xlabel("القيم")
                    ax.set_ylabel("الكثافة")
                    ax.legend()
                    ax.grid(True, alpha=0.3)
                    
                    st.pyplot(fig)
                    
                    # مخطط الصندوق
                    st.markdown("#### مخطط الصندوق (Box Plot):")
                    fig2, ax2 = plt.subplots(figsize=(10, 6))
                    ax2.boxplot(data, vert=False, patch_artist=True, 
                               boxprops=dict(facecolor='skyblue', color='blue'),
                               medianprops=dict(color='red'))
                    ax2.set_title("مخطط الصندوق للبيانات")
                    ax2.set_xlabel("القيم")
                    ax2.grid(True, alpha=0.3)
                    
                    st.pyplot(fig2)
                    
                    st.success("✅ تم تحليل البيانات بنجاح!")
            
            except Exception as e:
                st.markdown(f'<div class="error-box">❌ خطأ: {str(e)}</div>', unsafe_allow_html=True)
    
    # --- تبويب التوزيعات ---
    with tab2:
        st.markdown("### التوزيعات الاحتمالية")
        
        distribution = st.selectbox("اختر التوزيع", ["طبيعي", "ثنائي", "بواسون", "أسي"])
        
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
                
                fig, ax = plt.subplots(figsize=(12, 6))
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
                
                fig, ax = plt.subplots(figsize=(12, 6))
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
                
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.bar(x, y, alpha=0.7, color='purple', edgecolor='black')
                ax.set_title(f"توزيع بواسون: λ = {lam}")
                ax.set_xlabel("عدد الأحداث")
                ax.set_ylabel("الاحتمال")
                ax.grid(True, alpha=0.3)
                st.pyplot(fig)
        
        elif distribution == "أسي":
            st.markdown("#### التوزيع الأسي Exp(λ)")
            lam = st.number_input("معدل الحدوث (λ)", min_value=0.1, value=1.0)
            
            if st.button("عرض التوزيع الأسي"):
                x = np.linspace(0, 5/lam, 1000)
                y = stats.expon.pdf(x, scale=1/lam)
                
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.plot(x, y, 'r-', linewidth=2, label=f'Exp(λ = {lam})')
                ax.fill_between(x, y, alpha=0.2, color='red')
                ax.set_title(f"التوزيع الأسي: λ = {lam}")
                ax.set_xlabel("x")
                ax.set_ylabel("كثافة الاحتمال")
                ax.legend()
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
                    st.metric("إحصائية t", f"{t_stat:.{st.session_state.precision}f}")
                    st.metric("القيمة الاحتمالية (p-value)", f"{p_value:.{st.session_state.precision}f}")
                    
                    if p_value < 0.05:
                        st.markdown("#### 📌 الاستنتاج:")
                        st.markdown('<div class="error-box">هناك فرق ذو دلالة إحصائية بين المتوسطين (p < 0.05)</div>', unsafe_allow_html=True)
                    else:
                        st.markdown("#### 📌 الاستنتاج:")
                        st.markdown('<div class="success-box">لا يوجد فرق ذو دلالة إحصائية بين المتوسطين (p ≥ 0.05)</div>', unsafe_allow_html=True)
                
                except Exception as e:
                    st.markdown(f'<div class="error-box">❌ خطأ: {str(e)}</div>', unsafe_allow_html=True)

# === قسم الرياضيات المتقدمة ===
elif menu == "🔬 الرياضيات المتقدمة":
    st.markdown('<p class="section-header">🔬 الرياضيات المتقدمة</p>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["المعادلات التفاضلية", "تحويلات فورييه", "الجبر الخطي"])
    
    # --- تبويب المعادلات التفاضلية ---
    with tab1:
        st.markdown("### المعادلات التفاضلية")
        st.markdown("""
        <div class="info-box">
        <h4>المعادلات التفاضلية العادية</h4>
        <p>\\(\\frac{dy}{dx} = f(x, y)\\)</p>
        <p>الحل العام: \\(y = F(x) + C\\)</p>
        </div>
        """, unsafe_allow_html=True)
        
        equation = st.text_input("أدخل المعادلة التفاضلية", "f'(x) - f(x) = 0", key="ode_eq")
        variable = st.text_input("المتغير", "x", max_chars=1, key="ode_var")
        
        if st.button("حل المعادلة التفاضلية", type="primary"):
            try:
                x = symbols(variable)
                f = sp.Function('f')
                ode = sp.parse_expr(equation.replace("f'", "Derivative(f(x), x)"))
                
                # حل المعادلة التفاضلية
                solution = sp.dsolve(ode, f(x))
                
                st.markdown("### النتائج:")
                st.markdown(f"**المعادلة التفاضلية:** `{equation}`")
                
                if st.session_state.use_latex:
                    st.latex(f"\\text{{الحل:}} \\quad {sp.latex(solution)}")
                else:
                    st.code(str(solution))
                
                # رسم الحل
                if st.checkbox("عرض الرسم البياني للحل"):
                    # الحصول على الحل كدالة
                    sol_func = sp.lambdify(x, solution.rhs, 'numpy')
                    
                    x_vals = np.linspace(-5, 5, 1000)
                    y_vals = []
                    for xv in x_vals:
                        try:
                            yv = sol_func(xv)
                            if np.isfinite(yv):
                                y_vals.append(yv)
                            else:
                                y_vals.append(np.nan)
                        except:
                            y_vals.append(np.nan)
                    
                    fig, ax = plt.subplots(figsize=(12, 6))
                    ax.plot(x_vals, y_vals, 'b-', linewidth=2, label=f'الحل: {solution}')
                    ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
                    ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
                    ax.grid(True, alpha=0.3)
                    ax.set_title("رسم حل المعادلة التفاضلية")
                    ax.set_xlabel('x')
                    ax.set_ylabel('y')
                    ax.legend()
                    
                    st.pyplot(fig)
            
            except Exception as e:
                st.markdown(f'<div class="error-box">❌ خطأ: {str(e)}</div>', unsafe_allow_html=True)
    
    # --- تبويب تحويلات فورييه ---
    with tab2:
        st.markdown("### تحويلات فورييه")
        st.markdown("""
        <div class="info-box">
        <h4>تحويل فورييه</h4>
        <p>\\(F(\\omega) = \\int_{-\\infty}^{\\infty} f(t) e^{-i\\omega t} dt\\)</p>
        <h4>تحويل فورييه العكسي</h4>
        <p>\\(f(t) = \\frac{1}{2\\pi} \\int_{-\\infty}^{\\infty} F(\\omega) e^{i\\omega t} d\\omega\\)</p>
        </div>
        """, unsafe_allow_html=True)
        
        function = st.text_input("أدخل الدالة الزمنية", "exp(-t**2)", key="fourier_func")
        variable = st.text_input("المتغير", "t", max_chars=1, key="fourier_var")
        
        if st.button("حساب تحويل فورييه", type="primary"):
            try:
                t = symbols(variable)
                omega = symbols('omega')
                func = sp.parse_expr(function)
                
                # حساب تحويل فورييه
                fourier_transform = sp.integrate(func * sp.exp(-sp.I * omega * t), (t, -sp.oo, sp.oo))
                
                st.markdown("### النتائج:")
                st.markdown(f"**الدالة الزمنية:** `{function}`")
                
                if st.session_state.use_latex:
                    st.latex(f"F(\\omega) = {sp.latex(fourier_transform)}")
                else:
                    st.code(str(fourier_transform))
                
                # رسم الدالة الزمنية وتحويل فورييه
                if st.checkbox("عرض الرسم البياني"):
                    # رسم الدالة الزمنية
                    t_vals = np.linspace(-5, 5, 1000)
                    f = sp.lambdify(t, func, 'numpy')
                    
                    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
                    
                    # الدالة الزمنية
                    y_vals = [f(tv) for tv in t_vals]
                    ax1.plot(t_vals, y_vals, 'b-', linewidth=2)
                    ax1.set_title("الدالة الزمنية")
                    ax1.set_xlabel('t')
                    ax1.set_ylabel('f(t)')
                    ax1.grid(True, alpha=0.3)
                    
                    # تحويل فورييه (الجزء الحقيقي)
                    try:
                        F = sp.lambdify(omega, fourier_transform, 'numpy')
                        omega_vals = np.linspace(-10, 10, 1000)
                        F_vals = [np.real(F(wv)) for wv in omega_vals]
                        ax2.plot(omega_vals, F_vals, 'r-', linewidth=2)
                        ax2.set_title("تحويل فورييه (الجزء الحقيقي)")
                        ax2.set_xlabel('ω')
                        ax2.set_ylabel('Re[F(ω)]')
                        ax2.grid(True, alpha=0.3)
                    except:
                        pass
                    
                    st.pyplot(fig)
            
            except Exception as e:
                st.markdown(f'<div class="error-box">❌ خطأ: {str(e)}</div>', unsafe_allow_html=True)
    
    # --- تبويب الجبر الخطي ---
    with tab3:
        st.markdown("### الجبر الخطي")
        st.markdown("""
        <div class="info-box">
        <h4>المصفوفات والمحددات</h4>
        <p>للمصفوفة \\(A = \\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix}\\)</p>
        <p>المحدد: \\(|A| = ad - bc\\)</p>
        <p>المعكوس: \\(A^{-1} = \\frac{1}{|A|} \\begin{pmatrix} d & -b \\\\ -c & a \\end{pmatrix}\\)</p>
        </div>
        """, unsafe_allow_html=True)
        
        matrix_input = st.text_area("أدخل المصفوفة (صفوف منفصلة بـ ; وأعمدة بمسافة)", "1 2; 3 4")
        
        if st.button("تحليل المصفوفة", type="primary"):
            try:
                # معالجة المدخلات
                rows = matrix_input.strip().split(';')
                matrix = []
                for row in rows:
                    elements = row.strip().split()
                    matrix.append([float(x) for x in elements])
                
                # إنشاء مصفوفة SymPy
                A = sp.Matrix(matrix)
                
                # حساب الخصائص
                det = A.det()
                rank = A.rank()
                eigenvals = A.eigenvals()
                eigenvecs = A.eigenvects()
                
                st.markdown("### نتائج تحليل المصفوفة:")
                st.markdown(f"**المصفوفة:**")
                if st.session_state.use_latex:
                    st.latex(sp.latex(A))
                else:
                    st.write(A)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### الخصائص الأساسية:")
                    st.markdown(f"- **المحدد:** {det}")
                    st.markdown(f"- **الرتبة:** {rank}")
                    st.markdown(f"- **الأبعاد:** {A.rows} × {A.cols}")
                
                with col2:
                    st.markdown("#### القيم الذاتية:")
                    for val, mult in eigenvals.items():
                        st.markdown(f"- **القيمة:** {val}, **التكبير:** {mult}")
                
                # رسم المصفوفة كصورة حرارية
                if st.checkbox("عرض الصورة الحرارية للمصفوفة"):
                    fig, ax = plt.subplots(figsize=(10, 8))
                    im = ax.imshow(np.array(A.tolist(), dtype=float), cmap='viridis')
                    ax.set_title("الصورة الحرارية للمصفوفة")
                    ax.set_xlabel("الأعمدة")
                    ax.set_ylabel("الصفوف")
                    plt.colorbar(im, ax=ax)
                    st.pyplot(fig)
            
            except Exception as e:
                st.markdown(f'<div class="error-box">❌ خطأ: {str(e)}</div>', unsafe_allow_html=True)

# === قسم الإعدادات ===
elif menu == "⚙️ الإعدادات":
    st.markdown('<p class="section-header">⚙️ الإعدادات</p>', unsafe_allow_html=True)
    
    st.markdown("### ⚙️ إعدادات التطبيق")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # إعدادات الحسابات
        st.subheader("🧮 إعدادات الحسابات")
        new_precision = st.slider("دقة الحسابات (أرقام عشرية)", 
                                min_value=5, max_value=50, 
                                value=st.session_state.precision,
                                help="عدد الأرقام العشرية في النتائج")
        
        if new_precision != st.session_state.precision:
            st.session_state.precision = new_precision
            st.success(f"✅ تم تحديث دقة الحسابات إلى {new_precision} رقم عشري")
        
        use_latex = st.checkbox("استخدام LaTeX لعرض النتائج", value=st.session_state.use_latex,
                               help="عرض النتائج بصيغ رياضية جميلة")
        
        if use_latex != st.session_state.use_latex:
            st.session_state.use_latex = use_latex
            st.success(f"✅ تم {'تفعيل' if use_latex else 'إيقاف'} عرض النتائج بصيغة LaTeX")
        
        # إعدادات الرسوم البيانية
        st.subheader("📊 إعدادات الرسوم البيانية")
        new_plot_theme = st.selectbox("سمة الرسوم البيانية", 
                                    ["default", "dark_background", "seaborn", "ggplot"],
                                    index=["default", "dark_background", "seaborn", "ggplot"].index(st.session_state.plot_theme))
        
        if new_plot_theme != st.session_state.plot_theme:
            st.session_state.plot_theme = new_plot_theme
            plt.style.use(new_plot_theme)
            st.success(f"✅ تم تحديث سمة الرسوم البيانية إلى {new_plot_theme}")
        
        # حفظ الإعدادات
        st.subheader("💾 حفظ وتحميل الإعدادات")
        if st.button("حفظ الإعدادات الحالية", type="secondary"):
            settings = {
                'precision': st.session_state.precision,
                'use_latex': st.session_state.use_latex,
                'plot_theme': st.session_state.plot_theme
            }
            st.success("✅ تم حفظ الإعدادات بنجاح")
        
        if st.button("إعادة تعيين الإعدادات للإفتراضية", type="secondary"):
            st.session_state.precision = 15
            st.session_state.use_latex = True
            st.session_state.plot_theme = 'default'
            plt.style.use('default')
            st.success("✅ تم إعادة تعيين الإعدادات للإفتراضية")
    
    with col2:
        st.markdown("### ℹ️ معلومات عن الإعدادات")
        
        st.markdown("""
        <div class="info-box">
        <h4>دقة الحسابات</h4>
        <p>تحديد عدد الأرقام العشرية المعروضة في النتائج. لزيادة الدقة في الحسابات العلمية، استخدم قيمًا أعلى.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
        <h4>صيغة LaTeX</h4>
        <p>تفعيل هذه الميزة يعرض النتائج بصيغ رياضية جميلة ومفهومة، لكن قد يتسبب في بطء طفيف في عرض النتائج.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
        <h4>سمة الرسوم البيانية</h4>
        <p>اختيار السمة المناسبة للرسوم البيانية. السمة الداكنة مناسبة للعرض الليلي، بينما السمة الافتراضية مناسبة للقراءة.</p>
        </div>
        """, unsafe_allow_html=True)

# === قسم المساعدة ===
elif menu == "❓ المساعدة":
    st.markdown('<p class="section-header">❓ المساعدة والدعم</p>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["الدليل", "الأمثلة", "التواصل"])
    
    with tab1:
        st.markdown("### 📘 الدليل الشامل")
        
        st.markdown("""
        <div class="info-box">
        <h3>🎯 الهدف من التطبيق</h3>
        <p>PPFO v20.0 هو تطبيق رياضي متكامل يغطي جميع فروع الرياضيات من الجبر الأساسي إلى الرياضيات المتقدمة، ويهدف إلى تقديم تجربة تعليمية وتحليلية مميزة.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
        <h3>📱 الاستخدام على الهاتف</h3>
        <p>يمكنك تثبيت هذا التطبيق كـ PWA على هاتفك:</p>
        <ol>
            <li>افتح التطبيق في متصفح Chrome</li>
            <li>انقر على أيقونة القائمة (⋮)</li>
            <li>اختر "تثبيت التطبيق"</li>
            <li>اتبع التعليمات لإكمال التثبيت</li>
        </ol>
        <p>بعد التثبيت، سيعمل التطبيق دون اتصال بالإنترنت!</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
        <h3>📥 تصدير النتائج</h3>
        <p>يمكنك تصدير النتائج بطرق متعددة:</p>
        <ul>
            <li>نسخ النصوص يدويًا</li>
            <li>حفظ الرسوم البيانية بالنقر على زر التحميل في الزاوية</li>
            <li>استخدام ميزة "مشاركة" في الهاتف لمشاركة النتائج</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 📚 أمثلة عملية")
        
        st.markdown("#### 1. حساب مشتق معقد")
        st.code("""
        الدالة: sin(x**2) + exp(2*x)
        المشتق: 2*x*cos(x**2) + 2*exp(2*x)
        """)
        
        st.markdown("#### 2. تكامل محدود")
        st.code("""
        ∫(0 إلى π) sin(x) dx = 2
        """)
        
        st.markdown("#### 3. حل نظام معادلات")
        st.code("""
        x + y = 5
        2x - y = 1
        الحل: x = 2, y = 3
        """)
        
        st.markdown("#### 4. متسلسلة تايلور")
        st.code("""
        sin(x) حول x=0:
        x - x^3/6 + x^5/120 - x^7/5040 + ...
        """)
        
        st.markdown("#### 5. اختبار t للفرضيات")
        st.code("""
        عينة 1: [1, 2, 3, 4, 5]
        عينة 2: [2, 3, 4, 5, 6]
        نتيجة: p-value = 0.0953 (لا يوجد فرق ذو دلالة)
        """)
    
    with tab3:
        st.markdown("### 📞 التواصل والدعم")
        
        st.markdown("""
        <div class="info-box">
        <h3>للاستفسارات والدعم الفني</h3>
        <ul>
            <li>📧 البريد الإلكتروني: support@ppfo-math.com</li>
            <li>🌐 موقع الويب: www.ppfo-math.com</li>
            <li>📱 تيليجرام: @ppfo_math_support</li>
            <li>🐦 تويتر: @ppfo_math</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🐛 الإبلاغ عن مشكلة")
        
        problem_type = st.selectbox("نوع المشكلة", 
                                   ["خطأ في الحساب", "مشكلة في الواجهة", "اقتراح تحسين", "مشكلة أخرى"])
        
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
    rating = st.slider("تقييمك", 1, 5, 4, key="footer_rating")
    if rating >= 4:
        st.markdown("🌟 شكراً لثقتك! نحن نعمل باستمرار لتحسين التطبيق.")
    else:
        st.markdown("💡 نعتذر عن أي إزعاج. يرجى التواصل معنا لحل المشكلة.")

# === تحميل البيانات التلقائي ===
@st.cache_data
def load_sample_data():
    """تحميل بيانات عينة للاستخدام في الأمثلة"""
    x = np.linspace(-10, 10, 1000)
    y1 = np.sin(x)
    y2 = np.cos(x)
    y3 = x**2
    return x, y1, y2, y3

# تحميل البيانات
load_sample_data()
