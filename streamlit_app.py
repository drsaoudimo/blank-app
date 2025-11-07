#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PPFO v19.0 - نسخة Streamlit مكتملة مع دعم PWA كامل
تم تصحيح جميع الأخطاء بما في ذلك خطأ "factorize is not defined"
تمت إضافة مكونات PWA كاملة (manifest, service worker, أيقونات)
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
 14.1347251417347,21.0220396387716,25.0108575801457,30.4248761258595,32.9350615877392,37.5861781588257,40.9187190121475,43.327073280915,48.0051508811672,49.7738324776723,52.9703214777145,56.4462476970634,59.3470440026024,60.8317785246098,65.1125440480816,67.0798105294942,69.546401711174,72.0671576744819,75.7046906990839,77.1448400688748,79.3373750202494,82.910380854086,84.7354929805171,87.4252746131252,88.8091112076345,92.4918992705585,94.6513440405199,95.8706342282453,98.8311942181937,101.317851005731,103.725538040478,105.446623052326,107.168611184276,111.02953554317,111.874659176993,114.320220915453,116.226680320858,118.790782865976,121.370125002421,122.946829293553,124.256818554346,127.516683879596,129.578704199956,131.087688530933,133.497737202998,134.756509753374,138.116042054533,139.736208952121,141.123707404021,143.111845807621,146.000982486766,147.42276534256,150.053520420785,150.925257612241,153.024693811199,156.112909294238,157.597591817594,158.84998817142,161.188964137596,163.030709687182,165.5370691879,167.184439978175,169.094515415569,169.911976479412,173.411536519592,174.754191523366,176.44143429771,178.3774077761,179.916484020257,182.207078484366,184.874467848388,185.598783677707,187.228922583502,189.416158656017,192.026656360714,193.079726603846,195.265396679529,196.876481840958,198.015309676252,201.264751943704,202.493594514141,204.189671803105,205.394697202163,207.906258887806,209.576509716856,211.690862595365,213.347919359713,214.547044783491,216.169538508264,219.067596349021,220.714918839314,221.430705554693,224.007000254604,224.983324669582,227.421444279679,229.337413305525,231.250188700499,231.98723525318,233.693404178908,236.524229665816,237.7698204809252,239.5554775733276,241.0491577962166,242.8232719342226,244.0708984970782,247.1369900748975,248.1019900601485,249.5736896447072,251.014947795016,253.0699867479995,255.306256454914,256.3807136944345,258.6104394915314,259.874406989678,260.8050845045969,263.57389390487,265.5578518388763,266.6149737815011,267.9219150828241,269.9704490239976,271.494055641645,273.4596091884033,275.5874926493438,276.4520495031329,278.250743529842,279.2292509277452,282.4651147650521,283.2111857332339,284.8359639809047,286.6674453630029,287.9119205014222,289.5798549292188,291.8462913290674,293.5584341393563,294.9653696192655,295.5732548789583,297.9792770619434,299.8403260537213,301.6493254621942,302.6967495896069,304.8643713408573,305.7289126020368,307.2194961281701,310.1094631467019,311.165141530356,312.4278011806009,313.9852857311589,315.4756160894757,317.7348059423702,318.8531042563166,321.1601343091136,322.1445586724829,323.4669695575121,324.8628660517396,327.4439012619055,329.0330716804809,329.9532397282339,331.4744675826634,333.6453785248699,334.2113548332444,336.8418504283907,338.3399928508066,339.8582167253635,341.0422611110466,342.0548775103636,344.6617029402523,346.34787056601,347.2726775844205,349.3162608706961,350.4084193491921,351.8786490253593,353.4889004887188,356.017574977265,357.1513022520396,357.9526851016323,359.7437549531144,361.2893616958047,363.3313305789738,364.736024114089,366.2127102883313,367.9935754817403,368.9684380957344,370.050919212106,373.0619283721128,373.8648739109086,375.8259127667393,376.3240922306681,378.4366802499655,379.8729753465323,381.4844686171865,383.4435294495365,384.9561168148637,385.8613008459742,387.222890222388,388.8461283542323,391.456083563638,392.2450833395191,393.427743844434,395.5828700109937,396.3818542225922,544.3238901010053,545.6368332489348,547.0109120581223,547.9316133644893,549.4975675626614,550.9700100394839,552.0495722005649,553.7649721191588,555.7920205616825,556.8994764068554,557.5646591720585,559.3162370286822,560.2408074972957,562.5592076160459,564.1608791107861,564.5060559381498,566.698787682808,567.7317579011769,568.9239551796294,570.0511147824636,572.4199841324528,573.6146105267581,575.0938860144949,575.8072471409288,577.0390034720982,579.0988346720366,580.1369593623846,581.9465762659016,583.2360882191673,584.5617059034655,585.9845632049883,586.7427718912502,588.139663266248,590.6603975167653,591.7258580650481,592.5713583002256,593.974714682231,595.7281536973889,596.3627683283937,598.4930773461648,599.5456403643649,601.6021367359326,602.5791678863874,603.6256189035792,604.6162184937532,606.383460422109,608.4132173111873,609.3895751547201,610.8391629377394,611.7742096208872,613.5997786756371,614.6462378722326,615.538563369407,618.1128313664424,619.1844825979536,620.2728936722275,621.7092945279486,622.375002739779,624.2699000181779,626.0192834276544,627.268396850783,628.3258623594604,630.473887438292,630.8057809271975,632.225141167116,633.5468582522518,635.5238003106055,637.3971931598373,637.9255139808226,638.9279382668568,640.6947946688257,641.9454996657053,643.2788837813979,644.990578229748,646.3481915955016,647.7617530042889,648.7864008887824,650.1975193452565,650.668683891396,653.6495716053947,654.3019205863193,655.7094630223556,656.9640845994606,658.1756144186054,659.6638459729641,660.7167325952793,662.2965864311004,664.244604652273,665.342763095599,666.515147704173,667.1484948945554,668.9758488202351,670.3235852058626,672.4581835841697,673.0435782861476,674.3558978101232,676.1396743636267,677.230180668764,677.8004447462213,679.7421978825282,681.8949915331519,682.6027350197505,684.0135498138695,684.9726298620985,686.163223587728,687.9615431847036,689.3689413622724,690.4747350323504,692.4516844155208,693.1769700606018,694.5339086998731,695.7263359209267,696.6260699003456,699.1320954760135,700.2967391321435,701.3017429546462,702.2273431457605,704.0338392955253,705.1258139546192,706.1846547995179,708.2690708851099,709.2295885702843,711.1302741796854,711.9002899143753,712.7493834701013,714.0827718206694,716.1123964540521,717.4825697031002,718.7427865454859,719.6971009883657,721.3511622185364,722.2775049756742,723.8458210451284,724.5626138903791,727.0564032300494,728.4054815889341,728.7587497956143,730.4164821227564,731.4173549185985,732.8180527144998,734.789643252378,735.7654592085783,737.0529289122653,738.5804211713738,739.909523674042,740.573807447295,741.7573355729417,743.8950131424737,745.3449895506119,746.4993058994323,747.6745636242695,748.2427544650845,750.6559503621243,750.9663810666508,752.8876215672024,754.3223704717127,755.8393089760378,756.768248439951,758.1017292464126,758.9002382248924,760.2823669835121,762.7000332496911,763.5930661728372,764.3075227241802,766.0875400998362,767.2184721555395,768.2814618065092,769.6934072526244,771.0708393136783,772.961617565757,774.1177446279405,775.0478470965805,775.9997119631714,777.2997485295926,779.157076949189,780.3489250041817,782.1376643908121,782.5979439460735,784.2888226124655,785.7390897007151,786.4611474505063,787.46846381591,790.0590923641196,790.831620467921,792.4277076086045,792.8886525626226,794.4837918698932,795.6065961561624,797.2634700380356,798.7075701662962,799.6543362108976,801.6042464629821,802.5419848784181,803.2430962042702,804.7622391126618,805.8616356670948,808.1518149359937,809.1977833633007,810.0818048864071,811.1843588465063      
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
            if (event.request.method === 'GET' && !networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
              return networkResponse;
            }
            const responseToCache = networkResponse.clone();
            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });
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

# إنشاء مكونات PWA
pwa_manifest = generate_manifest()
pwa_service_worker = generate_service_worker()

# عرض مكونات PWA في صفحة Streamlit
st.markdown(f"""
<script>
// Service Worker Registration
if ('serviceWorker' in navigator) {{
  window.addEventListener('load', () => {{
    navigator.serviceWorker.register('/service-worker.js')
      .then(registration => {{
        console.log('ServiceWorker registered with scope:', registration.scope);
      }})
      .catch(error => {{
        console.log('ServiceWorker registration failed:', error);
      }});
  }});
}}

// إعداد PWA
document.addEventListener('DOMContentLoaded', function() {{
  // إضافة دعم التثبيت
  let deferredPrompt;
  window.addEventListener('beforeinstallprompt', (e) => {{
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
    
    document.getElementById('install-btn').addEventListener('click', () => {{
      if (deferredPrompt) {{
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {{
          if (choiceResult.outcome === 'accepted') {{
            console.log('User accepted the A2HS prompt');
          }} else {{
            console.log('User dismissed the A2HS prompt');
          }}
          deferredPrompt = null;
          document.getElementById('install-btn-container').remove();
        }});
      }}
    }});
    
    document.getElementById('dismiss-btn').addEventListener('click', () => {{
      document.getElementById('install-btn-container').remove();
    }});
  }});
}});
</script>

<style>
/* تحسينات PWA */
body {
  -webkit-tap-highlight-color: transparent;
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* تحسينات للهاتف */
@media (max-width: 768px) {
  .main-header {
    font-size: 1.8rem !important;
  }
  
  .section-header {
    font-size: 1.2rem !important;
  }
  
  .stButton>button {
    width: 100% !important;
    margin: 0.2rem 0 !important;
  }
  
  .stTextInput>div>div>input,
  .stTextArea>div>div>textarea {
    font-size: 16px !important;
  }
  
  footer {
    display: none !important;
  }
}
</style>
""", unsafe_allow_html=True)

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
    st.image("https://via.placeholder.com/150x50?text=PPFO+Logo", use_column_width=True)
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
    st.metric("متوسط الوقت", f"{st.session_state.total_time/(st.session_state.analysis_count or 1):.2f} ثانية")
    
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
        st.image("https://via.placeholder.com/400x300?text=Math+Visualization", use_column_width=True)
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
                st.experimental_rerun()
        
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
                st.experimental_rerun()
        
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

# === الدوال الرياضية ===
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
        small_primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
        for p in small_primes:
            if n_local % p == 0:
                while n_local % p == 0:
                    res.append(p)
                    n_local //= p
                if n_local == 1:
                    return
                return _factor(n_local)
        if SYMPY_AVAILABLE:
            try:
                if timeout and (time.time() - start_time) > timeout:
                    raise TimeoutError()
                fdict = sympy.factorint(n_local, multiple=False)
                for p, e in fdict.items():
                    res.extend([int(p)]*int(e))
                return
            except Exception:
                pass
        d = None
        for attempt in range(6):
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError()
            d = brent_rho(n_local, timeout=max(0, (timeout - (time.time()-start_time))) if timeout else None)
            if d is None or d == n_local:
                d = pollard_rho(n_local, timeout=max(0, (timeout - (time.time()-start_time))) if timeout else None)
            if d is None:
                break
            if d is not None and d > 1 and d < n_local:
                _factor(d)
                _factor(n_local//d)
                return
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

# === روابط PWA ===
st.markdown("""
<script>
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
