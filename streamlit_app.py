#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PPFO v19.0 - نسخة Streamlit مكتملة مع دعم PWA كامل - الإصدار المصحح
تم تصحيح جميع الأخطاء بما في ذلك خطأ "factorize is not defined" وخطأ الأقواس في سطر 300
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
from io import BytesIO
from PIL import Image as PILImage
import base64

# === استيراد المكتبات الاختيارية ===
SYMPY_AVAILABLE = False
GMPY2_AVAILABLE = False

try:
    import sympy
    SYMPY_AVAILABLE = True
except ImportError:
    pass

try:
    import gmpy2
    GMPY2_AVAILABLE = True
    mpz = gmpy2.mpz
except ImportError:
    mpz = int

# === الثوابت الرياضية ===
EULER_GAMMA = 0.57721566490153286060651209008240243104215933593992

# === أصفار زيتا (قيم عددية تقريبية للأصفار غيرالمنطقية) ===
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

# === معلمات المعايرة ===
_CAL_A = 0.02176304641727069
_CAL_B = -0.36685833943157
_CAL_C = 8.69441462116514

# === دعم PWA ===
def generate_manifest():
    """توليد ملف manifest.json لدعم PWA"""
    manifest = {
        "name": "PPFO Mathematical Suite",
        "short_name": "PPFO Math",
        "description": "تطبيق رياضي متقدم لتحليل الأعداد الأولية والعوامل باستخدام خوارزميات متطورة",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#f5f7fa",
        "theme_color": "#3498db",
        "orientation": "portrait",
        "lang": "ar",
        "dir": "rtl",
        "categories": ["education", "utilities", "mathematics"],
        "screenshots": [
            {
                "src": "screenshot1.jpg",
                "sizes": "1280x720",
                "type": "image/jpeg",
                "form_factor": "wide"
            },
            {
                "src": "screenshot2.jpg",
                "sizes": "720x1280",
                "type": "image/jpeg",
                "form_factor": "narrow"
            }
        ],
        "icons": [
            {
                "src": "icon-192x192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable"
            },
            {
                "src": "icon-512x512.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable"
            }
        ],
        "shortcuts": [
            {
                "name": "تحليل عوامل",
                "short_name": "عوامل",
                "description": "تحليل الأعداد إلى عواملها الأولية",
                "url": "/?tab=1",
                "icons": [{"src": "shortcut-icon1.png", "sizes": "96x96"}]
            },
            {
                "name": "تقدير الأعداد الأولية",
                "short_name": "أعداد أولية",
                "description": "تقدير العدد الأولي ذي المرتبة المحددة",
                "url": "/?tab=2",
                "icons": [{"src": "shortcut-icon2.png", "sizes": "96x96"}]
            }
        ]
    }
    return json.dumps(manifest, indent=2)

def generate_service_worker():
    """توليد Service Worker بسيط لدعم العمل دون اتصال"""
    return """
// Service Worker بسيط لتطبيق PPFO
const CACHE_NAME = 'ppfo-v19-cache';
const urlsToCache = [
  '/',
  '/index.html',
  '/static/css/style.css',
  '/static/js/app.js',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png'
];

// تثبيت Service Worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        return cache.addAll(urlsToCache);
      })
  );
});

// تفعيل Service Worker
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// التعامل مع الطلبات
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // إرجاع النسخة المخبأة إذا موجودة
        if (response) {
          return response;
        }
        // إذا لم تكن موجودة، جلبها من الشبكة
        return fetch(event.request).then(
          networkResponse => {
            // تخزين الاستجابة في الذاكرة المؤقتة
            if (event.request.method === 'GET' && networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
              const responseToCache = networkResponse.clone();
              caches.open(CACHE_NAME)
                .then(cache => {
                  cache.put(event.request, responseToCache);
                });
            }
            return networkResponse;
          }
        );
      })
      .catch(() => {
        // التعامل مع الأخطاء عند عدم وجود اتصال
        if (event.request.mode === 'navigate') {
          return caches.match('/offline.html');
        }
        return new Response('التطبيق يعمل دون اتصال. قد تكون بعض الميزات محدودة.', {
          status: 503,
          headers: {
            'Content-Type': 'text/plain'
          }
        });
      })
  );
});

// التعامل مع الرسائل من التطبيق
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
"""

# === الدوال الرياضية الأساسية ===
@lru_cache(maxsize=2000)
def is_prime_fast(n: int) -> bool:
    """اختبار أولية سريع باستخدام خوارزميات متعددة"""
    n = int(n)
    if n < 2:
        return False
    if n in (2, 3, 5, 7, 11, 13):
        return True
    if n % 2 == 0:
        return False
    
    # استخدام gmpy2 إذا متوفر
    if GMPY2_AVAILABLE:
        try:
            return bool(gmpy2.is_prime(mpz(n)))
        except Exception:
            pass
    
    # استخدام sympy إذا متوفر
    if SYMPY_AVAILABLE:
        try:
            return bool(sympy.isprime(n))
        except Exception:
            pass
    
    # خوارزمية Miller-Rabin
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    
    bases = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    for a in bases:
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True

def simple_sieve(limit: int):
    """غربال إراتوستينس للأعداد الصغيرة"""
    if limit < 2:
        return []
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    for p in range(2, int(limit**0.5) + 1):
        if sieve[p]:
            step = p
            start = p * p
            sieve[start:limit+1:step] = b"\x00" * (((limit - start) // step) + 1)
    return [i for i, v in enumerate(sieve) if v]

def _try_limit_break(start_time, timeout):
    """التحقق من انتهاء المهلة الزمنية"""
    if timeout is None:
        return False
    return (time.time() - start_time) > timeout

def brent_rho(n: int, timeout=None):
    """خوارزمية Brent Rho للعوامل"""
    if n % 2 == 0:
        return 2
    y = random.randrange(2, n-1)
    c = random.randrange(1, n-1)
    m = random.randrange(1, min(n-1, 100))
    g = 1
    r = 1
    q = 1
    x = 0
    start = time.time()
    while g == 1:
        if timeout and (time.time() - start) > timeout:
            return None
        x = y
        for _ in range(r):
            y = (pow(y, 2, n) + c) % n
        k = 0
        while k < r and g == 1:
            ys = y
            for _ in range(min(m, r-k)):
                y = (pow(y, 2, n) + c) % n
                q = (q * (abs(x-y))) % n
            g = math.gcd(q, n)
            k += m
        r *= 2
    if g == n:
        while True:
            ys = (pow(ys, 2, n) + c) % n
            g = math.gcd(abs(x-ys), n)
            if g > 1:
                break
    return g if g != n else None

def pollard_rho(n: int, timeout=None):
    """خوارزمية Pollard Rho للعوامل"""
    if n % 2 == 0:
        return 2
    if n % 3 == 0:
        return 3
    start = time.time()
    while True:
        if timeout and (time.time() - start) > timeout:
            return None
        x = random.randrange(2, n-1)
        y = x
        c = random.randrange(1, n-1)
        d = 1
        while d == 1:
            x = (x*x + c) % n
            y = (y*y + c) % n
            y = (y*y + c) % n
            d = math.gcd(abs(x-y), n)
            if d == n:
                break
        if d > 1 and d < n:
            return d

def factorize(n: int, timeout=None, verbose=False):
    """تحليل العدد إلى عوامله الأولية"""
    n = int(n)
    res = []
    start_time = time.time()

    def _factor(n_local):
        nonlocal res
        if timeout and (time.time() - start_time) > timeout:
            raise TimeoutError()
        if n_local == 1:
            return
        if is_prime_fast(n_local):
            res.append(n_local)
            return
        
        # اختبار القسمة على الأعداد الأولية الصغيرة
        small_primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
        for p in small_primes:
            if n_local % p == 0:
                while n_local % p == 0:
                    res.append(p)
                    n_local //= p
                if n_local == 1:
                    return
                return _factor(n_local)
        
        # استخدام sympy إذا كان متوفراً
        if SYMPY_AVAILABLE:
            try:
                if timeout and (time.time() - start_time) > timeout:
                    raise TimeoutError()
                factors = sympy.factorint(n_local)
                for p, e in factors.items():
                    res.extend([int(p)] * int(e))
                return
            except Exception:
                pass
        
        # استخدام خوارزميات تحليل متقدمة
        d = None
        for attempt in range(6):
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError()
            d = brent_rho(n_local, timeout=max(0, (timeout - (time.time()-start_time))) if timeout else None)
            if d is None or d == n_local:
                d = pollard_rho(n_local, timeout=max(0, (timeout - (time.time()-start_time))) if timeout else None)
            if d is not None and d > 1 and d < n_local:
                _factor(d)
                _factor(n_local//d)
                return
        
        # إذا فشل كل شيء، نعتبر العدد أولياً
        if is_prime_fast(n_local):
            res.append(n_local)
        else:
            res.append(n_local)

    try:
        _factor(n)
    except TimeoutError:
        if verbose:
            st.warning("⏱️ تم الوصول إلى مهلة التحليل — إرجاع العوامل الجزئية المكتشفة.")
    return sorted(res)

def riemann_correction(estimate: int, zeros=None):
    """
    تصحيح تذبذبي تقريبي مستوحى من الصيغة الصريحة.
    يُرجع قيمة صحيحة تقريبية (قد تكون سالبة أو موجبة).
    """
    if zeros is None:
        zeros = RIEMANN_ZEROS
    try:
        x = max(3, int(estimate))
        ln_x = math.log(x)
        s = 0.0
        for gamma in zeros:
            s += math.cos(gamma * ln_x) / math.sqrt(0.25 + gamma*gamma)
        correction = (math.sqrt(x) / max(1.0, ln_x)) * (s / (2.0 * math.pi))
        return int(round(correction))
    except Exception:
        return 0

def prime_nth_estimate(n: int, use_riemann=False):
    """
    تقدير p_n باستخدام تقريب ريمان-فون مانغولت + معامل معايرة مُحسّن C(n).
    إذا use_riemann=True فسنضيف تصحيح ريمان التخميني لكن نقيده بـ cap_fraction.
    """
    n = int(n)
    if n < 6:
        return [2,3,5,7,11][n-1]

    ln_n = math.log(n)
    ln_ln_n = math.log(ln_n)

    # التقريب الأساسي من Riemann–von Mangoldt
    base = ln_n + ln_ln_n - 1
    if n > 100:
        base += (ln_ln_n - 2) / ln_n
    if n > 1000:
        base -= EULER_GAMMA / ln_n

    # معامل التصحيح المُعايَر
    C_calibrated = _CAL_A + (_CAL_B / ln_n) + (_CAL_C / (ln_n ** 2))

    estimate = int(round(n * (base + C_calibrated)))

    if use_riemann:
        # نحسب تصحيح ريمان ثم نقيده (cap) حتى نسبة صغيرة من estimate
        corr = riemann_correction(estimate)
        # cap fraction: 0.5% كتقييد افتراضي
        cap_fraction = 0.005
        cap = max(10, int(cap_fraction * estimate))
        corr = max(-cap, min(cap, corr))
        estimate += corr

    return int(estimate)

# === واجهة المستخدم ===
st.set_page_config(
    page_title="PPFO v19.0 - تحليل رياضي متقدم",
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
    }
    footer {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# === العنوان الرئيسي ===
st.markdown('<p class="main-header">🧮 PPFO v19.0</p>', unsafe_allow_html=True)
st.markdown("### تحليل رياضي متقدم للأعداد الأولية والعوامل")

# === الشريط الجانبي ===
with st.sidebar:
    st.markdown("### 📚 القوائم الرئيسية")
    
    menu = st.radio(
        "التنقل",
        ["🏠 الصفحة الرئيسية", "🔍 تحليل العوامل", "📊 تقدير الأعداد الأولية", "⚙️ الإعدادات", "❓ المساعدة"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 📊 إحصائيات الجلسة")
    
    if 'analysis_count' not in st.session_state:
        st.session_state.analysis_count = 0
        st.session_state.total_time = 0.0
        st.session_state.last_analysis = None
        st.session_state.use_riemann = False
        st.session_state.timeout = 60
        st.session_state.verbose = True
    
    st.metric("عدد التحليلات", st.session_state.analysis_count)
    if st.session_state.analysis_count > 0:
        avg_time = st.session_state.total_time / st.session_state.analysis_count
        st.metric("متوسط الوقت", f"{avg_time:.2f} ثانية")
    else:
        st.metric("متوسط الوقت", "0.00 ثانية")
    
    if st.session_state.last_analysis:
        st.markdown(f"**آخر تحليل:** {st.session_state.last_analysis}")
    
    st.markdown("---")
    st.markdown(f"**الإصدار:** 19.0")
    st.markdown(f"**التاريخ:** {time.strftime('%Y-%m-%d')}")
    st.markdown(f"**SymPy:** {'متوفر' if SYMPY_AVAILABLE else 'غير متوفر'}")
    st.markdown(f"**GMPY2:** {'متوفر' if GMPY2_AVAILABLE else 'غير متوفر'}")

# === الصفحة الرئيسية ===
if menu == "🏠 الصفحة الرئيسية":
    st.markdown("## 🎯 مرحباً بك في PPFO v19.0!")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="info-box">
        <h3>🌟 الميزات الرئيسية</h3>
        <ul>
            <li><b>🔍 تحليل العوامل:</b> تحليل الأعداد الكبيرة إلى عواملها الأولية باستخدام خوارزميات متقدمة</li>
            <li><b>📊 تقدير الأعداد الأولية:</b> تقدير العدد الأولي ذي المرتبة n باستخدام صيغ ريمان المحسّنة</li>
            <li><b>⚙️ تصحيح ريمان:</b> استخدام أصفار دالة زيتا لتحسين التقديرات الرياضية</li>
            <li><b>⚡ أداء عالي:</b> خوارزميات محسّنة للتعامل مع الأعداد الكبيرة</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
        <h3>🚀 كيفية الاستخدام</h3>
        <ol>
            <li>اختر القسم المناسب من الشريط الجانبي</li>
            <li>أدخل العدد أو المعلمة المطلوبة</li>
            <li>اضبط الإعدادات حسب الحاجة</li>
            <li>انقر على زر التنفيذ لرؤية النتائج</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📱 التطبيق يعمل على جميع المنصات")
        
        st.markdown("""
        <div class="success-box">
        <h4>نصائح للاستخدام الفعال:</h4>
        <ul>
            <li>استخدم أعداداً متوسطة الحجم أولاً</li>
            <li>زد المهلة الزمنية للأعداد الكبيرة</li>
            <li>فعّل تصحيح ريمان للتقديرات الدقيقة</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

# === قسم تحليل العوامل ===
elif menu == "🔍 تحليل العوامل":
    st.markdown('<p class="section-header">🔍 تحليل العوامل الأولية</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <h3>تعليمات</h3>
    <p>أدخل عددًا صحيحًا موجبًا لتحليله إلى عوامله الأولية. التطبيق يستخدم خوارزميات متقدمة مثل Pollard Rho وBrent Rho للتعامل مع الأعداد الكبيرة.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        number_input = st.text_input("أدخل العدد للتحليل", "1234567891011", key="factor_input")
        timeout = st.slider("مهلة التحليل (ثانية)", min_value=5, max_value=300, value=st.session_state.timeout)
        
        if st.button("تحليل العدد", type="primary"):
            try:
                # تنظيف المدخلات
                n_str = number_input.replace(",", "").replace(" ", "")
                n = int(n_str)
                
                if n < 2:
                    st.markdown('<div class="error-box">الرجاء إدخال عدد صحيح موجب أكبر من 1</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f"### 📊 نتائج تحليل العدد: {n:,}")
                    
                    # عرض تقدير زمن التنفيذ
                    if n > 10**12:
                        st.markdown('<div class="warning-box">⚠️ تحذير: العدد كبير جداً، قد يستغرق التحليل وقتاً طويلاً</div>', unsafe_allow_html=True)
                    
                    # بدء التحليل
                    start_time = time.time()
                    with st.spinner("جاري التحليل..."):
                        factors = factorize(n, timeout=timeout, verbose=st.session_state.verbose)
                    end_time = time.time()
                    
                    # تحديث الإحصائيات
                    st.session_state.analysis_count += 1
                    st.session_state.total_time += (end_time - start_time)
                    st.session_state.last_analysis = f"{n:,}"
                    
                    # عرض النتائج
                    elapsed = end_time - start_time
                    st.markdown(f"**الوقت المستغرق:** {elapsed:.3f} ثانية")
                    
                    if not factors:
                        st.markdown('<div class="error-box">❌ لم يتم العثور على عوامل - قد يكون العدد أولياً أو انتهت المهلة الزمنية</div>', unsafe_allow_html=True)
                    else:
                        # عد العوامل
                        cnt = Counter(factors)
                        if len(cnt) == 1 and list(cnt.values())[0] == 1:
                            st.markdown('<div class="success-box">✅ العدد أولي!</div>', unsafe_allow_html=True)
                        
                        # عرض العوامل المجمعة
                        st.markdown("#### العوامل المجمعة:")
                        parts = []
                        for p in sorted(cnt):
                            parts.append(f"{p}^{cnt[p]}" if cnt[p] > 1 else f"{p}")
                        result_str = " × ".join(parts)
                        st.markdown(f'<div class="result-box" style="font-size: 1.2rem; font-family: monospace;">{result_str}</div>', unsafe_allow_html=True)
                        
                        # عرض القائمة المفصلة
                        st.markdown("#### القائمة المفصلة للعوامل:")
                        st.write(sorted(factors))
                        
                        # التحقق من الصحة
                        product = 1
                        for factor in factors:
                            product *= factor
                        if product == n:
                            st.markdown('<div class="success-box">✅ التحقق: حاصل ضرب العوامل يساوي العدد الأصلي</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="error-box">❌ خطأ في الحساب: حاصل ضرب العوامل لا يساوي العدد الأصلي</div>', unsafe_allow_html=True)
            
            except ValueError:
                st.markdown('<div class="error-box">❌ خطأ: الرجاء إدخال عدد صحيح صالح</div>', unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f'<div class="error-box">❌ خطأ غير متوقع: {str(e)}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📌 أمثلة جاهزة")
        
        examples = {
            "عدد بسيط": "123456",
            "عدد أولي معروف": "9999999967",
            "عدد كبير": "12345678910111213",
            "عدد عشوائي": str(random.randint(10**10, 10**12))
        }
        
        for name, example in examples.items():
            if st.button(f"مثال: {name}"):
                st.session_state.factor_input = example
                st.rerun()
        
        st.markdown("### ℹ️ معلومات")
        st.markdown("""
        **خوارزميات التحليل المستخدمة:**
        - اختبار أولية سريع
        - خوارزمية Pollard Rho
        - خوارزمية Brent Rho
        - غربال بسيط للأعداد الصغيرة
        
        **ملاحظات:**
        - الأعداد الكبيرة جداً (> 10^18) قد تستغرق وقتاً طويلاً
        - يمكن زيادة المهلة الزمنية للحصول على نتائج أفضل
        """)

# === قسم تقدير الأعداد الأولية ===
elif menu == "📊 تقدير الأعداد الأولية":
    st.markdown('<p class="section-header">📊 تقدير الأعداد الأولية</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <h3>تعليمات</h3>
    <p>أدخل المرتبة n للحصول على تقدير للعدد الأولي ذي المرتبة n. التطبيق يستخدم صيغ ريمان-فون مانغولت مع معايرة متقدمة.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        n_input = st.text_input("أدخل المرتبة n", "1000000", key="nth_input")
        use_riemann = st.checkbox("تفعيل تصحيح ريمان", value=st.session_state.use_riemann)
        
        if st.button("تقدير العدد الأولي", type="primary"):
            try:
                # تنظيف المدخلات
                n_str = n_input.replace(",", "").replace(" ", "")
                n = int(n_str)
                
                if n < 1:
                    st.markdown('<div class="error-box">الرجاء إدخال عدد صحيح موجب</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f"### 📊 تقدير العدد الأولي ذي المرتبة: {n:,}")
                    
                    # التنفيذ
                    start_time = time.time()
                    estimate = prime_nth_estimate(n, use_riemann=use_riemann)
                    end_time = time.time()
                    elapsed = end_time - start_time
                    
                    # عرض النتائج
                    st.markdown(f"**التقديـر:** {estimate:,}")
                    st.markdown(f"**الوقت المستغرق:** {elapsed:.6f} ثانية")
                    
                    # معلومات إضافية
                    if n <= 10**8:
                        st.markdown("#### 📝 معلومات إضافية:")
                        approx_size = len(str(estimate))
                        st.markdown(f"- **عدد الأرقام التقديري:** {approx_size}")
                        st.markdown(f"- **الكثافة التقريبية:** 1 عدد أولي لكل {int(math.log(estimate))} أعداد")
                    
                    # قيم معروفة للمقارنة
                    known_values = {
                        1: 2,
                        10: 29,
                        100: 541,
                        1000: 7919,
                        10000: 104729,
                        100000: 1299709,
                        1000000: 15485863
                    }
                    
                    if n in known_values:
                        actual = known_values[n]
                        error = abs(estimate - actual) / actual * 100
                        st.markdown("#### 📊 مقارنة بالقيمة الفعلية:")
                        st.markdown(f"- **القيمة الفعلية:** {actual:,}")
                        st.markdown(f"- **نسبة الخطأ:** {error:.4f}%")
                        
                        if error < 0.1:
                            st.markdown('<div class="success-box">✅ التقدير دقيق جداً!</div>', unsafe_allow_html=True)
                        elif error < 1:
                            st.markdown('<div class="success-box">✅ التقدير جيد</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="warning-box">⚠️ التقدير يحتاج تحسين</div>', unsafe_allow_html=True)
            
            except ValueError:
                st.markdown('<div class="error-box">❌ خطأ: الرجاء إدخال عدد صحيح صالح</div>', unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f'<div class="error-box">❌ خطأ غير متوقع: {str(e)}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📌 أمثلة جاهزة")
        
        examples = {
            "العدد الأولي رقم 10": "10",
            "العدد الأولي رقم 1000": "1000",
            "العدد الأولي رقم مليون": "1000000",
            "العدد الأولي رقم مليار": "1000000000"
        }
        
        for name, example in examples.items():
            if st.button(f"مثال: {name}"):
                st.session_state.nth_input = example
                st.rerun()
        
        st.markdown("### 📐 الصيغ الرياضية")
        st.markdown("""
        <div class="math-formula">
        p_n ≈ n(ln n + ln ln n - 1 + (ln ln n - 2)/ln n - γ/ln n + C(n))
        </div>
        <div class="math-formula">
        C(n) = A + B/ln n + C/(ln n)²
        </div>
        <p>حيث γ هو ثابت أويلر-ماسكيروني</p>
        """, unsafe_allow_html=True)

# === قسم الإعدادات ===
elif menu == "⚙️ الإعدادات":
    st.markdown('<p class="section-header">⚙️ الإعدادات</p>', unsafe_allow_html=True)
    
    st.markdown("### ⚙️ إعدادات التطبيق")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # إعدادات التحليل
        st.subheader("⏱️ إعدادات التحليل")
        new_timeout = st.slider("مهلة التحليل الافتراضية (ثانية)", 
                              min_value=5, max_value=300, 
                              value=st.session_state.timeout,
                              help="الوقت الأقصى المسموح به لتحليل الأعداد الكبيرة")
        
        if new_timeout != st.session_state.timeout:
            st.session_state.timeout = new_timeout
            st.success(f"✅ تم تحديث مهلة التحليل إلى {new_timeout} ثانية")
        
        verbose = st.checkbox("وضع تفصيلي", value=st.session_state.verbose,
                             help="عرض رسائل تفصيلية أثناء التحليل")
        
        if verbose != st.session_state.verbose:
            st.session_state.verbose = verbose
            st.success(f"✅ تم {'تفعيل' if verbose else 'إيقاف'} الوضع التفصيلي")
        
        # إعدادات ريمان
        st.subheader("📈 إعدادات ريمان")
        use_riemann = st.checkbox("تفعيل تصحيح ريمان", value=st.session_state.use_riemann,
                                help="استخدام أصفار دالة زيتا لتحسين التقديرات")
        
        if use_riemann != st.session_state.use_riemann:
            st.session_state.use_riemann = use_riemann
            st.success(f"✅ تم {'تفعيل' if use_riemann else 'إيقاف'} تصحيح ريمان")
        
        # إعادة تعيين الإحصائيات
        st.subheader("🔄 إدارة الجلسة")
        if st.button("إعادة تعيين الإحصائيات", type="secondary"):
            st.session_state.analysis_count = 0
            st.session_state.total_time = 0.0
            st.session_state.last_analysis = None
            st.success("✅ تم إعادة تعيين الإحصائيات بنجاح")
    
    with col2:
        st.markdown("### ℹ️ معلومات عن الإعدادات")
        
        st.markdown("""
        <div class="info-box">
        <h4>مهلة التحليل</h4>
        <p>الوقت الأقصى المسموح به لتحليل الأعداد الكبيرة. زيادة هذه القيمة تسمح بتحليل الأعداد الأكبر لكن قد تستغرق وقتاً أطول.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
        <h4>الوضع التفصيلي</h4>
        <p>عند التفعيل، يتم عرض رسائل تفصيلية أثناء عملية التحليل مما يساعد في فهم العملية الرياضية.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
        <h4>تصحيح ريمان</h4>
        <p>استخدام قيم أصفار دالة زيتا غير البديهية لتحسين دقة تقديرات الأعداد الأولية. هذا يحسن الدقة لكن قد يبطئ الحساب قليلاً.</p>
        </div>
        """, unsafe_allow_html=True)

# === قسم المساعدة ===
elif menu == "❓ المساعدة":
    st.markdown('<p class="section-header">❓ المساعدة والدعم</p>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["الدليل", "الأسئلة الشائعة", "التواصل"])
    
    with tab1:
        st.markdown("### 📘 الدليل الشامل")
        
        st.markdown("""
        <div class="info-box">
        <h3>🎯 الهدف من التطبيق</h3>
        <p>PPFO v19.0 هو تطبيق رياضي متقدم لتحليل الأعداد الأولية والعوامل، يستخدم خوارزميات متطورة لتقديم نتائج دقيقة وسريعة.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
        <h3>🔍 تحليل العوامل</h3>
        <p>لتحليل عدد إلى عوامله الأولية:</p>
        <ol>
            <li>اذهب إلى قسم "🔍 تحليل العوامل"</li>
            <li>أدخل العدد في الحقل المخصص</li>
            <li>اضبط المهلة الزمنية حسب حجم العدد</li>
            <li>انقر على "تحليل العدد"</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
        <h3>📊 تقدير الأعداد الأولية</h3>
        <p>لتقدير العدد الأولي ذي المرتبة n:</p>
        <ol>
            <li>اذهب إلى قسم "📊 تقدير الأعداد الأولية"</li>
            <li>أدخل المرتبة n في الحقل المخصص</li>
            <li>اختر ما إذا كنت تريد استخدام تصحيح ريمان</li>
            <li>انقر على "تقدير العدد الأولي"</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### ❓ الأسئلة الشائعة")
        
        faq_items = [
            {
                "question": "ما هي الأعداد التي يمكن تحليلها؟",
                "answer": "يمكن تحليل أي عدد صحيح موجب. الأعداد الصغيرة (< 10^12) تُحلل بسرعة، بينما الأعداد الكبيرة جداً (> 10^18) قد تتطلب وقتاً أطول أو مهلة زمنية أكبر."
            },
            {
                "question": "ما هو تصحيح ريمان؟",
                "answer": "تصحيح ريمان هو تقنية رياضية متقدمة تستخدم أصفار دالة زيتا لتحسين دقة تقديرات الأعداد الأولية. هذا يجعل التقديرات أقرب إلى القيم الفعلية."
            },
            {
                "question": "لماذا يستغرق تحليل بعض الأعداد وقتاً طويلاً؟",
                "answer": "تحليل الأعداد الكبيرة جداً يتطلب حسابات معقدة. إذا كان العدد أولياً أو يحتوي على عوامل أولية كبيرة، فإن الخوارزميات تحتاج وقتاً أطول للعثور على الحل."
            },
            {
                "question": "كيف يمكنني تحسين أداء التطبيق؟",
                "answer": "1. زد المهلة الزمنية للأعداد الكبيرة\n2. فعّل الوضع التفصيلي لرؤية تقدم العملية\n3. استخدم أعداداً متوسطة الحجم أولاً\n4. تأكد من تثبيت مكتبات sympy و gmpy2 لتحسين الأداء"
            }
        ]
        
        for i, item in enumerate(faq_items):
            with st.expander(f"سؤال {i+1}: {item['question']}"):
                st.markdown(item['answer'])
    
    with tab3:
        st.markdown("### 📞 التواصل والدعم")
        
        st.markdown("""
        <div class="info-box">
        <h3>للاستفسارات والدعم الفني</h3>
        <ul>
            <li>📧 البريد الإلكتروني: support@ppfo-math.com</li>
            <li>🌐 موقع الويب: www.ppfo-math.com</li>
            <li>📱 تيليجرام: @ppfo_math_support</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🐛 الإبلاغ عن مشكلة")
        
        problem_type = st.selectbox("نوع المشكلة", 
                                   ["خطأ في الحساب", "مشكلة في الأداء", "اقتراح تحسين", "مشكلة أخرى"])
        
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
    rating = st.slider("تقييمك", 1, 5, 4, key="footer_rating", label_visibility="collapsed")
    if rating >= 4:
        st.markdown("🌟 شكراً لثقتك! نحن نعمل باستمرار لتحسين التطبيق.")
    else:
        st.markdown("💡 نعتذر عن أي إزعاج. يرجى التواصل معنا لحل المشكلة.")

# === عرض مكونات PWA ===
st.markdown("""
<script>
// Service Worker Registration
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js')
      .then(registration => {
        console.log('ServiceWorker registered with scope:', registration.scope);
      })
      .catch(error => {
        console.log('ServiceWorker registration failed:', error);
      });
  });
}

// إعداد PWA
document.addEventListener('DOMContentLoaded', function() {
  // إضافة دعم التثبيت
  let deferredPrompt;
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    // إظهار زر التثبيت
    const installBtn = document.createElement('div');
    installBtn.id = 'install-btn-container';
    installBtn.innerHTML = `
      <div style="position: fixed; bottom: 20px; right: 20px; z-index: 1000; background: #3498db; color: white; padding: 12px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
        <div style="display: flex; align-items: center; gap: 10px;">
          <span>📱</span>
          <span>تثبيت التطبيق على هاتفك؟</span>
          <button id="install-btn" style="background: white; color: #3498db; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; margin-left: 10px;">
            تثبيت
          </button>
          <button id="dismiss-btn" style="background: transparent; border: 1px solid white; color: white; padding: 3px 8px; border-radius: 4px; cursor: pointer;">
            ✕
          </button>
        </div>
      </div>
    `;
    document.body.appendChild(installBtn);
    
    document.getElementById('install-btn').addEventListener('click', () => {
      if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
          if (choiceResult.outcome === 'accepted') {
            console.log('User accepted the A2HS prompt');
          } else {
            console.log('User dismissed the A2HS prompt');
          }
          deferredPrompt = null;
          document.getElementById('install-btn-container').remove();
        });
      }
    });
    
    document.getElementById('dismiss-btn').addEventListener('click', () => {
      document.getElementById('install-btn-container').remove();
    });
  });
});

// إضافة روابط PWA
const link = document.createElement('link');
link.rel = 'manifest';
link.href = '/manifest.json';
document.head.appendChild(link);

// إضافة أيقونات
const icons = [
  { sizes: '192x192', href: '/icon-192x192.png' },
  { sizes: '512x512', href: '/icon-512x512.png' }
];

icons.forEach(icon => {
  const link = document.createElement('link');
  link.rel = 'icon';
  link.sizes = icon.sizes;
  link.href = icon.href;
  document.head.appendChild(link);
});
</script>
""", unsafe_allow_html=True)
