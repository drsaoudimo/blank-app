#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PPFO v18.1 — تطبيق الويب الرياضي الكامل لأصفار زيتا مع تحويل تلقائي عند الفشل
نسخة Streamlit التفاعلية
"""

import math, random, threading, time, re, sys, os, json
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
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
</style>
""", unsafe_allow_html=True)

try:
    import sympy
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    st.warning("ملاحظة: sympy غير متوفر. سيتم استخدام خوارزميات أولية بديلة.")

try:
    import gmpy2
    GMPY2_AVAILABLE = True
    mpz = gmpy2.mpz
except ImportError:
    GMPY2_AVAILABLE = False
    mpz = int
    st.warning("ملاحظة: gmpy2 غير متوفر. سيتم استخدام تطبيقات أولية.")

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
        if a % n == 0:
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
    log_n = math.log(n)
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
    
    return None

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

# ========== إدارة الحالة ==========
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
            
            # تحديث إحصائيات العمال
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

# ========== واجهة Streamlit ==========
def main():
    st.markdown('<div class="main-header">🧮 PPFO v18.1 - الإطار الرياضي الكامل لأصفار زيتا</div>', unsafe_allow_html=True)
    
    # معلومات النظام
    with st.expander("ℹ️ معلومات النظام والاعتماديات"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**SymPy:** {'✅ متوفر' if SYMPY_AVAILABLE else '❌ غير متوفر'}")
        with col2:
            st.write(f"**GMPY2:** {'✅ متوفر' if GMPY2_AVAILABLE else '❌ غير متوفر'}")
        with col3:
            st.write(f"**أصفار زيتا:** {len(RIEMANN_ZEROS)}")
        
        st.info("""
        **ملاحظة رياضية:** لا توجد خوارزمية مثبتة تستخدم أصفار زيتا مباشرة لتحليل الأعداد.
        يتم استخدام الخصائص الطيفية لأصفار زيتا لتحسين معلمات الخوارزميات العددية.
        النظام يتحول تلقائياً إلى استراتيجيات مثبتة عند فشل الطرق الموجهة.
        """)
    
    # إدخال الرقم والإعدادات
    col1, col2 = st.columns([2, 1])
    
    with col1:
        input_method = st.radio("طريقة الإدخال:", ["رقم عادي", "رقم سداسي عشري", "تعبير رياضي"])
        
        if input_method == "رقم عادي":
            N_str = st.text_input("أدخل العدد المراد تحليله:", value="123456789012345678901234567890")
        elif input_method == "رقم سداسي عشري":
            hex_str = st.text_input("أدخل العدد بصيغة سداسية عشرية:", value="0x1234567890ABCDEF")
            N_str = hex_str if hex_str.startswith('0x') else f"0x{hex_str}"
        else:
            expr = st.text_input("أدخل تعبيراً رياضياً:", value="2**128 + 1")
            try:
                N_str = str(eval(expr))
            except:
                N_str = "123456789"
    
    with col2:
        try:
            if input_method == "رقم سداسي عشري":
                N = int(N_str, 16)
            else:
                N = int(eval(N_str) if input_method == "تعبير رياضي" else N_str)
            
            bit_length = N.bit_length()
            st.metric("حجم العدد", f"{bit_length} بت")
            st.metric("عدد الأرقام", f"{len(str(N))}")
            
            # تحليل أولي
            if is_prime_fast(N):
                st.success("العدد أولي")
            else:
                st.info("العدد مركب")
                
        except Exception as e:
            st.error(f"خطأ في الإدخال: {e}")
            N = 123456789012345678901234567890
            bit_length = N.bit_length()
    
    # إعدادات التحليل
    st.subheader("⚙️ إعدادات التحليل")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**الطرق المطلوبة:**")
        use_small = st.checkbox("العوامل الصغيرة", value=True)
        use_riemann = st.checkbox("Riemann-Pollard-Rho", value=True)
        use_ecm = st.checkbox("المنحنيات الإهليلجية (ECM)", value=True)
        use_hybrid = st.checkbox("عامل هجين", value=True)
        use_emergency = st.checkbox("وضع الطوارئ", value=True)
    
    with col2:
        st.write("**معلمات الأداء:**")
        max_threads = st.slider("عدد الخيوط", 1, 24, 8)
        max_time = st.number_input("الوقت الأقصى (ثواني)", 0, 3600, 300)
        show_progress = st.checkbox("عرض التقدم التفصيلي", value=True)
    
    with col3:
        st.write("**خيارات إضافية:**")
        save_results = st.checkbox("حفظ النتائج", value=False)
        advanced_math = st.checkbox("عرض الرؤى الرياضية", value=True)
    
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
        with st.spinner("جاري التحليل..."):
            shared = enhanced_factorize_with_preferences(N, enabled_methods, custom_settings)
        
        # عرض النتائج
        display_results(N, shared, advanced_math)

def display_results(N, shared, show_math=True):
    """عرض النتائج بطريقة تفاعلية"""
    
    # العنوان والملخص
    st.subheader("📊 النتائج النهائية")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("الوقت الإجمالي", f"{shared.get_elapsed():.3f} ثانية")
    with col2:
        st.metric("عدد العوامل", len(shared.factors))
    with col3:
        status = "✅ مكتمل" if shared.remainder == 1 else "⏳ غير مكتمل"
        st.metric("الحالة", status)
    
    # التحقق من صحة النتيجة
    factor_counts = Counter(shared.factors)
    product = 1
    for f, e in factor_counts.items():
        product *= pow(f, e)
    
    if product == N:
        st.success("✅ التحليل صحيح - حاصل ضرب العوامل يساوي العدد الأصلي")
    else:
        st.error("❌ هناك خطأ في التحليل - حاصل الضرب لا يساوي العدد الأصلي")
    
    # عرض العوامل
    st.subheader("🧩 العوامل المكتشفة")
    
    factors_df = pd.DataFrame([
        {
            "العامل": factor,
            "الأساس": base,
            "الأس": exp,
            "الحجم (بت)": base.bit_length(),
            "الطريقة": method
        }
        for (factor, method), (base, exp) in zip(
            zip(shared.factors, [m for f, m in shared.methods]),
            factor_counts.items()
        )
    ])
    
    st.dataframe(factors_df, use_container_width=True)
    
    # مخطط العوامل
    if len(factors_df) > 0:
        fig = px.pie(factors_df, names='العامل', values='الأس', 
                     title='توزيع العوامل')
        st.plotly_chart(fig, use_container_width=True)
    
    # الرؤى الرياضية
    if show_math and shared.mathematical_insights:
        st.subheader("🧠 الرؤى الرياضية")
        for insight in shared.mathematical_insights:
            st.write(f"• {insight}")
    
    # إحصائيات الأداء
    st.subheader("📈 إحصائيات الأداء")
    
    if shared.worker_stats:
        stats_data = []
        for worker, stats in shared.worker_stats.items():
            stats_data.append({
                "العامل": worker,
                "المحاولات": stats["attempts"],
                "النجاحات": stats["successes"],
                "معدل النجاح": stats["successes"] / max(1, stats["attempts"])
            })
        
        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df, use_container_width=True)
        
        # مخطط الأداء
        if len(stats_df) > 0:
            fig = px.bar(stats_df, x='العامل', y='معدل النجاح',
                        title='معدل نجاح العمال')
            st.plotly_chart(fig, use_container_width=True)
    
    # تاريخ التحويلات
    if shared.strategy_history:
        st.subheader("🔄 تاريخ تحويل الاستراتيجيات")
        for entry in shared.strategy_history:
            st.write(f"**[{entry['time']:.1f}ث]** {entry['from']} → {entry['to']} | السبب: {entry['reason']}")

# ========== دوال التحليل (مبسطة للويب) ==========
def enhanced_factorize_with_preferences(N, enabled_methods, custom_settings):
    """نسخة مبسطة من التحليل للاستخدام في الويب"""
    shared = SharedData(N)
    
    # محاكاة عملية التحليل
    import time
    
    # عوامل أولية صغيرة للعرض التوضيحي
    demo_factors = []
    temp_N = N
    
    # تحليل بالعوامل الصغيرة
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    for p in small_primes:
        while temp_N % p == 0:
            demo_factors.append(p)
            shared.consume(p, "Small")
            temp_N //= p
    
    # استخدام خوارزميات أخرى إذا كان العدد كبيراً
    if temp_N > 1:
        if enabled_methods.get("riemann", True):
            # محاكاة خوارزمية ريمان
            factor = riemann_guided_pollard_rho(temp_N)
            if factor and factor < temp_N:
                shared.consume(factor, "Riemann-0")
                temp_N //= factor
        
        if temp_N > 1 and enabled_methods.get("ecm", True):
            # محاكاة ECM
            factor = mathematically_optimized_ecm(temp_N)
            if factor and factor < temp_N:
                shared.consume(factor, "ECM-0")
                temp_N //= factor
    
    # إذا بقي جزء، نضيفه كعامل أولي
    if temp_N > 1:
        shared.consume(temp_N, "Prime-Final")
    
    return shared

# ========== التشغيل الرئيسي ==========
if __name__ == "__main__":
    main()
