import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import time
import os
from urllib.parse import urljoin, urlparse
import base64
from PIL import Image
import io
import re

# إعدادات الجلسة
SESSION_DIR = "/tmp/browser_sessions"
os.makedirs(SESSION_DIR, exist_ok=True)

# تثبيت CSS لمحاكاة المتصفح الحقيقي
st.markdown("""
<style>
    /* تصميم المتصفح الرئيسي */
    .browser-container {
        border: 1px solid #ccc;
        border-radius: 12px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        background: white;
        margin: 10px 0;
        overflow: hidden;
        font-family: 'Segoe UI', system-ui, sans-serif;
    }
    
    .browser-toolbar {
        background: #f5f5f5;
        padding: 12px 16px;
        border-bottom: 1px solid #e0e0e0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .browser-controls {
        display: flex;
        gap: 8px;
    }
    
    .browser-btn {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        border: none;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .browser-btn:hover {
        transform: scale(1.05);
    }
    
    .btn-close { background: #ff5f57; color: white; }
    .btn-minimize { background: #ffbd2e; color: white; }
    .btn-maximize { background: #28ca42; color: white; }
    
    .url-bar {
        flex: 1;
        background: white;
        border: 1px solid #ddd;
        border-radius: 24px;
        padding: 8px 16px;
        font-size: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .url-bar input {
        border: none;
        outline: none;
        flex: 1;
        font-size: 14px;
        background: transparent;
    }
    
    .security-icon {
        color: #4CAF50;
        font-size: 16px;
    }
    
    .browser-tabs {
        background: #f8f9fa;
        border-bottom: 1px solid #e0e0e0;
        display: flex;
        padding: 0 16px;
    }
    
    .browser-tab {
        background: #e9ecef;
        padding: 10px 20px;
        border-radius: 8px 8px 0 0;
        margin-right: 4px;
        cursor: pointer;
        border: 1px solid #dee2e6;
        border-bottom: none;
        max-width: 200px;
        min-width: 120px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .browser-tab.active {
        background: white;
        border-color: #ccc;
    }
    
    .tab-favicon {
        width: 16px;
        height: 16px;
        border-radius: 2px;
    }
    
    .tab-title {
        flex: 1;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        font-size: 13px;
    }
    
    .tab-close {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: #6c757d;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 10px;
        cursor: pointer;
    }
    
    .browser-content {
        height: 70vh;
        background: white;
        overflow: auto;
        padding: 20px;
    }
    
    .new-tab-btn {
        padding: 10px 16px;
        background: transparent;
        border: none;
        font-size: 18px;
        cursor: pointer;
        color: #6c757d;
    }
    
    /* محاكاة محتوى الويب */
    .website-content {
        max-width: 1200px;
        margin: 0 auto;
        font-family: system-ui, sans-serif;
        line-height: 1.6;
    }
    
    .website-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 40px 20px;
        text-align: center;
        border-radius: 8px;
        margin-bottom: 30px;
    }
    
    .website-nav {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    
    .nav-links {
        display: flex;
        gap: 20px;
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .nav-links a {
        color: #495057;
        text-decoration: none;
        font-weight: 500;
    }
    
    .nav-links a:hover {
        color: #007bff;
    }
    
    .content-grid {
        display: grid;
        grid-template-columns: 2fr 1fr;
        gap: 30px;
        margin-bottom: 30px;
    }
    
    .main-content {
        background: white;
        padding: 25px;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .sidebar {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
    }
    
    .article-card {
        background: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    .article-card h3 {
        color: #333;
        margin-bottom: 10px;
    }
    
    .website-footer {
        background: #343a40;
        color: white;
        padding: 30px 20px;
        text-align: center;
        border-radius: 8px;
        margin-top: 40px;
    }
    
    /* محاكاة عناصر الويب */
    .web-button {
        background: #007bff;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        cursor: pointer;
        font-size: 14px;
        margin: 5px;
    }
    
    .web-input {
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 5px;
        width: 100%;
        margin: 5px 0;
    }
    
    .web-form {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        margin: 20px 0;
    }
    
    /* حالة التحميل */
    .loading-bar {
        height: 3px;
        background: linear-gradient(90deg, #007bff, #00c851);
        width: 0%;
        transition: width 0.3s;
        position: absolute;
        top: 0;
        left: 0;
    }
</style>
""", unsafe_allow_html=True)

class RealBrowserSimulator:
    def __init__(self):
        self.session = requests.Session()
        self.current_url = ""
        self.tabs = [{"id": 1, "title": "علامة تبويب جديدة", "url": "", "favicon": "🌐", "content": ""}]
        self.active_tab = 1
        self.history = []
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
        })
    
    def navigate(self, url, tab_id=None):
        """التنقل إلى رابط في علامة تبويب محددة"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            if tab_id is None:
                tab_id = self.active_tab
            
            # تحديث علامة التبويب النشطة
            for tab in self.tabs:
                if tab['id'] == tab_id:
                    tab['url'] = response.url
                    tab['content'] = response.text
                    tab['title'] = self.extract_title(response.text)
                    tab['favicon'] = self.extract_favicon(response.text, response.url)
                    break
            
            # إضافة إلى التاريخ
            self.history.append({
                'url': response.url,
                'title': self.extract_title(response.text),
                'timestamp': time.time()
            })
            
            return True
            
        except Exception as e:
            # إنشاء صفحة خطأ
            error_content = self.create_error_page(str(e), url)
            for tab in self.tabs:
                if tab['id'] == self.active_tab:
                    tab['url'] = url
                    tab['content'] = error_content
                    tab['title'] = "خطأ في التحميل"
                    tab['favicon'] = "❌"
                    break
            return False
    
    def extract_title(self, html_content):
        """استخراج عنوان الصفحة"""
        soup = BeautifulSoup(html_content, 'html.parser')
        title = soup.title
        return title.string.strip() if title else "بدون عنوان"
    
    def extract_favicon(self, html_content, base_url):
        """استخراج الأيقونة"""
        soup = BeautifulSoup(html_content, 'html.parser')
        favicon = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
        if favicon and favicon.get('href'):
            return favicon['href']
        return "🌐"
    
    def create_error_page(self, error, url):
        """إنشاء صفحة خطأ مشابهة لمتصفحات حقيقية"""
        return f"""
        <div class="website-content">
            <div class="website-header">
                <h1>⚠️ تعذر العثور على هذا الموقع</h1>
                <p>لا يمكن الوصول إلى {url}</p>
            </div>
            <div class="main-content">
                <h3>تفاصيل الخطأ:</h3>
                <p>{error}</p>
                <div class="web-form">
                    <h4>جرب ما يلي:</h4>
                    <ul>
                        <li>تحقق من اتصال الشبكة</li>
                        <li>تحقق من كتابة العنوان</li>
                        <li>جرب استخدام HTTPS بدلاً من HTTP</li>
                    </ul>
                    <button class="web-button" onclick="window.location.reload()">إعادة المحاولة</button>
                </div>
            </div>
        </div>
        """
    
    def add_tab(self, url=""):
        """إضافة علامة تبويب جديدة"""
        new_tab_id = max([tab['id'] for tab in self.tabs]) + 1 if self.tabs else 1
        self.tabs.append({
            "id": new_tab_id,
            "title": "علامة تبويب جديدة",
            "url": url,
            "favicon": "🌐",
            "content": ""
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
        for tab in self.tabs:
            if tab['id'] == self.active_tab:
                return tab
        return self.tabs[0]

# تهيئة المتصفح في حالة الجلسة
if 'browser' not in st.session_state:
    st.session_state.browser = RealBrowserSimulator()

# الواجهة الرئيسية للمتصفح
st.markdown("""
<div class="browser-container">
    <div class="loading-bar" id="loadingBar"></div>
    <div class="browser-toolbar">
        <div class="browser-controls">
            <div class="browser-btn btn-close" title="إغلاق">×</div>
            <div class="browser-btn btn-minimize" title="تصغير">–</div>
            <div class="browser-btn btn-maximize" title="تكبير">□</div>
        </div>
        
        <div class="browser-controls">
            <button class="browser-btn" title="السابق" onclick="handleBack()">←</button>
            <button class="browser-btn" title="التالي" onclick="handleForward()">→</button>
            <button class="browser-btn" title="إعادة التحميل" onclick="handleReload()">↻</button>
        </div>
        
        <div class="url-bar">
            <span class="security-icon">🔒</span>
            <input type="text" id="urlInput" placeholder="ابحث أو أدخل عنوان الويب" 
                   value="{current_url}">
            <button class="browser-btn" title="الذهاب" onclick="handleNavigate()">↵</button>
        </div>
        
        <div class="browser-controls">
            <button class="browser-btn" title="الإشارات المرجعية">☆</button>
            <button class="browser-btn" title="التاريخ">☰</button>
        </div>
    </div>
    
    <div class="browser-tabs">
        {tabs_html}
        <button class="new-tab-btn" title="علامة تبويب جديدة" onclick="handleNewTab()">+</button>
    </div>
    
    <div class="browser-content" id="browserContent">
        {content_html}
    </div>
</div>
""", unsafe_allow_html=True)

# JavaScript للتحكم في المتصفح
st.markdown("""
<script>
function handleNavigate() {
    const url = document.getElementById('urlInput').value;
    window.location.href = window.location.pathname + '?url=' + encodeURIComponent(url);
}

function handleNewTab() {
    // إضافة علامة تبويب جديدة
    window.location.href = window.location.pathname + '?new_tab=true';
}

function handleTabClick(tabId) {
    window.location.href = window.location.pathname + '?tab=' + tabId;
}

function handleCloseTab(tabId, event) {
    event.stopPropagation();
    window.location.href = window.location.pathname + '?close_tab=' + tabId;
}

function handleBack() {
    // الرجوع للخلف
    window.location.href = window.location.pathname + '?action=back';
}

function handleForward() {
    // التقدم للأمام
    window.location.href = window.location.pathname + '?action=forward';
}

function handleReload() {
    // إعادة التحميل
    window.location.href = window.location.pathname + '?action=reload';
}

// محاكاة شريط التحميل
function simulateLoading() {
    const loadingBar = document.getElementById('loadingBar');
    let width = 0;
    const interval = setInterval(() => {
        if (width >= 100) {
            clearInterval(interval);
            loadingBar.style.width = '0%';
        } else {
            width += Math.random() * 10;
            loadingBar.style.width = width + '%';
        }
    }, 100);
}

// بدء محاكاة التحميل عند فتح الصفحة
setTimeout(simulateLoading, 500);
</script>
""", unsafe_allow_html=True)

# معالجة الأحداث من JavaScript
def handle_browser_events():
    query_params = st.experimental_get_query_params()
    
    # التنقل إلى رابط
    if 'url' in query_params:
        url = query_params['url'][0]
        st.session_state.browser.navigate(url)
        st.experimental_set_query_params()
    
    # علامة تبويب جديدة
    if 'new_tab' in query_params:
        st.session_state.browser.add_tab()
        st.experimental_set_query_params()
    
    # تغيير علامة التبويب
    if 'tab' in query_params:
        tab_id = int(query_params['tab'][0])
        st.session_state.browser.active_tab = tab_id
        st.experimental_set_query_params()
    
    # إغلاق علامة تبويب
    if 'close_tab' in query_params:
        tab_id = int(query_params['close_tab'][0])
        st.session_state.browser.close_tab(tab_id)
        st.experimental_set_query_params()

# تشغيل معالجة الأحداث
handle_browser_events()

# تحديث واجهة المتصفح
def update_browser_interface():
    browser = st.session_state.browser
    active_tab = browser.get_active_tab()
    
    # تحديث شريط العنوان
    current_url = active_tab['url'] if active_tab['url'] else "about:blank"
    
    # إنشاء HTML لعلامات التبويب
    tabs_html = ""
    for tab in browser.tabs:
        is_active = "active" if tab['id'] == browser.active_tab else ""
        tabs_html += f"""
        <div class="browser-tab {is_active}" onclick="handleTabClick({tab['id']})">
            <span class="tab-favicon">{tab['favicon']}</span>
            <span class="tab-title">{tab['title']}</span>
            <span class="tab-close" onclick="handleCloseTab({tab['id']}, event)">×</span>
        </div>
        """
    
    # عرض محتوى الصفحة النشطة
    content_html = active_tab['content'] if active_tab['content'] else """
    <div class="website-content">
        <div class="website-header">
            <h1>🌐 المتصفح المحاكي</h1>
            <p>أدخل عنوان URL في شريط العنوان لبدء التصفح</p>
        </div>
        
        <div class="content-grid">
            <div class="main-content">
                <h2>مرحباً بك في المتصفح المحاكي</h2>
                <p>هذا متصفح ويب محاكي كامل يعمل داخل Streamlit. يمكنك:</p>
                
                <div class="article-card">
                    <h3>🔍 زيارة المواقع</h3>
                    <p>أدخل أي عنوان URL في شريط العنوان واضغط Enter</p>
                </div>
                
                <div class="article-card">
                    <h3>📑 فتح علامات تبويب متعددة</h3>
                    <p>انقر على زر + لفتح علامات تبويب جديدة</p>
                </div>
                
                <div class="article-card">
                    <h3>🔄 التنقل بين الصفحات</h3>
                    <p>استخدم أزرار السابق والتالي للتنقل في التاريخ</p>
                </div>
            </div>
            
            <div class="sidebar">
                <h3>مواقع مقترحة</h3>
                <div class="web-form">
                    <button class="web-button" onclick="window.location.href='?url=google.com'">Google</button>
                    <button class="web-button" onclick="window.location.href='?url=wikipedia.org'">Wikipedia</button>
                    <button class="web-button" onclick="window.location.href='?url=github.com'">GitHub</button>
                    <button class="web-button" onclick="window.location.href='?url=stackoverflow.com'">Stack Overflow</button>
                </div>
                
                <h3>إحصائيات</h3>
                <p>علامات التبويب المفتوحة: {tabs_count}</p>
                <p>الصفحات المزورة: {history_count}</p>
            </div>
        </div>
    </div>
    """.format(
        tabs_count=len(browser.tabs),
        history_count=len(browser.history)
    )
    
    return current_url, tabs_html, content_html

# تحديث الواجهة
current_url, tabs_html, content_html = update_browser_interface()

# لوحة التحكم الجانبية
with st.sidebar:
    st.header("🛠️ أدوات المطور")
    
    st.subheader("علامات التبويب المفتوحة")
    for tab in st.session_state.browser.tabs:
        if st.button(f"🔗 {tab['title'][:20]}...", key=f"tab_{tab['id']}", use_container_width=True):
            st.session_state.browser.active_tab = tab['id']
            st.rerun()
    
    st.subheader("سجل التصفح")
    if st.session_state.browser.history:
        for i, visit in enumerate(reversed(st.session_state.browser.history[-10:])):
            if st.button(f"📄 {visit['title'][:25]}...", key=f"hist_{i}", use_container_width=True):
                st.session_state.browser.navigate(visit['url'])
                st.rerun()
    else:
        st.info("لا يوجد سجل تصفح بعد")
    
    st.subheader("أدوات متقدمة")
    if st.button("🧹 مسح الذاكرة المؤقتة"):
        st.session_state.browser.session.cookies.clear()
        st.success("تم مسح الذاكرة المؤقتة")
    
    if st.button("🔄 إعادة تعيين المتصفح"):
        st.session_state.browser = RealBrowserSimulator()
        st.success("تم إعادة تعيين المتصفح")
        st.rerun()

# معلومات إضافية
with st.expander("📊 معلومات المتصفح"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("علامات التبويب", len(st.session_state.browser.tabs))
    
    with col2:
        st.metric("الصفحات المزورة", len(st.session_state.browser.history))
    
    with col3:
        active_tab = st.session_state.browser.get_active_tab()
        st.metric("الصفحة النشطة", active_tab['title'][:15] + "...")

# تذييل الصفحة
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    <p><strong>المتصفح المحاكي v2.0</strong> | محاكاة كاملة لمتصفح الويب الحقيقي</p>
    <p>⚡ يعمل داخل Streamlit • 🔒 آمن • 🌐 متعدد العلامات</p>
</div>
""", unsafe_allow_html=True)
