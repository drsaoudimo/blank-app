#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PPFO v29.0 - إصدار متعدد اللغات مع دعم كامل للرياضيات المتقدمة
دعم اللغات: العربية، الفرنسية، الإنجليزية
"""

import streamlit as st
import math, random, time, re, json
from functools import lru_cache
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from scipy import integrate, stats
import sympy as sp

# 🌐 نظام تعدد اللغات
LANGUAGES = {
    'ar': 'العربية',
    'fr': 'Français',
    'en': 'English'
}

# 📱 إعدادات الصفحة
st.set_page_config(
    page_title="PPFO v29.0 - Mathematics",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 🎨 تنسيقات CSS - تصميم متجاوب مع دعم كامل للغات
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700;800;900&family=Roboto:wght@300;400;500;700&display=swap');
    
    :root {
        --primary: #4F46E5;
        --secondary: #7C3AED;
        --accent: #EC4899;
        --success: #10B981;
        --warning: #F59E0B;
        --danger: #EF4444;
        --info: #3B82F6;
        --light: #F9FAFB;
        --dark: #1E293B;
        --gray: #64748B;
    }
    
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.8rem !important;
        }
        
        .sub-header {
            font-size: 1.1rem !important;
        }
        
        .math-container {
            padding: 12px !important;
        }
        
        .stButton>button {
            font-size: 0.95rem !important;
            padding: 12px 18px !important;
        }
    }
    
    body {
        font-family: 'Cairo', sans-serif;
    }
    
    .main-header {
        font-size: 2.4rem;
        color: var(--primary);
        text-align: center;
        margin-bottom: 1.2rem;
        font-weight: 800;
        text-shadow: 0 2px 4px rgba(79, 70, 229, 0.2);
    }
    
    .sub-header {
        font-size: 1.3rem;
        color: var(--secondary);
        text-align: center;
        margin-bottom: 2rem;
        opacity: 0.9;
    }
    
    .math-container {
        background: white;
        border-radius: 14px;
        padding: 20px;
        margin: 12px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .math-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    }
    
    .math-title {
        color: var(--primary);
        font-weight: 700;
        margin-bottom: 10px;
        font-size: 1.2rem;
    }
    
    .math-formula {
        font-size: 1.4rem;
        color: var(--dark);
        margin: 8px 0;
        text-align: center;
        font-family: 'Cambria Math', 'Times New Roman', serif;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }
    
    .math-description {
        color: var(--gray);
        font-size: 0.95rem;
        margin-top: 8px;
        line-height: 1.5;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        border: none;
        border-radius: 12px;
        padding: 14px 24px;
        font-weight: 600;
        font-size: 1.05rem;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(79, 70, 229, 0.4);
    }
    
    .language-selector {
        position: fixed;
        top: 10px;
        left: 10px;
        z-index: 1000;
    }
    
    .visualization-container {
        background: white;
        border-radius: 14px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    
    .info-box {
        background: linear-gradient(135deg, #dbeafe, #bfdbfe);
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid var(--info);
    }
    
    .success-box {
        background: linear-gradient(135deg, #dcfce7, #bbf7d0);
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid var(--success);
    }
    
    .section-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--primary), transparent);
        margin: 25px 0;
    }
    
    .mobile-card {
        background: white;
        border-radius: 16px;
        padding: 18px;
        margin: 12px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 1px solid #e5e7eb;
        transition: all 0.3s ease;
    }
    
    .scroll-container {
        max-width: 100%;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        padding: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# 🌐 تحميل ترجمات اللغة
@st.cache_data
def load_translations():
    return {
        'ar': {
            'app_name': 'PPFO v29.0 - الرياضيات المتقدمة',
            'language_selector': 'اختر اللغة',
            'home': '🏠 الصفحة الرئيسية',
            'zeta_zeros': '𝛇 أصفار زيتا - مصححة',
            'full_zeta': '🧮 دالة زيتا الكاملة',
            'prime_numbers': '🔍 الأعداد الأولية',
            'advanced_apps': '📊 تطبيقات متقدمة',
            'algebra': '🎯 الجبر',
            'geometry': '📐 الهندسة',
            'topology': '🌐 الطبولوجيا',
            'calculus': '📈 التفاضل والتكامل',
            'other_math': '🔬 علوم رياضية أخرى',
            'welcome': 'مرحباً بك في PPFO v29.0',
            'calculation': 'حساب',
            'result': 'النتيجة',
            'time_taken': 'الوقت المستغرق',
            'error': 'خطأ',
            'success': 'نجاح',
            'warning': 'تحذير',
            'info': 'معلومات',
            'function': 'الدالة',
            'variable': 'المتغير',
            'enter_function': 'أدخل الدالة',
            'calculate': 'حساب',
            'plot': 'رسم بياني',
            'derivative': 'المشتقة',
            'integral': 'التكامل',
            'limit': 'النهاية',
            'matrix': 'المصفوفة',
            'equation': 'المعادلة',
            'solve': 'حل',
            'geometric_shape': 'الشكل الهندسي',
            'topological_space': 'الفضاء الطبولوجي',
            'examples': 'أمثلة',
            'settings': 'الإعدادات'
        },
        'fr': {
            'app_name': 'PPFO v29.0 - Mathématiques avancées',
            'language_selector': 'Choisir la langue',
            'home': '🏠 Page d\'accueil',
            'zeta_zeros': '𝛇 Zéros de Zêta - corrigés',
            'full_zeta': '🧮 Fonction Zêta complète',
            'prime_numbers': '🔍 Nombres premiers',
            'advanced_apps': '📊 Applications avancées',
            'algebra': '🎯 Algèbre',
            'geometry': '📐 Géométrie',
            'topology': '🌐 Topologie',
            'calculus': '📈 Calcul différentiel et intégral',
            'other_math': '🔬 Autres sciences mathématiques',
            'welcome': 'Bienvenue dans PPFO v29.0',
            'calculation': 'Calcul',
            'result': 'Résultat',
            'time_taken': 'Temps écoulé',
            'error': 'Erreur',
            'success': 'Succès',
            'warning': 'Avertissement',
            'info': 'Information',
            'function': 'Fonction',
            'variable': 'Variable',
            'enter_function': 'Entrez la fonction',
            'calculate': 'Calculer',
            'plot': 'Graphique',
            'derivative': 'Dérivée',
            'integral': 'Intégrale',
            'limit': 'Limite',
            'matrix': 'Matrice',
            'equation': 'Équation',
            'solve': 'Résoudre',
            'geometric_shape': 'Forme géométrique',
            'topological_space': 'Espace topologique',
            'examples': 'Exemples',
            'settings': 'Paramètres'
        },
        'en': {
            'app_name': 'PPFO v29.0 - Advanced Mathematics',
            'language_selector': 'Select Language',
            'home': '🏠 Home Page',
            'zeta_zeros': '𝛇 Zeta Zeros - Corrected',
            'full_zeta': '🧮 Full Zeta Function',
            'prime_numbers': '🔍 Prime Numbers',
            'advanced_apps': '📊 Advanced Applications',
            'algebra': '🎯 Algebra',
            'geometry': '📐 Geometry',
            'topology': '🌐 Topology',
            'calculus': '📈 Calculus',
            'other_math': '🔬 Other Mathematical Sciences',
            'welcome': 'Welcome to PPFO v29.0',
            'calculation': 'Calculation',
            'result': 'Result',
            'time_taken': 'Time Taken',
            'error': 'Error',
            'success': 'Success',
            'warning': 'Warning',
            'info': 'Info',
            'function': 'Function',
            'variable': 'Variable',
            'enter_function': 'Enter function',
            'calculate': 'Calculate',
            'plot': 'Plot',
            'derivative': 'Derivative',
            'integral': 'Integral',
            'limit': 'Limit',
            'matrix': 'Matrix',
            'equation': 'Equation',
            'solve': 'Solve',
            'geometric_shape': 'Geometric Shape',
            'topological_space': 'Topological Space',
            'examples': 'Examples',
            'settings': 'Settings'
        }
    }

# تحميل الترجمات
translations = load_translations()

# 🌐 تحديد اللغة الحالية
if 'language' not in st.session_state:
    st.session_state.language = 'ar'  # اللغة الافتراضية

# 🌐 محدد اللغة في الزاوية
with st.container():
    col1, col2, col3 = st.columns([1, 10, 1])
    with col1:
        language = st.selectbox(
            translations[st.session_state.language]['language_selector'],
            options=list(LANGUAGES.keys()),
            format_func=lambda x: LANGUAGES[x],
            key='language_selector',
            label_visibility='collapsed'
        )
        st.session_state.language = language
    
    # 🎯 العنوان الرئيسي
    with col2:
        st.markdown(f'<h1 class="main-header">{translations[st.session_state.language]["app_name"]}</h1>', 
                   unsafe_allow_html=True)
        st.markdown(f'<h2 class="sub-header">{translations[st.session_state.language]["welcome"]}</h2>', 
                   unsafe_allow_html=True)

# 📐 تخصيص مكتبات الرياضيات
try:
    import sympy as sp
    SYMPY_AVAILABLE = True
    sp.init_printing(use_unicode=True)
except Exception as e:
    SYMPY_AVAILABLE = False
    st.warning(f"Sympy not available: {e}")

try:
    import mpmath as mp
    MP_MATH_AVAILABLE = True
    mp.mp.dps = 50
except Exception as e:
    MP_MATH_AVAILABLE = False
    st.warning(f"mpmath not available: {e}")

# ===================== وظائف الدعم متعددة اللغات =====================

def t(key):
    """الحصول على ترجمة للمفتاح الحالي"""
    return translations[st.session_state.language][key]

def show_math_formula(formula, title="", description="", bg_color="white"):
    """عرض صيغة رياضية بطريقة أنيقة"""
    st.markdown(f"""
    <div class="math-container" style="background: {bg_color};">
        <div class="math-title">{title}</div>
        <div class="scroll-container">
            <div class="math-formula">{formula}</div>
        </div>
        <div class="math-description">{description}</div>
    </div>
    """, unsafe_allow_html=True)

def show_info_box(content, title=t('info'), type="info"):
    """عرض معلومات بطريقة أنيقة"""
    colors = {
        "info": "--info",
        "success": "--success", 
        "warning": "--warning",
        "danger": "--danger"
    }
    
    st.markdown(f"""
    <div class="info-box" style="border-left-color: var({colors[type]});">
        <strong>{title}:</strong> {content}
    </div>
    """, unsafe_allow_html=True)

def show_success_box(content, title=t('success')):
    st.markdown(f"""
    <div class="success-box">
        <strong>{title}:</strong> {content}
    </div>
    """, unsafe_allow_html=True)

# ===================== الرياضيات الأساسية =====================

def parse_large_number(input_str):
    """تحويل النص إلى عدد كبير مع دعم التنسيقات المختلفة"""
    if not input_str or not input_str.strip():
        raise ValueError("الرجاء إدخال عدد" if st.session_state.language == 'ar' else 
                        "Veuillez entrer un nombre" if st.session_state.language == 'fr' else
                        "Please enter a number")
    
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
        raise ValueError(f"لا يمكن تحويل '{input_str}' إلى عدد صحيح" if st.session_state.language == 'ar' else
                        f"Impossible de convertir '{input_str}' en nombre entier" if st.session_state.language == 'fr' else
                        f"Cannot convert '{input_str}' to integer")

# ===================== أصفار زيتا - النسخة المحسنة =====================

@st.cache_data(ttl=3600)
def zeta_zero_advanced(n, precision=30):
    """حساب الصفر غير التافه رقم n لدالة زيتا بدقة عالية"""
    if not MP_MATH_AVAILABLE:
        # قيمة تقريبية
        return (2 * math.pi * n) / math.log(n / (2 * math.pi)) if n > 1 else 14.134725
    
    try:
        mp.mp.dps = precision
        zero = mp.zetazero(n)
        return float(zero.imag)
    except Exception as e:
        st.warning(f"Error calculating zeta zero: {e}")
        return (2 * math.pi * n) / math.log(n / (2 * math.pi)) if n > 1 else 14.134725

# ===================== خدمات الجبر =====================

def algebra_section():
    """قسم خدمات الجبر"""
    st.header("🎯 " + t('algebra'))
    
    # 📐 عرض صيغة جبرية
    show_math_formula(
        r"ax^2 + bx + c = 0 \quad \Rightarrow \quad x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}",
        t('equation'),
        t('solve') + " " + ("المعادلة التربيعية" if st.session_state.language == 'ar' else 
                          "l'équation quadratique" if st.session_state.language == 'fr' else 
                          "quadratic equation")
    )
    
    tab1, tab2, tab3 = st.tabs([
        t('matrix'),
        t('equation'),
        t('polynomial')
    ])
    
    with tab1:
        st.subheader("🧮 " + ("العمليات على المصفوفات" if st.session_state.language == 'ar' else
                           "Opérations matricielles" if st.session_state.language == 'fr' else
                           "Matrix Operations"))
        
        col1, col2 = st.columns(2)
        with col1:
            rows = st.number_input("عدد الصفوف" if st.session_state.language == 'ar' else 
                                  "Nombre de lignes" if st.session_state.language == 'fr' else
                                  "Number of rows", 
                                  min_value=2, max_value=5, value=2)
        
        with col2:
            cols = st.number_input("عدد الأعمدة" if st.session_state.language == 'ar' else
                                  "Nombre de colonnes" if st.session_state.language == 'fr' else
                                  "Number of columns", 
                                  min_value=2, max_value=5, value=2)
        
        st.markdown("### " + ("أدخل عناصر المصفوفة" if st.session_state.language == 'ar' else
                           "Entrez les éléments de la matrice" if st.session_state.language == 'fr' else
                           "Enter matrix elements"))
        
        matrix = []
        for i in range(rows):
            row = []
            cols_input = st.columns(cols)
            for j in range(cols):
                with cols_input[j]:
                    val = st.number_input(f"a[{i+1},{j+1}]", value=0.0, key=f"matrix_{i}_{j}")
                    row.append(val)
            matrix.append(row)
        
        if st.button(t('calculate'), key="matrix_calc"):
            if SYMPY_AVAILABLE:
                M = sp.Matrix(matrix)
                with st.expander("📊 " + ("نتائج العمليات" if st.session_state.language == 'ar' else
                                       "Résultats des opérations" if st.session_state.language == 'fr' else
                                       "Operation Results")):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**" + ("المحدد" if st.session_state.language == 'ar' else
                                          "Déterminant" if st.session_state.language == 'fr' else
                                          "Determinant") + "**")
                        try:
                            det = M.det()
                            st.latex(f"\\det(M) = {sp.latex(det.evalf(4))}")
                        except:
                            st.write("غير محدد" if st.session_state.language == 'ar' else
                                    "Non défini" if st.session_state.language == 'fr' else
                                    "Undefined")
                    
                    with col2:
                        st.markdown("**" + ("الرتبة" if st.session_state.language == 'ar' else
                                          "Rang" if st.session_state.language == 'fr' else
                                          "Rank") + "**")
                        rank = M.rank()
                        st.latex(f"\\text{{rang}}(M) = {rank}")
                    
                    st.markdown("### " + ("المصفوفة المعكوسة" if st.session_state.language == 'ar' else
                                       "Matrice inverse" if st.session_state.language == 'fr' else
                                       "Inverse Matrix"))
                    try:
                        inv = M.inv()
                        st.latex(sp.latex(inv.evalf(2)))
                    except:
                        st.write("غير قابلة للعكس" if st.session_state.language == 'ar' else
                                "Non inversible" if st.session_state.language == 'fr' else
                                "Not invertible")
    
    with tab2:
        st.subheader("🧮 " + ("حل المعادلات" if st.session_state.language == 'ar' else
                           "Résolution d'équations" if st.session_state.language == 'fr' else
                           "Equation Solver"))
        
        equation_input = st.text_input(
            t('enter_function') + ":" + (" (استخدم x كمتغير)" if st.session_state.language == 'ar' else
                                       " (utilisez x comme variable)" if st.session_state.language == 'fr' else
                                       " (use x as variable)"),
            value="x**2 - 4"
        )
        
        if st.button(t('solve'), key="equation_solve"):
            if SYMPY_AVAILABLE:
                try:
                    x = sp.Symbol('x')
                    eq = sp.sympify(equation_input)
                    solutions = sp.solve(eq, x)
                    
                    st.markdown("### " + ("الحلول" if st.session_state.language == 'ar' else
                                       "Solutions" if st.session_state.language == 'fr' else
                                       "Solutions"))
                    
                    for i, sol in enumerate(solutions):
                        st.latex(f"x_{{{i+1}}} = {sp.latex(sol.evalf(6))}")
                    
                    # رسم بياني للدالة
                    if st.checkbox(t('plot') + " " + t('function'), key="plot_eq"):
                        x_vals = np.linspace(-10, 10, 400)
                        y_vals = [float(eq.subs(x, val)) for val in x_vals]
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=x_vals, y=y_vals,
                            mode='lines',
                            name=equation_input,
                            line=dict(color='#4F46E5', width=3)
                        ))
                        fig.add_hline(y=0, line_dash="dash", line_color="gray")
                        
                        fig.update_layout(
                            title=('رسم بياني للدالة' if st.session_state.language == 'ar' else
                                  'Graphique de la fonction' if st.session_state.language == 'fr' else
                                  'Function Graph'),
                            xaxis_title='x',
                            yaxis_title='f(x)',
                            plot_bgcolor='white',
                            hovermode='x unified'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                except Exception as e:
                    show_info_box(
                        str(e) if st.session_state.language == 'en' else
                        "خطأ في تحليل المعادلة" if st.session_state.language == 'ar' else
                        "Erreur dans l'analyse de l'équation",
                        t('error'),
                        "danger"
                    )
    
    with tab3:
        st.subheader("📊 " + ("الحدوديات" if st.session_state.language == 'ar' else
                           "Polynômes" if st.session_state.language == 'fr' else
                           "Polynomials"))
        
        poly_input = st.text_input(
            t('enter_function') + ":" + (" (حدودية)" if st.session_state.language == 'ar' else
                                       " (polynôme)" if st.session_state.language == 'fr' else
                                       " (polynomial)"),
            value="x**3 - 6*x**2 + 11*x - 6"
        )
        
        if st.button(t('factor'), key="factor_poly"):
            if SYMPY_AVAILABLE:
                try:
                    x = sp.Symbol('x')
                    poly = sp.sympify(poly_input)
                    factored = sp.factor(poly)
                    roots = sp.nroots(poly)
                    
                    st.markdown("### " + ("التحليل إلى عوامل" if st.session_state.language == 'ar' else
                                       "Factorisation" if st.session_state.language == 'fr' else
                                       "Factorization"))
                    st.latex(f"{sp.latex(poly)} = {sp.latex(factored)}")
                    
                    st.markdown("### " + ("جذور الحدودية" if st.session_state.language == 'ar' else
                                       "Racines du polynôme" if st.session_state.language == 'fr' else
                                       "Polynomial Roots"))
                    for i, root in enumerate(roots):
                        st.latex(f"x_{{{i+1}}} = {root:.4f}")
                        
                except Exception as e:
                    show_info_box(
                        str(e) if st.session_state.language == 'en' else
                        "خطأ في تحليل الحدودية" if st.session_state.language == 'ar' else
                        "Erreur dans l'analyse du polynôme",
                        t('error'),
                        "danger"
                    )

# ===================== خدمات الهندسة =====================

def geometry_section():
    """قسم خدمات الهندسة"""
    st.header("📐 " + t('geometry'))
    
    # 📐 عرض صيغة هندسية
    show_math_formula(
        r"A = \\pi r^2 \\quad,\\quad V = \\frac{4}{3} \\pi r^3",
        ("مساحة الدائرة وحجم الكرة" if st.session_state.language == 'ar' else
         "Aire du cercle et volume de la sphère" if st.session_state.language == 'fr' else
         "Circle Area and Sphere Volume"),
        ("الصيغ الأساسية" if st.session_state.language == 'ar' else
         "Formules de base" if st.session_state.language == 'fr' else
         "Basic formulas")
    )
    
    shape = st.selectbox(
        t('geometric_shape') + ":",
        ["دائرة", "مثلث", "مستطيل", "كرة", "مكعب"] if st.session_state.language == 'ar' else
        ["Cercle", "Triangle", "Rectangle", "Sphère", "Cube"] if st.session_state.language == 'fr' else
        ["Circle", "Triangle", "Rectangle", "Sphere", "Cube"]
    )
    
    if shape == "دائرة" or shape == "Cercle" or shape == "Circle":
        radius = st.number_input(
            ("نصف القطر" if st.session_state.language == 'ar' else
             "Rayon" if st.session_state.language == 'fr' else
             "Radius"), 
            min_value=0.1, value=1.0, step=0.1
        )
        
        area = math.pi * radius ** 2
        circumference = 2 * math.pi * radius
        
        col1, col2 = st.columns(2)
        with col1:
            show_success_box(f"{area:.4f}", 
                            ("المساحة" if st.session_state.language == 'ar' else
                             "Aire" if st.session_state.language == 'fr' else
                             "Area"))
        
        with col2:
            show_success_box(f"{circumference:.4f}", 
                            ("المحيط" if st.session_state.language == 'ar' else
                             "Périmètre" if st.session_state.language == 'fr' else
                             "Circumference"))
        
        if st.button(t('plot'), key="plot_circle"):
            theta = np.linspace(0, 2*math.pi, 100)
            x = radius * np.cos(theta)
            y = radius * np.sin(theta)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=x, y=y,
                mode='lines',
                name='Circle',
                line=dict(color='#4F46E5', width=3)
            ))
            
            fig.update_layout(
                title=('دائرة نصف قطرها' if st.session_state.language == 'ar' else
                      'Cercle de rayon' if st.session_state.language == 'fr' else
                      'Circle with radius') + f' {radius}',
                xaxis_title='x',
                yaxis_title='y',
                aspectmode='equal',
                plot_bgcolor='white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    elif shape == "مثلث" or shape == "Triangle":
        st.subheader(("مثلث قائم الزاوية" if st.session_state.language == 'ar' else
                     "Triangle rectangle" if st.session_state.language == 'fr' else
                     "Right Triangle"))
        
        a = st.number_input(
            ("الضلع الأول" if st.session_state.language == 'ar' else
             "Premier côté" if st.session_state.language == 'fr' else
             "First side"), 
            min_value=0.1, value=3.0, step=0.1
        )
        b = st.number_input(
            ("الضلع الثاني" if st.session_state.language == 'ar' else
             "Deuxième côté" if st.session_state.language == 'fr' else
             "Second side"), 
            min_value=0.1, value=4.0, step=0.1
        )
        
        c = math.sqrt(a**2 + b**2)
        area = 0.5 * a * b
        
        col1, col2 = st.columns(2)
        with col1:
            show_success_box(f"{c:.4f}", 
                            ("الوتر" if st.session_state.language == 'ar' else
                             "Hypoténuse" if st.session_state.language == 'fr' else
                             "Hypotenuse"))
        
        with col2:
            show_success_box(f"{area:.4f}", 
                            ("المساحة" if st.session_state.language == 'ar' else
                             "Aire" if st.session_state.language == 'fr' else
                             "Area"))

# ===================== خدمات التفاضل والتكامل =====================

def calculus_section():
    """قسم خدمات التفاضل والتكامل"""
    st.header("📈 " + t('calculus'))
    
    # 📐 عرض صيغة التفاضل والتكامل
    show_math_formula(
        r"\\frac{d}{dx}f(x) = \\lim_{h \\to 0} \\frac{f(x+h) - f(x)}{h} \\quad,\\quad \\int_a^b f(x)dx = F(b) - F(a)",
        ("المشتقة والتكامل" if st.session_state.language == 'ar' else
         "Dérivée et intégrale" if st.session_state.language == 'fr' else
         "Derivative and Integral"),
        ("المفاهيم الأساسية" if st.session_state.language == 'ar' else
         "Concepts fondamentaux" if st.session_state.language == 'fr' else
         "Fundamental concepts")
    )
    
    tab1, tab2, tab3 = st.tabs([
        t('derivative'),
        t('integral'),
        t('limit')
    ])
    
    with tab1:
        st.subheader("⚡ " + ("المشتقة" if st.session_state.language == 'ar' else
                           "Dérivée" if st.session_state.language == 'fr' else
                           "Derivative"))
        
        func_input = st.text_input(
            t('enter_function') + ":" + (" (استخدم x كمتغير)" if st.session_state.language == 'ar' else
                                       " (utilisez x comme variable)" if st.session_state.language == 'fr' else
                                       " (use x as variable)"),
            value="x**2 + 3*x + 1"
        )
        
        if st.button(t('calculate'), key="derivative_calc"):
            if SYMPY_AVAILABLE:
                try:
                    x = sp.Symbol('x')
                    func = sp.sympify(func_input)
                    derivative = sp.diff(func, x)
                    
                    st.markdown("### " + ("الدالة الأصلية" if st.session_state.language == 'ar' else
                                       "Fonction originale" if st.session_state.language == 'fr' else
                                       "Original Function"))
                    st.latex(f"f(x) = {sp.latex(func)}")
                    
                    st.markdown("### " + ("المشتقة" if st.session_state.language == 'ar' else
                                       "Dérivée" if st.session_state.language == 'fr' else
                                       "Derivative"))
                    st.latex(f"f'(x) = {sp.latex(derivative)}")
                    
                    if st.checkbox(t('plot'), key="plot_derivative"):
                        x_vals = np.linspace(-5, 5, 400)
                        f_vals = [float(func.subs(x, val)) for val in x_vals]
                        d_vals = [float(derivative.subs(x, val)) for val in x_vals]
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=x_vals, y=f_vals,
                            mode='lines',
                            name='f(x)',
                            line=dict(color='#4F46E5', width=3)
                        ))
                        fig.add_trace(go.Scatter(
                            x=x_vals, y=d_vals,
                            mode='lines',
                            name="f'(x)",
                            line=dict(color='#10B981', width=3, dash='dash')
                        ))
                        
                        fig.update_layout(
                            title=('رسم بياني للدالة ومشتقتها' if st.session_state.language == 'ar' else
                                  'Graphique de la fonction et sa dérivée' if st.session_state.language == 'fr' else
                                  'Function and Derivative Graph'),
                            xaxis_title='x',
                            yaxis_title='y',
                            plot_bgcolor='white',
                            hovermode='x unified'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                except Exception as e:
                    show_info_box(
                        str(e) if st.session_state.language == 'en' else
                        "خطأ في حساب المشتقة" if st.session_state.language == 'ar' else
                        "Erreur dans le calcul de la dérivée",
                        t('error'),
                        "danger"
                    )
    
    with tab2:
        st.subheader("🔢 " + ("التكامل" if st.session_state.language == 'ar' else
                           "Intégrale" if st.session_state.language == 'fr' else
                           "Integral"))
        
        func_input = st.text_input(
            t('enter_function') + ":" + (" (استخدم x كمتغير)" if st.session_state.language == 'ar' else
                                       " (utilisez x comme variable)" if st.session_state.language == 'fr' else
                                       " (use x as variable)"),
            value="x**2",
            key="integral_func"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            a = st.number_input(
                "a" + (" (الحد الأدنى)" if st.session_state.language == 'ar' else
                      " (borne inférieure)" if st.session_state.language == 'fr' else
                      " (lower bound)"),
                value=0.0
            )
        
        with col2:
            b = st.number_input(
                "b" + (" (الحد الأعلى)" if st.session_state.language == 'ar' else
                      " (borne supérieure)" if st.session_state.language == 'fr' else
                      " (upper bound)"),
                value=1.0
            )
        
        if st.button(t('calculate'), key="integral_calc"):
            if SYMPY_AVAILABLE:
                try:
                    x = sp.Symbol('x')
                    func = sp.sympify(func_input)
                    indefinite_integral = sp.integrate(func, x)
                    definite_integral = sp.integrate(func, (x, a, b))
                    
                    st.markdown("### " + ("التكامل غير المحدود" if st.session_state.language == 'ar' else
                                       "Intégrale indéfinie" if st.session_state.language == 'fr' else
                                       "Indefinite Integral"))
                    st.latex(f"\\int {sp.latex(func)} dx = {sp.latex(indefinite_integral)} + C")
                    
                    st.markdown("### " + ("التكامل المحدود" if st.session_state.language == 'ar' else
                                       "Intégrale définie" if st.session_state.language == 'fr' else
                                       "Definite Integral"))
                    st.latex(f"\\int_{{{a}}}^{{{b}}} {sp.latex(func)} dx = {definite_integral.evalf(6)}")
                    
                    # رسم بياني
                    if st.checkbox(t('plot'), key="plot_integral"):
                        x_vals = np.linspace(min(a-1, -5), max(b+1, 5), 400)
                        y_vals = [float(func.subs(x, val)) for val in x_vals]
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=x_vals, y=y_vals,
                            mode='lines',
                            name=func_input,
                            line=dict(color='#4F46E5', width=3)
                        ))
                        
                        # تظليل منطقة التكامل
                        x_fill = np.linspace(a, b, 100)
                        y_fill = [float(func.subs(x, val)) for val in x_fill]
                        fig.add_trace(go.Scatter(
                            x=list(x_fill) + list(x_fill[::-1]),
                            y=list(y_fill) + [0]*len(y_fill),
                            fill='toself',
                            fillcolor='rgba(79, 70, 229, 0.2)',
                            line=dict(color='rgba(255,255,255,0)'),
                            hoverinfo="skip",
                            name='المنطقة المتكاملة'
                        ))
                        
                        fig.update_layout(
                            title=('تكامل دالة' if st.session_state.language == 'ar' else
                                  'Intégrale de la fonction' if st.session_state.language == 'fr' else
                                  'Function Integral'),
                            xaxis_title='x',
                            yaxis_title='f(x)',
                            plot_bgcolor='white',
                            hovermode='x unified'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                except Exception as e:
                    show_info_box(
                        str(e) if st.session_state.language == 'en' else
                        "خطأ في حساب التكامل" if st.session_state.language == 'ar' else
                        "Erreur dans le calcul de l'intégrale",
                        t('error'),
                        "danger"
                    )

# ===================== الواجهة الرئيسية =====================

def main():
    # 🌐 تحميل الترجمات
    trans = translations[st.session_state.language]
    
    # 📱 قائمة التنقل الرئيسية
    sections = [
        trans['home'],
        trans['zeta_zeros'],
        trans['algebra'],
        trans['geometry'],
        trans['calculus'],
        trans['topology'],
        trans['other_math']
    ]
    
    # 🎛️ محدد القسم
    section = st.selectbox(
        trans['language_selector'] + ":" if st.session_state.language == 'ar' else
        trans['language_selector'] + " :",
        sections,
        key='main_section'
    )
    
    # ===================== الصفحة الرئيسية =====================
    if section == trans['home']:
        st.markdown('<div class="mobile-card">', unsafe_allow_html=True)
        st.subheader(trans['welcome'])
        
        # حالة المكتبات
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**mpmath:** {'🟢 متوفر' if MP_MATH_AVAILABLE else '🔴 غير متوفر'}"
                       if st.session_state.language == 'ar' else
                       f"**mpmath:** {'🟢 Disponible' if MP_MATH_AVAILABLE else '🔴 Non disponible'}"
                       if st.session_state.language == 'fr' else
                       f"**mpmath:** {'🟢 Available' if MP_MATH_AVAILABLE else '🔴 Not available'}")
        
        with col2:
            st.markdown(f"**sympy:** {'🟢 متوفر' if SYMPY_AVAILABLE else '🔴 غير متوفر'}"
                       if st.session_state.language == 'ar' else
                       f"**sympy:** {'🟢 Disponible' if SYMPY_AVAILABLE else '🔴 Non disponible'}"
                       if st.session_state.language == 'fr' else
                       f"**sympy:** {'🟢 Available' if SYMPY_AVAILABLE else '🔴 Not available'}")
        
        st.markdown("""
        **الميزات الرئيسية:**
        - ✅ أصفار زيتا غير التافهة بدقة عالية
        - 🧮 الجبر: حل المعادلات، المصفوفات، الحدوديات
        - 📐 الهندسة: حساب المساحات والأحجام
        - 📈 التفاضل والتكامل: المشتقات والتكاملات
        - 🌐 الطبولوجيا والرياضيات المتقدمة
        - 🌍 دعم متعدد اللغات (العربية، الفرنسية، الإنجليزية)
        
        اختر القسم الذي تريد استكشافه من القائمة أعلاه.
        """ if st.session_state.language == 'ar' else """
        **Fonctionnalités principales :**
        - ✅ Zéros de Zêta non triviaux avec haute précision
        - 🧮 Algèbre : résolution d'équations, matrices, polynômes
        - 📐 Géométrie : calcul des aires et volumes
        - 📈 Calcul différentiel et intégral
        - 🌐 Topologie et mathématiques avancées
        - 🌍 Support multilingue (arabe, français, anglais)
        
        Choisissez la section que vous souhaitez explorer dans le menu ci-dessus.
        """ if st.session_state.language == 'fr' else """
        **Main Features:**
        - ✅ Non-trivial Zeta zeros with high precision
        - 🧮 Algebra: equation solving, matrices, polynomials
        - 📐 Geometry: area and volume calculations
        - 📈 Calculus: derivatives and integrals
        - 🌐 Topology and advanced mathematics
        - 🌍 Multilingual support (Arabic, French, English)
        
        Choose the section you want to explore from the menu above.
        """)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # مثال سريع
        st.markdown('<div class="mobile-card" style="border-top: 4px solid var(--success);">', unsafe_allow_html=True)
        st.subheader(trans['examples'])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("𝛇 " + ("الصفر 167" if st.session_state.language == 'ar' else
                              "Zéro 167" if st.session_state.language == 'fr' else
                              "Zero 167"),
                       use_container_width=True):
                with st.spinner("جاري الحساب..." if st.session_state.language == 'ar' else
                              "Calcul en cours..." if st.session_state.language == 'fr' else
                              "Calculating..."):
                    zero_167 = zeta_zero_advanced(167, precision=40)
                    show_success_box(
                        f"{zero_167:.12f}",
                        ("الصفر 167 لزيتا" if st.session_state.language == 'ar' else
                         "Zéro 167 de Zêta" if st.session_state.language == 'fr' else
                         "Zeta Zero 167")
                    )
        
        with col2:
            if st.button("∫ " + ("تكامل x²" if st.session_state.language == 'ar' else
                              "Intégrale x²" if st.session_state.language == 'fr' else
                              "Integral x²"),
                       use_container_width=True):
                if SYMPY_AVAILABLE:
                    x = sp.Symbol('x')
                    integral = sp.integrate(x**2, (x, 0, 1))
                    show_success_box(
                        f"{integral.evalf():.6f}",
                        ("∫₀¹ x² dx" if st.session_state.language == 'ar' else
                         "∫₀¹ x² dx" if st.session_state.language == 'fr' else
                         "∫₀¹ x² dx")
                    )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ===================== أصفار زيتا =====================
    elif section == trans['zeta_zeros']:
        st.header("𝛇 " + ("أصفار زيتا غير التافهة" if st.session_state.language == 'ar' else
                       "Zéros non triviaux de Zêta" if st.session_state.language == 'fr' else
                       "Non-trivial Zeta Zeros"))
        
        show_math_formula(
            r"\\zeta\\left(\\frac{1}{2} + i t_n\\right) = 0",
            ("الصيغة الأساسية" if st.session_state.language == 'ar' else
             "Formule de base" if st.session_state.language == 'fr' else
             "Basic Formula"),
            ("أصفار دالة زيتا غير التافهة على الخط الحرج" if st.session_state.language == 'ar' else
             "Zéros non triviaux de la fonction Zêta sur la ligne critique" if st.session_state.language == 'fr' else
             "Non-trivial zeros of the Zeta function on the critical line")
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            n_input = st.text_input(
                ("رقم الصفر" if st.session_state.language == 'ar' else
                 "Numéro du zéro" if st.session_state.language == 'fr' else
                 "Zero number") + ":",
                value="167"
            )
        
        with col2:
            precision = st.slider(
                ("دقة الحساب (خانات عشرية)" if st.session_state.language == 'ar' else
                 "Précision (décimales)" if st.session_state.language == 'fr' else
                 "Precision (decimal places)"),
                min_value=15, max_value=60, value=30, step=5
            )
        
        if st.button("🎯 " + ("حساب الصفر" if st.session_state.language == 'ar' else
                           "Calculer le zéro" if st.session_state.language == 'fr' else
                           "Calculate Zero"),
                     type="primary"):
            try:
                n = parse_large_number(n_input)
                if n < 1:
                    show_info_box(
                        "يجب أن يكون رقم الصفر موجباً" if st.session_state.language == 'ar' else
                        "Le numéro du zéro doit être positif" if st.session_state.language == 'fr' else
                        "Zero number must be positive",
                        trans['error'],
                        "danger"
                    )
                else:
                    with st.spinner("جاري الحساب..." if st.session_state.language == 'ar' else
                                  "Calcul en cours..." if st.session_state.language == 'fr' else
                                  "Calculating..."):
                        start_time = time.time()
                        zero_value = zeta_zero_advanced(n, precision=precision)
                        end_time = time.time()
                        
                        show_success_box(
                            f"{zero_value:.15f}",
                            f"t_{{{n}}} ="
                        )
                        
                        if n == 167 and abs(zero_value - 346.347870566) < 1e-6:
                            st.balloons()
                            st.success("🎉 " + ("تم التحقق! الحساب دقيق للصفر رقم 167" if st.session_state.language == 'ar' else
                                             "Vérifié ! Calcul précis pour le zéro numéro 167" if st.session_state.language == 'fr' else
                                             "Verified! Accurate calculation for zero number 167"))
                        
                        show_info_box(
                            f"{end_time - start_time:.3f} " + ("ثانية" if st.session_state.language == 'ar' else
                                                            "secondes" if st.session_state.language == 'fr' else
                                                            "seconds"),
                            trans['time_taken']
                        )
                        
            except ValueError as e:
                show_info_box(str(e), trans['error'], "danger")
            except Exception as e:
                show_info_box(
                    str(e) if st.session_state.language == 'en' else
                    "حدث خطأ أثناء الحساب" if st.session_state.language == 'ar' else
                    "Une erreur s'est produite lors du calcul",
                    trans['error'], "danger"
                )
    
    # ===================== الجبر =====================
    elif section == trans['algebra']:
        algebra_section()
    
    # ===================== الهندسة =====================
    elif section == trans['geometry']:
        geometry_section()
    
    # ===================== التفاضل والتكامل =====================
    elif section == trans['calculus']:
        calculus_section()
    
    # ===================== الطبولوجيا (مبدئي) =====================
    elif section == trans['topology']:
        st.header("🌐 " + ("الطبولوجيا" if st.session_state.language == 'ar' else
                        "Topologie" if st.session_state.language == 'fr' else
                        "Topology"))
        
        show_math_formula(
            r"\\text{مجموعة مفتوحة: } U \\subseteq X \\text{ بحيث } \\forall x \\in U, \\exists \\epsilon > 0: B(x,\\epsilon) \\subseteq U",
            ("المجموعات المفتوحة" if st.session_state.language == 'ar' else
             "Ensembles ouverts" if st.session_state.language == 'fr' else
             "Open Sets"),
            ("التعريف الطبولوجي الأساسي" if st.session_state.language == 'ar' else
             "Définition topologique fondamentale" if st.session_state.language == 'fr' else
             "Fundamental topological definition")
        )
        
        st.markdown("""
        <div class="info-box">
        <p>الطبولوجيا هي فرع من الرياضيات يدرس الخصائص التي لا تتغير تحت التحويلات المستمرة.</p>
        <p>في هذا الإصدار، نقدم بعض المفاهيم الأساسية:</p>
        <ul>
            <li>المجموعات المفتوحة والمغلقة</li>
            <li>الاتصال والاستمرارية</li>
            <li>الفضاءات المتريّة</li>
            <li>التشابه الطبولوجي</li>
        </ul>
        </div>
        """ if st.session_state.language == 'ar' else """
        <div class="info-box">
        <p>La topologie est une branche des mathématiques qui étudie les propriétés invariantes sous les transformations continues.</p>
        <p>Dans cette version, nous présentons quelques concepts fondamentaux :</p>
        <ul>
            <li>Ensembles ouverts et fermés</li>
            <li>Connexité et continuité</li>
            <li>Espaces métriques</li>
            <li>Homéomorphisme</li>
        </ul>
        </div>
        """ if st.session_state.language == 'fr' else """
        <div class="info-box">
        <p>Topology is a branch of mathematics that studies properties invariant under continuous transformations.</p>
        <p>In this version, we present some fundamental concepts:</p>
        <ul>
            <li>Open and closed sets</li>
            <li>Connectedness and continuity</li>
            <li>Metric spaces</li>
            <li>Homeomorphism</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🎨 " + ("عرض مثال على التشويه المستمر" if st.session_state.language == 'ar' else
                           "Voir un exemple de déformation continue" if st.session_state.language == 'fr' else
                           "Show continuous deformation example")):
            st.info("سيتم إضافة أمثلة تفاعلية للطبولوجيا في الإصدارات القادمة" if st.session_state.language == 'ar' else
                   "Des exemples interactifs de topologie seront ajoutés dans les prochaines versions" if st.session_state.language == 'fr' else
                   "Interactive topology examples will be added in future versions")
    
    # ===================== علوم رياضية أخرى =====================
    elif section == trans['other_math']:
        st.header("🔬 " + ("علوم رياضية أخرى" if st.session_state.language == 'ar' else
                        "Autres sciences mathématiques" if st.session_state.language == 'fr' else
                        "Other Mathematical Sciences"))
        
        tab1, tab2, tab3 = st.tabs([
            "📊 " + ("الإحصاء والاحتمالات" if st.session_state.language == 'ar' else
                    "Statistiques et probabilités" if st.session_state.language == 'fr' else
                    "Statistics and Probability"),
            "🎮 " + ("نظرية الألعاب" if st.session_state.language == 'ar' else
                    "Théorie des jeux" if st.session_state.language == 'fr' else
                    "Game Theory"),
            "⚛️ " + ("الرياضيات التطبيقية" if st.session_state.language == 'ar' else
                    "Mathématiques appliquées" if st.session_state.language == 'fr' else
                    "Applied Mathematics")
        ])
        
        with tab1:
            st.subheader("📈 " + ("توزيع طبيعي" if st.session_state.language == 'ar' else
                               "Distribution normale" if st.session_state.language == 'fr' else
                               "Normal Distribution"))
            
            col1, col2 = st.columns(2)
            with col1:
                mean = st.number_input(
                    "μ" + (" (المتوسط)" if st.session_state.language == 'ar' else
                          " (moyenne)" if st.session_state.language == 'fr' else
                          " (mean)"),
                    value=0.0
                )
            
            with col2:
                std = st.number_input(
                    "σ" + (" (الانحراف المعياري)" if st.session_state.language == 'ar' else
                          " (écart-type)" if st.session_state.language == 'fr' else
                          " (standard deviation)"),
                    value=1.0, min_value=0.1
                )
            
            if st.button("📊 " + ("عرض التوزيع" if st.session_state.language == 'ar' else
                               "Afficher la distribution" if st.session_state.language == 'fr' else
                               "Show Distribution")):
                x = np.linspace(mean - 4*std, mean + 4*std, 100)
                y = (1/(std * np.sqrt(2*np.pi))) * np.exp(-0.5 * ((x-mean)/std)**2)
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=x, y=y,
                    mode='lines',
                    name='Normal Distribution',
                    line=dict(color='#4F46E5', width=3),
                    fill='tozeroy'
                ))
                
                fig.update_layout(
                    title=('توزيع طبيعي' if st.session_state.language == 'ar' else
                          'Distribution normale' if st.session_state.language == 'fr' else
                          'Normal Distribution'),
                    xaxis_title='x',
                    yaxis_title='f(x)',
                    plot_bgcolor='white'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("### " + ("خصائص التوزيع" if st.session_state.language == 'ar' else
                                   "Propriétés de la distribution" if st.session_state.language == 'fr' else
                                   "Distribution Properties"))
                col1, col2, col3 = st.columns(3)
                with col1:
                    show_success_box(f"{mean:.4f}", "μ")
                with col2:
                    show_success_box(f"{std:.4f}", "σ")
                with col3:
                    show_success_box(f"{std**2:.4f}", "σ²")

    # 📝 تذييل الصفحة
    st.markdown("""
    <div style="text-align: center; padding: 20px; margin-top: 2rem; color: #64748b; font-size: 0.9rem;">
        <p>✨ PPFO v29.0 - تطبيق رياضي متقدم متعدد اللغات</p>
        <p>تم التطوير باستخدام Streamlit, SymPy, و mpmath</p>
        <p>© 2024 - جميع الحقوق محفوظة</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
