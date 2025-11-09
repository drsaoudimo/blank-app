import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import time
import os
from urllib.parse import urljoin, urlparse
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
        background: #e0e0e0;
    }
    
    .browser-btn:hover {
        background: #d0d0d0;
        transform: scale(1.05);
    }
    
    .url-bar-container {
        flex: 1;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
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
    
    .security-icon {
        color: #4CAF50;
        font-size: 16px;
    }
    
    .browser-tabs {
        background: #f8f9fa;
        border-bottom: 1px solid #e0e0e0;
        display: flex;
        padding: 0 16px;
        overflow-x: auto;
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
    
    .website-footer {
        background: #343a40;
        color: white;
        padding: 30px 20px;
        text-align: center;
        border-radius: 8px;
        margin-top: 40px;
    }
    
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
</style>
""", unsafe_allow_html=True)

class RealBrowserSimulator:
    def __init__(self):
        self.session = requests.Session()
        self.current_url = ""
        self.tabs = [{"id": 1, "title": "علامة تبويب جديدة", "url": "", "favicon": "🌐", "content": "", "status": "active"}]
        self.active_tab = 1
        self.history = []
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
        })
    
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
            "content": "",
            "status": "active"
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

# تهيئة المتصفح في حالة الجلسة
if 'browser' not in st.session_state:
    st.session_state.browser = RealBrowserSimulator()

# العنوان الرئيسي
st.title("🌐 متصفح ويب محاكي حقيقي")

# شريط العنوان والمتصفح
st.markdown('<div class="browser-container">', unsafe_allow_html=True)

# شريط أدوات المتصفح
col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
with col1:
    st.markdown('<div class="browser-controls">', unsafe_allow_html=True)
    if st.button("←", help="السابق"):
        pass
    if st.button("→", help="التالي"):
        pass
    if st.button("↻", help="إعادة التحميل"):
        if st.session_state.browser.get_active_tab() and st.session_state.browser.get_active_tab()['url']:
            st.session_state.browser.navigate(st.session_state.browser.get_active_tab()['url'])
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # شريط العنوان
    current_url = st.session_state.browser.get_active_tab()['url'] if st.session_state.browser.get_active_tab() else ""
    url_input = st.text_input(
        "أدخل عنوان الويب",
        value=current_url,
        placeholder="https://www.example.com",
        label_visibility="collapsed"
    )
    
    # معالجة إدخال العنوان
    if url_input and url_input != current_url:
        st.session_state.browser.navigate(url_input)

with col3:
    if st.button("☆", help="الإشارات المرجعية"):
        st.info("ميزة الإشارات المرجعية قريباً!")

with col4:
    if st.button("☰", help="القائمة"):
        st.info("قائمة المتصفح")

st.markdown('</div>', unsafe_allow_html=True)

# علامات التبويب
st.markdown('<div class="browser-tabs">', unsafe_allow_html=True)

# عرض علامات التبويب الحالية
cols = st.columns(len(st.session_state.browser.tabs) + 1)
for idx, tab in enumerate(st.session_state.browser.tabs):
    with cols[idx]:
        tab_label = f"{tab['favicon']} {tab['title'][:15]}..."
        is_active = "🟢" if tab['id'] == st.session_state.browser.active_tab else "⚪"
        
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(f"{is_active} {tab_label}", key=f"tab_{tab['id']}", use_container_width=True):
                st.session_state.browser.active_tab = tab['id']
        with col2:
            if st.button("×", key=f"close_{tab['id']}", help="إغلاق علامة التبويب"):
                st.session_state.browser.close_tab(tab['id'])
                st.rerun()

# زر إضافة علامة تبويب جديدة
with cols[-1]:
    if st.button("+", help="علامة تبويب جديدة", use_container_width=True):
        st.session_state.browser.add_tab()
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# محتوى المتصفح
st.markdown('<div class="browser-content">', unsafe_allow_html=True)

active_tab = st.session_state.browser.get_active_tab()
if active_tab and active_tab['content']:
    # عرض محتوى الصفحة
    try:
        soup = BeautifulSoup(active_tab['content'], 'html.parser')
        
        # استخراج وتحسين المحتوى للعرض
        title = soup.title.string if soup.title else "بدون عنوان"
        st.subheader(title)
        
        # عرض النص الرئيسي
        texts = []
        for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            text = element.get_text(strip=True)
            if text and len(text) > 20:
                texts.append(text)
        
        for text in texts[:10]:  # عرض أول 10 نصوص فقط
            st.write(text)
            st.divider()
            
        # عرض الروابط
        links = []
        for link in soup.find_all('a', href=True):
            link_text = link.get_text(strip=True)
            if link_text:
                links.append((link_text, link['href']))
        
        if links:
            with st.expander(f"🔗 الروابط ({len(links)})"):
                for i, (text, href) in enumerate(links[:20]):
                    full_url = urljoin(active_tab['url'], href)
                    st.write(f"{i+1}. **{text}**")
                    st.caption(full_url)
                    
    except Exception as e:
        st.error(f"خطأ في معالجة المحتوى: {e}")
        st.code(active_tab['content'][:2000])
else:
    # الصفحة الافتراضية
    st.markdown("""
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
                    <p>جرب هذه المواقع:</p>
                    <ul>
                        <li><a href="#" onclick="window.location.href='?url=google.com'">Google</a></li>
                        <li><a href="#" onclick="window.location.href='?url=wikipedia.org'">Wikipedia</a></li>
                        <li><a href="#" onclick="window.location.href='?url=github.com'">GitHub</a></li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)  # إغلاق container المتصفح

# لوحة التحكم الجانبية
with st.sidebar:
    st.header("🛠️ أدوات المطور")
    
    st.subheader("علامات التبويب المفتوحة")
    for tab in st.session_state.browser.tabs:
        tab_text = f"{tab['favicon']} {tab['title'][:20]}..."
        if st.button(tab_text, key=f"sidebar_tab_{tab['id']}", use_container_width=True):
            st.session_state.browser.active_tab = tab['id']
            st.rerun()
    
    st.subheader("سجل التصفح")
    if st.session_state.browser.history:
        for i, visit in enumerate(reversed(st.session_state.browser.history[-5:])):
            if st.button(f"📄 {visit['title'][:25]}...", key=f"hist_{i}", use_container_width=True):
                st.session_state.browser.navigate(visit['url'])
                st.rerun()
    else:
        st.info("لا يوجد سجل تصفح بعد")
    
    st.subheader("أدوات متقدمة")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧹 مسح الذاكرة"):
            st.session_state.browser.session.cookies.clear()
            st.success("تم مسح الذاكرة المؤقتة")
    
    with col2:
        if st.button("🔄 إعادة تعيين"):
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
        if active_tab:
            st.metric("الصفحة النشطة", active_tab['title'][:15] + "...")
        else:
            st.metric("الصفحة النشطة", "لا يوجد")

# تذييل الصفحة
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    <p><strong>المتصفح المحاكي v2.0</strong> | محاكاة كاملة لمتصفح الويب الحقيقي</p>
    <p>⚡ يعمل داخل Streamlit • 🔒 آمن • 🌐 متعدد العلامات</p>
</div>
""", unsafe_allow_html=True)
