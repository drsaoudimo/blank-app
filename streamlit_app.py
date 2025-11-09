import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
import os
from urllib.parse import urljoin, urlparse
import json
import re

# إعدادات الجلسة
SESSION_DIR = "/tmp/desktop_browser"
os.makedirs(SESSION_DIR, exist_ok=True)

# تثبيت CSS لمتصفح ديسكتوب عالي الجودة
st.markdown("""
<style>
    /* إعادة ضبط عام */
    .main {
        padding: 0 !important;
    }
    
    /* متصفح الديسكتوب */
    .desktop-browser {
        width: 100%;
        height: 75vh;
        border: 1px solid #c0c0c0;
        border-radius: 8px;
        background: white;
        margin: 10px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        position: relative;
        overflow: hidden;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    }
    
    /* شريط العنوان */
    .title-bar {
        background: linear-gradient(180deg, #ebebeb 0%, #d5d5d5 100%);
        border-bottom: 1px solid #b0b0b0;
        padding: 4px 8px;
        display: flex;
        align-items: center;
        gap: 8px;
        height: 30px;
        user-select: none;
    }
    
    .window-controls {
        display: flex;
        gap: 6px;
    }
    
    .control-btn {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        border: none;
        cursor: pointer;
    }
    
    .close-btn { background: #ff5f57; }
    .minimize-btn { background: #ffbd2e; }
    .maximize-btn { background: #28ca42; }
    
    .window-title {
        flex: 1;
        text-align: center;
        font-size: 12px;
        color: #444;
        font-weight: 500;
    }
    
    /* شريط الأدوات */
    .toolbar {
        background: #f0f0f0;
        border-bottom: 1px solid #d0d0d0;
        padding: 6px 10px;
        display: flex;
        align-items: center;
        gap: 8px;
        height: 40px;
    }
    
    .toolbar-btn {
        background: #ffffff;
        border: 1px solid #c0c0c0;
        border-radius: 3px;
        padding: 5px 10px;
        cursor: pointer;
        font-size: 12px;
        display: flex;
        align-items: center;
        gap: 4px;
        transition: all 0.2s;
    }
    
    .toolbar-btn:hover {
        background: #f8f8f8;
        border-color: #a0a0a0;
    }
    
    .toolbar-btn:active {
        background: #e8e8e8;
    }
    
    .url-container {
        flex: 1;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .url-bar {
        flex: 1;
        background: white;
        border: 1px solid #c0c0c0;
        border-radius: 15px;
        padding: 6px 12px;
        font-size: 13px;
        outline: none;
    }
    
    .url-bar:focus {
        border-color: #0078d4;
        box-shadow: 0 0 0 1px #0078d4;
    }
    
    .security-badge {
        background: #107c10;
        color: white;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 11px;
        font-weight: 500;
    }
    
    /* علامات التبويب */
    .tab-container {
        background: #f8f8f8;
        border-bottom: 1px solid #d0d0d0;
        display: flex;
        padding: 0 8px;
        overflow-x: auto;
    }
    
    .browser-tab {
        background: #e8e8e8;
        padding: 8px 16px;
        border: 1px solid #c0c0c0;
        border-bottom: none;
        border-radius: 8px 8px 0 0;
        margin-right: 2px;
        cursor: pointer;
        min-width: 160px;
        max-width: 240px;
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 12px;
        transition: all 0.2s;
    }
    
    .browser-tab.active {
        background: white;
        border-color: #c0c0c0;
        border-bottom: 1px solid white;
        margin-bottom: -1px;
    }
    
    .tab-favicon {
        width: 14px;
        height: 14px;
        border-radius: 2px;
    }
    
    .tab-title {
        flex: 1;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        font-weight: 500;
    }
    
    .tab-close {
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background: #888;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 9px;
        cursor: pointer;
        opacity: 0.7;
    }
    
    .tab-close:hover {
        opacity: 1;
    }
    
    .new-tab-btn {
        background: transparent;
        border: none;
        padding: 8px 12px;
        font-size: 16px;
        cursor: pointer;
        color: #666;
    }
    
    /* منطقة المحتوى */
    .content-area {
        height: calc(100% - 110px);
        background: white;
        position: relative;
        overflow: hidden;
    }
    
    .browser-content {
        width: 100%;
        height: 100%;
        border: none;
        background: white;
    }
    
    /* شريط الحالة */
    .status-bar {
        background: #0078d4;
        color: white;
        padding: 3px 10px;
        font-size: 11px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    /* تحسينات للمحتوى */
    .website-content {
        width: 100%;
        min-height: 100%;
        padding: 20px;
        background: white;
        box-sizing: border-box;
    }
    
    .content-frame {
        width: 100%;
        height: 100%;
        border: none;
    }
    
    /* التحميل والرسائل */
    .loading-indicator {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
        flex-direction: column;
        gap: 15px;
        background: white;
    }
    
    .spinner {
        width: 32px;
        height: 32px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #0078d4;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .error-message {
        background: #fef2f2;
        border: 1px solid #fecaca;
        color: #dc2626;
        padding: 20px;
        border-radius: 6px;
        text-align: center;
        margin: 20px;
    }
    
    .success-message {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        color: #16a34a;
        padding: 15px;
        border-radius: 6px;
        margin: 10px;
    }
    
    /* شريط التقدم */
    .progress-bar {
        height: 3px;
        background: linear-gradient(90deg, #0078d4, #00b294);
        width: 0%;
        transition: width 0.3s ease;
        position: absolute;
        top: 0;
        left: 0;
        z-index: 1000;
    }
    
    /* تحسينات للاستجابة */
    @media (max-width: 1200px) {
        .desktop-browser {
            height: 70vh;
        }
    }
    
    @media (max-width: 768px) {
        .desktop-browser {
            height: 65vh;
        }
        
        .toolbar {
            padding: 4px 8px;
            height: 36px;
        }
        
        .toolbar-btn {
            padding: 4px 8px;
            font-size: 11px;
        }
        
        .browser-tab {
            min-width: 120px;
            padding: 6px 12px;
        }
    }
</style>
""", unsafe_allow_html=True)

class ProfessionalDesktopBrowser:
    def __init__(self):
        self.session = requests.Session()
        # User Agent حديث لمتصفح الديسكتوب
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
        })
        self.tabs = [{
            "id": 1, 
            "title": "علامة تبويب جديدة", 
            "url": "", 
            "favicon": "🌐", 
            "content": "", 
            "status": "active",
            "loading": False
        }]
        self.active_tab = 1
        self.history = []
        self.future = []
        self.loading_progress = 0
        
    def navigate_to(self, url, tab_id=None):
        """التنقل إلى رابط جديد مع ضمان الجودة"""
        if not url or url.strip() == "":
            return False, "الرابط فارغ"
            
        if tab_id is None:
            tab_id = self.active_tab
            
        # تنظيف الرابط
        clean_url = url.strip()
        if not clean_url.startswith(('http://', 'https://')):
            clean_url = 'https://' + clean_url
            
        # التحقق من صحة الرابط
        try:
            parsed = urlparse(clean_url)
            if not parsed.netloc:
                return False, "رابط غير صالح"
        except:
            return False, "رابط غير صالح"
        
        # بدء التحميل
        for tab in self.tabs:
            if tab['id'] == tab_id:
                tab['loading'] = True
                tab['url'] = clean_url
                break
                
        # إضافة للسجل
        if any(tab['id'] == tab_id for tab in self.tabs):
            current_tab = self.get_tab_by_id(tab_id)
            if current_tab and current_tab.get('url'):
                self.history.append({
                    'url': current_tab['url'],
                    'title': current_tab['title'],
                    'timestamp': time.time()
                })
                self.future.clear()
        
        # محاكاة شريط التقدم
        self.simulate_loading()
        
        # جلب المحتوى
        success, content = self.fetch_page_content(clean_url)
        
        # تحديث علامة التبويب
        for tab in self.tabs:
            if tab['id'] == tab_id:
                tab['loading'] = False
                tab['content'] = content
                if success:
                    tab['title'] = self.extract_page_title(content) or parsed.netloc
                else:
                    tab['title'] = "خطأ في التحميل"
                break
                
        return success, "تم التحميل بنجاح" if success else content
    
    def simulate_loading(self):
        """محاكاة شريط تقدم التحميل"""
        self.loading_progress = 0
        # في تطبيق حقيقي، يمكن استخدام مؤشر تقدم حقيقي
    
    def fetch_page_content(self, url):
        """جلب محتوى الصفحة بجودة عالية"""
        try:
            response = self.session.get(url, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            # التحقق من نوع المحتوى
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                return False, "هذا النوع من المحتوى غير مدعوم"
                
            return True, response.text
            
        except requests.exceptions.Timeout:
            return False, "انتهت مهلة الاتصال"
        except requests.exceptions.ConnectionError:
            return False, "تعذر الاتصال بالخادم"
        except requests.exceptions.HTTPError as e:
            return False, f"خطأ HTTP: {e.response.status_code}"
        except Exception as e:
            return False, f"خطأ غير متوقع: {str(e)}"
    
    def extract_page_title(self, html_content):
        """استخراج عنوان الصفحة بدقة"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            title = soup.find('title')
            if title and title.string:
                return title.string.strip()
            
            # البحث في عناصر h1 إذا لم يوجد title
            h1 = soup.find('h1')
            if h1 and h1.get_text(strip=True):
                return h1.get_text(strip=True)
                
            return None
        except:
            return None
    
    def process_content_for_display(self, html_content, base_url):
        """معالجة المحتوى لعرض تفاعلي عالي الجودة"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # إضافة base href لضمان عمل الروابط
            base_tag = soup.new_tag('base', href=base_url)
            if soup.head:
                soup.head.insert(0, base_tag)
            
            # معالجة جميع الروابط لجعلها قابلة للنقر
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = urljoin(base_url, href)
                
                # جعل الروابط تفاعلية
                link['onclick'] = f'''
                event.preventDefault();
                window.parent.postMessage({{
                    type: 'BROWSER_NAVIGATE',
                    url: '{absolute_url}'
                }}, '*');
                '''
                link['style'] = 'color: #0066cc; text-decoration: underline; cursor: pointer;'
                link['title'] = f'انتقل إلى: {absolute_url}'
            
            # تحسين الصور
            for img in soup.find_all('img', src=True):
                img_src = img['src']
                absolute_src = urljoin(base_url, img_src)
                img['src'] = absolute_src
                img['style'] = 'max-width: 100%; height: auto;'
                img['loading'] = 'lazy'
            
            # تحسين النماذج
            for form in soup.find_all('form'):
                form['onsubmit'] = '''
                event.preventDefault();
                window.parent.postMessage({
                    type: 'BROWSER_FORM_SUBMIT',
                    formData: Object.fromEntries(new FormData(this)),
                    action: this.action,
                    method: this.method
                }, '*');
                return false;
                '''
            
            # إضافة CSS لتحسين العرض
            style_tag = soup.new_tag('style')
            style_tag.string = """
                body {
                    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    color: #242424;
                    background: white;
                    max-width: 100%;
                    overflow-x: hidden;
                }
                * {
                    box-sizing: border-box;
                }
                a {
                    color: #0066cc;
                    text-decoration: underline;
                    cursor: pointer;
                }
                a:hover {
                    color: #004499;
                    text-decoration: none;
                }
                img {
                    max-width: 100%;
                    height: auto;
                    border-radius: 4px;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 10px 0;
                }
                table, th, td {
                    border: 1px solid #ddd;
                }
                th, td {
                    padding: 8px 12px;
                    text-align: left;
                }
                th {
                    background: #f5f5f5;
                }
                form {
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 6px;
                    margin: 10px 0;
                }
                input, textarea, select {
                    width: 100%;
                    padding: 8px 12px;
                    margin: 5px 0;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    font-family: inherit;
                }
                button {
                    background: #0078d4;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 4px;
                    cursor: pointer;
                    margin: 5px;
                }
                button:hover {
                    background: #106ebe;
                }
                @media (max-width: 768px) {
                    body {
                        padding: 15px;
                        font-size: 14px;
                    }
                }
            """
            if soup.head:
                soup.head.append(style_tag)
            
            return str(soup)
            
        except Exception as e:
            return f"""
            <div class="error-message">
                <h3>⚠️ خطأ في معالجة المحتوى</h3>
                <p>تعذر معالجة الصفحة للعرض التفاعلي.</p>
                <p><strong>الخطأ:</strong> {str(e)}</p>
                <button onclick="window.location.reload()" style="background: #0078d4; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin-top: 10px;">
                    إعادة تحميل الصفحة
                </button>
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
            "status": "active",
            "loading": False
        })
        self.active_tab = new_tab_id
        return new_tab_id
    
    def close_tab(self, tab_id):
        """إغلاق علامة تبويب"""
        if len(self.tabs) > 1:
            self.tabs = [tab for tab in self.tabs if tab['id'] != tab_id]
            if self.active_tab == tab_id:
                self.active_tab = self.tabs[0]['id']
            return True
        return False
    
    def get_active_tab(self):
        """الحصول على علامة التبويب النشطة"""
        for tab in self.tabs:
            if tab['id'] == self.active_tab:
                return tab
        if self.tabs:
            self.active_tab = self.tabs[0]['id']
            return self.tabs[0]
        return None
    
    def get_tab_by_id(self, tab_id):
        """الحصول على علامة تبويب حسب المعرف"""
        for tab in self.tabs:
            if tab['id'] == tab_id:
                return tab
        return None

# تهيئة المتصفح
if 'desktop_browser' not in st.session_state:
    st.session_state.desktop_browser = ProfessionalDesktopBrowser()

# JavaScript للتفاعل
browser_js = """
<script>
// التعامل مع التنقل من المحتوى
window.addEventListener('message', function(event) {
    if (event.data.type === 'BROWSER_NAVIGATE') {
        // إرسال طلب التنقل إلى Streamlit
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: event.data.url
        }, '*');
    }
});

// جعل الصفحة تفاعلية
document.addEventListener('click', function(e) {
    if (e.target.tagName === 'A' && e.target.onclick) {
        e.preventDefault();
        e.target.onclick(e);
    }
});

// التعامل مع النماذج
document.addEventListener('submit', function(e) {
    if (e.target.tagName === 'FORM' && e.target.onsubmit) {
        e.preventDefault();
        e.target.onsubmit(e);
    }
});
</script>
"""

# واجهة المستخدم الرئيسية
st.title("🖥️ متصفح ديسكتوب محترف")

# شريط التحكم العلوي
col1, col2, col3, col4, col5 = st.columns([1, 1, 4, 1, 1])

with col1:
    if st.button("◀", help="العودة", use_container_width=True):
        active_tab = st.session_state.desktop_browser.get_active_tab()
        if active_tab and st.session_state.desktop_browser.history:
            st.session_state.desktop_browser.future.append({
                'url': active_tab['url'],
                'title': active_tab['title'],
                'timestamp': time.time()
            })
            last_page = st.session_state.desktop_browser.history.pop()
            st.session_state.desktop_browser.navigate_to(last_page['url'])
            st.rerun()

with col2:
    if st.button("▶", help="التقدم", use_container_width=True):
        if st.session_state.desktop_browser.future:
            next_page = st.session_state.desktop_browser.future.pop()
            st.session_state.desktop_browser.navigate_to(next_page['url'])
            st.rerun()

with col3:
    active_tab = st.session_state.desktop_browser.get_active_tab()
    current_url = active_tab['url'] if active_tab else ""
    
    url_input = st.text_input(
        "أدخل عنوان الويب:",
        value=current_url,
        placeholder="https://www.example.com",
        label_visibility="collapsed",
        key="url_input"
    )
    
    if st.button("➤ انتقل", use_container_width=True) or (url_input and url_input != current_url):
        success, message = st.session_state.desktop_browser.navigate_to(url_input)
        if success:
            st.success("تم تحميل الصفحة بنجاح")
        else:
            st.error(f"خطأ: {message}")
        st.rerun()

with col4:
    if st.button("↻", help="إعادة تحميل", use_container_width=True):
        active_tab = st.session_state.desktop_browser.get_active_tab()
        if active_tab and active_tab['url']:
            st.session_state.desktop_browser.navigate_to(active_tab['url'])
            st.rerun()

with col5:
    if st.button("➕", help="علامة تبويب جديدة", use_container_width=True):
        st.session_state.desktop_browser.add_tab()
        st.rerun()

# عرض علامات التبويب
browser = st.session_state.desktop_browser
if browser.tabs:
    st.write("**علامات التبويب النشطة:**")
    tab_cols = st.columns(len(browser.tabs) + 1)
    
    for idx, tab in enumerate(browser.tabs):
        with tab_cols[idx]:
            tab_label = f"{tab['favicon']} {tab['title'][:15]}..."
            is_active = tab['id'] == browser.active_tab
            
            if st.button(tab_label, 
                       key=f"tab_{tab['id']}", 
                       use_container_width=True,
                       type="primary" if is_active else "secondary"):
                browser.active_tab = tab['id']
                st.rerun()

# متصفح الديسكتوب
st.markdown("### نافذة المتصفح:")

# جلب المحتوى الحالي
active_tab = browser.get_active_tab()
display_content = ""

if active_tab:
    if active_tab['loading']:
        display_content = """
        <div class="loading-indicator">
            <div class="spinner"></div>
            <p>جاري تحميل الصفحة...</p>
        </div>
        """
    elif active_tab['content']:
        display_content = browser.process_content_for_display(
            active_tab['content'], 
            active_tab['url']
        )
    else:
        display_content = """
        <div class="website-content">
            <div style="text-align: center; padding: 80px 20px;">
                <h1 style="color: #0078d4; font-size: 48px; margin-bottom: 20px;">🌐</h1>
                <h2 style="color: #242424; margin-bottom: 15px;">مرحباً بك في المتصفح المحترف</h2>
                <p style="color: #666; margin-bottom: 30px; font-size: 16px; line-height: 1.6;">
                    أدخل عنوان URL في شريط العنوان أعلاه لبدء تصفح الإنترنت<br>
                    استخدم علامات التبويب لفتح عدة صفحات في وقت واحد
                </p>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; max-width: 800px; margin: 0 auto;">
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border: 1px solid #e9ecef;">
                        <h3 style="color: #242424; margin-bottom: 10px;">🔍 تصفح سريع</h3>
                        <p style="color: #666; font-size: 14px;">ابحث وانتقل لأي موقع بسهولة</p>
                    </div>
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border: 1px solid #e9ecef;">
                        <h3 style="color: #242424; margin-bottom: 10px;">📑 علامات متعددة</h3>
                        <p style="color: #666; font-size: 14px;">افتح عدة صفحات معاً</p>
                    </div>
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border: 1px solid #e9ecef;">
                        <h3 style="color: #242424; margin-bottom: 10px;">⚡ أداء عالي</h3>
                        <p style="color: #666; font-size: 14px;">تجربة تصفح سريعة وسلسة</p>
                    </div>
                </div>
            </div>
        </div>
        """

# بناء واجهة المتصفح الكاملة
desktop_html = f"""
<div class="desktop-browser">
    <div class="progress-bar" style="width: {browser.loading_progress}%"></div>
    
    <div class="title-bar">
        <div class="window-controls">
            <div class="control-btn close-btn"></div>
            <div class="control-btn minimize-btn"></div>
            <div class="control-btn maximize-btn"></div>
        </div>
        <div class="window-title">{active_tab['title'] if active_tab else 'متصفح ديسكتوب'}</div>
    </div>
    
    <div class="toolbar">
        <button class="toolbar-btn" onclick="window.history.back()">◀ عودة</button>
        <button class="toolbar-btn" onclick="window.history.forward()">▶ تقدم</button>
        <button class="toolbar-btn" onclick="window.location.reload()">↻ إعادة تحميل</button>
        
        <div class="url-container">
            <div class="security-badge">آمن</div>
            <input type="text" class="url-bar" value="{active_tab['url'] if active_tab else ''}" readonly>
        </div>
        
        <button class="toolbar-btn" onclick="window.parent.postMessage({{type: 'BROWSER_HOME'}}, '*')">🏠 رئيسية</button>
    </div>
    
    <div class="tab-container">
        {"".join([f'''
        <div class="browser-tab {'active' if tab['id'] == browser.active_tab else ''}" 
             onclick="window.parent.postMessage({{type: 'BROWSER_SWITCH_TAB', tabId: {tab['id']}}}, '*')">
            <span class="tab-favicon">{tab['favicon']}</span>
            <span class="tab-title">{tab['title']}</span>
            <span class="tab-close" onclick="event.stopPropagation(); window.parent.postMessage({{type: 'BROWSER_CLOSE_TAB', tabId: {tab['id']}}}, '*')">×</span>
        </div>
        ''' for tab in browser.tabs])}
        <button class="new-tab-btn" onclick="window.parent.postMessage({{type: 'BROWSER_NEW_TAB'}}, '*')">+</button>
    </div>
    
    <div class="content-area">
        <div class="browser-content">
            {display_content}
            {browser_js}
        </div>
    </div>
    
    <div class="status-bar">
        <span>مستعد</span>
        <span>متصفح ديسكتوب محترف</span>
    </div>
</div>
"""

# عرض المتصفح
st.components.v1.html(desktop_html, height=600, scrolling=True)

# لوحة التحكم الجانبية
with st.sidebar:
    st.header("⚙️ لوحة التحكم")
    
    st.subheader("🌐 مواقع سريعة")
    quick_sites = [
        ("Google", "https://www.google.com"),
        ("Wikipedia", "https://www.wikipedia.org"),
        ("GitHub", "https://www.github.com"),
        ("Stack Overflow", "https://stackoverflow.com"),
        ("YouTube", "https://www.youtube.com"),
        ("Amazon", "https://www.amazon.com"),
        ("Twitter", "https://twitter.com"),
        ("LinkedIn", "https://www.linkedin.com")
    ]
    
    for site_name, site_url in quick_sites:
        if st.button(site_name, use_container_width=True, key=f"quick_{site_name}"):
            success, message = browser.navigate_to(site_url)
            if success:
                st.success(f"تم الانتقال إلى {site_name}")
            else:
                st.error(f"خطأ: {message}")
            st.rerun()
    
    st.subheader("📚 سجل التصفح")
    if browser.history:
        for i, visit in enumerate(reversed(browser.history[-8:])):
            display_title = visit['title'][:25] + "..." if len(visit['title']) > 25 else visit['title']
            if st.button(f"📄 {display_title}", key=f"hist_{i}", use_container_width=True):
                browser.navigate_to(visit['url'])
                st.rerun()
    else:
        st.info("لا يوجد سجل تصفح بعد")
    
    st.subheader("🔧 أدوات متقدمة")
    
    if st.button("🧹 مسح الذاكرة المؤقتة", use_container_width=True):
        browser.session.cookies.clear()
        st.success("تم مسح الذاكرة المؤقتة")
    
    if st.button("🗑️ مسح سجل التصفح", use_container_width=True):
        browser.history.clear()
        browser.future.clear()
        st.success("تم مسح سجل التصفح")
    
    if st.button("🔄 إعادة تعيين المتصفح", use_container_width=True):
        st.session_state.desktop_browser = ProfessionalDesktopBrowser()
        st.success("تم إعادة تعيين المتصفح")
        st.rerun()
    
    st.subheader("ℹ️ معلومات")
    st.info("""
    **مميزات المتصفح:**
    
    - ✅ تنقل كامل بين الصفحات
    - 📑 علامات تبويب متعددة
    - 🔍 بحث سريع ومباشر
    - 🛡️ عرض آمن ومحمي
    - ⚡ أداء عالي وسريع
    - 💾 حفظ السجل والتاريخ
    """)

# معلومات إضافية
with st.expander("📊 إحصائيات المتصفح"):
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("علامات التبويب", len(browser.tabs))
    
    with col2:
        st.metric("الصفحات المزورة", len(browser.history))
    
    with col3:
        st.metric("الصفحات القادمة", len(browser.future))
    
    with col4:
        if active_tab:
            domain = urlparse(active_tab['url']).netloc
            st.metric("المجال الحالي", domain[:12] + "..." if len(domain) > 12 else domain)

# تذييل الصفحة
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p style='font-size: 16px; font-weight: bold; color: #0078d4;'>🖥️ متصفح ديسكتوب محترف</p>
    <p style='font-size: 14px;'>تجربة تصفح حقيقية • أداء عالي • واجهة مستخدم متطورة</p>
</div>
""", unsafe_allow_html=True)
