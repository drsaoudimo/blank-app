import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import time
import os
from urllib.parse import urljoin, urlparse
import re
import base64

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
    }
    
    .url-bar-mobile {
        flex: 1;
        background: white;
        border: 1px solid #ddd;
        border-radius: 15px;
        padding: 6px 12px;
        font-size: 14px;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    
    .security-icon-mobile {
        color: #4CAF50;
        font-size: 12px;
    }
    
    /* منطقة المحتوى */
    .mobile-content {
        height: calc(100% - 64px);
        overflow-y: auto;
        background: white;
        -webkit-overflow-scrolling: touch;
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
    }
    
    .toolbar-btn:hover {
        background: #e0e0e0;
    }
    
    /* محاكاة محتوى الجوال */
    .mobile-website {
        width: 100%;
        min-height: 100%;
        background: white;
    }
    
    .mobile-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 60px 20px 20px;
        text-align: center;
    }
    
    .mobile-nav {
        background: #f8f9fa;
        padding: 15px;
        border-bottom: 1px solid #e0e0e0;
    }
    
    .mobile-nav-links {
        display: flex;
        gap: 15px;
        list-style: none;
        padding: 0;
        margin: 0;
        overflow-x: auto;
    }
    
    .mobile-nav-links a {
        color: #495057;
        text-decoration: none;
        font-weight: 500;
        white-space: nowrap;
    }
    
    .mobile-content-area {
        padding: 15px;
    }
    
    .mobile-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        border: 1px solid #e0e0e0;
    }
    
    .mobile-button {
        background: #007bff;
        color: white;
        border: none;
        padding: 12px 20px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 16px;
        width: 100%;
        margin: 5px 0;
    }
    
    .mobile-input {
        padding: 12px;
        border: 1px solid #ddd;
        border-radius: 8px;
        width: 100%;
        margin: 5px 0;
        font-size: 16px;
    }
    
    .mobile-footer {
        background: #343a40;
        color: white;
        padding: 20px;
        text-align: center;
        margin-top: 20px;
    }
    
    /* تأثيرات التحميل */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #007bff;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* التمرير على الجوال */
    .mobile-content::-webkit-scrollbar {
        width: 3px;
    }
    
    .mobile-content::-webkit-scrollbar-thumb {
        background: #ccc;
        border-radius: 10px;
    }
    
    /* علامات التبويب على الجوال */
    .mobile-tabs {
        display: flex;
        background: #f8f9fa;
        border-bottom: 1px solid #e0e0e0;
        overflow-x: auto;
    }
    
    .mobile-tab {
        padding: 12px 16px;
        background: #e9ecef;
        border-right: 1px solid #dee2e6;
        cursor: pointer;
        min-width: 120px;
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
    }
    
    .mobile-tab.active {
        background: white;
        border-bottom: 2px solid #007bff;
    }
    
    .tab-close-mobile {
        margin-left: auto;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

class MobileBrowserSimulator:
    def __init__(self):
        self.session = requests.Session()
        # User Agent لمحاكاة الهاتف
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
        })
        self.current_url = ""
        self.tabs = [{"id": 1, "title": "علامة تبويب جديدة", "url": "", "favicon": "🌐", "content": ""}]
        self.active_tab = 1
        self.history = []
        self.viewport_width = 375  # عرض شاشة iPhone SE
        
    def navigate(self, url, tab_id=None):
        """التنقل إلى رابط في علامة تبويب محددة"""
        if not url:
            return False
            
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
            # إنشاء صفحة خطأ للجوال
            error_content = self.create_mobile_error_page(str(e), url)
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
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            title = soup.title
            return title.string.strip() if title and title.string else "بدون عنوان"
        except:
            return "بدون عنوان"
    
    def extract_favicon(self, html_content, base_url):
        """استخراج الأيقونة"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            favicon = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
            if favicon and favicon.get('href'):
                return favicon['href']
        except:
            pass
        return "🌐"
    
    def create_mobile_error_page(self, error, url):
        """إنشاء صفحة خطأ مخصصة للجوال"""
        return f"""
        <div class="mobile-website">
            <div class="mobile-header">
                <h1>⚠️</h1>
                <h2>تعذر العثور على هذا الموقع</h2>
                <p>لا يمكن الوصول إلى {url}</p>
            </div>
            <div class="mobile-content-area">
                <div class="mobile-card">
                    <h3>تفاصيل الخطأ:</h3>
                    <p>{error}</p>
                </div>
                <div class="mobile-card">
                    <h4>جرب ما يلي:</h4>
                    <ul>
                        <li>تحقق من اتصال الشبكة</li>
                        <li>تحقق من كتابة العنوان</li>
                        <li>جرب استخدام HTTPS بدلاً من HTTP</li>
                    </ul>
                    <button class="mobile-button" onclick="window.location.reload()">إعادة المحاولة</button>
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
        return self.tabs[0] if self.tabs else None
    
    def convert_to_mobile_view(self, html_content, base_url):
        """تحويل محتوى HTML لعرضه على الجوال"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # إضافة viewport meta tag لمحاكاة الجوال
            viewport_tag = soup.new_tag('meta', attrs={'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'})
            if soup.head:
                soup.head.append(viewport_tag)
            
            # تحسين النماذج والعناصر للجوال
            for input_elem in soup.find_all(['input', 'textarea', 'select']):
                input_elem['style'] = 'font-size: 16px;'  # منع التكبير في iOS
            
            # تحسين الروابط والعناصر للجوال
            for link in soup.find_all('a'):
                link['style'] = 'min-height: 44px; display: inline-block; padding: 12px;'
            
            return str(soup)
        except Exception as e:
            return html_content

# تهيئة المتصفح في حالة الجلسة
if 'mobile_browser' not in st.session_state:
    st.session_state.mobile_browser = MobileBrowserSimulator()

# العنوان الرئيسي
st.title("📱 متصفح محاكي للهواتف")

# شريط التحكم
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("🔄", help="إعادة تحميل"):
        active_tab = st.session_state.mobile_browser.get_active_tab()
        if active_tab and active_tab['url']:
            st.session_state.mobile_browser.navigate(active_tab['url'])

with col2:
    current_url = st.session_state.mobile_browser.get_active_tab()['url'] if st.session_state.mobile_browser.get_active_tab() else ""
    new_url = st.text_input(
        "أدخل عنوان الويب:",
        value=current_url,
        placeholder="https://example.com",
        label_visibility="collapsed"
    )
    
    if new_url and new_url != current_url:
        st.session_state.mobile_browser.navigate(new_url)

with col3:
    if st.button("➕", help="علامة تبويب جديدة"):
        st.session_state.mobile_browser.add_tab()
        st.rerun()

# عرض علامات التبويب
if st.session_state.mobile_browser.tabs:
    st.markdown("### علامات التبويب المفتوحة:")
    cols = st.columns(len(st.session_state.mobile_browser.tabs))
    for idx, tab in enumerate(st.session_state.mobile_browser.tabs):
        with cols[idx]:
            tab_label = f"{tab['favicon']} {tab['title'][:12]}..."
            is_active = "🟢" if tab['id'] == st.session_state.mobile_browser.active_tab else "⚪"
            
            if st.button(f"{is_active} {tab_label}", key=f"mobile_tab_{tab['id']}", use_container_width=True):
                st.session_state.mobile_browser.active_tab = tab['id']
                st.rerun()

# متصفح الهاتف المحاكي
st.markdown("### 📱 شاشة الهاتف:")

# حاوية متصفح الهاتف
st.markdown("""
<div class="mobile-browser-container">
    <div class="mobile-screen">
        <div class="status-bar">
            <div class="status-time" id="currentTime">14:30</div>
            <div class="status-icons">
                <span>📶</span>
                <span>📡</span>
                <span>🔋</span>
            </div>
        </div>
        
        <div class="mobile-nav-bar">
            <button class="nav-btn" onclick="handleBack()">←</button>
            <button class="nav-btn" onclick="handleForward()">→</button>
            <div class="url-bar-mobile">
                <span class="security-icon-mobile">🔒</span>
                <span id="mobileUrl">{current_url_display}</span>
            </div>
            <button class="nav-btn" onclick="handleReload()">↻</button>
        </div>
        
        <div class="mobile-content" id="mobileContent">
            {mobile_content}
        </div>
        
        <div class="mobile-toolbar">
            <button class="toolbar-btn" onclick="handleHome()">🏠</button>
            <button class="toolbar-btn" onclick="handleBack()">◀</button>
            <button class="toolbar-btn" onclick="handleForward()">▶</button>
            <button class="toolbar-btn" onclick="handleTabs()">📑</button>
            <button class="toolbar-btn" onclick="handleMenu()">⋯</button>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# JavaScript لتحديث الوقت ومحاكاة الأحداث
st.markdown("""
<script>
// تحديث الوقت
function updateTime() {
    const now = new Date();
    const timeString = now.getHours().toString().padStart(2, '0') + ':' + 
                      now.getMinutes().toString().padStart(2, '0');
    document.getElementById('currentTime').textContent = timeString;
}

// تحديث الوقت كل دقيقة
setInterval(updateTime, 60000);
updateTime();

// محاكاة أحداث المتصفح
function handleBack() {
    alert('زر الرجوع - تحت التطوير');
}

function handleForward() {
    alert('زر التقدم - تحت التطوير');
}

function handleReload() {
    window.location.reload();
}

function handleHome() {
    window.location.href = window.location.pathname;
}

function handleTabs() {
    alert('إدارة العلامات - تحت التطوير');
}

function handleMenu() {
    alert('القائمة - تحت التطوير');
}

// محاكاة التمرير السلس للجوال
document.addEventListener('touchstart', function(e) {
    // إضافة تأثيرات اللمس
});

// تحديث رابط الجوال
function updateMobileUrl(url) {
    const urlElement = document.getElementById('mobileUrl');
    if (urlElement && url) {
        // تقصير الرابط لعرضه بشكل أفضل
        const shortUrl = url.length > 25 ? url.substring(0, 25) + '...' : url;
        urlElement.textContent = shortUrl;
    }
}

// تحديث المحتوى
function updateMobileContent(content) {
    const contentElement = document.getElementById('mobileContent');
    if (contentElement) {
        contentElement.innerHTML = content;
    }
}
</script>
""", unsafe_allow_html=True)

# تحديث محتوى المتصفح
active_tab = st.session_state.mobile_browser.get_active_tab()
current_url_display = active_tab['url'] if active_tab and active_tab['url'] else "about:blank"

if active_tab and active_tab['content']:
    # معالجة المحتوى لعرضه على الجوال
    mobile_content = st.session_state.mobile_browser.convert_to_mobile_view(active_tab['content'], active_tab['url'])
    
    # استخراج وعرض المحتوى بطريقة مناسبة للجوال
    try:
        soup = BeautifulSoup(mobile_content, 'html.parser')
        
        # إزالة scripts وstyles معقدة
        for script in soup(["script", "style", "iframe"]):
            script.decompose()
        
        # تحسين الصور للجوال
        for img in soup.find_all('img'):
            img['style'] = 'max-width: 100%; height: auto;'
        
        # تحسين الجداول للجوال
        for table in soup.find_all('table'):
            table['style'] = 'width: 100%; overflow-x: auto; display: block;'
        
        mobile_content = str(soup)
        
    except Exception as e:
        mobile_content = f"""
        <div class="mobile-website">
            <div class="mobile-content-area">
                <div class="mobile-card">
                    <h3>محتوى الصفحة:</h3>
                    <p>تم تحميل الصفحة بنجاح ولكن قد يكون هناك بعض مشاكل التنسيق.</p>
                </div>
            </div>
        </div>
        """
else:
    # الصفحة الافتراضية للجوال
    mobile_content = """
    <div class="mobile-website">
        <div class="mobile-header">
            <h1>📱</h1>
            <h2>متصفح الجوال المحاكي</h2>
            <p>أدخل عنوان URL لبدء التصفح</p>
        </div>
        
        <div class="mobile-content-area">
            <div class="mobile-card">
                <h3>مواقع مقترحة:</h3>
                <button class="mobile-button" onclick="window.location.href='?url=google.com'">Google</button>
                <button class="mobile-button" onclick="window.location.href='?url=wikipedia.org'">Wikipedia</button>
                <button class="mobile-button" onclick="window.location.href='?url=github.com'">GitHub</button>
            </div>
            
            <div class="mobile-card">
                <h3>مميزات المتصفح:</h3>
                <ul>
                    <li>تصميم متجاوب للجوال</li>
                    <li>محرك تصفح حقيقي</li>
                    <li>علامات تبويب متعددة</li>
                    <li>سجل التصفح</li>
                </ul>
            </div>
        </div>
        
        <div class="mobile-footer">
            <p>المتصفح المحاكي للجوال v1.0</p>
        </div>
    </div>
    """

# تحديث JavaScript بالمحتوى الفعلي
st.markdown(f"""
<script>
updateMobileUrl("{current_url_display}");
updateMobileContent(`{mobile_content}`);
</script>
""", unsafe_allow_html=True)

# لوحة التحكم الجانبية
with st.sidebar:
    st.header("🎮 تحكم الجوال")
    
    st.subheader("إعدادات الشاشة")
    screen_size = st.selectbox("حجم الشاشة:", ["iPhone SE (375x667)", "iPhone 12 (390x844)", "Samsung Galaxy (412x915)"])
    
    st.subheader("إدارة العلامات")
    for tab in st.session_state.mobile_browser.tabs:
        if st.button(f"إغلاق {tab['title'][:15]}...", key=f"close_{tab['id']}"):
            st.session_state.mobile_browser.close_tab(tab['id'])
            st.rerun()
    
    st.subheader("سجل التصفح")
    if st.session_state.mobile_browser.history:
        for visit in reversed(st.session_state.mobile_browser.history[-5:]):
            if st.button(f"📄 {visit['title'][:20]}...", key=f"history_{visit['timestamp']}"):
                st.session_state.mobile_browser.navigate(visit['url'])
                st.rerun()
    else:
        st.info("لا يوجد سجل تصفح")
    
    st.subheader("أدوات المطور")
    if st.button("مسح الذاكرة المؤقتة"):
        st.session_state.mobile_browser.session.cookies.clear()
        st.success("تم مسح الذاكرة المؤقتة")
    
    if st.button("إعادة تعيين المتصفح"):
        st.session_state.mobile_browser = MobileBrowserSimulator()
        st.success("تم إعادة التعيين")
        st.rerun()

# معلومات إضافية
with st.expander("📊 إحصائيات المتصفح"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("العلامات المفتوحة", len(st.session_state.mobile_browser.tabs))
    
    with col2:
        st.metric("الصفحات المزورة", len(st.session_state.mobile_browser.history))
    
    with col3:
        if active_tab:
            st.metric("الصفحة النشطة", active_tab['title'][:12] + "...")

# تذييل الصفحة
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>📱 متصفح الجوال المحاكي</strong> | تجربة تصفح حقيقية للهواتف</p>
    <p>✨ تصميم متجاوب • 🚀 أداء سريع • 📱 محاكاة واقعية</p>
</div>
""", unsafe_allow_html=True)
