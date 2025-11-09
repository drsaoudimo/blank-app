import streamlit as st
import time
from urllib.parse import urlparse

"""
## 📱 متصفح هاتفي محسّن لتجنب الشاشة السوداء

يتعامل هذا الإصدار مع مشاكل الشاشة السوداء ويقدم حلولاً عملية للمواقع غير المتوافقة.
"""

# CSS محسّن للتعامل مع الأخطاء
st.markdown("""
<style>
/* تصميم الهاتف المتجاوب */
.mobile-container {
    width: 100%;
    max-width: 414px;
    margin: 20px auto;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.mobile-browser {
    border-radius: 35px;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    background: #000;
    position: relative;
    width: 100%;
    aspect-ratio: 9/19;
    margin: 0 auto;
}

.status-bar {
    background: #000;
    color: white;
    padding: 8px 15px;
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    height: 25px;
}

.browser-chrome {
    height: calc(100% - 25px);
    background: white;
    display: flex;
    flex-direction: column;
}

.nav-bar {
    display: flex;
    padding: 8px 15px;
    background: #f8f8f8;
    border-bottom: 1px solid #ddd;
    gap: 10px;
}

.nav-btn {
    background: #e0e0e0;
    border: none;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s;
}

.nav-btn:active {
    transform: scale(0.9);
    background: #d0d0d0;
}

.url-display {
    flex: 1;
    background: white;
    border: 1px solid #ddd;
    border-radius: 20px;
    padding: 5px 12px;
    font-size: 12px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.browser-content {
    flex: 1;
    overflow: hidden;
    position: relative;
    background: #f5f5f5;
}

.browser-iframe {
    width: 100%;
    height: 100%;
    border: none;
    position: absolute;
    top: 0;
    left: 0;
    background: white;
    transition: opacity 0.3s;
}

/* أخطاء iframe */
.iframe-error {
    padding: 30px 20px;
    text-align: center;
    color: #666;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background: white;
    z-index: 10;
}

.iframe-error h3 {
    color: #dc3545;
    margin-bottom: 15px;
    font-size: 18px;
}

.error-icon {
    font-size: 48px;
    margin-bottom: 15px;
    color: #dc3545;
}

.external-link {
    display: inline-block;
    margin-top: 15px;
    padding: 8px 15px;
    background: #007bff;
    color: white;
    text-decoration: none;
    border-radius: 8px;
    font-size: 14px;
    transition: all 0.2s;
}

.external-link:hover {
    background: #0069d9;
    transform: translateY(-2px);
}

.alternative-view {
    background: #e9ecef;
    padding: 20px;
    border-radius: 10px;
    margin: 15px;
    text-align: center;
}

.alternative-view button {
    background: #28a745;
    color: white;
    border: none;
    padding: 8px 15px;
    border-radius: 5px;
    margin-top: 10px;
    cursor: pointer;
}

.loading-indicator {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    background: white;
    position: absolute;
    width: 100%;
    z-index: 5;
}

.spinner {
    border: 4px solid rgba(0, 0, 0, 0.1);
    border-radius: 50%;
    border-top: 4px solid #007bff;
    width: 30px;
    height: 30px;
    animation: spin 1s linear infinite;
    margin: 0 auto;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* المواقع السريعة */
.quick-tabs {
    display: flex;
    gap: 8px;
    overflow-x: auto;
    padding: 10px 0;
    margin: 15px 0;
}

.tab-btn {
    min-width: 80px;
    padding: 8px 12px;
    border-radius: 15px;
    background: #f0f0f0;
    border: 1px solid #ddd;
    text-align: center;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.2s;
}

.tab-btn:hover, .tab-btn.active {
    background: #007bff;
    color: white;
    border-color: #007bff;
}
</style>
""", unsafe_allow_html=True)

# تهيئة حالة الجلسة
if 'current_url' not in st.session_state:
    st.session_state.current_url = 'https://example.com'
if 'history' not in st.session_state:
    st.session_state.history = [{'url': 'https://example.com', 'title': 'صفحة البداية'}]
if 'back_enabled' not in st.session_state:
    st.session_state.back_enabled = False
if 'forward_enabled' not in st.session_state:
    st.session_state.forward_enabled = False
if 'frame_loaded' not in st.session_state:
    st.session_state.frame_loaded = True
if 'load_attempts' not in st.session_state:
    st.session_state.load_attempts = 0
if 'error_occurred' not in st.session_state:
    st.session_state.error_occurred = False

# المواقع الشائعة - مع إضافة مواقع تعمل بشكل أفضل في iframe
QUICK_SITES = [
    {"name": "جوجل", "url": "https://www.google.com", "icon": "🔍"},
    {"name": "ويكيبيديا", "url": "https://www.wikipedia.org", "icon": "📚"},
    {"name": "جيثب", "url": "https://github.com", "icon": "💻"},
    {"name": "موقع بديل", "url": "https://example.com", "icon": "⭐"},
    {"name": "موقع وثائق", "url": "https://httpbin.org/html", "icon": "📄"},
]

def navigate_to(url):
    """التنقل إلى رابط جديد وإضافة إلى التاريخ"""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # إعادة تعيين حالة التحميل
    st.session_state.frame_loaded = False
    st.session_state.error_occurred = False
    st.session_state.load_attempts = 0
    
    # إضافة إلى التاريخ
    st.session_state.history.append({'url': url, 'title': urlparse(url).netloc})
    st.session_state.current_url = url
    
    # تحديث حالة الأزرار
    st.session_state.back_enabled = len(st.session_state.history) > 1
    st.session_state.forward_enabled = False
    
    return url

def go_back():
    """العودة للصفحة السابقة"""
    if len(st.session_state.history) > 1:
        # حفظ الصفحة الحالية في ذاكرة مؤقتة للتنقل للأمام
        current_page = st.session_state.history.pop()
        if not hasattr(st.session_state, 'forward_stack'):
            st.session_state.forward_stack = []
        st.session_state.forward_stack.append(current_page)
        
        # تحديث الصفحة الحالية
        st.session_state.current_url = st.session_state.history[-1]['url']
        st.session_state.frame_loaded = False
        st.session_state.error_occurred = False
        st.session_state.load_attempts = 0
        st.session_state.back_enabled = len(st.session_state.history) > 1
        st.session_state.forward_enabled = True

def go_forward():
    """التقدم للصفحة التالية"""
    if hasattr(st.session_state, 'forward_stack') and st.session_state.forward_stack:
        next_page = st.session_state.forward_stack.pop()
        st.session_state.history.append(next_page)
        st.session_state.current_url = next_page['url']
        st.session_state.frame_loaded = False
        st.session_state.error_occurred = False
        st.session_state.load_attempts = 0
        st.session_state.back_enabled = True
        st.session_state.forward_enabled = len(st.session_state.forward_stack) > 0

def try_alternative_url():
    """تجربة رابط بديل عند فشل التحميل"""
    alternatives = [
        'https://example.com',
        'https://httpbin.org/html',
        'https://www.wikipedia.org'
    ]
    
    for alt_url in alternatives:
        try:
            # نحاول تحميل الرابط البديل
            st.session_state.current_url = alt_url
            st.session_state.frame_loaded = True
            st.session_state.error_occurred = False
            st.session_state.load_attempts = 0
            return True
        except:
            continue
    
    # إذا فشلت جميع المحاولات
    st.session_state.current_url = 'https://example.com'
    st.session_state.frame_loaded = True
    st.session_state.error_occurred = False
    return True

# العنوان الرئيسي
st.title("📱 متصفح هاتفي محسّن")

# رسالة تنبيه إذا كانت هناك مشكلة في الشاشة السوداء
if st.session_state.load_attempts >= 3 or st.session_state.error_occurred:
    st.warning("يبدو أن هناك مشكلة في تحميل الصفحة. نقترح استخدام المواقع البديلة التي تعمل بشكل أفضل داخل المتصفح.")

# المواقع السريعة
st.markdown('<div class="quick-tabs">', unsafe_allow_html=True)
cols = st.columns(len(QUICK_SITES))
for i, site in enumerate(QUICK_SITES):
    with cols[i]:
        if st.button(f"{site['icon']} {site['name']}", key=f"quick_{site['name']}"):
            navigate_to(site['url'])
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# شريط العناوين
col1, col2, col3 = st.columns([1, 4, 1])

with col1:
    st.button("←", key="back_btn", disabled=not st.session_state.back_enabled, 
             on_click=go_back, use_container_width=True)

with col2:
    url_input = st.text_input("العنوان:", value=st.session_state.current_url, 
                             label_visibility="collapsed")
    if url_input and url_input != st.session_state.current_url:
        navigate_to(url_input)
        st.rerun()

with col3:
    st.button("→", key="forward_btn", disabled=not st.session_state.forward_enabled, 
             on_click=go_forward, use_container_width=True)

# متصفح الهاتف المتجاوب
st.markdown('<div class="mobile-container">', unsafe_allow_html=True)
st.markdown('<div class="mobile-browser">', unsafe_allow_html=True)

# شريط الحالة
st.markdown(f"""
<div class="status-bar">
    <div>{time.strftime('%H:%M')}</div>
    <div>📶 📶 🔋</div>
</div>
""", unsafe_allow_html=True)

# شريط التنقل
current_url_display = st.session_state.current_url
if len(current_url_display) > 25:
    current_url_display = current_url_display[:25] + "..."

st.markdown(f"""
<div class="browser-chrome">
    <div class="nav-bar">
        <button class="nav-btn" onclick="goBack()">←</button>
        <button class="nav-btn" onclick="goForward()">→</button>
        <button class="nav-btn" onclick="reloadPage()">↻</button>
        <div class="url-display">{current_url_display}</div>
        <button class="nav-btn" onclick="homePage()">🏠</button>
    </div>
""", unsafe_allow_html=True)

# محتوى المتصفح مع معالجة الأخطاء
if not st.session_state.frame_loaded or st.session_state.load_attempts >= 3 or st.session_state.error_occurred:
    # عرض واجهة بديلة عند حدوث الأخطاء
    st.markdown(f"""
    <div class="browser-content">
        <div class="loading-indicator">
            <div class="spinner"></div>
        </div>
        <div id="error-message" class="iframe-error" style="display: block;">
            <div class="error-icon">🖥️</div>
            <h3>{"جارٍ التحميل..." if st.session_state.load_attempts < 3 else "تعذر تحميل الصفحة"}</h3>
            <p class="mobile-text">بعض المواقع لا تعمل بشكل صحيح داخل إطار المتصفح</p>
            <a href="{st.session_state.current_url}" target="_blank" class="external-link">فتح في نافذة جديدة</a>
            <div class="alternative-view">
                <p>جرب استخدام هذه المواقع التي تعمل بشكل أفضل:</p>
                <button onclick="useAlternative()">استخدام موقع بديل</button>
            </div>
        </div>
    </div>
    </div>
    </div>
    """, unsafe_allow_html=True)
else:
    # عرض iframe بشكل طبيعي
    st.markdown(f"""
    <div class="browser-content">
        <iframe 
            class="browser-iframe"
            src="{st.session_state.current_url}"
            sandbox="allow-same-origin allow-scripts allow-popups allow-forms allow-modals allow-top-navigation allow-downloads"
            allow="camera; microphone; geolocation; accelerometer; gyroscope; autoplay"
            scrolling="yes"
            id="phone-iframe"
            style="opacity: 1;">
        </iframe>
    </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

# JavaScript للتحكم في iframe ومعالجة الأخطاء
st.markdown("""
<script>
// وظائف التحكم في iframe
function goBack() {
    const iframe = document.getElementById('phone-iframe');
    try {
        iframe.contentWindow.history.back();
    } catch (e) {
        console.log("Cannot access iframe history:", e);
    }
}

function goForward() {
    const iframe = document.getElementById('phone-iframe');
    try {
        iframe.contentWindow.history.forward();
    } catch (e) {
        console.log("Cannot access iframe history:", e);
    }
}

function reloadPage() {
    const iframe = document.getElementById('phone-iframe');
    try {
        iframe.contentWindow.location.reload();
    } catch (e) {
        console.log("Cannot reload iframe:", e);
        // إعادة تعيين iframe بالكامل
        iframe.src = iframe.src;
    }
}

function homePage() {
    const iframe = document.getElementById('phone-iframe');
    iframe.src = 'https://example.com';
}

function useAlternative() {
    // استخدام موقع بديل يعمل بشكل أفضل
    const iframe = document.getElementById('phone-iframe');
    iframe.src = 'https://httpbin.org/html';
}

// الكشف عن تحميل iframe
const iframe = document.getElementById('phone-iframe');
const errorMessage = document.getElementById('error-message');

let loadAttempts = 0;
const maxAttempts = 3;

if (iframe) {
    iframe.onload = function() {
        loadAttempts = 0;
        console.log("Iframe loaded successfully");
        
        // إخفاء مؤشر التحميل
        const loadingIndicator = document.querySelector('.loading-indicator');
        if (loadingIndicator) {
            loadingIndicator.style.display = 'none';
        }
        
        // محاولة الوصول إلى محتوى iframe
        try {
            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
            
            // التحقق مما إذا كان iframe فارغًا
            if (!iframeDoc || !iframeDoc.body || iframeDoc.body.innerHTML.trim() === '') {
                throw new Error('Empty iframe content');
            }
            
            // التحقق من وجود أخطاء في الصفحة
            if (iframeDoc.title && (iframeDoc.title.includes('Error') || iframeDoc.title.includes('404') || iframeDoc.title.includes('Not Found'))) {
                throw new Error('Page load error');
            }
            
            // إخفاء رسالة الخطأ إذا تم التحميل بنجاح
            if (errorMessage) {
                errorMessage.style.display = 'none';
            }
            iframe.style.opacity = '1';
            
        } catch (e) {
            console.log("Iframe content access issue:", e);
            showErrorMessage();
        }
    };
    
    iframe.onerror = function() {
        console.log("Iframe load error");
        showErrorMessage();
    };
    
    function showErrorMessage() {
        loadAttempts++;
        
        if (loadAttempts >= maxAttempts) {
            const loadingIndicator = document.querySelector('.loading-indicator');
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }
            
            if (errorMessage) {
                errorMessage.style.display = 'flex';
            }
            iframe.style.opacity = '0';
        }
    }
}

// تحديث شريط العنوان عند تغيير iframe
setInterval(function() {
    try {
        const iframe = document.getElementById('phone-iframe');
        if (iframe) {
            const currentUrl = iframe.contentWindow.location.href;
            
            // تحديث شريط العنوان
            const urlDisplay = document.querySelector('.url-display');
            if (urlDisplay) {
                urlDisplay.textContent = currentUrl.length > 25 ? 
                    currentUrl.substring(0, 25) + '...' : currentUrl;
            }
        }
    } catch (e) {
        // خطأ في CORS، لا يمكن الوصول لمحتوى iframe
        console.log("CORS error:", e);
    }
}, 1000);

// إرسال رسالة إلى Streamlit عند حدوث خطأ
function reportErrorToStreamlit(message) {
    if (window.parent !== window) {
        window.parent.postMessage({
            type: 'iframe-error',
            message: message
        }, '*');
    }
}

// تحديد وقت الانتهاء
setTimeout(function() {
    if (loadAttempts < maxAttempts && iframe && iframe.style.opacity === '1') {
        // التحقق مما إذا كان iframe لا يزال فارغًا
        try {
            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
            if (iframeDoc && iframeDoc.body && iframeDoc.body.innerHTML.trim() === '') {
                showErrorMessage();
            }
        } catch (e) {
            showErrorMessage();
        }
    }
}, 10000);
</script>
""", unsafe_allow_html=True)

# لوحة التحكم
with st.sidebar:
    st.header("🔧 حلول مشاكل الشاشة السوداء")
    
    st.subheader("نصائح مهمة")
    st.markdown("""
    - ✅ استخدم المواقع التي تعمل بشكل أفضل مع iframe
    - ✅ تجنب المواقع التي تحظر العرض داخل إطارات
    - ✅ استخدم زر "فتح في نافذة جديدة" للمواقع المعقدة
    - ✅ جرب إعادة التحميل عدة مرات
    """)
    
    st.subheader("مواقع متوافقة")
    compatible_sites = [
        "https://example.com",
        "https://httpbin.org/html",
        "https://www.wikipedia.org",
        "https://icanhazip.com"
    ]
    
    for site in compatible_sites:
        if st.button(f"🌐 {site}", use_container_width=True):
            navigate_to(site)
            st.rerun()
    
    st.subheader("أدوات")
    if st.button("🔄 إعادة تحميل الصفحة"):
        st.session_state.frame_loaded = False
        st.session_state.error_occurred = False
        st.session_state.load_attempts = 0
        st.rerun()
    
    if st.button("🔧 إصلاح الأخطاء"):
        try_alternative_url()
        st.success("✓ تم تجربة موقع بديل")
        st.rerun()

# معلومات إضافية في تذييل الصفحة
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 10px;'>
    <p><strong>💡 نصائح لتجنب الشاشة السوداء:</strong></p>
    <p>• استخدم مواقع بسيطة مثل example.com أو httpbin.org</p>
    <p>• تجنب المواقع المعقدة مثل فيسبوك ويوتيوب</p>
    <p>• إذا استمرت المشكلة، استخدم رابط "فتح في نافذة جديدة"</p>
</div>
""", unsafe_allow_html=True)
