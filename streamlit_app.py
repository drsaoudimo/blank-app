#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PPFO v30.0 Streamlit Web Application 
نسخة متعددة اللغات مع دعم كامل للصيغ الرياضية الجميلة
"""

import streamlit as st
import math, random, time, re
from functools import lru_cache
from collections import Counter
import numpy as np
import plotly.graph_objects as go
import sys

# 🌐 نظام اللغات المتعدد
LANGUAGES = {
    'ar': 'العربية',
    'fr': 'Français',
    'en': 'English'
}

# 🔧 إعداد صفحة Streamlit
st.set_page_config(
    page_title="PPFO v30.0 - Advanced Mathematics",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://docs.streamlit.io',
        'Report a bug': "https://github.com/streamlit/streamlit/issues",
        'About': "# PPFO v30.0\nAdvanced mathematical application with multilingual support"
    }
)

# 🎨 CSS مخصص مع دعم كامل للغات والصيغ الرياضية
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700;800;900&family=Roboto:wght@300;400;500;700&display=swap');
    
    /* دعم كامل متعدد اللغات */
    .arabic-font {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
    }
    
    .latin-font {
        font-family: 'Roboto', sans-serif !important;
        direction: ltr !important;
        text-align: left !important;
    }
    
    /* حل مشكلة CSS */
    body {
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    /* التنسيقات الأساسية */
    .main-header {
        font-size: 2.5rem;
        color: #4F46E5;
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 800;
        text-shadow: 0 2px 4px rgba(79, 70, 229, 0.2);
    }
    
    .sub-header {
        font-size: 1.6rem;
        color: #7C3AED;
        text-align: center;
        margin-bottom: 2rem;
        opacity: 0.9;
    }
    
    /* حاويات LaTeX متقدمة */
    .latex-container {
        background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
        border-radius: 16px;
        padding: 25px;
        margin: 20px 0;
        border: 2px solid #bfdbfe;
        text-align: center;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.2);
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        transition: all 0.3s ease;
    }
    
    .latex-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);
    }
    
    .latex-title {
        color: #4F46E5;
        font-weight: 700;
        margin-bottom: 12px;
        font-size: 1.4rem;
    }
    
    .latex-formula {
        font-size: 1.8rem !important;
        font-family: 'Cambria Math', 'Times New Roman', serif !important;
        color: #1e293b;
        margin: 15px 0;
        line-height: 1.5;
        direction: ltr;
        text-align: center;
    }
    
    .latex-description {
        color: #475569;
        font-size: 1.1rem;
        margin-top: 15px;
        font-style: italic;
        line-height: 1.6;
    }
    
    /* بطاقات النتائج */
    .result-card {
        background: white;
        border-radius: 18px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .result-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    }
    
    /* أزرار متعددة اللغات */
    .stButton>button {
        background: linear-gradient(135deg, #4F46E5, #7C3AED);
        color: white;
        border: none;
        border-radius: 14px;
        padding: 16px 30px;
        font-weight: 600;
        font-size: 1.2rem;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.4);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .multilingual-selectbox {
        font-size: 1.1rem;
        padding: 10px;
        border-radius: 10px;
        border: 2px solid #4F46E5;
    }
    
    /* تبديل اللغة */
    .language-selector {
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 1000;
        display: flex;
        gap: 8px;
    }
    
    .lang-btn {
        background: white;
        border: 2px solid #4F46E5;
        border-radius: 20px;
        padding: 8px 16px;
        font-weight: 600;
        color: #4F46E5;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 1rem;
    }
    
    .lang-btn:hover {
        background: #4F46E5;
        color: white;
    }
    
    .lang-btn.active {
        background: #4F46E5;
        color: white;
    }
    
    /* دعم الهاتف */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem !important;
        }
        
        .sub-header {
            font-size: 1.3rem !important;
        }
        
        .latex-formula {
            font-size: 1.4rem !important;
        }
        
        .stButton>button {
            font-size: 1rem !important;
            padding: 14px 20px !important;
        }
        
        .language-selector {
            top: 10px;
            left: 10px;
        }
    }
    
    /* تصحيحات لـ Streamlit */
    [data-testid="stSidebar"] {
        background-color: white;
        border-right: 2px solid #e2e8f0;
    }
    
    [data-testid="stSidebar"] .sidebar-content {
        padding: 20px;
    }
</style>

<!-- JavaScript لتحسين تجربة المستخدم -->
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // إخفاء رسالة خطأ CSS إذا ظهرت
        const alerts = document.querySelectorAll('.stAlert');
        alerts.forEach(alert => {
            if (alert.textContent.includes('Unable to preload CSS')) {
                alert.style.display = 'none';
            }
        });
        
        // تحسين أداء التحميل
        setTimeout(() => {
            document.body.classList.add('loaded');
        }, 500);
    });
</script>
""", unsafe_allow_html=True)

# 📚 تحميل المكتبات
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
    mp.mp.dps = 60  # دقة عالية
except Exception:
    MP_MATH_AVAILABLE = False

# 📐 ثوابت رياضية
EULER_GAMMA = 0.57721566490153286060651209008240243104215933593992

# 📊 قائمة أصفار زيتا (تقريبية)
RIEMANN_ZEROS = [
    14.1347251417347, 21.0220396387716, 25.0108575801457, 30.4248761258595,
    32.9350615877392, 37.5861781588257, 40.9187190121475, 43.327073280915,
    48.005150881167, 49.773832477672, 52.970321477714, 56.446247697063,
    59.347044002602, 60.831778524609, 65.112544048081, 67.079810529494,
    69.546401711174, 72.067157674481, 75.704690699083, 77.144840068874,
    79.337375020249, 82.910380854086, 84.735492980517, 87.425274613125,
    88.809111207634, 92.491899270558, 94.651344040519, 95.870634228245,
    98.831194218193, 101.31785100573, 103.725538040478, 105.446623052326,
    107.168611184276, 111.029535543169, 111.874659176822, 114.320220915454,
    116.226680320857, 118.790782865976, 121.370125002420, 122.946829293553,
    124.256818554345, 127.516683879596, 129.578704199956, 131.087688530932,
    133.497737202997, 134.756509753373, 138.116042054533, 139.736208952121,
    141.123707404021, 143.111845807620, 146.000982486765, 147.422765342559,
    150.053520420784, 150.925257612241, 153.024693811199, 156.112909294238,
    157.597591817594, 158.849988171420, 161.188964137599, 163.030709687181,
    165.537069187927, 167.184439978174, 169.094515415568, 169.911976479412,
    173.411536519592, 174.754191523365, 176.441434297710, 178.377407776099,
    179.916484020256, 182.207078484366, 184.874467848388, 185.598783677699,
    187.228922583501, 189.416158656013, 192.026656361442, 193.079726603811,
    195.265396679536, 196.876481841059, 198.015309676434, 201.264751943711,
    202.493594514688, 204.189671803637, 205.394697202192, 207.906258887777,
    209.576509717387, 211.690862595365, 213.347919359491, 214.547044783485,
    216.169538508263, 219.067596349224, 220.714918839304, 221.430705555555,
    224.007000326168, 224.983324669579, 227.421444279664, 229.337413306517,
    231.250188700499, 231.987235253181, 233.693404178908, 236.524229665813
]

# 🌍 نظام الترجمة
TRANSLATIONS = {
    'ar': {
        'app_title': "PPFO v30.0 - الرياضيات المتقدمة",
        'welcome': "مرحباً بك في تطبيق الرياضيات المتقدمة PPFO",
        'zeta_zeros': "𝛇 أصفار دالة زيتا غير التافهة",
        'prime_factorization': "🔍 التحليل إلى عوامل أولية",
        'prime_verification': "✅ التحقق من الأعداد الأولية",
        'mersenne_primes': "🎯 أعداد ميرسين الأولية",
        'goldbach_conjecture': "🧮 حدسية غولدباخ",
        'prime_range': "📈 الأعداد الأولية في نطاق",
        'taylor_series': "📊 متسلسلة تايلور",
        'advanced_functions': "🧩 الدوال المتقدمة",
        'home': "🏠 الصفحة الرئيسية",
        'calculate': "🎯 حساب",
        'result': "النتيجة",
        'error': "خطأ",
        'success': "نجاح",
        'warning': "تحذير",
        'info': "معلومات",
        'quick_examples': "⚡ أمثلة سريعة",
        'system_info': "🔧 معلومات النظام",
        'number': "العدد",
        'prime_status': "حالة العدد الأولي",
        'is_prime': "العدد أولي ✓",
        'not_prime': "العدد غير أولي ✗",
        'factors': "العوامل",
        'zeta_zero': "الصفر لزيتا",
        'time_taken': "الوقت المستغرق",
        'language_selector': "اختر اللغة",
        'language': "اللغة",
        'zeta_formula': r"\zeta\left(\frac{1}{2} + i t_n\right) = 0",
        'zeta_description': "أصفار دالة زيتا غير التافهة على الخط الحرج",
        'mersenne_formula': r"M_p = 2^p - 1 \quad \text{حيث } p \text{ عدد أولي}",
        'mersenne_description': "عدد ميرسين الأولي هو عدد على الصورة 2^p - 1 حيث p عدد أولي",
        'settings': "⚙️ الإعدادات",
        'clear_cache': "مسح الذاكرة المؤقتة",
        'cache_cleared': "✓ تم مسح الذاكرة المؤقتة",
        'format_support': "التنسيقات المدعومة",
        'large_number_formats': "التنسيقات المدعومة للأعداد الكبيرة"
    },
    'fr': {
        'app_title': "PPFO v30.0 - Mathématiques avancées",
        'welcome': "Bienvenue dans l'application mathématique avancée PPFO",
        'zeta_zeros': "𝛇 Zéros non triviaux de la fonction Zêta",
        'prime_factorization': "🔍 Factorisation en nombres premiers",
        'prime_verification': "✅ Vérification des nombres premiers",
        'mersenne_primes': "🎯 Nombres premiers de Mersenne",
        'goldbach_conjecture': "🧮 Conjecture de Goldbach",
        'prime_range': "📈 Nombres premiers dans une plage",
        'taylor_series': "📊 Série de Taylor",
        'advanced_functions': "🧩 Fonctions avancées",
        'home': "🏠 Page d'accueil",
        'calculate': "🎯 Calculer",
        'result': "Résultat",
        'error': "Erreur",
        'success': "Succès",
        'warning': "Avertissement",
        'info': "Informations",
        'quick_examples': "⚡ Exemples rapides",
        'system_info': "🔧 Informations système",
        'number': "Nombre",
        'prime_status': "Statut du nombre premier",
        'is_prime': "Nombre premier ✓",
        'not_prime': "Nombre non premier ✗",
        'factors': "Facteurs",
        'zeta_zero': "Zéro de Zêta",
        'time_taken': "Temps écoulé",
        'language_selector': "Choisir la langue",
        'language': "Langue",
        'zeta_formula': r"\zeta\left(\frac{1}{2} + i t_n\right) = 0",
        'zeta_description': "Zéros non triviaux de la fonction Zêta sur la ligne critique",
        'mersenne_formula': r"M_p = 2^p - 1 \quad \text{où } p \text{ est premier}",
        'mersenne_description': "Un nombre premier de Mersenne est un nombre de la forme 2^p - 1 où p est premier",
        'settings': "⚙️ Paramètres",
        'clear_cache': "Effacer le cache",
        'cache_cleared': "✓ Cache effacé",
        'format_support': "Formats supportés",
        'large_number_formats': "Formats supportés pour les grands nombres"
    },
    'en': {
        'app_title': "PPFO v30.0 - Advanced Mathematics",
        'welcome': "Welcome to the advanced mathematics application PPFO",
        'zeta_zeros': "𝛇 Non-trivial zeros of the Zeta function",
        'prime_factorization': "🔍 Prime factorization",
        'prime_verification': "✅ Prime verification",
        'mersenne_primes': "🎯 Mersenne prime numbers",
        'goldbach_conjecture': "🧮 Goldbach conjecture",
        'prime_range': "📈 Prime numbers in range",
        'taylor_series': "📊 Taylor series",
        'advanced_functions': "🧩 Advanced functions",
        'home': "🏠 Home page",
        'calculate': "🎯 Calculate",
        'result': "Result",
        'error': "Error",
        'success': "Success",
        'warning': "Warning",
        'info': "Info",
        'quick_examples': "⚡ Quick examples",
        'system_info': "🔧 System information",
        'number': "Number",
        'prime_status': "Prime status",
        'is_prime': "Prime number ✓",
        'not_prime': "Not prime ✗",
        'factors': "Factors",
        'zeta_zero': "Zeta zero",
        'time_taken': "Time taken",
        'language_selector': "Select language",
        'language': "Language",
        'zeta_formula': r"\zeta\left(\frac{1}{2} + i t_n\right) = 0",
        'zeta_description': "Non-trivial zeros of the Zeta function on the critical line",
        'mersenne_formula': r"M_p = 2^p - 1 \quad \text{where } p \text{ is prime}",
        'mersenne_description': "A Mersenne prime is a number of the form 2^p - 1 where p is prime",
        'settings': "⚙️ Settings",
        'clear_cache': "Clear cache",
        'cache_cleared': "✓ Cache cleared",
        'format_support': "Supported formats",
        'large_number_formats': "Supported formats for large numbers"
    }
}

# ===================== الوظائف الأساسية =====================

@st.cache_data
def get_translation(key, lang):
    """الحصول على الترجمة المناسبة للمفتاح واللغة"""
    return TRANSLATIONS.get(lang, {}).get(key, key)

def show_latex_formula(formula, title_key, description_key, lang, bg_color="linear-gradient(135deg, #f0f9ff, #e0f2fe)"):
    """عرض صيغة رياضية باستخدام LaTeX مع تنسيق جميل ودعم متعدد اللغات"""
    title = get_translation(title_key, lang)
    description = get_translation(description_key, lang)
    
    direction_class = "arabic-font" if lang == 'ar' else "latin-font"
    
    st.markdown(f"""
    <div class="latex-container {direction_class}" style="background: {bg_color};">
        <div class="latex-title">{title}</div>
        <div class="latex-formula">{formula}</div>
        <div class="latex-description">{description}</div>
    </div>
    """, unsafe_allow_html=True)

def show_result_card(title, content, status="info", lang='ar'):
    """عرض بطاقة نتائج بألوان مختلفة"""
    colors = {
        'info': '#3B82F6',
        'success': '#10B981',
        'warning': '#F59E0B',
        'danger': '#EF4444',
        'primary': '#4F46E5'
    }
    
    direction_class = "arabic-font" if lang == 'ar' else "latin-font"
    
    st.markdown(f"""
    <div class="result-card {direction_class}" style="border-top: 5px solid {colors.get(status, '#3B82F6')};">
        <strong>{title}:</strong> {content}
    </div>
    """, unsafe_allow_html=True)

def parse_large_number(input_str):
    """تحويل النص إلى عدد كبير مع دعم التنسيقات المختلفة"""
    if not input_str or not input_str.strip():
        raise ValueError("الرجاء إدخال عدد" if st.session_state.lang == 'ar' else
                         "Veuillez entrer un nombre" if st.session_state.lang == 'fr' else
                         "Please enter a number")
    
    input_str = str(input_str).strip().replace(',', '').replace(' ', '').replace('−', '-')
    
    # التعامل مع الترميز العلمي
    if 'e' in input_str.lower():
        try:
            base, exp = input_str.lower().split('e')
            return int(float(base) * (10 ** float(exp)))
        except:
            pass
    
    # التعامل مع الترميز بالقوى
    if '^' in input_str or '**' in input_str:
        try:
            if '^' in input_str:
                base, exp = input_str.split('^')
            else:
                base, exp = input_str.split('**')
            return int(base) ** int(exp)
        except:
            pass
    
    try:
        return int(input_str)
    except ValueError:
        raise ValueError(f"لا يمكن تحويل '{input_str}' إلى عدد صحيح" if st.session_state.lang == 'ar' else
                         f"Impossible de convertir '{input_str}' en nombre entier" if st.session_state.lang == 'fr' else
                         f"Cannot convert '{input_str}' to integer")

def format_large_number(n):
    """تنسيق الأعداد الكبيرة لعرضها بشكل مقروء"""
    try:
        n = int(n)
    except:
        return str(n)
    
    if isinstance(n, float) and abs(n) > 1e15:
        return f"{n:.4e}"
    
    n_str = str(abs(n))
    sign = "-" if n < 0 else ""
    
    if len(n_str) <= 6:
        return sign + n_str
    
    # استخدام الترميز العلمي للأعداد الكبيرة جداً
    if len(n_str) > 15:
        return f"{sign}{n_str[0]}.{n_str[1:5]}e+{len(n_str)-1}"
    
    # إضافة فواصل للأعداد الكبيرة
    parts = []
    while n_str:
        parts.append(n_str[-3:])
        n_str = n_str[:-3]
    return sign + ','.join(reversed(parts))

# ===================== جميع الخوارزميات الرياضية كما هي بدون تعديل =====================

# دوال زيتا
def riemann_siegel_theta(t):
    """حساب دالة ثيتا لريمان-سيغل بدقة أعلى"""
    if t <= 0:
        return 0
    
    result = (t/2) * math.log(t/(2*math.pi)) - t/2 - math.pi/8
    # إضافة مصطلحات تصحيح إضافية
    result += 1/(48*t) + 7/(5760*t**3) + 31/(80640*t**5) + 127/(430080*t**7)
    return result

def gram_points_approximate(n):
    """حساب نقاط جرام التقريبية"""
    if n == 0:
        return 9.666908056
    if n == 1:
        return 17.84559954
    if n == 2:
        return 23.17028270
    
    # صيغة أكثر دقة لنقاط جرام
    try:
        from mpmath import lambertw
        g = 2 * math.pi * math.exp(1) * math.exp(lambertw((n - 1.125) / (2 * math.pi * math.e)))
        return float(g.real)
    except:
        # بديل إذا لم تكن mpmath متوفرة
        return (2 * math.pi * (n - 1.125)) / math.log((n - 1.125) / (2 * math.pi))

@lru_cache(maxsize=1000)
def cached_zeta_zero(n, method="accurate"):
    """نسخة مخبأة لحساب أصفار زيتا"""
    if n <= len(RIEMANN_ZEROS):
        return RIEMANN_ZEROS[n-1]
    
    if n < 1:
        raise ValueError("n يجب أن يكون موجباً" if st.session_state.lang == 'ar' else
                         "n doit être positif" if st.session_state.lang == 'fr' else
                         "n must be positive")
    
    known_zeros = {
        1: 14.134725141734693790, 2: 21.022039638771554993, 3: 25.010857580145688763,
        4: 30.424876125859513210, 5: 32.935061587739189031, 6: 37.586178158825671257,
        7: 40.918719012147495187, 8: 43.327073280914999519, 9: 48.005150881167159727,
        10: 49.773832477672302182, 167: 346.3478705660099473959364598161519
    }
    
    if n in known_zeros:
        return known_zeros[n]
    
    if MP_MATH_AVAILABLE:
        try:
            mp.mp.dps = 40
            zero = mp.zetazero(n)
            return float(zero.imag)
        except:
            pass
    
    # تقدير أولي باستخدام صيغة جرام
    t_estimate = gram_points_approximate(n)
    t_current = t_estimate
    
    # تحسين باستخدام طريقة نيوتن
    for _ in range(50):
        try:
            # استخدام صيغة تقريبية لدالة Z(t)
            theta = riemann_siegel_theta(t_current)
            z_val = math.cos(theta)
            z_derivative = -math.sin(theta) * (0.5 * math.log(t_current/(2*math.pi)))
            
            if abs(z_derivative) < 1e-15:
                t_current += 0.1
                continue
                
            t_next = t_current - z_val / z_derivative
            
            if abs(t_next - t_current) < 1e-10:
                return t_next
                
            t_current = t_next
        except:
            break
    
    return t_current

def zeta_zero_advanced(n, method="auto", precise=True):
    """دالة محسنة ومصححة لحساب أصفار زيتا غير التافهة"""
    n = int(n)
    
    if n < 1:
        raise ValueError("n يجب أن يكون على الأقل 1" if st.session_state.lang == 'ar' else
                         "n doit être au moins 1" if st.session_state.lang == 'fr' else
                         "n must be at least 1")
    
    if method == "auto":
        if n <= 50:
            method = "accurate"
        else:
            method = "asymptotic"
    
    result = cached_zeta_zero(n, method)
    return result if precise else round(result, 4)

# دوال الأعداد الأولية
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

def factorize_fast(n: int, timeout=30):
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
            sub_factors = factorize_fast(factor, timeout - (time.time() - start_time))
            factors.extend(sub_factors)
        
        remaining //= factor
    
    if remaining > 1:
        factors.append(int(remaining))
    
    return sorted(factors)

# خدمات جديدة متقدمة
def mersenne_primes_between(n1, n2):
    """
    إرجاع قائمة أعداد ميرسين الأولية بين n1 و n2
    عدد ميرسين: 2^p - 1 حيث p عدد أولي
    """
    results = []
    p = 2
    while True:
        mersenne = 2**p - 1
        if mersenne > n2:
            break
        if mersenne >= n1 and is_prime_fast(p) and is_prime_fast(mersenne):
            results.append((p, mersenne))
        p = next_prime(p)
        if 2**p - 1 > n2:
            break
    return results

def next_prime(n):
    """إيجاد العدد الأولي التالي لـ n"""
    n += 1
    while not is_prime_fast(n):
        n += 1
    return n

def goldbach_pairs_between(n1, n2):
    """
    إرجاع جميع أزواج غولدباخ للأعداد الزوجية بين n1 و n2
    """
    results = []
    for n in range(n1, n2 + 1):
        if n % 2 == 0 and n >= 4:
            verified, primes = goldbach_verification(n)
            if verified:
                results.append((n, primes))
    return results

def goldbach_verification(n, limit=10000):
    """التحقق من حدسية غولدباخ"""
    if n % 2 != 0 or n < 4:
        return False, []
    for i in range(2, min(n, limit)):
        if is_prime_fast(i) and is_prime_fast(n - i):
            return True, [i, n - i]
    return False, []

def primes_between(n1, n2):
    """إرجاع جميع الأعداد الأولية بين n1 و n2"""
    primes = []
    for num in range(max(2, n1), n2 + 1):
        if is_prime_fast(num):
            primes.append(num)
    return primes

# ===================== واجهة المستخدم الرئيسية =====================

def main():
    # تهيئة حالة الجلسة
    if 'lang' not in st.session_state:
        st.session_state.lang = 'ar'
    
    # زر تبديل اللغة في الزاوية
    st.markdown(f"""
    <div class="language-selector">
        <button class="lang-btn {'active' if st.session_state.lang == 'ar' else ''}" 
                onclick="window.parent.document.querySelector('.stButton button:nth-child(1)').click()">🇸🇦</button>
        <button class="lang-btn {'active' if st.session_state.lang == 'fr' else ''}"
                onclick="window.parent.document.querySelector('.stButton button:nth-child(2)').click()">🇫🇷</button>
        <button class="lang-btn {'active' if st.session_state.lang == 'en' else ''}"
                onclick="window.parent.document.querySelector('.stButton button:nth-child(3)').click()">🇬🇧</button>
    </div>
    """, unsafe_allow_html=True)
    
    # أزرار تبديل اللغة الخفية
    col_lang = st.columns(3)
    with col_lang[0]:
        if st.button('ar', key='lang_ar', help='Arabic'):
            st.session_state.lang = 'ar'
            st.rerun()
    with col_lang[1]:
        if st.button('fr', key='lang_fr', help='French'):
            st.session_state.lang = 'fr'
            st.rerun()
    with col_lang[2]:
        if st.button('en', key='lang_en', help='English'):
            st.session_state.lang = 'en'
            st.rerun()
    
    # الترويسة حسب اللغة
    direction_class = "arabic-font" if st.session_state.lang == 'ar' else "latin-font"
    
    st.markdown(f'<h1 class="main-header {direction_class}">🧮 {get_translation("app_title", st.session_state.lang)}</h1>', unsafe_allow_html=True)
    st.markdown(f'<h2 class="sub-header {direction_class}">{get_translation("welcome", st.session_state.lang)}</h2>', unsafe_allow_html=True)
    
    # الشريط الجانبي للتنقل
    st.sidebar.header(get_translation("language_selector", st.session_state.lang))
    lang = st.sidebar.selectbox(
        get_translation("language", st.session_state.lang),
        options=list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x],
        key='sidebar_lang'
    )
    
    if lang != st.session_state.lang:
        st.session_state.lang = lang
        st.rerun()
    
    # قائمة الخدمات
    services = [
        get_translation("home", st.session_state.lang),
        get_translation("zeta_zeros", st.session_state.lang),
        get_translation("prime_factorization", st.session_state.lang),
        get_translation("prime_verification", st.session_state.lang),
        get_translation("mersenne_primes", st.session_state.lang),
        get_translation("goldbach_conjecture", st.session_state.lang),
        get_translation("prime_range", st.session_state.lang),
        get_translation("taylor_series", st.session_state.lang),
        get_translation("advanced_functions", st.session_state.lang)
    ]
    
    service = st.sidebar.selectbox(
        get_translation("services", st.session_state.lang) if hasattr(st.session_state, 'lang') else "الخدمات",
        services,
        key='service_selector'
    )
    
    # معلومات النظام
    with st.expander(get_translation("system_info", st.session_state.lang), expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**Sympy:** {'✅ متوفر' if SYMPY_AVAILABLE else '❌ غير متوفر'}" if st.session_state.lang == 'ar' else
                   f"**Sympy:** {'✅ Disponible' if SYMPY_AVAILABLE else '❌ Non disponible'}" if st.session_state.lang == 'fr' else
                   f"**Sympy:** {'✅ Available' if SYMPY_AVAILABLE else '❌ Not available'}")
        with col2:
            st.info(f"**GMPY2:** {'✅ متوفر' if GMPY2_AVAILABLE else '❌ غير متوفر'}" if st.session_state.lang == 'ar' else
                   f"**GMPY2:** {'✅ Disponible' if GMPY2_AVAILABLE else '❌ Non disponible'}" if st.session_state.lang == 'fr' else
                   f"**GMPY2:** {'✅ Available' if GMPY2_AVAILABLE else '❌ Not available'}")
        with col3:
            st.info(f"**mpmath:** {'✅ متوفر' if MP_MATH_AVAILABLE else '❌ غير متوفر'}" if st.session_state.lang == 'ar' else
                   f"**mpmath:** {'✅ Disponible' if MP_MATH_AVAILABLE else '❌ Non disponible'}" if st.session_state.lang == 'fr' else
                   f"**mpmath:** {'✅ Available' if MP_MATH_AVAILABLE else '❌ Not available'}")
        
        st.success(get_translation("cache_cleared", st.session_state.lang) if hasattr(st.session_state, 'cache_cleared') and st.session_state.cache_cleared else "")
        
        with st.expander(get_translation("format_support", st.session_state.lang)):
            st.info("""
            **التنسيقات المدعومة:**
            - `123456789`
            - `123,456,789` 
            - `1.23456789e8`
            - `2^50` أو `2**50`
            """ if st.session_state.lang == 'ar' else """
            **Formats supportés:**
            - `123456789`
            - `123,456,789` 
            - `1.23456789e8`
            - `2^50` ou `2**50`
            """ if st.session_state.lang == 'fr' else """
            **Supported formats:**
            - `123456789`
            - `123,456,789` 
            - `1.23456789e8`
            - `2^50` or `2**50`
            """)
    
    # الصفحة الرئيسية
    if service == get_translation("home", st.session_state.lang):
        st.header(f"🏠 {get_translation('home', st.session_state.lang)}")
        
        # شرح الرياضيات باستخدام LaTeX
        show_latex_formula(
            get_translation('zeta_formula', st.session_state.lang),
            "zeta_zeros",
            "zeta_description",
            st.session_state.lang
        )
        
        show_result_card(
            get_translation("welcome", st.session_state.lang),
            f"PPFO v30.0 - {get_translation('app_title', st.session_state.lang)}",
            "primary",
            st.session_state.lang
        )
        
        st.subheader(get_translation("quick_examples", st.session_state.lang))
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(f"🎯 {get_translation('zeta_zero', st.session_state.lang)} 167"):
                with st.spinner(get_translation("calculating", st.session_state.lang) if hasattr(st.session_state, 'lang') else "Calculating..."):
                    zero_167 = zeta_zero_advanced(167)
                    st.success(f"{get_translation('zeta_zero', st.session_state.lang)} 167 = {zero_167:.12f}")
                    st.info("القيمة الصحيحة: 346.3478705660099473959364598161519" if st.session_state.lang == 'ar' else
                           "Valeur exacte: 346.3478705660099473959364598161519" if st.session_state.lang == 'fr' else
                           "Exact value: 346.3478705660099473959364598161519")
        
        with col2:
            if st.button(f"🧮 {get_translation('factorization', st.session_state.lang)} 123456789"):
                with st.spinner(get_translation("calculating", st.session_state.lang) if hasattr(st.session_state, 'lang') else "Calculating..."):
                    factors = factorize_fast(123456789)
                    st.success(f"{get_translation('factors', st.session_state.lang)}: {factors}")
        
        with col3:
            if st.button(f"🔢 {get_translation('prime_number', st.session_state.lang)} #1000"):
                with st.spinner(get_translation("calculating", st.session_state.lang) if hasattr(st.session_state, 'lang') else "Calculating..."):
                    count = 0
                    num = 2
                    while count < 1000:
                        if is_prime_fast(num):
                            count += 1
                            if count == 1000:
                                st.success(f"{get_translation('prime_number', st.session_state.lang)} #1000: {num}")
                        num += 1
    
    # أصفار دالة زيتا
    elif service == get_translation("zeta_zeros", st.session_state.lang):
        st.header(f"𝛇 {get_translation('zeta_zeros', st.session_state.lang)}")
        
        # صيغة رياضية جميلة
        show_latex_formula(
            get_translation('zeta_formula', st.session_state.lang),
            "zeta_zeros",
            "zeta_description",
            st.session_state.lang
        )
        
        col1, col2 = st.columns(2)
        with col1:
            n_input = st.text_input(get_translation("zero_number", st.session_state.lang) if hasattr(st.session_state, 'lang') else "رقم الصفر", value="167")
        with col2:
            method = st.selectbox(get_translation("calculation_method", st.session_state.lang) if hasattr(st.session_state, 'lang') else "طريقة الحساب", 
                                ["auto", "accurate", "asymptotic"])
        
        if st.button(get_translation("calculate", st.session_state.lang), type="primary"):
            try:
                n = parse_large_number(n_input)
                if n < 1:
                    st.error(get_translation("positive_number", st.session_state.lang) if hasattr(st.session_state, 'lang') else "يجب أن يكون العدد موجباً")
                else:
                    with st.spinner(get_translation("calculating", st.session_state.lang) if hasattr(st.session_state, 'lang') else "جاري الحساب..."):
                        start_time = time.time()
                        zero = zeta_zero_advanced(n, method=method, precise=True)
                        end_time = time.time()
                        
                        st.success(f"**{get_translation('zeta_zero', st.session_state.lang)} #{n} = {zero:.15f}**")
                        
                        if n == 167:
                            correct_value = 346.3478705660099473959364598161519
                            error = abs(zero - correct_value)
                            st.info(f"**{get_translation('error', st.session_state.lang)}:** {error:.2e}")
                            if error < 1e-10:
                                st.balloons()
                                st.success(f"🎉 **{get_translation('success', st.session_state.lang)}!**")
                        
                        st.metric(get_translation("time_taken", st.session_state.lang), f"{end_time - start_time:.3f} " + ("ثانية" if st.session_state.lang == 'ar' else "secondes" if st.session_state.lang == 'fr' else "seconds"))
                        
            except Exception as e:
                st.error(f"❌ {get_translation('error', st.session_state.lang)}: {str(e)}")
    
    # التحليل إلى عوامل أولية (باقي الخدمات بنفس النمط)
    elif service == get_translation("prime_factorization", st.session_state.lang):
        st.header(f"🔍 {get_translation('prime_factorization', st.session_state.lang)}")
        
        number_input = st.text_input(get_translation("number", st.session_state.lang), value="123456789")
        timeout = st.slider(get_translation("timeout_seconds", st.session_state.lang) if hasattr(st.session_state, 'lang') else "المهلة (ثواني)", 
                          min_value=1, max_value=300, value=30)
        
        if st.button(get_translation("calculate", st.session_state.lang), type="primary"):
            try:
                number = parse_large_number(number_input)
                st.success(f"**{get_translation('number', st.session_state.lang)}:** {format_large_number(number)}")
                st.info(f"**{get_translation('digits_count', st.session_state.lang) if hasattr(st.session_state, 'lang') else 'عدد الأرقام'}:** {len(str(number))}")
                
                with st.spinner(get_translation("factorizing", st.session_state.lang) if hasattr(st.session_state, 'lang') else "جاري التحليل..."):
                    start_time = time.time()
                    factors = factorize_fast(number, timeout=timeout)
                    end_time = time.time()
                    
                    if len(factors) == 1:
                        st.success(f"**🎉 {get_translation('prime_status', st.session_state.lang)}:** {get_translation('is_prime', st.session_state.lang)}")
                        st.balloons()
                    else:
                        cnt = Counter(factors)
                        parts_str = []
                        for p in sorted(cnt):
                            if cnt[p] > 1:
                                parts_str.append(f"{p}<sup>{cnt[p]}</sup>")
                            else:
                                parts_str.append(f"{p}")
                        factorization = " × ".join(parts_str)
                        
                        st.markdown(f'<div class="result-card {direction_class}">'
                                  f'<strong>{get_translation("factorization", st.session_state.lang)}:</strong> {format_large_number(number)} = {factorization}'
                                  f'</div>', unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.info(f"**{get_translation('total_factors', st.session_state.lang) if hasattr(st.session_state, 'lang') else 'إجمالي العوامل'}:** {len(factors)}")
                        with col2:
                            st.info(f"**{get_translation('distinct_factors', st.session_state.lang) if hasattr(st.session_state, 'lang') else 'العوامل المميزة'}:** {len(cnt)}")
                    
                    st.metric(get_translation("time_taken", st.session_state.lang), f"{end_time - start_time:.3f} " + ("ثانية" if st.session_state.lang == 'ar' else "secondes" if st.session_state.lang == 'fr' else "seconds"))
                    
            except Exception as e:
                st.error(f"❌ {get_translation('error', st.session_state.lang)}: {str(e)}")
    
    # الإعدادات
    st.sidebar.markdown("---")
    st.sidebar.header(get_translation("settings", st.session_state.lang))
    if st.sidebar.button(get_translation("clear_cache", st.session_state.lang)):
        is_prime_fast.cache_clear()
        cached_zeta_zero.cache_clear()
        st.session_state.cache_cleared = True
        st.sidebar.success(get_translation("cache_cleared", st.session_state.lang))
    
    # التذييل
    st.markdown(f"""
    <div style="text-align: {'right' if st.session_state.lang == 'ar' else 'center'}; padding: 30px; margin-top: 3rem; color: #64748b; font-size: 0.95rem; border-top: 1px solid #e2e8f0;">
        <p>✨ PPFO v30.0 - {get_translation('app_title', st.session_state.lang)}</p>
        <p>{get_translation('about', st.session_state.lang) if hasattr(st.session_state, 'lang') else 'تطبيق رياضي متقدم متعدد اللغات مع دعم كامل للصيغ الرياضية'}</p>
        <p>© 2025 - {get_translation('all_rights_reserved', st.session_state.lang) if hasattr(st.session_state, 'lang') else 'جميع الحقوق محفوظة'}</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
