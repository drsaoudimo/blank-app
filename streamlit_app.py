import streamlit as st
import requests
from bs4 import BeautifulSoup
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
        overflow-y: auto;
        background: white;
        padding: 0;
        margin: 0;
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
    
    /* محاكاة محتوى الجوال */
    .mobile-website {
        width: 100%;
        min-height: 100%;
        background: white;
        padding: 15px;
        box-sizing: border-box;
    }
    
    .mobile-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 40px 20px 20px;
        text-align: center;
        border-radius: 10px;
        margin-bottom: 20px;
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
    
    .mobile-footer {
        background: #343a40;
        color: white;
        padding: 20px;
        text-align: center;
        border-radius: 10px;
        margin-top: 20px;
    }
    
    /* تحسين النص للجوال */
    .mobile-text {
        font-size: 16px;
        line-height: 1.6;
        color: #333;
    }
    
    .mobile-link {
        color: #007bff;
        text-decoration: none;
        display: block;
        padding: 10px;
        border-bottom: 1px solid #eee;
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
        self.current_url = ""
        self.tabs = [{"id": 1, "title": "علامة تبويب جديدة", "url": "", "favicon": "🌐", "content": ""}]
        self.active_tab = 1
        self.history = []
        
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
            <div class="mobile-card">
                <h3>تفاصيل الخطأ:</h3>
                <p class="mobile-text">{error}</p>
            </div>
            <div class="mobile-card">
                <h3>جرب ما يلي:</h3>
                <ul class="mobile-text">
                    <li>تحقق من اتصال الشبكة</li>
                    <li>تحقق من كتابة العنوان</li>
                    <li>جرب استخدام HTTPS بدلاً من HTTP</li>
                </ul>
            </div>
        </div>
        """
    
    def process_content_for_mobile(self, html_content, base_url):
        """معالجة المحتوى لعرضه على الجوال"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # إزالة العناصر غير المرغوب فيها
            for element in soup(["script", "style", "iframe", "nav", "header", "footer"]):
                element.decompose()
            
            # تحسين الصور
            for img in soup.find_all('img'):
                img['style'] = 'max-width: 100%; height: auto; border-radius: 8px;'
                if not img.get('alt'):
                    img['alt'] = 'صورة'
            
            # تحسين الروابط
            for link in soup.find_all('a'):
                link['style'] = 'color: #007bff; text-decoration: none; display: block; padding: 10px; border-bottom: 1px solid #eee;'
                link['class'] = 'mobile-link'
            
            # تحسين النصوص
            for text_element in soup.find_all(['p', 'span', 'div']):
                if text_element.get_text(strip=True):
                    text_element['style'] = 'font-size: 16px; line-height: 1.6; color: #333; margin: 10px 0;'
            
            # تحسين العناوين
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                heading['style'] = 'color: #333; margin: 15px 0 10px 0;'
            
            return f"""
            <div class="mobile-website">
                {str(soup)}
            </div>
            """
        except Exception as e:
            return f"""
            <div class="mobile-website">
                <div class="mobile-card">
                    <h3>محتوى الصفحة:</h3>
                    <p class="mobile-text">تم تحميل الصفحة ولكن هناك مشكلة في التنسيق.</p>
                    <p class="mobile-text">الخطأ: {str(e)}</p>
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
        """الحصول على علامة التبويب النشطة - مع معالجة الأخطاء"""
        try:
            if not self.tabs:
                # إذا لم تكن هناك علامات تبويب، إنشاء واحدة افتراضية
                self.tabs = [{"id": 1, "title": "علامة تبويب جديدة", "url": "", "favicon": "🌐", "content": ""}]
                self.active_tab = 1
            
            for tab in self.tabs:
                if tab['id'] == self.active_tab:
                    return tab
            
            # إذا لم يتم العثور على العلامة النشطة، استخدم الأولى
            self.active_tab = self.tabs[0]['id']
            return self.tabs[0]
            
        except Exception as e:
            # في حالة أي خطأ، إعادة تعيين المتصفح
            self.tabs = [{"id": 1, "title": "علامة تبويب جديدة", "url": "", "favicon": "🌐", "content": ""}]
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
            st.session_state.mobile_browser.navigate(active_tab['url'])
            st.rerun()

with col2:
    # الحصول على العنوان الحالي بشكل آمن
    active_tab = st.session_state.mobile_browser.get_active_tab()
    current_url = active_tab.get('url', '') if active_tab else ''
    
    new_url = st.text_input(
        "أدخل عنوان الويب:",
        value=current_url,
        placeholder="https://example.com",
        label_visibility="collapsed"
    )
    
    if new_url and new_url != current_url:
        st.session_state.mobile_browser.navigate(new_url)
        st.rerun()

with col3:
    if st.button("➕", help="علامة تبويب جديدة", use_container_width=True):
        st.session_state.mobile_browser.add_tab()
        st.rerun()

# عرض علامات التبويب - بشكل آمن
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

# الحصول على المحتوى الحالي بشكل آمن
active_tab = st.session_state.mobile_browser.get_active_tab()

# القيم الافتراضية الآمنة
current_url_display = ""
mobile_content = ""

if active_tab:
    current_url_display = active_tab.get('url', '')
    if active_tab.get('content'):
        mobile_content = st.session_state.mobile_browser.process_content_for_mobile(
            active_tab['content'], active_tab.get('url', '')
        )
    else:
        # الصفحة الافتراضية للجوال
        mobile_content = """
        <div class="mobile-website">
            <div class="mobile-header">
                <h1>📱</h1>
                <h2>متصفح الجوال المحاكي</h2>
                <p>أدخل عنوان URL لبدء التصفح</p>
            </div>
            
            <div class="mobile-card">
                <h3>مواقع مقترحة:</h3>
                <div style="display: flex; flex-direction: column; gap: 10px;">
                    <a href="#" class="mobile-link" onclick="alert('Google - اضغط على زر التصفح أعلاه')">Google</a>
                    <a href="#" class="mobile-link" onclick="alert('Wikipedia - اضغط على زر التصفح أعلاه')">Wikipedia</a>
                    <a href="#" class="mobile-link" onclick="alert('GitHub - اضغط على زر التصفح أعلاه')">GitHub</a>
                </div>
            </div>
            
            <div class="mobile-card">
                <h3>مميزات المتصفح:</h3>
                <ul class="mobile-text">
                    <li>تصميم متجاوب للجوال</li>
                    <li>محرك تصفح حقيقي</li>
                    <li>علامات تبويب متعددة</li>
                    <li>سجل التصفح</li>
                </ul>
            </div>
            
            <div class="mobile-footer">
                <p>المتصفح المحاكي للجوال v2.0</p>
            </div>
        </div>
        """
else:
    # حالة الطوارئ عندما لا يكون هناك علامات تبويب
    mobile_content = """
    <div class="mobile-website">
        <div class="mobile-header">
            <h1>⚠️</h1>
            <h2>خطأ في المتصفح</h2>
            <p>انقر على زر إعادة التعيين في الشريط الجانبي</p>
        </div>
    </div>
    """

# تقصير الرابط للعرض
short_url = current_url_display[:25] + "..." if len(current_url_display) > 25 else current_url_display

# بناء واجهة الهاتف كاملة
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
            <button class="nav-btn" onclick="window.location.reload()">←</button>
            <button class="nav-btn" onclick="window.location.reload()">→</button>
            <div class="url-bar-mobile">
                <span class="security-icon-mobile">🔒</span>
                <span>{short_url or 'about:blank'}</span>
            </div>
            <button class="nav-btn" onclick="window.location.reload()">↻</button>
        </div>
        
        <div class="mobile-content">
            {mobile_content}
        </div>
        
        <div class="mobile-toolbar">
            <button class="toolbar-btn" onclick="window.location.href=window.location.pathname">🏠</button>
            <button class="toolbar-btn" onclick="window.location.reload()">◀</button>
            <button class="toolbar-btn" onclick="window.location.reload()">▶</button>
            <button class="toolbar-btn" onclick="alert('إدارة العلامات')">📑</button>
            <button class="toolbar-btn" onclick="alert('القائمة')">⋯</button>
        </div>
    </div>
</div>
"""

# عرض متصفح الهاتف باستخدام st.components.v1.html
try:
    st.components.v1.html(mobile_html, height=700)
except Exception as e:
    st.error(f"خطأ في عرض المتصفح: {e}")
    # عرض بديل في حالة الخطأ
    st.info("""
    **عذراً، هناك مشكلة في عرض متصفح الهاتف المحاكي.**
    
    جرب:
    1. تحديث الصفحة
    2. استخدام زر إعادة التعيين في الشريط الجانبي
    3. التحقق من اتصال الإنترنت
    """)

# لوحة التحكم الجانبية
with st.sidebar:
    st.header("🎮 تحكم الجوال")
    
    st.subheader("إعدادات الشاشة")
    screen_size = st.selectbox("حجم الشاشة:", 
                              ["iPhone SE (375x667)", "iPhone 12 (390x844)", "Samsung Galaxy (412x915)"])
    
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
    
    st.subheader("أدوات المطور")
    if st.button("🧹 مسح الذاكرة المؤقتة"):
        if hasattr(st.session_state.mobile_browser, 'session'):
            st.session_state.mobile_browser.session.cookies.clear()
        st.success("تم مسح الذاكرة المؤقتة")
    
    if st.button("🔄 إعادة تعيين المتصفح"):
        st.session_state.mobile_browser = MobileBrowserSimulator()
        st.success("تم إعادة التعيين")
        st.rerun()

# معلومات إضافية
with st.expander("📊 إحصائيات المتصفح"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tabs_count = len(st.session_state.mobile_browser.tabs) if hasattr(st.session_state.mobile_browser, 'tabs') else 0
        st.metric("العلامات المفتوحة", tabs_count)
    
    with col2:
        history_count = len(st.session_state.mobile_browser.history) if hasattr(st.session_state.mobile_browser, 'history') else 0
        st.metric("الصفحات المزورة", history_count)
    
    with col3:
        active_tab = st.session_state.mobile_browser.get_active_tab()
        if active_tab:
            title = active_tab.get('title', 'بدون عنوان')[:10] + "..."
            st.metric("الصفحة النشطة", title)
        else:
            st.metric("الصفحة النشطة", "لا يوجد")

# تذييل الصفحة
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>📱 متصفح الجوال المحاكي</strong> | تجربة تصفح حقيقية للهواتف</p>
    <p>✨ تصميم متجاوب • 🚀 أداء سريع • 📱 محاكاة واقعية</p>
</div>
""", unsafe_allow_html=True)
