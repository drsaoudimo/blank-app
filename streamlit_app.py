#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PPFO v18.1 — تطبيق الويب الرياضي الكامل لأصفار زيتا مع تحويل تلقائي عند الفشل
نسخة Streamlit التفاعلية المحسنة والمصححة
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
    .factor-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .method-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.8rem;
        font-weight: bold;
        margin: 0.1rem;
    }
    .riemann-badge { background-color: #e83e8c; color: white; }
    .ecm-badge { background-color: #20c997; color: white; }
    .small-badge { background-color: #6f42c1; color: white; }
    .hybrid-badge { background-color: #fd7e14; color: white; }
    .emergency-badge { background-color: #dc3545; color: white; }
    
    /* تخصيص Streamlit */
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
    .st-bb {
        background-color: transparent;
    }
    .st-at {
        background-color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# فحص المكتبات
try:
    import sympy
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    st.warning("⚠️ **ملاحظة:** sympy غير متوفر. سيتم استخدام خوارزميات أولية بديلة.")

try:
    import gmpy2
    GMPY2_AVAILABLE = True
    mpz = gmpy2.mpz
except ImportError:
    GMPY2_AVAILABLE = False
    mpz = int
    st.warning("⚠️ **ملاحظة:** gmpy2 غير متوفر. سيتم استخدام تطبيقات أولية.")

# ========== دوال رياضية أساسية ==========
@lru_cache(maxsize=1000)
def is_prime_fast(n):
    """اختبار أولية سريع - يستخدم gmpy2/sympy إذا متوفر"""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
        
    if GMPY2_AVAILABLE:
        return gmpy2.is_prime(n)
        
    if SYMPY_AVAILABLE:
        return sympy.isprime(n)
    
    # Miller-Rabin المحسن
    d, s = n-1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]:
        if a >= n:
            continue
        x = pow(a, d, n)
        if x in (1, n-1):
            continue
        for _ in range(s-1):
            x = pow(x, 2, n)
            if x == n-1:
                break
        else:
            return False
    return True

is_prime = is_prime_fast

def gcd(a, b):
    """حساب القاسم المشترك الأكبر مع تحسين للأعداد الكبيرة"""
    if GMPY2_AVAILABLE and hasattr(gmpy2, 'gcd'):
        return int(gmpy2.gcd(a, b))
    
    while b:
        a, b = b, a % b
    return a

def is_perfect_power(n):
    """التحقق إذا كان العدد قوة كاملة مع تحسين رياضي"""
    if n < 2:
        return False, None, None
    
    # التحقق من القوى الثنائية أولاً (أسرع)
    for k in range(2, int(math.log2(n)) + 2):
        root = int(round(n ** (1/k)))
        if root ** k == n:
            return True, root, k
        if (root + 1) ** k == n:
            return True, root + 1, k
        if (root - 1) ** k == n:
            return True, root - 1, k
    return False, None, None

# ========== الإطار الرياضي لأصفار زيتا ==========
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
    65.112544048081606391926278248523,
    67.079810529494173714478828896696,
    69.546401711173979252926857526674,
    72.067157674481907582522107969829,
    75.704690699083933168138139078727,
    77.144840068874805372682664861296
]

def estimate_factor_size_riemann(n):
    """تقدير حجم العوامل باستخدام نظرية ريمان-فون مانغولت"""
    bit_len = n.bit_length()
    if bit_len < 30:
        return bit_len // 2
    
    expected_bits = bit_len / 2
    correction = 0
    log_n = math.log(max(n, 2))
    weight_sum = 0
    
    for i, gamma in enumerate(RIEMANN_ZEROS[:5]):
        weight = 1 / math.sqrt(gamma)
        weight_sum += weight
        oscillation = math.cos(log_n * gamma + math.pi/4)
        correction += weight * oscillation
    
    if weight_sum > 0:
        correction /= weight_sum
    
    expected_bits *= (1 + 0.05 * correction)
    return max(20, min(bit_len-20, int(expected_bits)))

def seed_riemann_mathematical(n, zero_idx):
    """توليد بذور رياضية باستخدام أصفار زيتا"""
    if zero_idx >= len(RIEMANN_ZEROS):
        zero_idx = zero_idx % len(RIEMANN_ZEROS)
    
    gamma = RIEMANN_ZEROS[zero_idx]
    log_n = math.log(n + 1)
    
    real_part = math.cos(gamma * log_n)
    imag_part = math.sin(gamma * log_n)
    
    seed_val = int(abs(real_part + imag_part) * 1e9)
    seed_val ^= (zero_idx << 16) ^ (n % (1 << 24))
    
    return 2 + (seed_val % max(2, n-3))

def riemann_guided_pollard_rho(n, zero_idx=0, max_attempts=10):
    """خوارزمية بولارد رو موجهة بواسطة أصفار زيتا"""
    if n < 2:
        return None
    if n % 2 == 0:
        return 2
    if n % 3 == 0:
        return 3
    if is_prime(n):
        return n
    
    expected_bits = estimate_factor_size_riemann(n)
    expected_size = 2 ** expected_bits
    iter_limit = int(1.3 * math.sqrt(expected_size))
    iter_limit = min(500000, max(10000, iter_limit))
    
    optimal_c = 1
    if n % 2 == 1:
        for candidate in range(1, 10):
            if pow(candidate, (n-1)//2, n) != 1:
                optimal_c = candidate
                break
    
    best_factor = None
    best_probability = 0
    
    for attempt in range(max_attempts):
        current_zero_idx = (zero_idx + attempt) % len(RIEMANN_ZEROS)
        gamma = RIEMANN_ZEROS[current_zero_idx]
        
        seed_val = seed_riemann_mathematical(n, current_zero_idx)
        rng = random.Random(seed_val)
        
        x = rng.randrange(2, n-1)
        y = x
        c = optimal_c
        gamma_copy = gamma
        
        max_prob = 0
        
        for i in range(1, iter_limit + 1):
            alpha = 1.0 / math.sqrt(i) if i > 0 else 1.0
            
            try:
                log_val = math.log(n & 0xFFFFF + 2)
                perturb = int(alpha * math.cos(gamma_copy * log_val) * 10)
            except:
                perturb = 0
            
            x = (pow(x, 2, n) + c + perturb) % n
            y = (pow(y, 2, n) + c + perturb) % n
            y = (pow(y, 2, n) + c + perturb) % n
            
            d = gcd(abs(x-y), n)
            
            if d == n:
                break
            if d > 1:
                factor_bits = d.bit_length()
                prob = math.exp(-abs(factor_bits - expected_bits) / 15)
                
                if prob > max_prob:
                    max_prob = prob
                
                if prob > best_probability:
                    best_probability = prob
                    best_factor = d
                
                if prob > 0.85:
                    return d
            
            if i % 1000 == 0:
                gamma_copy += 0.01
        
        if best_probability > 0.6 and best_factor is not None:
            return best_factor
    
    return best_factor

# ========== التحسينات الرياضية المتقدمة ==========
def prime_sieve(limit):
    """غربال إراتوستينس الفعّال"""
    if limit < 2:
        return []
    sieve = bytearray(b'\x01') * (limit+1)
    sieve[:2] = b'\x00\x00'
    for i in range(2, int(limit**0.5)+1):
        if sieve[i]:
            sieve[i*i:limit+1:i] = b'\x00' * ((limit - i*i)//i + 1)
    return [i for i, is_prime in enumerate(sieve) if is_prime]

def elliptic_double(x, z, A, n):
    """ضعف نقطة على منحنى مونتغمري"""
    if z == 0:
        return x, z
    
    t1 = (x - z) % n
    t2 = (x + z) % n
    t1 = (t1 * t1) % n
    t2 = (t2 * t2) % n
    t3 = (t2 - t1) % n
    new_x = (t1 * t2) % n
    new_z = (t3 * ((A + 2) * t1 + A * t3)) % n
    return new_x, new_z

def elliptic_add(x1, z1, x2, z2, x0, z0, n):
    """جمع نقطتين على منحنى مونتغمري"""
    if z1 == 0:
        return x2, z2
    if z2 == 0:
        return x1, z1
    
    t1 = (x1 - z1) * (x2 + z2) % n
    t2 = (x1 + z1) * (x2 - z2) % n
    t3 = (t1 + t2) % n
    t4 = (t1 - t2) % n
    t5 = t3 * t3 % n
    t6 = t4 * t4 % n
    new_x = (x0 * t5) % n
    new_z = (z0 * t6) % n
    return new_x, new_z

def mathematically_optimized_ecm(n, curves=50):
    """ECM محسّن رياضياً باستخدام نظرية المنحنيات الإهليلجية"""
    if n % 2 == 0:
        return 2
    if n < 2:
        return None
    if is_prime_fast(n):
        return n
    
    bit_len = n.bit_length()
    if bit_len < 60:
        B1 = 1000
        B2 = 10000
    elif bit_len < 100:
        B1 = 5000
        B2 = 50000
    else:
        p_size_estimate = bit_len * 0.2
        B1 = int(2 ** (p_size_estimate * 0.25))
        B2 = B1 * 100
    
    for curve_index in range(curves):
        sigma = random.randrange(6, n-1)
        u = (sigma*sigma - 5) % n
        v = (4*sigma) % n
        u3 = pow(u, 3, n)
        
        try:
            inv_4u3 = pow(4*u3, n-2, n) if not GMPY2_AVAILABLE else int(gmpy2.invert(4*u3, n))
            A = ((u3 + v*v*(3*u + 1)) * inv_4u3 - 2) % n
        except Exception as e:
            continue
        
        Qx, Qz = u, v
        primes = prime_sieve(min(B1, 10000))
        
        for p in primes:
            if p > B1:
                break
                
            q = p
            while q <= B1 // p:
                q *= p
            
            for _ in range(q):
                Qx, Qz = elliptic_double(Qx, Qz, A, n)
                if Qz == 0:
                    break
        
        g = gcd(Qz, n)
        if 1 < g < n:
            return g
        
        # مرحلة 2 مبسطة
        if B2 > B1 and Qz != 0:
            Sx, Sz = elliptic_double(Qx, Qz, A, n)
            prime_differences = []
            current = B1 + 1
            while current <= B2 and len(prime_differences) < 500:
                if is_prime_fast(current):
                    prime_differences.append(current)
                current += 2
            
            T = 100
            for i in range(0, len(prime_differences), T):
                block = prime_differences[i:i+T]
                if not block:
                    continue
                
                Rx, Rz = Qx, Qz
                for prime in block:
                    Rx, Rz = elliptic_add(Rx, Rz, Qx, Qz, Sx, Sz, n)
                    if Rz == 0:
                        break
                
                if Rz != 0:
                    g = gcd(Rz, n)
                    if 1 < g < n:
                        return g
    
    return None

def enhanced_pollard_rho_brent(n, max_iter=None):
    """نسخة محسنة من Pollard Rho باستخدام خوارزمية Brent"""
    if n % 2 == 0:
        return 2
    if n % 3 == 0:
        return 3
    if n < 2:
        return None
    if is_prime_fast(n):
        return n
    
    if max_iter is None:
        bit_len = n.bit_length()
        max_iter = min(500000, max(10000, int(1.3 * math.sqrt(2 ** (bit_len // 3)))))
    
    optimal_c = 1
    if n % 2 == 1:
        for candidate in range(1, 10):
            if pow(candidate, (n-1)//2, n) != 1:
                optimal_c = candidate
                break
    
    def f(x, c):
        return (pow(x, 2, n) + c) % n
    
    y = random.randrange(2, n-1)
    c = optimal_c
    m = random.randrange(1, n-1)
    
    g, r, q = 1, 1, 1
    while g == 1 and r < max_iter:
        x = y
        for _ in range(r):
            y = f(y, c)
        
        k = 0
        while k < r and g == 1:
            ys = y
            for _ in range(min(m, r - k)):
                y = f(y, c)
                q = (q * abs(x - y)) % n
            g = gcd(q, n)
            k += m
        r *= 2
    
    if g == n:
        while True:
            ys = f(ys, c)
            g = gcd(abs(x - ys), n)
            if g > 1:
                break
    
    return g if 1 < g < n else None

def quadratic_sieve_enhanced(n, factor_base_size=None):
    """الغربال التربيعي المحسن مع قاعدة أولية مثلى"""
    if n < 2:
        return None
    if is_perfect_power(n)[0]:
        return is_perfect_power(n)[1]
    
    bit_len = n.bit_length()
    if factor_base_size is None:
        if bit_len < 60:
            factor_base_size = 100
        elif bit_len < 100:
            factor_base_size = 500
        else:
            factor_base_size = 2000
    
    factor_base = []
    p = 2
    while len(factor_base) < factor_base_size and p < 10000:
        if is_prime_fast(p) and pow(n, (p-1)//2, p) == 1:
            factor_base.append(p)
        p = p + 1 if p == 2 else p + 2
    
    smooth_relations = []
    x = math.isqrt(n) + 1
    max_relations = len(factor_base) + 10
    
    for _ in range(2 * max_relations):
        y = x*x - n
        if y > 0:
            factors = {}
            temp = y
            for p in factor_base:
                while temp % p == 0:
                    factors[p] = factors.get(p, 0) + 1
                    temp //= p
            
            if temp == 1:
                smooth_relations.append((x, y, factors))
                if len(smooth_relations) >= max_relations:
                    break
        x += 1
    
    if len(smooth_relations) < len(factor_base):
        return None
    
    for i in range(len(smooth_relations)):
        for j in range(i+1, len(smooth_relations)):
            x1, y1, f1 = smooth_relations[i]
            x2, y2, f2 = smooth_relations[j]
            
            combined_factors = {}
            for p, e in f1.items():
                combined_factors[p] = combined_factors.get(p, 0) + e
            for p, e in f2.items():
                combined_factors[p] = combined_factors.get(p, 0) + e
            
            if all(e % 2 == 0 for e in combined_factors.values()):
                x_product = (x1 * x2) % n
                y_product = 1
                for p, e in combined_factors.items():
                    y_product = (y_product * pow(p, e//2, n)) % n
                
                factor = gcd(abs(x_product - y_product), n)
                if 1 < factor < n:
                    return factor
    
    return None

def mathematically_optimized_p1(n, B1=None, B2=None):
    """Pollard's p-1 محسّن رياضياً"""
    if n % 2 == 0:
        return 2
    if n < 2:
        return None
    if is_prime_fast(n):
        return n
    
    bit_len = n.bit_length()
    if B1 is None:
        B1 = max(1000, int(2 ** (bit_len * 0.1)))
    if B2 is None:
        B2 = B1 * 100
    
    a = 2
    for p in prime_sieve(B1):
        e = int(math.log(B1) / math.log(p))
        a = pow(a, pow(p, e), n)
        g = gcd(a-1, n)
        if 1 < g < n:
            return g
    
    if B2 > B1:
        block_size = 1000
        for start in range(B1, B2, block_size):
            end = min(start + block_size, B2)
            block_primes = [p for p in prime_sieve(end) if p >= start]
            
            if not block_primes:
                continue
            
            product = 1
            for p in block_primes:
                product = (product * p) % n
            
            a = pow(a, product, n)
            g = gcd(a-1, n)
            if 1 < g < n:
                return g
    
    return None

# ========== إدارة الحالة للويب ==========
class SharedData:
    def __init__(self, N):
        self.lock = threading.Lock()
        self.N = N
        self.remainder = N
        self.factors = []
        self.methods = []
        self.stop_event = threading.Event()
        self.start_time = time.time()
        self.last_remainder = N
        self.stagnation_count = 0
        self.worker_stats = defaultdict(lambda: {"attempts": 0, "successes": 0})
        self.factorization_path = []
        self.mathematical_insights = []
        self.strategy_history = []
        self.progress_bar = None
        self.status_text = None

    def consume(self, factor, method):
        with self.lock:
            if self.remainder <= 1 or factor <= 1 or self.remainder % factor != 0:
                return False
                
            count = 0
            temp = self.remainder
            while temp % factor == 0:
                temp //= factor
                count += 1
            
            self.factors.append(factor)
            self.remainder = temp
            self.methods.append((factor, f"{method}(^{count})"))
            self.factorization_path.append((factor, method, count, temp))
            
            bit_len = factor.bit_length()
            self.mathematical_insights.append(f"عامل {bit_len} بت تم الحصول عليه بواسطة {method}")
            
            worker_match = re.search(r'(\w+)-(\d+)', method)
            if worker_match:
                worker_type, worker_id = worker_match.groups()
                self.worker_stats[f"{worker_type}-{worker_id}"]["successes"] += 1
            
            if self.remainder == 1:
                self.stop_event.set()
            return True

    def get_elapsed(self):
        return time.time() - self.start_time

    def detect_stagnation(self):
        with self.lock:
            if self.remainder == self.last_remainder:
                self.stagnation_count += 1
                return self.stagnation_count > 25
            else:
                self.stagnation_count = 0
                self.last_remainder = self.remainder
                return False

    def log_worker_attempt(self, worker_name):
        with self.lock:
            self.worker_stats[worker_name]["attempts"] += 1

    def record_strategy_switch(self, from_strategy, to_strategy, reason):
        """تسجيل تحويل الاستراتيجية"""
        entry = {
            "time": time.time() - self.start_time,
            "from": from_strategy,
            "to": to_strategy,
            "reason": reason,
            "current_remainder": self.remainder
        }
        self.strategy_history.append(entry)

    def get_progress(self):
        """حساب التقدم كنسبة مئوية"""
        if self.remainder == 1:
            return 100.0
        try:
            progress = 100 * (1 - math.log(self.remainder) / math.log(self.N))
            return max(0, min(100, progress))
        except:
            return 0.0

# ========== واجهة Streamlit المحسنة ==========
def main():
    st.markdown('<div class="main-header">🧮 PPFO v18.1 - الإطار الرياضي الكامل لأصفار زيتا</div>', unsafe_allow_html=True)
    
    # معلومات النظام
    with st.sidebar:
        st.header("⚙️ معلومات النظام")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**SymPy:** {'✅' if SYMPY_AVAILABLE else '❌'}")
            st.write(f"**GMPY2:** {'✅' if GMPY2_AVAILABLE else '❌'}")
        with col2:
            st.write(f"**أصفار زيتا:** {len(RIEMANN_ZEROS)}")
            st.write(f"**إصدار Streamlit:** 1.35.0")
        
        st.markdown("---")
        st.markdown("""
        **ℹ️ ملاحظة رياضية:**
        - لا توجد خوارزمية مثبتة تستخدم أصفار زيتا مباشرة لتحليل الأعداد
        - يتم استخدام الخصائص الطيفية لأصفار زيتا لتحسين معلمات الخوارزميات
        - النظام يتحول تلقائياً إلى استراتيجيات مثبتة عند فشل الطرق الموجهة
        """)
    
    # إدخال الرقم والإعدادات
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
            
            # تحليل أولي
            if N < 2:
                st.error("العدد يجب أن يكون أكبر من 1")
                return
            elif is_prime_fast(N):
                st.success("✅ العدد أولي")
            else:
                st.info("🔢 العدد مركب")
                
        except Exception as e:
            st.error(f"❌ خطأ في الإدخال: {e}")
            # استخدام رقم افتراضي
            N = 123456789012345678901234567890
            bit_length = N.bit_length()
    
    # إعدادات التحليل
    st.subheader("⚙️ إعدادات التحليل")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**الطرق المطلوبة:**")
        use_small = st.checkbox("العوامل الصغيرة", value=True, help="البحث عن عوامل أولية صغيرة (<200)")
        use_riemann = st.checkbox("Riemann-Pollard-Rho", value=True, help="الإطار الرياضي لأصفار زيتا")
        use_ecm = st.checkbox("المنحنيات الإهليلجية (ECM)", value=True, help="خوارزمية رياضية متقدمة للعوامل المتوسطة")
    
    with col2:
        st.write("**معلمات الأداء:**")
        use_hybrid = st.checkbox("عامل هجين", value=True, help="دمج عدة خوارزميات حسب حجم العدد")
        use_emergency = st.checkbox("وضع الطوارئ", value=True, help="تفعيل طرق بديلة عند الركود")
        max_threads = st.slider("عدد الخيوط", 1, 16, 8, help="عدد الخيوط المتوازية للتحليل")
    
    with col3:
        st.write("**خيارات إضافية:**")
        max_time = st.number_input("الوقت الأقصى (ثواني)", 0, 3600, 300, help="الوقت الأقصى للتشغيل")
        show_progress = st.checkbox("عرض التقدم التفصيلي", value=True)
        advanced_math = st.checkbox("عرض الرؤى الرياضية", value=True)
        save_results = st.checkbox("حفظ النتائج", value=False)
    
    # زر البدء
    if st.button("🚀 بدء التحليل", type="primary", use_container_width=True):
        if N < 2:
            st.error("❌ العدد يجب أن يكون أكبر من 1")
            return
        
        # إعدادات التحليل
        enabled_methods = {
            "small": use_small,
            "riemann": use_riemann, 
            "ecm": use_ecm,
            "hybrid": use_hybrid,
            "emergency": use_emergency
        }
        
        custom_settings = {
            "threads": max_threads,
            "verbose": show_progress,
            "max_time": max_time,
            "save_results": save_results
        }
        
        # بدء التحليل
        with st.spinner("جاري التحليل... قد تستغرق العملية بعض الوقت للأعداد الكبيرة"):
            shared = enhanced_factorize_with_preferences(N, enabled_methods, custom_settings)
        
        # عرض النتائج
        display_results(N, shared, advanced_math, save_results)

def enhanced_factorize_with_preferences(N, enabled_methods, custom_settings):
    """نسخة محسنة ومصححة من التحليل للاستخدام في الويب"""
    shared = SharedData(N)
    
    # إنشاء عناصر الواجهة
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    shared.progress_bar = progress_bar
    shared.status_text = status_text
    
    # محاكاة عملية التحليل مع تحديثات حية
    import time
    
    # عوامل أولية صغيرة للبدء
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 
                   53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 
                   109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 
                   173, 179, 181, 191, 193, 197, 199]
    
    start_time = time.time()
    max_time = custom_settings["max_time"]
    
    # تحديث الواجهة
    def update_display():
        progress = shared.get_progress()
        shared.progress_bar.progress(int(progress))
        
        elapsed = time.time() - start_time
        factors_found = len(shared.factors)
        remaining_bits = shared.remainder.bit_length() if shared.remainder > 1 else 0
        
        status_info = f"""
        **⏱️ الوقت المنقضي:** {elapsed:.1f} ثانية  
        **📊 التقدم:** {progress:.1f}%  
        **🔢 العوامل المكتشفة:** {factors_found}  
        **🔍 الباقي:** {remaining_bits} بت  
        """
        
        if shared.methods:
            unique_methods = set(m for _, m in shared.methods)
            status_info += f"**🔎 الطرق المستخدمة:** {', '.join(unique_methods)}"
        
        shared.status_text.markdown(status_info)
    
    # التحليل الحقيقي - التصحيح الأساسي هنا
    def factorize_number(n, method_name, method_func):
        """دالة مساعدة لتحليل عدد باستخدام طريقة محددة"""
        if n <= 1 or is_prime_fast(n):
            return n, None
        
        factor = method_func(n)
        if factor and 1 < factor < n:
            # التحقق من أن العامل يقبل القسمة
            if n % factor == 0:
                return factor, n // factor
        return None, None
    
    # التحليل بالعوامل الصغيرة أولاً
    if enabled_methods.get("small", True):
        current_n = shared.remainder
        for p in small_primes:
            if current_n % p == 0:
                count = 0
                while current_n % p == 0:
                    count += 1
                    current_n //= p
                shared.consume(p, "Small")
                update_display()
                
                if time.time() - start_time > max_time > 0:
                    shared.status_text.warning("⏰ انتهى الوقت المحدد")
                    return shared
    
    # استخدام خوارزميات متقدمة للباقي
    strategies = []
    if enabled_methods.get("riemann", True):
        strategies.append(("Riemann", riemann_guided_pollard_rho))
    if enabled_methods.get("ecm", True):
        strategies.append(("ECM", mathematically_optimized_ecm))
    if enabled_methods.get("hybrid", True):
        strategies.extend([
            ("Pollard-Rho", enhanced_pollard_rho_brent),
            ("p-1", mathematically_optimized_p1),
            ("QS", quadratic_sieve_enhanced)
        ])
    
    strategy_idx = 0
    attempts_without_progress = 0
    max_attempts_without_progress = 10
    
    current_remainder = shared.remainder
    
    while current_remainder > 1 and not shared.stop_event.is_set():
        if time.time() - start_time > max_time > 0:
            shared.status_text.warning("⏰ انتهى الوقت المحدد")
            break
        
        # إذا كان العدد أولي، أضفه كعامل نهائي
        if is_prime_fast(current_remainder):
            shared.consume(current_remainder, "Prime-Final")
            break
        
        # تجربة الاستراتيجية الحالية
        strategy_name, strategy_func = strategies[strategy_idx % len(strategies)]
        
        # استخدام الطريقة الحالية للتحليل
        factor, new_remainder = factorize_number(current_remainder, strategy_name, strategy_func)
        
        if factor is not None:
            # نجحنا في إيجاد عامل
            shared.consume(factor, strategy_name)
            current_remainder = shared.remainder  # تحديث من shared object
            attempts_without_progress = 0
            update_display()
        else:
            # فشل في إيجاد عامل
            attempts_without_progress += 1
            
            # تغيير الاستراتيجية إذا فشلت多次
            if attempts_without_progress >= max_attempts_without_progress:
                old_strategy = strategies[strategy_idx % len(strategies)][0]
                strategy_idx += 1
                new_strategy = strategies[strategy_idx % len(strategies)][0]
                shared.record_strategy_switch(
                    old_strategy,
                    new_strategy,
                    f"فشل {attempts_without_progress} محاولات متتالية"
                )
                attempts_without_progress = 0
        
        # تحديث الواجهة بشكل دوري
        update_display()
        
        # إضافة تأخير صغير لمنع الحمل الزائد
        time.sleep(0.1)
    
    # التحقق النهائي من أن الباقي أولي
    if shared.remainder > 1 and is_prime_fast(shared.remainder):
        shared.consume(shared.remainder, "Prime-Final")
    
    shared.progress_bar.progress(100)
    shared.status_text.success("✅ اكتمل التحليل")
    
    return shared

def display_results(N, shared, show_math=True, save_results=False):
    """عرض النتائج بطريقة تفاعلية ومحسنة"""
    
    st.markdown("---")
    st.subheader("📊 النتائج النهائية")
    
    # البطاقات العلوية
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        elapsed = shared.get_elapsed()
        st.metric("⏱️ الوقت الإجمالي", f"{elapsed:.3f} ثانية")
    
    with col2:
        total_factors = len(shared.factors)
        st.metric("🔢 عدد العوامل", total_factors)
    
    with col3:
        status = "✅ مكتمل" if shared.remainder == 1 else "⏳ غير مكتمل"
        st.metric("📈 الحالة", status)
    
    with col4:
        if shared.remainder > 1:
            remainder_bits = shared.remainder.bit_length()
            st.metric("🔍 الباقي", f"{remainder_bits} بت")
        else:
            st.metric("🎯 الدقة", "100%")
    
    # التحقق من صحة النتيجة - التصحيح الأساسي هنا
    factor_counts = Counter(shared.factors)
    product = 1
    for factor, count in factor_counts.items():
        product *= (factor ** count)
    
    if product == N:
        st.success("✅ التحليل صحيح - حاصل ضرب العوامل يساوي العدد الأصلي")
    else:
        st.error("❌ هناك خطأ في التحليل - حاصل الضرب لا يساوي العدد الأصلي")
        st.info(f"الفرق: {N - product}")
        
        # عرض تفاصيل الخطأ للمساعدة في التصحيح
        with st.expander("🔍 تفاصيل الخطأ"):
            st.write(f"**العدد الأصلي:** {N}")
            st.write(f"**حاصل الضرب:** {product}")
            st.write(f"**العوامل:** {dict(factor_counts)}")
    
    # عرض العوامل
    st.subheader("🧩 العوامل المكتشفة")
    
    if shared.factors:
        # حساب التكرارات بشكل صحيح
        factor_counts = Counter(shared.factors)
        factors_data = []
        
        for factor, count in factor_counts.items():
            # العثور على الطريقة المستخدمة لهذا العامل
            method = next((m for f, m in shared.methods if f == factor), "Unknown")
            factors_data.append({
                "العامل": factor,
                "الأساس": factor,
                "الأس": count,
                "الحجم (بت)": factor.bit_length(),
                "الطريقة": method,
                "النسبة (%)": (factor.bit_length() * count / N.bit_length()) * 100
            })
        
        factors_df = pd.DataFrame(factors_data)
        st.dataframe(factors_df, use_container_width=True)
        
        # مخططات العوامل
        col1, col2 = st.columns(2)
        
        with col1:
            if len(factors_df) > 0:
                fig = px.pie(factors_df, names='العامل', values='الأس', 
                            title='توزيع العوامل حسب التكرار')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if len(factors_df) > 0:
                fig = px.bar(factors_df, x='العامل', y='الحجم (بت)',
                            color='الطريقة', title='حجم العوامل بالبت')
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ لم يتم العثور على أي عوامل")
    
    # الرؤى الرياضية
    if show_math and shared.mathematical_insights:
        st.subheader("🧠 الرؤى الرياضية")
        insights_col1, insights_col2 = st.columns(2)
        
        with insights_col1:
            for i, insight in enumerate(shared.mathematical_insights[:len(shared.mathematical_insights)//2]):
                st.write(f"• {insight}")
        
        with insights_col2:
            for i, insight in enumerate(shared.mathematical_insights[len(shared.mathematical_insights)//2:]):
                st.write(f"• {insight}")
    
    # إحصائيات الأداء
    st.subheader("📈 إحصائيات الأداء")
    
    if shared.worker_stats:
        stats_data = []
        for worker, stats in shared.worker_stats.items():
            success_rate = (stats["successes"] / max(1, stats["attempts"])) * 100
            stats_data.append({
                "العامل": worker,
                "المحاولات": stats["attempts"],
                "النجاحات": stats["successes"],
                "معدل النجاح %": round(success_rate, 2)
            })
        
        stats_df = pd.DataFrame(stats_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.dataframe(stats_df, use_container_width=True)
        
        with col2:
            if len(stats_df) > 0:
                fig = px.bar(stats_df, x='العامل', y='معدل النجاح %',
                            title='كفاءة العمال (%)', color='معدل النجاح %')
                st.plotly_chart(fig, use_container_width=True)
    
    # تاريخ التحويلات
    if shared.strategy_history:
        st.subheader("🔄 تاريخ تحويل الاستراتيجيات")
        for i, entry in enumerate(shared.strategy_history):
            with st.expander(f"تحويل {i+1}: {entry['from']} → {entry['to']}"):
                st.write(f"**الوقت:** {entry['time']:.1f} ثانية")
                st.write(f"**السبب:** {entry['reason']}")
                st.write(f"**الباقي وقت التحويل:** {entry['current_remainder']}")
    
    # خيارات التصدير
    if save_results:
        st.subheader("💾 حفظ النتائج")
        
        # إنشاء تقرير
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report = f"""
        تقرير تحليل PPFO v18.1
        =====================
        التاريخ: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        العدد المدخل: {N}
        الحجم: {N.bit_length()} بت
        الوقت الإجمالي: {shared.get_elapsed():.3f} ثانية
        عدد العوامل: {len(shared.factors)}
        الحالة: {'مكتمل' if shared.remainder == 1 else 'غير مكتمل'}
        
        العوامل:
        {chr(10).join(f'- {factor}^{count}' for factor, count in Counter(shared.factors).items())}
        
        الرؤى الرياضية:
        {chr(10).join(f'- {insight}' for insight in shared.mathematical_insights)}
        """
        
        st.download_button(
            label="📥 تحميل التقرير",
            data=report,
            file_name=f"ppfo_analysis_{timestamp}.txt",
            mime="text/plain"
        )

# ========== التشغيل الرئيسي ==========
if __name__ == "__main__":
    main()
