#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PPFO v24.0 Streamlit Web Application — نسخة محسنة مع خدمات جديدة وتحسينات السرعة
تطبيق ويب باستخدام Streamlit
"""
import streamlit as st
import math, random, time, sys
from functools import lru_cache
from collections import Counter

# إعداد صفحة Streamlit
st.set_page_config(
    page_title="PPFO v24.0 - النسخة المحسنة",
    page_icon="🔢",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

EULER_GAMMA = 0.57721566490153286060651209008240243104215933593992

# ------ أصفار زيتا (قيم تقريبية) - مكبرة
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

# ===================== دوال زيتا غير التافهة الذاتية =====================

def riemann_zeta_zeros_approximate(n, max_iterations=100, tolerance=1e-10):
    """حساب تقريبي للأصفار غير التافهة لدالة زيتا لريمان"""
    def zeta_derivative_approx(s, h=1e-8):
        return (zeta_approx(s + h) - zeta_approx(s - h)) / (2 * h)
    
    def zeta_approx(s, terms=100):
        result = 0
        for k in range(1, terms + 1):
            result += 1 / (k ** s)
        return result
    
    def z_function(t):
        theta = (t/2) * math.log(t/(2*math.pi)) - t/2 - math.pi/8
        theta += 1/(48*t)
        zeta_val = zeta_approx(0.5 + 1j * t, 50)
        return abs(zeta_val) * math.cos(theta - math.atan2(zeta_val.imag, zeta_val.real))
    
    if n == 1:
        t_estimate = 14.0
    else:
        t_estimate = (2 * math.pi * n) / math.log(n)
    
    t_current = t_estimate
    for iteration in range(max_iterations):
        z_val = z_function(t_current)
        z_derivative = (z_function(t_current + tolerance) - z_function(t_current - tolerance)) / (2 * tolerance)
        
        if abs(z_derivative) < 1e-15:
            t_current += 0.1
            continue
            
        t_next = t_current - z_val / z_derivative
        
        if abs(t_next - t_current) < tolerance:
            return t_next
            
        t_current = t_next
    
    return t_current

def riemann_siegel_theta(t):
    """حساب دالة ثيتا لريمان-سيغل بدقة أعلى"""
    result = (t/2) * math.log(t/(2*math.pi)) - t/2 - math.pi/8
    result += 1/(48*t) + 7/(5760*t**3) + 31/(80640*t**5)
    return result

def gram_points_approximate(n):
    """حساب نقاط جرام التقريبية"""
    if n == 0:
        return 0.0
    return (2 * math.pi * n) / math.log(n) * (1 + 1/(2 * math.log(n)))

@lru_cache(maxsize=1000)
def cached_zeta_zero(n, method="hybrid"):
    """نسخة مخبأة لحساب أصفار زيتا مع خيارات متعددة للطرق"""
    if n <= len(RIEMANN_ZEROS):
        return RIEMANN_ZEROS[n-1]
    
    if method == "gram":
        g_n = gram_points_approximate(n)
        g_n_minus_1 = gram_points_approximate(n-1)
        
        t_low = g_n_minus_1
        t_high = g_n
        
        for _ in range(50):
            t_mid = (t_low + t_high) / 2
            if riemann_siegel_theta(t_mid) < (n-1) * math.pi:
                t_low = t_mid
            else:
                t_high = t_mid
        
        return (t_low + t_high) / 2
    
    elif method == "asymptotic":
        if n > 100:
            t = (2 * math.pi * n) / math.log(n)
            t -= (math.log(2*math.pi) - 1) / (2*math.pi) * math.log(n)
            t += (math.log(2*math.pi)**2 - 2*math.log(2*math.pi) - 1) / (8*math.pi*math.log(n))
            return t
        else:
            return riemann_zeta_zeros_approximate(n)
    
    else:  # hybrid method
        if n <= 50:
            return riemann_zeta_zeros_approximate(n)
        else:
            asymptotic = (2 * math.pi * n) / math.log(n)
            correction = 0.5 * math.log(n) / math.pi
            return asymptotic - correction

def zeta_zero_advanced(n, method="auto", precise=True):
    """دالة محسنة لحساب أصفار زيتا غير التافهة"""
    n = int(n)
    
    if n < 1:
        raise ValueError("n يجب أن يكون على الأقل 1")
    
    known_zeros = {
        1: 14.134725141734693790, 2: 21.022039638771554993, 3: 25.010857580145688763,
        4: 30.424876125859513210, 5: 32.935061587739189031, 6: 37.586178158825671257,
        7: 40.918719012147495187, 8: 43.327073280914999519, 9: 48.005150881167159727,
        10: 49.773832477672302182
    }
    
    if n in known_zeros:
        result = known_zeros[n]
        return result if precise else round(result, 4)
    
    if method == "auto":
        if n <= 20:
            method = "numeric"
        elif n <= 100:
            method = "hybrid"
        else:
            method = "asymptotic"
    
    if method == "numeric":
        result = riemann_zeta_zeros_approximate(n)
    elif method == "gram":
        result = cached_zeta_zero(n, "gram")
    elif method == "asymptotic":
        result = cached_zeta_zero(n, "asymptotic")
    else:
        result = cached_zeta_zero(n, "hybrid")
    
    return result if precise else round(result, 4)

# ===================== خدمات جديدة متقدمة =====================

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

def primes_between(n1, n2):
    """إرجاع جميع الأعداد الأولية بين n1 و n2"""
    primes = []
    for num in range(max(2, n1), n2 + 1):
        if is_prime_fast(num):
            primes.append(num)
    return primes

# ===================== متسلسلة تايلور ودوال متقدمة =====================

class TaylorSeries:
    """فئة لحساب متسلسلة تايلور للدوال المختلفة"""
    
    @staticmethod
    def exp(x, terms=20):
        """متسلسلة تايلور لـ e^x"""
        result = 0
        for n in range(terms):
            result += (x ** n) / math.factorial(n)
        return result
    
    @staticmethod
    def sin(x, terms=20):
        """متسلسلة تايلور لـ sin(x)"""
        result = 0
        for n in range(terms):
            term = ((-1) ** n) * (x ** (2 * n + 1)) / math.factorial(2 * n + 1)
            result += term
        return result
    
    @staticmethod
    def cos(x, terms=20):
        """متسلسلة تايلور لـ cos(x)"""
        result = 0
        for n in range(terms):
            term = ((-1) ** n) * (x ** (2 * n)) / math.factorial(2 * n)
            result += term
        return result
    
    @staticmethod
    def ln(x, terms=50):
        """متسلسلة تايلور لـ ln(1+x) للـ x بين -1 و 1"""
        if x <= -1 or x > 1:
            raise ValueError("x يجب أن يكون في المجال (-1, 1]")
        result = 0
        for n in range(1, terms + 1):
            term = ((-1) ** (n + 1)) * (x ** n) / n
            result += term
        return result
    
    @staticmethod
    def arctan(x, terms=50):
        """متسلسلة تايلور لـ arctan(x)"""
        result = 0
        for n in range(terms):
            term = ((-1) ** n) * (x ** (2 * n + 1)) / (2 * n + 1)
            result += term
        return result
    
    @staticmethod
    def sinh(x, terms=20):
        """متسلسلة تايلور لـ sinh(x)"""
        result = 0
        for n in range(terms):
            term = (x ** (2 * n + 1)) / math.factorial(2 * n + 1)
            result += term
        return result
    
    @staticmethod
    def cosh(x, terms=20):
        """متسلسلة تايلور لـ cosh(x)"""
        result = 0
        for n in range(terms):
            term = (x ** (2 * n)) / math.factorial(2 * n)
            result += term
        return result

def taylor_series_function(func_name, x, terms=20, center=0):
    """
    حساب قيمة دالة باستخدام متسلسلة تايلور
    """
    x_centered = x - center
    taylor = TaylorSeries()
    
    if func_name == 'exp':
        return taylor.exp(x_centered, terms)
    elif func_name == 'sin':
        return taylor.sin(x_centered, terms)
    elif func_name == 'cos':
        return taylor.cos(x_centered, terms)
    elif func_name == 'ln':
        return taylor.ln(x_centered, terms)
    elif func_name == 'arctan':
        return taylor.arctan(x_centered, terms)
    elif func_name == 'sinh':
        return taylor.sinh(x_centered, terms)
    elif func_name == 'cosh':
        return taylor.cosh(x_centered, terms)
    else:
        raise ValueError(f"الدالة {func_name} غير مدعومة")

def advanced_functions(func_name, x):
    """
    دوال متقدمة غير موجودة في مكتبة math القياسية
    """
    if func_name == 'erf':
        return erf_taylor(x)
    elif func_name == 'gamma':
        return gamma_approx(x)
    elif func_name == 'zeta':
        return zeta_approx(x)
    else:
        raise ValueError(f"الدالة المتقدمة {func_name} غير مدعومة")

def erf_taylor(x, terms=50):
    """دالة الخطأ باستخدام متسلسلة تايلور"""
    result = 0
    for n in range(terms):
        term = ((-1) ** n) * (x ** (2 * n + 1)) / (math.factorial(n) * (2 * n + 1))
        result += term
    return (2 / math.sqrt(math.pi)) * result

def gamma_approx(x, terms=30):
    """تقريب دالة غاما باستخدام متسلسلة"""
    if x <= 0:
        raise ValueError("x يجب أن يكون موجباً لدالة غاما")
    
    g = 7
    p = [
        0.99999999999980993, 676.5203681218851, -1259.1392167224028,
        771.32342877765313, -176.61502916214059, 12.507343278686905,
        -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7
    ]
    
    if x < 0.5:
        return math.pi / (math.sin(math.pi * x) * gamma_approx(1 - x))
    
    x -= 1
    a = p[0]
    for i in range(1, len(p)):
        a += p[i] / (x + i)
    
    t = x + g + 0.5
    return math.sqrt(2 * math.pi) * (t ** (x + 0.5)) * math.exp(-t) * a

def zeta_approx(s, terms=100):
    """تقريب دالة زيتا لريمان"""
    if s.real > 1:
        result = 0
        for n in range(1, terms + 1):
            result += 1 / (n ** s)
        return result
    else:
        return (2 ** s) * (math.pi ** (s - 1)) * math.sin(math.pi * s / 2) * math.gamma(1 - s) * zeta_approx(1 - s, terms)

# ===================== تحسينات سرعة التحليل =====================

@lru_cache(maxsize=10000)
def is_prime_fast(n: int) -> bool:
    """نسخة محسنة وسريعة من التحقق من الأعداد الأولية"""
    n = int(n)
    if n < 2: return False
    if n in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29): return True
    if n % 2 == 0: return False
    
    small_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    for p in small_primes:
        if n % p == 0:
            return n == p
    
    if GMPY2_AVAILABLE:
        try: return bool(gmpy2.is_prime(mpz(n)))
        except: pass
    if SYMPY_AVAILABLE:
        try: return bool(sympy.isprime(n))
        except: pass
    
    d, s = n - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    
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

def factorize_fast(n: int, timeout=None, verbose=True):
    """نسخة محسنة وسريعة للتحليل إلى عوامل أولية"""
    n = int(n)
    if n < 2:
        return []
    if is_prime_fast(n):
        return [n]
    
    factors = []
    start_time = time.time()
    
    while n % 2 == 0:
        factors.append(2)
        n //= 2
    
    small_primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    for p in small_primes:
        while n % p == 0:
            factors.append(p)
            n //= p
        if n == 1:
            return sorted(factors)
    
    if is_prime_fast(n):
        factors.append(n)
        return sorted(factors)
    
    if SYMPY_AVAILABLE:
        try:
            sympy_factors = sympy.factorint(n)
            for prime, exp in sympy_factors.items():
                factors.extend([int(prime)] * int(exp))
            return sorted(factors)
        except:
            pass
    
    def pollard_rho_optimized(m, timeout_time):
        if m % 2 == 0: return 2
        if m % 3 == 0: return 3
        
        x = random.randint(2, m-2)
        y = x
        c = random.randint(1, m-1)
        d = 1
        
        while d == 1:
            if timeout_time and time.time() > timeout_time:
                return None
            x = (x * x + c) % m
            y = (y * y + c) % m
            y = (y * y + c) % m
            d = math.gcd(abs(x - y), m)
            if d == m:
                break
        return d if 1 < d < m else None
    
    timeout_time = start_time + timeout if timeout else None
    remaining = n
    
    while remaining > 1 and not is_prime_fast(remaining):
        if timeout_time and time.time() > timeout_time:
            factors.append(remaining)
            break
        
        factor = pollard_rho_optimized(remaining, timeout_time)
        if factor is None:
            factors.append(remaining)
            break
        
        factors.extend(factorize_fast(factor, timeout, verbose))
        remaining //= factor
    
    if remaining > 1:
        factors.append(remaining)
    
    return sorted(factors)

# ===================== دوال مساعدة =====================

def logarithmic_integral(x):
    """تكامل لوغاريتمي دقيق - Li(x)"""
    if x <= 1:
        return 0
    result = EULER_GAMMA + math.log(abs(math.log(x)))
    term = 1
    k_factorial = 1
    for k in range(1, 100):
        k_factorial *= k
        term *= math.log(x)
        current_term = term / (k * k_factorial)
        if abs(current_term) < 1e-15:
            break
        result += current_term
    return result

def riemann_R(x):
    """دالة ريمان R"""
    if x < 1:
        return 0
    result = 0
    for k in range(1, 10):
        mu = mobius(k)
        if mu == 0:
            continue
        term = mu / k * logarithmic_integral(x**(1/k))
        if abs(term) < 1e-12:
            break
        result += term
    return result

def mobius(n):
    """دالة موبيوس μ(n)"""
    if n == 1:
        return 1
    factors = factorize_simple(n)
    if not factors:
        return 1
    if len(factors) != len(set(factors)):
        return 0
    return (-1) ** len(factors)

def factorize_simple(n):
    """تحليل بسيط للعوامل الأولية"""
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors

def prime_nth_estimate_advanced(n: int, use_riemann=False, method="cramer"):
    """تقدير محسن للعدد الأولي ذي المرتبة n"""
    n = int(n)
    
    if n <= 100:
        primes_100 = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
        if n <= len(primes_100):
            return primes_100[n-1]
    
    ln_n = math.log(n)
    ln_ln_n = math.log(ln_n)
    
    if method == "cramer":
        base = ln_n + ln_ln_n - 1.0 + (ln_ln_n - 2.0) / ln_n
        estimate = n * base
    elif method == "dusart":
        base = ln_n + ln_ln_n - 1.0 + (ln_ln_n - 2.0) / ln_n - (ln_ln_n**2 - 6 * ln_ln_n + 10.273) / (2 * ln_n**2)
        estimate = n * base
    elif method == "axler":
        if n > 100000:
            base = ln_n + ln_ln_n - 1.0 + (ln_ln_n - 2.0) / ln_n - (ln_ln_n**2 - 6 * ln_ln_n + 11.508) / (2 * ln_n**2)
        else:
            base = ln_n + ln_ln_n - 1.0 + (ln_ln_n - 2.1) / ln_n - (ln_ln_n**2 - 6.5 * ln_ln_n + 12.25) / (2 * ln_n**2)
        estimate = n * base
    else:
        base = ln_n + ln_ln_n - 1.0 + (ln_ln_n - 2.0) / ln_n
        estimate = n * base
    
    return int(round(estimate))

def zetazero(n:int, precise=True, method="auto"):
    """إرجاع الصفر غير التافه رقم n"""
    return zeta_zero_advanced(n, method=method, precise=precise)

def goldbach_verification(n, limit=10000):
    """التحقق من حدسية غولدباخ"""
    if n % 2 != 0 or n < 4:
        return False, []
    for i in range(2, min(n, limit)):
        if is_prime_fast(i) and is_prime_fast(n - i):
            return True, [i, n - i]
    return False, []

def is_semi_prime(n:int):
    """التحقق إذا كان العدد شبه أولي"""
    factors = factorize_fast(n, timeout=5, verbose=False)
    return len(factors) == 2

# ===================== واجهة Streamlit =====================

def main():
    # ترويسة التطبيق
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #A23B72;
        text-align: center;
        margin-bottom: 3rem;
    }
    .service-card {
        background-color: #F8F9FA;
        padding: 2rem;
        border-radius: 10px;
        border-left: 5px solid #2E86AB;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">🔢 PPFO v24.0</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">النسخة المحسنة مع خدمات جديدة وتحسينات السرعة</h2>', unsafe_allow_html=True)
    
    # معلومات النظام
    with st.expander("معلومات النظام", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**Sympy:** {'✅ متوفر' if SYMPY_AVAILABLE else '❌ غير متوفر'}")
        with col2:
            st.info(f"**GMPY2:** {'✅ متوفر' if GMPY2_AVAILABLE else '❌ غير متوفر'}")
        with col3:
            st.info("**الإصدار:** 24.0")
    
    # شريط جانبي للتنقل
    st.sidebar.title("🧭 التنقل")
    service = st.sidebar.selectbox(
        "اختر الخدمة:",
        [
            "التحليل إلى عوامل أولية",
            "أعداد ميرسين الأولية", 
            "حدسية غولدباخ",
            "الأعداد الأولية في نطاق",
            "متسلسلة تايلور",
            "الدوال المتقدمة",
            "تقدير الأعداد الأولية",
            "أصفار دالة زيتا"
        ]
    )
    
    # قسم التحليل إلى عوامل أولية
    if service == "التحليل إلى عوامل أولية":
        st.header("🔍 التحليل إلى عوامل أولية")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            number = st.number_input("أدخل العدد للتحليل:", min_value=2, value=100, step=1)
        with col2:
            timeout = st.number_input("المهلة (بالثواني):", min_value=1, value=30, step=1)
        
        if st.button("تحليل العدد", type="primary"):
            with st.spinner("جاري التحليل..."):
                start_time = time.time()
                factors = factorize_fast(number, timeout=timeout, verbose=False)
                end_time = time.time()
                
                if len(factors) == 1:
                    st.success(f"**{number} هو عدد أولي**")
                else:
                    cnt = Counter(factors)
                    parts_str = [f"{p}<sup>{cnt[p]}</sup>" if cnt[p] > 1 else f"{p}" for p in sorted(cnt)]
                    factorization = " × ".join(parts_str)
                    
                    st.success(f"**التحليل:** {number} = {factorization}")
                    st.info(f"**العوامل المفردة:** {factors}")
                
                st.metric("الوقت المستغرق", f"{end_time - start_time:.3f} ثانية")
    
    # قسم أعداد ميرسين الأولية
    elif service == "أعداد ميرسين الأولية":
        st.header("🔢 أعداد ميرسين الأولية")
        
        col1, col2 = st.columns(2)
        with col1:
            n1 = st.number_input("الحد الأدنى:", min_value=2, value=3, step=1)
        with col2:
            n2 = st.number_input("الحد الأعلى:", min_value=2, value=1000, step=1)
        
        if st.button("إيجاد أعداد ميرسين", type="primary"):
            with st.spinner("جاري البحث عن أعداد ميرسين الأولية..."):
                results = mersenne_primes_between(n1, n2)
                
                if results:
                    st.success(f"تم العثور على {len(results)} عدد ميرسين أولي")
                    for p, m in results:
                        st.write(f"**2^{p} - 1 = {m}**")
                else:
                    st.warning("لم يتم العثور على أعداد ميرسين أولية في هذا النطاق")
    
    # قسم حدسية غولدباخ
    elif service == "حدسية غولدباخ":
        st.header("💰 حدسية غولدباخ")
        
        col1, col2 = st.columns(2)
        with col1:
            n1 = st.number_input("الحد الأدنى (زوجي):", min_value=4, value=4, step=2)
        with col2:
            n2 = st.number_input("الحد الأعلى (زوجي):", min_value=4, value=100, step=2)
        
        if st.button("إيجاد أزواج غولدباخ", type="primary"):
            with st.spinner("جاري البحث عن أزواج غولدباخ..."):
                results = goldbach_pairs_between(n1, n2)
                
                if results:
                    st.success(f"تم العثور على {len(results)} عدد زوجي يمكن تحليله")
                    for n, primes in results[:20]:  # عرض أول 20 نتيجة فقط
                        st.write(f"**{n} = {primes[0]} + {primes[1]}**")
                    
                    if len(results) > 20:
                        st.info(f"عرض {20} من أصل {len(results)} نتيجة. استخدم نطاق أصفر لعرض جميع النتائج.")
                else:
                    st.warning("لم يتم العثور على أزواج غولدباخ في هذا النطاق")
    
    # قسم الأعداد الأولية في نطاق
    elif service == "الأعداد الأولية في نطاق":
        st.header("🔢 الأعداد الأولية في نطاق")
        
        col1, col2 = st.columns(2)
        with col1:
            n1 = st.number_input("الحد الأدنى:", min_value=2, value=1, step=1)
        with col2:
            n2 = st.number_input("الحد الأعلى:", min_value=2, value=100, step=1)
        
        if st.button("إيجاد الأعداد الأولية", type="primary"):
            with st.spinner("جاري البحث عن الأعداد الأولية..."):
                primes_list = primes_between(n1, n2)
                
                if primes_list:
                    st.success(f"تم العثور على {len(primes_list)} عدد أولي")
                    
                    # عرض الأعداد الأولية في أعمدة
                    cols = st.columns(5)
                    for i, prime in enumerate(primes_list):
                        with cols[i % 5]:
                            st.write(f"**{prime}**")
                else:
                    st.warning("لم يتم العثور على أعداد أولية في هذا النطاق")
    
    # قسم متسلسلة تايلور
    elif service == "متسلسلة تايلور":
        st.header("📈 متسلسلة تايلور")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            func_name = st.selectbox(
                "اختر الدالة:",
                ['exp', 'sin', 'cos', 'ln', 'arctan', 'sinh', 'cosh']
            )
        with col2:
            x = st.number_input("قيمة x:", value=1.0)
        with col3:
            terms = st.number_input("عدد الحدود:", min_value=1, value=20, step=1)
        
        if st.button("حساب متسلسلة تايلور", type="primary"):
            try:
                result = taylor_series_function(func_name, x, terms)
                
                st.success(f"**{func_name}({x}) ≈ {result:.10f}**")
                
                # مقارنة مع القيمة الحقيقية إذا كانت موجودة
                if hasattr(math, func_name):
                    exact = getattr(math, func_name)(x)
                    st.info(f"**القيمة الدقيقة:** {exact:.10f}")
                    st.info(f"**الفرق:** {abs(result - exact):.2e}")
                
            except Exception as e:
                st.error(f"خطأ: {e}")
    
    # قسم الدوال المتقدمة
    elif service == "الدوال المتقدمة":
        st.header("⚡ الدوال المتقدمة")
        
        col1, col2 = st.columns(2)
        with col1:
            func_name = st.selectbox(
                "اختر الدالة المتقدمة:",
                ['erf', 'gamma', 'zeta']
            )
        with col2:
            x = st.number_input("قيمة x:", value=1.0, key="advanced_x")
        
        if st.button("حساب الدالة المتقدمة", type="primary"):
            try:
                result = advanced_functions(func_name, x)
                st.success(f"**{func_name}({x}) ≈ {result:.10f}**")
            except Exception as e:
                st.error(f"خطأ: {e}")
    
    # قسم تقدير الأعداد الأولية
    elif service == "تقدير الأعداد الأولية":
        st.header("📊 تقدير الأعداد الأولية")
        
        n = st.number_input("المرتبة n:", min_value=1, value=100, step=1)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("تقدير كرامر", type="primary"):
                estimate = prime_nth_estimate_advanced(n, method="cramer")
                st.success(f"**p_{n} ≈ {estimate}**")
        
        with col2:
            if st.button("تقدير دوزار", type="primary"):
                estimate = prime_nth_estimate_advanced(n, method="dusart")
                st.success(f"**p_{n} ≈ {estimate}**")
        
        with col3:
            if st.button("تقدير أكسلر", type="primary"):
                estimate = prime_nth_estimate_advanced(n, method="axler")
                st.success(f"**p_{n} ≈ {estimate}**")
    
    # قسم أصفار دالة زيتا
    elif service == "أصفار دالة زيتا":
        st.header("𝛇 أصفار دالة زيتا غير التافهة")
        
        n = st.number_input("رقم الصفر n:", min_value=1, value=1, step=1)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("حساب الصفر", type="primary"):
                try:
                    zero = zetazero(n)
                    st.success(f"**الصفر غير التافه رقم {n} ≈ {zero:.10f}**")
                except Exception as e:
                    st.error(f"خطأ: {e}")
        
        with col2:
            if st.button("عرض معلومات", type="secondary"):
                st.info(f"**إجمالي الأصفار المعروفة:** {len(RIEMANN_ZEROS)}")
                st.info(f"**الصفر الأول:** {RIEMANN_ZEROS[0]}")
                st.info(f"**الصفر العاشر:** {RIEMANN_ZEROS[9]}")
    
    # معلومات إضافية في الشريط الجانبي
    st.sidebar.markdown("---")
    st.sidebar.header("ℹ️ معلومات")
    st.sidebar.info("""
    **PPFO v24.0** يحتوي على:
    - تحليل سريع للعوامل الأولية
    - أعداد ميرسين الأولية
    - حدسية غولدباخ
    - متسلسلة تايلور
    - دوال رياضية متقدمة
    - أصفار دالة زيتا
    """)
    
    st.sidebar.header("⚙️ الإعدادات")
    if st.sidebar.button("مسح الذاكرة المؤقتة"):
        is_prime_fast.cache_clear()
        cached_zeta_zero.cache_clear()
        st.sidebar.success("✓ تم مسح الذاكرة المؤقتة")

if __name__ == "__main__":
    main()
