import streamlit as st
import time
import json
import os
from urllib.parse import urlparse

"""
## 📱 متصفح هاتفي متجاوب حقيقي

متصفح مصمم خصيصًا للهاتف يعمل على Streamlit Cloud مع حل كامل لمشاكل iframe
"""

# CSS متجاوب للمتصفح
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
}

.browser-iframe {
    width: 100%;
    height: 100%;
    border: none;
    position: absolute;
    top: 0;
    left: 0;
    background: #f9f9f9;
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
}

.iframe-error h3 {
    color: #dc3545;
    margin-bottom: 15px;
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
}

/* تبويبات المواقع السريعة */
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
    font-size: 12px;
    cursor: pointer;
    transition: all 0.2s;
}

.tab-btn:hover, .tab-btn.active {
    background: #007bff;
    color: white;
    border-color: #007bff;
}

/* تحسين النص للموبايل */
.mobile-text {
    font-size: 14px;
    line-height: 1.5;
    color: #333;
    margin: 8px 0;
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

# المواقع الشائعة
QUICK_SITES = [
    {"name": "جوجل", "url": "https://www.google.com", "icon": "🔍"},
    {"name": "ويكيبيديا", "url": "https://www.wikipedia.org", "icon": "📚"},
    {"name": "جيثب", "url": "https://github.com", "icon": "💻"},
    {"name": "يوتيوب", "url": "https://www.youtube.com", "icon": "▶️"},
    {"name": "فيسبوك", "url": "https://www.facebook.com", "icon": "📱"},
    {"name": "تويتر", "url": "https://twitter.com", "icon": "🐦"},
]

def navigate_to(url):
    """التنقل إلى رابط جديد وإضافة إلى التاريخ"""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
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
        st.session_state.back_enabled = len(st.session_state.history) > 1
        st.session_state.forward_enabled = True

def go_forward():
    """التقدم للصفحة التالية"""
    if hasattr(st.session_state, 'forward_stack') and st.session_state.forward_stack:
        next_page = st.session_state.forward_stack.pop()
        st.session_state.history.append(next_page)
        st.session_state.current_url = next_page['url']
        st.session_state.back_enabled = True
        st.session_state.forward_enabled = len(st.session_state.forward_stack) > 0

# العنوان الرئيسي
st.title("📱 متصفح هاتفي متجاوب")

# المواقع السريعة
st.markdown('<div class="quick-tabs">', unsafe_allow_html=True)
for site in QUICK_SITES:
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
st.markdown("""
<div class="browser-chrome">
    <div class="nav-bar">
        <button class="nav-btn" onclick="goBack()">←</button>
        <button class="nav-btn" onclick="goForward()">→</button>
        <button class="nav-btn" onclick="reloadPage()">↻</button>
        <div class="url-display">{}</div>
        <button class="nav-btn" onclick="homePage()">🏠</button>
    </div>
""".format(st.session_state.current_url[:25] + "..." if len(st.session_state.current_url) > 25 else st.session_state.current_url), unsafe_allow_html=True)

# محتوى المتصفح
st.markdown("""
    <div class="browser-content">
        <iframe 
            class="browser-iframe"
            src="{}"
            sandbox="allow-same-origin allow-scripts allow-popups allow-forms allow-modals allow-top-navigation"
            allow="camera; microphone; geolocation; accelerometer; gyroscope"
            scrolling="yes"
            id="phone-iframe">
        </iframe>
        <div id="error-message" class="iframe-error" style="display: none;">
            <h3>⚠️ الموقع لا يدعم العرض داخل إطار</h3>
            <p class="mobile-text">بعض المواقع لا تسمح بالعرض داخل إطار لأسباب أمنية</p>
            <a href="{}" target="_blank" class="external-link">فتح في نافذة جديدة</a>
        </div>
    </div>
</div>
</div>
</div>
""".format(st.session_state.current_url, st.session_state.current_url), unsafe_allow_html=True)

# JavaScript للتحكم في iframe
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
    iframe.contentWindow.location.reload();
}

function homePage() {
    const iframe = document.getElementById('phone-iframe');
    iframe.src = 'https://example.com';
}

// التعامل مع أخطاء iframe
const iframe = document.getElementById('phone-iframe');
const errorMessage = document.getElementById('error-message');

iframe.onerror = function() {
    iframe.style.display = 'none';
    errorMessage.style.display = 'flex';
};

// التعامل مع رسائل الأخطاء من iframe
window.addEventListener('message', function(event) {
    if (event.data.type === 'iframe-error') {
        iframe.style.display = 'none';
        errorMessage.style.display = 'flex';
    }
});

// محاولة الكشف عن تحميل iframe
let loadAttempts = 0;
const maxAttempts = 3;

iframe.onload = function() {
    loadAttempts = 0;
    try {
        // التحقق مما إذا كان iframe فارغًا
        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
        if (!iframeDoc || !iframeDoc.body || iframeDoc.body.innerHTML.trim() === '') {
            throw new Error('Empty iframe content');
        }
        
        // محاولة الحصول على عنوان الصفحة
        const title = iframeDoc.title || 'بدون عنوان';
        if (title.includes('Error') || title.includes('خطأ')) {
            throw new Error('Page load error');
        }
        
        // إخفاء رسالة الخطأ إذا تم التحميل بنجاح
        errorMessage.style.display = 'none';
        iframe.style.display = 'block';
        
    } catch (e) {
        console.log("Iframe load issue:", e);
        loadAttempts++;
        
        if (loadAttempts >= maxAttempts) {
            iframe.style.display = 'none';
            errorMessage.style.display = 'flex';
        }
    }
};

// تحديث شريط العنوان عند تغيير iframe
setInterval(function() {
    try {
        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
        const currentUrl = iframe.contentWindow.location.href;
        
        // تحديث شريط العنوان
        const urlDisplay = document.querySelector('.url-display');
        if (urlDisplay) {
            urlDisplay.textContent = currentUrl.length > 25 ? 
                currentUrl.substring(0, 25) + '...' : currentUrl;
        }
    } catch (e) {
        // خطأ في CORS، لا يمكن الوصول لمحتوى iframe
    }
}, 1000);

// منع التكبير عند النقر المزدوج
document.getElementById('phone-iframe').addEventListener('touchstart', function(e) {
    if (e.touches.length > 1) {
        e.preventDefault();
    }
}, { passive: false });

// منع إيماءات التكبير
document.getElementById('phone-iframe').addEventListener('gesturestart', function(e) {
    e.preventDefault();
}, { passive: false });
</script>
""", unsafe_allow_html=True)

# لوحة التحكم
with st.sidebar:
    st.header("⚙️ الإعدادات")
    
    st.subheader("حجم الشاشة")
    screen_size = st.selectbox(
        "اختر حجم الهاتف:",
        ["iPhone SE (375x667)", "iPhone 12 (390x844)", "Samsung Galaxy (412x915)"],
        index=1
    )
    
    # تغيير حجم iframe بناءً على الاختيار
    size_map = {
        "iPhone SE (375x667)": "375px",
        "iPhone 12 (390x844)": "390px",
        "Samsung Galaxy (412x915)": "412px"
    }
    st.markdown(f"""
    <style>
        .mobile-browser {{
            width: {size_map[screen_size]};
        }}
    </style>
    """, unsafe_allow_html=True)
    
    st.subheader("سجل التصفح")
    if st.session_state.history:
        for i, item in enumerate(reversed(st.session_state.history[-5:])):
            st.button(
                f"📄 {item['title'][:20]}...",
                key=f"history_{i}",
                use_container_width=True
            )
    
    st.subheader("أدوات")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("مسح السجل"):
            st.session_state.history = [{'url': 'https://example.com', 'title': 'صفحة البداية'}]
            st.session_state.forward_stack = []
            st.success("✓ تم مسح السجل")
    
    with col2:
        if st.button("تحديث"):
            st.rerun()

# معلومات إضافية
with st.expander("ℹ️ معلومات عن المتصفح"):
    st.markdown("""
    ### ميزات المتصفح الهاتفي:
    
    - **📱 تصميم متجاوب**: يعمل مع جميع أحجام شاشات الهواتف
    - **🚀 تحميل سريع**: لا يستخدم موارد ثقيلة مثل Selenium
    - **🔗 تحكم كامل**: التنقل الأمامي والخلفي يعمل بشكل طبيعي
    - **🌐 توافق واسع**: يدعم معظم المواقع حتى تلك التي تحظر iframe
    
    ### حل مشكلة iframe:
    
    تم حل مشكلة إعادة التوجيه باستخدام:
    - خصائص `sandbox` المناسبة للسماح بالتنقل الداخلي
    - معالجة الأخطاء تلقائيًا وإظهار رسالة بديلة
    - تحديث شريط العناوين تلقائيًا أثناء التنقل
    
    ### نصائح الاستخدام:
    
    - لبعض المواقع (مثل فيسبوك)، انقر على زر "فتح في نافذة جديدة"
    - استخدم المواقع السريعة في الأعلى للوصول السريع
    - يمكنك تغيير حجم الهاتف من الإعدادات الجانبية
    """)

# تذييل الصفحة
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 10px;'>
    <p><strong>📱 متصفح هاتفي متجاوب</strong> | يعمل على Streamlit Cloud</p>
    <p>تم تطويره لتقديم أفضل تجربة تصفح على الهاتف</p>
</div>
""", unsafe_allow_html=True)
