import streamlit as st
import requests
import json
import time
import os
from urllib.parse import urljoin, urlparse
import re

# إعدادات الجلسة
SESSION_DIR = "/tmp/mobile_browser"
os.makedirs(SESSION_DIR, exist_ok=True)

# تثبيت CSS لمحاكاة متصفح الهاتف
st.markdown("""
<style>
    /* تصميم متصفح الهاتف */
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
    
    /* شاشة الهاتف */
    .mobile-screen {
        width: 100%;
        height: 100%;
        background: white;
        border-radius: 23px;
        overflow: hidden;
        position: relative;
    }
    
    /* شريط حالة الهاتف */
    .status-bar {
        background: #000;
        color: white;
        padding: 5px 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 12px;
        height: 20px;
    }
    
    .status-time {
        font-weight: bold;
    }
    
    .status-icons {
        display: flex;
        gap: 5px;
    }
    
    /* شريط التنقل */
    .mobile-nav-bar {
        background: #f8f8f8;
        border-bottom: 1px solid #e5e5e5;
        padding: 8px 15px;
        display: flex;
        align-items: center;
        gap: 10px;
        height: 44px;
    }
    
    .nav-btn {
        background: none;
        border: none;
        font-size: 18px;
        cursor: pointer;
        padding: 5px;
        color: #333;
    }
    
    .url-bar-mobile {
        flex: 1;
        background: white;
        border: 1px solid #ddd;
        border-radius: 15px;
        padding: 6px 12px;
        font-size: 12px;
        display: flex;
        align-items: center;
        gap: 5px;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
    }
    
    .security-icon-mobile {
        color: #4CAF50;
        font-size: 12px;
    }
    
    /* منطقة المحتوى */
    .mobile-content {
        height: calc(100% - 114px);
        overflow: hidden;
        background: white;
    }
    
    /* شريط الأدوات السفلي */
    .mobile-toolbar {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        background: #f8f8f8;
        border-top: 1px solid #e5e5e5;
        padding: 8px 15px;
        display: flex;
        justify-content: space-around;
        align-items: center;
        height: 50px;
    }
    
    .toolbar-btn {
        background: none;
        border: none;
        font-size: 20px;
        cursor: pointer;
        padding: 8px;
        border-radius: 8px;
        transition: background 0.2s;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

class MobileBrowserSimulator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
        })
        self.current_url = "https://example.com"
        self.tabs = [{"id": 1, "title": "علامة تبويب جديدة", "url": "https://example.com", "favicon": "🌐"}]
        self.active_tab = 1
        self.history = []
        
    def navigate(self, url, tab_id=None):
        """التنقل إلى رابط في علامة تبويب محددة"""
        if not url:
            return False
            
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        try:
            # تحديث علامة التبويب النشطة
            if tab_id is None:
                tab_id = self.active_tab
            
            for tab in self.tabs:
                if tab['id'] == tab_id:
                    tab['url'] = url
                    # نقوم فقط بتحديث الرابط دون محاولة الـ scraping
                    break
            
            # إضافة إلى التاريخ
            self.history.append({
                'url': url,
                'title': urlparse(url).netloc,
                'timestamp': time.time()
            })
            
            return True
            
        except Exception as e:
            return False
    
    def add_tab(self, url="https://example.com"):
        """إضافة علامة تبويب جديدة"""
        new_tab_id = max([tab['id'] for tab in self.tabs]) + 1 if self.tabs else 1
        self.tabs.append({
            "id": new_tab_id,
            "title": "علامة تبويب جديدة",
            "url": url,
            "favicon": "🌐"
        })
        self.active_tab = new_tab_id
        return new_tab_id
    
    def close_tab(self, tab_id):
        """إغلاق علامة تبويب"""
        if len(self.tabs) > 1:
            self.tabs = [tab for tab in self.tabs if tab['id'] != tab_id]
            if self.active_tab == tab_id:
                self.active_tab = self.tabs[0]['id']
    
    def get_active_tab(self):
        """الحصول على علامة التبويب النشطة"""
        try:
            if not self.tabs:
                self.tabs = [{"id": 1, "title": "علامة تبويب جديدة", "url": "https://example.com", "favicon": "🌐"}]
                self.active_tab = 1
            
            for tab in self.tabs:
                if tab['id'] == self.active_tab:
                    return tab
            
            self.active_tab = self.tabs[0]['id']
            return self.tabs[0]
            
        except Exception as e:
            self.tabs = [{"id": 1, "title": "علامة تبويب جديدة", "url": "https://example.com", "favicon": "🌐"}]
            self.active_tab = 1
            return self.tabs[0]

# تهيئة المتصفح في حالة الجلسة
if 'mobile_browser' not in st.session_state:
    st.session_state.mobile_browser = MobileBrowserSimulator()

# العنوان الرئيسي
st.title("📱 متصفح محاكي للهواتف")

# شريط التحكم العلوي
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.button("🔄", help="إعادة تحميل", use_container_width=True):
        active_tab = st.session_state.mobile_browser.get_active_tab()
        if active_tab and active_tab.get('url'):
            # تحديث الصفحة الحالية
            st.rerun()

with col2:
    # الحصول على العنوان الحالي
    active_tab = st.session_state.mobile_browser.get_active_tab()
    current_url = active_tab.get('url', 'https://example.com')
    
    new_url = st.text_input(
        "أدخل عنوان الويب:",
        value=current_url,
        placeholder="https://example.com ",
        label_visibility="collapsed"
    )
    
    if new_url and new_url != current_url:
        st.session_state.mobile_browser.navigate(new_url)
        st.rerun()

with col3:
    if st.button("➕", help="علامة تبويب جديدة", use_container_width=True):
        st.session_state.mobile_browser.add_tab()
        st.rerun()

# عرض علامات التبويب
browser = st.session_state.mobile_browser
tabs = browser.tabs if hasattr(browser, 'tabs') and browser.tabs else []

if tabs:
    st.write("**علامات التبويب المفتوحة:**")
    
    # إنشاء أعمدة للعلامات
    tab_cols = st.columns(min(len(tabs) + 1, 6))  # حد أقصى 6 أعمدة
    
    for idx, tab in enumerate(tabs):
        if idx < len(tab_cols) - 1:  # احتفظ بالعمود الأخير لزر الإغلاق
            with tab_cols[idx]:
                tab_label = f"{tab.get('favicon', '🌐')} {tab.get('title', 'علامة جديدة')[:10]}..."
                is_active = tab.get('id') == browser.active_tab
                
                if st.button(tab_label, key=f"tab_{tab.get('id', idx)}", 
                           use_container_width=True, type="primary" if is_active else "secondary"):
                    browser.active_tab = tab.get('id', 1)
                    st.rerun()
    
    # زر إغلاق الجميع في العمود الأخير
    if len(tabs) > 1 and len(tab_cols) > len(tabs):
        with tab_cols[len(tabs)]:
            if st.button("✕", help="إغلاق الجميع", use_container_width=True):
                # الاحتفاظ بعلامة تبويب واحدة فقط
                browser.tabs = [browser.tabs[0]]
                browser.active_tab = browser.tabs[0]['id']
                st.rerun()

# متصفح الهاتف المحاكي
st.markdown("### 📱 شاشة الهاتف:")

# الحصول على الرابط الحالي
active_tab = st.session_state.mobile_browser.get_active_tab()
current_url = active_tab.get('url', 'https://example.com') if active_tab else 'https://example.com'

# تقصير الرابط للعرض
short_url = current_url[:25] + "..." if len(current_url) > 25 else current_url

# بناء واجهة الهاتف مع iFrame
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
                <span>{short_url or 'about:blank'}</span>
            </div>
            <button class="nav-btn" onclick="window.location.reload()">↻</button>
        </div>
        
        <div class="mobile-content">
            <iframe 
                src="{current_url}" 
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
            <button class="toolbar-btn" onclick="alert('قريبًا')">📑</button>
            <button class="toolbar-btn" onclick="alert('قريبًا')">⋯</button>
        </div>
    </div>
</div>

<script>
// JavaScript للتحكم في iframe
const iframe = document.querySelector('iframe');
const urlBar = document.querySelector('.url-bar-mobile span:last-child');

// تحديث شريط العنوان عند تغيير iframe
iframe.onload = function() {{
    try {{
        const currentUrl = iframe.contentWindow.location.href;
        urlBar.textContent = currentUrl.length > 25 ? 
            currentUrl.substring(0, 25) + '...' : currentUrl;
        // تحديث التاريخ في Streamlit
        window.parent.postMessage({{
            type: 'url_change',
            url: currentUrl
        }}, '*');
    }} catch (e) {{
        // خطأ في CORS، لا يمكن الوصول لمحتوى iframe
    }}
}};

// تحديد الأزرار العلوية للتحكم في iframe
document.querySelector('.nav-btn:nth-child(1)').onclick = function(e) {{
    e.preventDefault();
    iframe.contentWindow.history.back();
}};

document.querySelector('.nav-btn:nth-child(2)').onclick = function(e) {{
    e.preventDefault();
    iframe.contentWindow.history.forward();
}};

document.querySelector('.nav-btn:nth-child(4)').onclick = function(e) {{
    e.preventDefault();
    iframe.contentWindow.location.reload();
}};
</script>
"""

# عرض متصفح الهاتف باستخدام st.components.v1.html
st.components.v1.html(mobile_html, height=700)

# لوحة التحكم الجانبية
with st.sidebar:
    st.header("🎮 تحكم الجوال")
    
    st.subheader("مواقع سريعة")
    quick_sites = {
        "Google": "https://www.google.com",
        "Wikipedia": "https://www.wikipedia.org",
        "GitHub": "https://github.com",
        "YouTube": "https://www.youtube.com"
    }
    
    for site_name, site_url in quick_sites.items():
        if st.button(f"{site_name}", use_container_width=True):
            st.session_state.mobile_browser.navigate(site_url)
            st.rerun()
    
    st.subheader("إدارة العلامات")
    if hasattr(st.session_state.mobile_browser, 'tabs') and st.session_state.mobile_browser.tabs:
        for tab in st.session_state.mobile_browser.tabs:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"{tab.get('favicon', '🌐')} {tab.get('title', 'علامة جديدة')[:15]}")
            with col2:
                if st.button("✕", key=f"close_{tab.get('id', 'unknown')}"):
                    if len(st.session_state.mobile_browser.tabs) > 1:
                        st.session_state.mobile_browser.close_tab(tab.get('id', 1))
                        st.rerun()
    else:
        st.info("لا توجد علامات تبويب")
    
    st.subheader("سجل التصفح")
    if hasattr(st.session_state.mobile_browser, 'history') and st.session_state.mobile_browser.history:
        for i, visit in enumerate(reversed(st.session_state.mobile_browser.history[-5:])):
            if st.button(f"📄 {visit.get('title', 'بدون عنوان')[:20]}...", key=f"history_{i}"):
                st.session_state.mobile_browser.navigate(visit.get('url', ''))
                st.rerun()
    else:
        st.info("لا يوجد سجل تصفح")
    
    st.subheader("إعدادات العرض")
    mobile_mode = st.selectbox("وضع الجوال:", ["iPhone (375px)", "Android (412px)"])
    
    if st.button("🔄 إعادة تعيين المتصفح"):
        st.session_state.mobile_browser = MobileBrowserSimulator()
        st.success("تم إعادة التعيين")
        st.rerun()

# تذييل الصفحة
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>📱 متصفح الجوال المحاكي</strong> | تجربة تصفح حقيقية للهواتف</p>
    <p>✨ تصميم متجاوب • 🚀 أداء سريع • 📱 محاكاة واقعية</p>
</div>
""", unsafe_allow_html=True)
