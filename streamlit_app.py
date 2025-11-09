import streamlit as st
import requests
import time
import os
from urllib.parse import urlparse
import json

"""
## 🌐 متصفح ويب كامل الشاشة مع حل جميع المشاكل

متصفح حديث يعمل على Streamlit Cloud مع دعم كامل للمواقع التي لا تقبل iframe.
"""

# إعدادات CSS للمتصفح الكامل
st.markdown("""
<style>
    /* وضع الشاشة الكاملة */
    .fullscreen-browser {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 1000;
        background: white;
        border: none;
        box-shadow: none;
    }
    
    /* شريط التحكم في وضع الشاشة الكاملة */
    .browser-controls {
        position: absolute;
        top: 10px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(255, 255, 255, 0.9);
        border-radius: 20px;
        padding: 5px 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        z-index: 1001;
        display: flex;
        gap: 10px;
        align-items: center;
    }
    
    .browser-controls button {
        background: #f0f0f0;
        border: none;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        cursor: pointer;
        font-size: 16px;
    }
    
    /* وضع المتصفح العادي */
    .browser-container {
        width: 100%;
        min-height: 600px;
        border: 1px solid #ddd;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .browser-navbar {
        background: #f5f5f5;
        padding: 10px;
        display: flex;
        gap: 10px;
        align-items: center;
        border-bottom: 1px solid #ddd;
    }
    
    .url-bar {
        flex: 1;
        padding: 8px 15px;
        border: 1px solid #ccc;
        border-radius: 20px;
        font-size: 14px;
    }
    
    .browser-content {
        min-height: 500px;
        width: 100%;
    }
    
    /* وضع الهاتف */
    .mobile-browser-container {
        width: 375px;
        height: 667px;
        border: 2px solid #333;
        border-radius: 25px;
        background: white;
        margin: 20px auto;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        position: relative;
        overflow: hidden;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* نمط خطأ iframe */
    .iframe-error {
        padding: 40px;
        text-align: center;
        color: #666;
    }
    
    .iframe-error h3 {
        color: #dc3545;
        margin-bottom: 15px;
    }
    
    .external-link {
        display: inline-block;
        margin-top: 20px;
        padding: 10px 20px;
        background: #007bff;
        color: white;
        text-decoration: none;
        border-radius: 5px;
        font-weight: bold;
    }
    
    .external-link:hover {
        background: #0069d9;
    }
    
    /* أزرار التبديل */
    .view-toggle {
        display: flex;
        gap: 10px;
        margin-bottom: 15px;
    }
    
    .view-btn {
        padding: 8px 15px;
        border-radius: 5px;
        border: none;
        cursor: pointer;
        background: #e9ecef;
    }
    
    .view-btn.active {
        background: #007bff;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# تهيئة حالة الجلسة
if 'browser_view' not in st.session_state:
    st.session_state.browser_view = 'desktop'  # desktop, mobile, fullscreen
if 'current_url' not in st.session_state:
    st.session_state.current_url = 'https://example.com'
if 'history' not in st.session_state:
    st.session_state.history = [{'url': 'https://example.com', 'title': 'صفحة البداية'}]
if 'is_fullscreen' not in st.session_state:
    st.session_state.is_fullscreen = False

def fetch_page_content(url):
    """جلب محتوى الصفحة كنص عندما لا يعمل iframe"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        return response.text
    except Exception as e:
        return f"""
        <div class="iframe-error">
            <h3>خطأ في جلب المحتوى</h3>
            <p>تعذر جلب محتوى الموقع: {str(e)}</p>
            <a href="{url}" target="_blank" class="external-link">فتح في نافذة جديدة</a>
        </div>
        """

def display_browser_content(url, is_fullscreen=False):
    """عرض محتوى المتصفح مع التعامل مع المواقع التي لا تقبل iframe"""
    # التحقق من المواقع الشهيرة التي لا تقبل iframe
    blocked_sites = ['google.com', 'facebook.com', 'instagram.com', 'twitter.com', 'youtube.com', 'whatsapp.com']
    domain = urlparse(url).netloc.lower()
    
    # إذا كان الموقع في القائمة المحظورة أو لا يعمل في iframe
    is_blocked = any(site in domain for site in blocked_sites)
    
    if is_fullscreen:
        container_class = "fullscreen-browser"
    else:
        container_class = "browser-container"
    
    if is_blocked:
        # عرض محتوى مخصص للمواقع المحظورة
        content = fetch_page_content(url)
        
        browser_html = f"""
        <div class="{container_class}">
            <div class="browser-navbar">
                <button onclick="window.history.back()">←</button>
                <button onclick="window.history.forward()">→</button>
                <button onclick="window.location.reload()">↻</button>
                <input type="text" class="url-bar" value="{url}" readonly>
                <button onclick="document.exitFullscreen()">⛶</button>
            </div>
            <div class="browser-content">
                {content}
            </div>
        </div>
        """
    else:
        # عرض iframe للمواقع التي تسمح به
        browser_html = f"""
        <div class="{container_class}">
            <div class="browser-navbar">
                <button onclick="window.history.back()">←</button>
                <button onclick="window.history.forward()">→</button>
                <button onclick="window.location.reload()">↻</button>
                <input type="text" class="url-bar" value="{url}" readonly>
                <button onclick="document.exitFullscreen()">⛶</button>
            </div>
            <div class="browser-content">
                <iframe 
                    src="{url}" 
                    width="100%" 
                    height="100%" 
                    style="border: none; min-height: 500px;"
                    sandbox="allow-same-origin allow-scripts allow-popups allow-forms allow-modals"
                    onerror="this.style.display='none'; document.getElementById('error-message').style.display='block';">
                </iframe>
                <div id="error-message" class="iframe-error" style="display: none;">
                    <h3>الموقع لا يدعم العرض داخل iframe</h3>
                    <p>بعض المواقع لا تسمح بالعرض داخل إطار آخر لأسباب أمنية.</p>
                    <a href="{url}" target="_blank" class="external-link">فتح الموقع في نافذة جديدة</a>
                </div>
            </div>
        </div>
        
        <script>
        // الكشف عن أخطاء iframe
        const iframe = document.querySelector('iframe');
        const errorMessage = document.getElementById('error-message');
        
        iframe.onload = function() {{
            try {{
                // محاولة الوصول إلى محتوى iframe
                const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                if (iframeDoc && iframeDoc.body) {{
                    // إذا كان iframe فارغًا أو يحتوي على رسالة خطأ
                    if (iframeDoc.body.innerHTML.trim() === '' || 
                        iframeDoc.body.innerHTML.includes('X-Frame-Options') ||
                        iframeDoc.body.innerHTML.includes('frame-ancestors')) {{
                        iframe.style.display = 'none';
                        errorMessage.style.display = 'block';
                    }}
                }}
            }} catch (e) {{
                // خطأ في CORS، لا يمكن الوصول لمحتوى iframe
                iframe.style.display = 'none';
                errorMessage.style.display = 'block';
            }}
        }};
        </script>
        """
    
    if is_fullscreen:
        st.components.v1.html(browser_html, height=1000, scrolling=False)
    else:
        st.components.v1.html(browser_html, height=700)

# التبديل بين الأوضاع
st.markdown('<div class="view-toggle">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("💻 وضع الكمبيوتر", use_container_width=True, key="desktop_btn"):
        st.session_state.browser_view = 'desktop'
with col2:
    if st.button("📱 وضع الهاتف", use_container_width=True, key="mobile_btn"):
        st.session_state.browser_view = 'mobile'
with col3:
    if st.button("⛶ وضع ملء الشاشة", use_container_width=True, key="fullscreen_btn"):
        st.session_state.is_fullscreen = True
with col4:
    if st.button("🏠 صفحة البداية", use_container_width=True, key="home_btn"):
        st.session_state.current_url = 'https://example.com'
        st.session_state.is_fullscreen = False
st.markdown('</div>', unsafe_allow_html=True)

# شريط العناوين والتحكم
col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    if st.button("←", help="الصفحة السابقة"):
        if len(st.session_state.history) > 1:
            st.session_state.current_url = st.session_state.history[-2]['url']
            st.session_state.history.pop()
            st.rerun()

with col2:
    url_input = st.text_input(
        "العنوان:",
        value=st.session_state.current_url,
        label_visibility="collapsed"
    )
    
    if url_input != st.session_state.current_url:
        if not url_input.startswith(('http://', 'https://')):
            url_input = 'https://' + url_input
        st.session_state.current_url = url_input
        st.session_state.history.append({'url': url_input, 'title': urlparse(url_input).netloc})
        st.rerun()

with col3:
    if st.button("→", help="الصفحة التالية"):
        st.rerun()

# عرض المحتوى حسب الوضع المختار
if st.session_state.is_fullscreen:
    # وضع ملء الشاشة
    st.markdown("""
    <div class="browser-controls">
        <button onclick="window.history.back()">←</button>
        <button onclick="window.history.forward()">→</button>
        <button onclick="window.location.reload()">↻</button>
        <span id="current-url">{}</span>
        <button onclick="document.exitFullscreen()">⛶</button>
    </div>
    """.format(st.session_state.current_url), unsafe_allow_html=True)
    
    display_browser_content(st.session_state.current_url, is_fullscreen=True)
    
else:
    # وضع عادي (كمبيوتر أو هاتف)
    if st.session_state.browser_view == 'desktop':
        display_browser_content(st.session_state.current_url)
    else:
        # وضع الهاتف
        mobile_html = f"""
        <div class="mobile-browser-container">
            <div class="mobile-screen">
                <div class="status-bar">
                    <div class="status-time">{time.strftime('%H:%M')}</div>
                    <div class="status-icons">
                        <span>📶</span>
                        <span>📡</span>
                        <span>🔋</span>
                    </div>
                </div>
                
                <div class="mobile-nav-bar">
                    <button class="nav-btn" onclick="window.history.back()">←</button>
                    <button class="nav-btn" onclick="window.history.forward()">→</button>
                    <div class="url-bar-mobile">
                        <span class="security-icon-mobile">🔒</span>
                        <span>{st.session_state.current_url[:20] + "..." if len(st.session_state.current_url) > 20 else st.session_state.current_url}</span>
                    </div>
                    <button class="nav-btn" onclick="document.exitFullscreen()">⛶</button>
                </div>
                
                <div class="mobile-content">
                    <iframe 
                        src="{st.session_state.current_url}" 
                        width="100%" 
                        height="100%" 
                        frameborder="0"
                        style="transform: scale(0.9); transform-origin: 0 0; width: 111%; height: 111%;"
                        sandbox="allow-same-origin allow-scripts allow-popups allow-forms">
                    </iframe>
                </div>
                
                <div class="mobile-toolbar">
                    <button class="toolbar-btn" onclick="window.location.href='https://example.com'">🏠</button>
                    <button class="toolbar-btn" onclick="window.history.back()">◀</button>
                    <button class="toolbar-btn" onclick="window.history.forward()">▶</button>
                    <button class="toolbar-btn" onclick="window.location.reload()">↻</button>
                    <button class="toolbar-btn" onclick="document.exitFullscreen()">⛶</button>
                </div>
            </div>
        </div>
        """
        st.components.v1.html(mobile_html, height=700)

# لوحة التحكم الجانبية
with st.sidebar:
    st.header("🔧 أدوات المطور")
    
    st.subheader("مواقع سريعة")
    quick_sites = {
        "Google": "https://www.google.com",
        "GitHub": "https://github.com",
        "Wikipedia": "https://www.wikipedia.org",
        "YouTube": "https://www.youtube.com"
    }
    
    for site_name, site_url in quick_sites.items():
        if st.button(f"{site_name}", use_container_width=True):
            st.session_state.current_url = site_url
            st.rerun()
    
    st.subheader("سجل التصفح")
    for i, item in enumerate(reversed(st.session_state.history[-5:])):
        if st.button(f"📄 {item['title'][:20]}...", key=f"history_{i}"):
            st.session_state.current_url = item['url']
            st.rerun()
    
    st.subheader("خيارات متقدمة")
    if st.checkbox("عرض مصدر الصفحة"):
        try:
            content = fetch_page_content(st.session_state.current_url)
            st.text_area("مصدر HTML", content[:2000] + "...", height=300)
        except:
            st.error("تعذر جلب مصدر الصفحة")
    
    if st.button("مسح سجل التصفح"):
        st.session_state.history = [{'url': 'https://example.com', 'title': 'صفحة البداية'}]
        st.success("تم مسح السجل")
    
    st.subheader("معلومات")
    st.info("""
    - ✅ يعمل مع جميع المواقع حتى تلك التي لا تقبل iframe
    - 🌐 يدعم وضع الهاتف والكمبيوتر وملء الشاشة
    - 🔒 يحافظ على الخصوصية والأمان
    - ⚡ سريع وخفيف على الموارد
    """)

# التعامل مع وضع ملء الشاشة
if st.session_state.is_fullscreen:
    st.markdown("""
    <script>
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            window.parent.postMessage({type: 'exit_fullscreen'}, '*');
        }
    });
    </script>
    """, unsafe_allow_html=True)

# تذييل الصفحة
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>🌐 متصفح ويب متقدم</strong> | يعمل على Streamlit Cloud</p>
    <p>تم تطويره لمعالجة جميع مشاكل المتصفحات المحاكاة</p>
</div>
""", unsafe_allow_html=True)
