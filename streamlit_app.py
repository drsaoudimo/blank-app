import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
import os
from urllib.parse import urljoin, urlparse
import json
import re
import chardet

# إعدادات الجلسة
SESSION_DIR = "/tmp/desktop_browser"
os.makedirs(SESSION_DIR, exist_ok=True)

# تثبيت CSS مع دعم كامل للغة العربية والحروف الخاصة
st.markdown("""
<style>
    /* إعدادات الخطوط العالمية */
    * {
        font-family: 'Segoe UI', 'Tahoma', 'Geneva', 'Verdana', 'Arial', sans-serif !important;
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
        font-family: 'Segoe UI', 'Tahoma', 'Arial', sans-serif !important;
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
        direction: ltr;
        text-align: left;
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
    
    /* منطقة المحتوى */
    .content-area {
        height: calc(100% - 110px);
        background: white;
        position: relative;
        overflow: auto;
    }
    
    .browser-content {
        width: 100%;
        min-height: 100%;
        background: white;
    }
    
    /* تحسينات الترميز */
    .unicode-content {
        font-family: 'Segoe UI', 'Tahoma', 'Arial', 'DejaVu Sans', sans-serif !important;
        line-height: 1.6;
    }
    
    .arabic-text {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', 'Tahoma', 'Arial', 'Times New Roman', serif !important;
    }
    
    .european-text {
        font-family: 'Segoe UI', 'Tahoma', 'Arial', 'DejaVu Sans', sans-serif !important;
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
</style>
""", unsafe_allow_html=True)

class UnicodeDesktopBrowser:
    def __init__(self):
        self.session = requests.Session()
        # User Agent مع دعم Unicode
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8,fr;q=0.7,de;q=0.6,es;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
        })
        self.tabs = [{
            "id": 1, 
            "title": "علامة تبويب جديدة", 
            "url": "", 
            "favicon": "🌐", 
            "content": "", 
            "status": "active",
            "loading": False,
            "encoding": "utf-8"
        }]
        self.active_tab = 1
        self.history = []
        self.future = []
        
    def detect_encoding(self, content):
        """كشف الترميز التلقائي للمحتوى"""
        try:
            # استخدام chardet للكشف التلقائي عن الترميز
            detected = chardet.detect(content)
            encoding = detected.get('encoding', 'utf-8')
            confidence = detected.get('confidence', 0)
            
            # إذا كانت الثقة منخفضة، نستخدم UTF-8 كافتراضي
            if confidence < 0.7:
                encoding = 'utf-8'
            
            # تحويل الترميزات المشابهة إلى القياسية
            encoding_map = {
                'iso-8859-1': 'windows-1252',
                'iso-8859-2': 'windows-1250',
                'iso-8859-6': 'windows-1256',  # للعربية
                'iso-8859-8': 'windows-1255',  # للعبرية
            }
            
            return encoding_map.get(encoding.lower(), encoding).lower()
        except:
            return 'utf-8'
    
    def convert_to_unicode(self, content, encoding):
        """تحويل المحتوى إلى Unicode"""
        try:
            if encoding.lower() == 'utf-8':
                return content.decode('utf-8', errors='replace')
            else:
                # محاولة التحويل من الترميز المحدد
                try:
                    return content.decode(encoding, errors='replace')
                except:
                    # إذا فشل، نجرب ترميزات بديلة
                    for alt_encoding in ['windows-1256', 'iso-8859-6', 'windows-1252', 'latin-1']:
                        try:
                            return content.decode(alt_encoding, errors='replace')
                        except:
                            continue
                    # إذا فشلت جميع المحاولات، نستخدم UTF-8 مع استبدال الأخطاء
                    return content.decode('utf-8', errors='replace')
        except Exception as e:
            # كملاذ أخير، نعيد النص كما هو
            try:
                return str(content, errors='replace')
            except:
                return "تعذر تحويل المحتوى إلى Unicode"
    
    def navigate_to(self, url, tab_id=None):
        """التنقل إلى رابط جديد مع دعم Unicode"""
        if not url or url.strip() == "":
            return False, "الرابط فارغ"
            
        if tab_id is None:
            tab_id = self.active_tab
            
        # تنظيف الرابط
        clean_url = url.strip()
        if not clean_url.startswith(('http://', 'https://')):
            clean_url = 'https://' + clean_url
            
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
        
        # جلب المحتوى
        success, content, encoding = self.fetch_page_content(clean_url)
        
        # تحديث علامة التبويب
        for tab in self.tabs:
            if tab['id'] == tab_id:
                tab['loading'] = False
                tab['content'] = content
                tab['encoding'] = encoding
                if success:
                    tab['title'] = self.extract_page_title(content) or parsed.netloc
                else:
                    tab['title'] = "خطأ في التحميل"
                break
                
        return success, "تم التحميل بنجاح" if success else content
    
    def fetch_page_content(self, url):
        """جلب محتوى الصفحة مع دعم Unicode"""
        try:
            # جلب المحتوى كـ bytes
            response = self.session.get(url, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            # كشف الترميز
            encoding = self.detect_encoding(response.content)
            
            # إذا كان الترميز معروفاً في رأس الاستجابة، نستخدمه
            if response.encoding:
                encoding = response.encoding
            
            # تحويل المحتوى إلى Unicode
            content = self.convert_to_unicode(response.content, encoding)
            
            return True, content, encoding
            
        except requests.exceptions.Timeout:
            error_msg = "⏰ انتهت مهلة الاتصال"
            return False, error_msg, 'utf-8'
        except requests.exceptions.ConnectionError:
            error_msg = "🔌 تعذر الاتصال بالخادم"
            return False, error_msg, 'utf-8'
        except requests.exceptions.HTTPError as e:
            error_msg = f"🌐 خطأ HTTP: {e.response.status_code}"
            return False, error_msg, 'utf-8'
        except Exception as e:
            error_msg = f"❌ خطأ غير متوقع: {str(e)}"
            return False, error_msg, 'utf-8'
    
    def extract_page_title(self, html_content):
        """استخراج عنوان الصفحة مع دعم Unicode"""
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
    
    def process_content_for_display(self, html_content, base_url, encoding):
        """معالجة المحتوى لعرض Unicode"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # إضافة meta charset لضمان عرض Unicode بشكل صحيح
            meta_charset = soup.new_tag('meta', charset='UTF-8')
            if soup.head:
                soup.head.insert(0, meta_charset)
            else:
                # إذا لم يكن هناك head، ننشئ واحداً
                head = soup.new_tag('head')
                head.append(meta_charset)
                soup.insert(0, head)
            
            # إضافة base href لضمان عمل الروابط
            base_tag = soup.new_tag('base', href=base_url)
            if soup.head:
                soup.head.append(base_tag)
            
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
            
            # إضافة CSS شامل لدعم Unicode
            style_tag = soup.new_tag('style')
            style_tag.string = """
                /* دعم Unicode شامل */
                * {
                    font-family: 'Segoe UI', 'Tahoma', 'Arial', 'DejaVu Sans', sans-serif !important;
                    unicode-bidi: embed;
                }
                
                body {
                    font-family: 'Segoe UI', 'Tahoma', 'Arial', 'DejaVu Sans', sans-serif !important;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    color: #242424;
                    background: white;
                    max-width: 100%;
                    overflow-x: hidden;
                    unicode-bidi: embed;
                }
                
                /* دعم اللغة العربية */
                [dir="rtl"], .arabic, :lang(ar) {
                    direction: rtl !important;
                    text-align: right !important;
                    font-family: 'Segoe UI', 'Tahoma', 'Arial', 'Times New Roman', serif !important;
                }
                
                /* دعم الحروف الأوروبية */
                .latin, :lang(fr), :lang(de), :lang(es), :lang(it) {
                    font-family: 'Segoe UI', 'Tahoma', 'Arial', 'DejaVu Sans', sans-serif !important;
                }
                
                /* تحسين عرض النصوص */
                p, div, span, li, td, th {
                    unicode-bidi: embed;
                    line-height: 1.6;
                }
                
                /* الروابط */
                a {
                    color: #0066cc;
                    text-decoration: underline;
                    cursor: pointer;
                    unicode-bidi: embed;
                }
                
                a:hover {
                    color: #004499;
                    text-decoration: none;
                }
                
                /* الصور */
                img {
                    max-width: 100%;
                    height: auto;
                    border-radius: 4px;
                }
                
                /* الجداول */
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 10px 0;
                    unicode-bidi: embed;
                }
                
                table, th, td {
                    border: 1px solid #ddd;
                }
                
                th, td {
                    padding: 8px 12px;
                    text-align: left;
                    unicode-bidi: embed;
                }
                
                th {
                    background: #f5f5f5;
                }
                
                /* النماذج */
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
                
                /* تحسينات للاستجابة */
                @media (max-width: 768px) {
                    body {
                        padding: 15px;
                        font-size: 14px;
                    }
                }
                
                /* ضمان عرض جميع الرموز */
                .unicode-fallback {
                    font-family: 'Segoe UI Symbol', 'Apple Color Emoji', 'Segoe UI Emoji', sans-serif !important;
                }
            """
            if soup.head:
                soup.head.append(style_tag)
            
            # إضافة فئة unicode للجسم
            if soup.body:
                soup.body['class'] = soup.body.get('class', []) + ['unicode-content']
            
            return str(soup)
            
        except Exception as e:
            return f"""
            <!DOCTYPE html>
            <html dir="ltr">
            <head>
                <meta charset="UTF-8">
                <title>خطأ في المعالجة</title>
                <style>
                    body {{ 
                        font-family: 'Segoe UI', Tahoma, sans-serif;
                        padding: 20px;
                        line-height: 1.6;
                        color: #242424;
                    }}
                    .error {{ 
                        background: #fef2f2;
                        border: 1px solid #fecaca;
                        color: #dc2626;
                        padding: 20px;
                        border-radius: 6px;
                    }}
                </style>
            </head>
            <body>
                <div class="error">
                    <h3>⚠️ خطأ في معالجة المحتوى</h3>
                    <p>تعذر معالجة الصفحة للعرض التفاعلي.</p>
                    <p><strong>الخطأ:</strong> {str(e)}</p>
                    <p><strong>الترميز:</strong> {encoding}</p>
                    <button onclick="window.location.reload()" style="background: #0078d4; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin-top: 10px;">
                        إعادة تحميل الصفحة
                    </button>
                </div>
            </body>
            </html>
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
            "loading": False,
            "encoding": "utf-8"
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
    st.session_state.desktop_browser = UnicodeDesktopBrowser()

# JavaScript للتفاعل
browser_js = """
<script>
// التعامل مع التنقل من المحتوى
window.addEventListener('message', function(event) {
    if (event.data.type === 'BROWSER_NAVIGATE') {
        // إرسال طلب التنقل إلى Streamlit
        const url = event.data.url;
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: url
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

// كشف اللغة وتطبيق التنسيق المناسب
function detectLanguageAndApplyStyles() {
    document.querySelectorAll('p, div, span, h1, h2, h3, h4, h5, h6').forEach(element => {
        const text = element.textContent || element.innerText;
        
        // كشف العربية
        if (/[\u0600-\u06FF]/.test(text)) {
            element.style.direction = 'rtl';
            element.style.textAlign = 'right';
            element.classList.add('arabic-text');
        }
        
        // كشف الحروف الأوروبية الخاصة
        if (/[éèêëïîíìôöóòûüùúÿýñç]/.test(text)) {
            element.classList.add('european-text');
        }
    });
}

// تطبيق الكشف عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', detectLanguageAndApplyStyles);
setTimeout(detectLanguageAndApplyStyles, 1000);
</script>
"""

# واجهة المستخدم الرئيسية
st.title("🖥️ متصفح ديسكتوب - دعم Unicode كامل")

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
            st.success("✅ تم تحميل الصفحة بنجاح")
        else:
            st.error(f"❌ {message}")
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
        <div style="display: flex; justify-content: center; align-items: center; height: 200px; flex-direction: column; gap: 15px;">
            <div style="width: 32px; height: 32px; border: 3px solid #f3f3f3; border-top: 3px solid #0078d4; border-radius: 50%; animation: spin 1s linear infinite;"></div>
            <p>جاري تحميل الصفحة...</p>
            <style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>
        </div>
        """
    elif active_tab['content']:
        display_content = browser.process_content_for_display(
            active_tab['content'], 
            active_tab['url'],
            active_tab['encoding']
        )
    else:
        display_content = """
        <!DOCTYPE html>
        <html dir="ltr">
        <head>
            <meta charset="UTF-8">
            <title>متصفح ديسكتوب</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, sans-serif;
                    padding: 40px 20px;
                    text-align: center;
                    line-height: 1.6;
                    color: #242424;
                }
                .welcome {
                    max-width: 800px;
                    margin: 0 auto;
                }
                .feature-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin: 30px 0;
                }
                .feature {
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    border: 1px solid #e9ecef;
                }
            </style>
        </head>
        <body>
            <div class="welcome">
                <h1 style="color: #0078d4; font-size: 48px; margin-bottom: 20px;">🌐</h1>
                <h2 style="color: #242424; margin-bottom: 15px;">مرحباً بك في المتصفح المحترف</h2>
                <p style="color: #666; margin-bottom: 30px; font-size: 16px; line-height: 1.6;">
                    يدعم هذا المتصفح جميع لغات العالم والرموز الخاصة<br>
                   包括中文、日本語、العربية、Français、Deutsch、Español等所有语言
                </p>
                
                <div class="feature-grid">
                    <div class="feature">
                        <h3>🔤 دعم Unicode</h3>
                        <p>يعرض جميع اللغات والرموز بشكل صحيح</p>
                    </div>
                    <div class="feature">
                        <h3>🌍 متعدد اللغات</h3>
                        <p>يدعم العربية، الإنجليزية، الفرنسية، etc.</p>
                    </div>
                    <div class="feature">
                        <h3>⚡ أداء عالي</h3>
                        <p>تحميل سريع وعرض دقيق</p>
                    </div>
                </div>
                
                <div style="margin-top: 30px; padding: 20px; background: #e7f3ff; border-radius: 8px;">
                    <h4>🔍 جرب هذه المواقع للاختبار:</h4>
                    <p style="margin: 10px 0;">
                        <strong>العربية:</strong> aljazeera.net • alarabiya.net<br>
                        <strong>Français:</strong> lemonde.fr • lefigaro.fr<br>
                        <strong>中文:</strong> baidu.com • sina.com.cn<br>
                        <strong>日本語:</strong> yahoo.co.jp • rakuten.co.jp
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

# بناء واجهة المتصفح الكاملة
desktop_html = f"""
<!DOCTYPE html>
<html dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0;">
    <div class="desktop-browser">
        <div class="title-bar">
            <div class="window-controls">
                <div class="control-btn close-btn"></div>
                <div class="control-btn minimize-btn"></div>
                <div class="control-btn maximize-btn"></div>
            </div>
            <div class="window-title">{active_tab['title'] if active_tab else 'متصفح ديسكتوب - Unicode'}</div>
        </div>
        
        <div class="toolbar">
            <button class="toolbar-btn" onclick="window.history.back()">◀ عودة</button>
            <button class="toolbar-btn" onclick="window.history.forward()">▶ تقدم</button>
            <button class="toolbar-btn" onclick="window.location.reload()">↻ إعادة تحميل</button>
            
            <div class="url-container">
                <div class="security-badge">🔒 آمن</div>
                <input type="text" class="url-bar" value="{active_tab['url'] if active_tab else ''}" readonly>
            </div>
        </div>
        
        <div class="tab-container">
            {"".join([f'''
            <div class="browser-tab {'active' if tab['id'] == browser.active_tab else ''}" 
                 onclick="window.parent.postMessage({{type: 'BROWSER_SWITCH_TAB', tabId: {tab['id']}}}, '*')">
                <span class="tab-favicon">{tab['favicon']}</span>
                <span class="tab-title">{tab['title']}</span>
            </div>
            ''' for tab in browser.tabs])}
        </div>
        
        <div class="content-area">
            <div class="browser-content">
                {display_content}
                {browser_js}
            </div>
        </div>
        
        <div class="status-bar">
            <span>✅ Unicode مدعوم - {active_tab['encoding'] if active_tab else 'UTF-8'}</span>
            <span>متصفح ديسكتوب متعدد اللغات</span>
        </div>
    </div>
</body>
</html>
"""

# عرض المتصفح
st.components.v1.html(desktop_html, height=600, scrolling=True)

# لوحة التحكم الجانبية
with st.sidebar:
    st.header("⚙️ لوحة التحكم - Unicode")
    
    st.subheader("🌐 مواقع اختبار Unicode")
    test_sites = [
        ("Al Jazeera (عربي)", "https://www.aljazeera.net"),
        ("BBC Arabic (عربي)", "https://www.bbc.com/arabic"),
        ("Le Monde (Français)", "https://www.lemonde.fr"),
        ("Der Spiegel (Deutsch)", "https://www.spiegel.de"),
        ("El País (Español)", "https://elpais.com"),
        ("百度 (中文)", "https://www.baidu.com"),
        ("Yahoo Japan (日本語)", "https://www.yahoo.co.jp"),
        ("Wikipedia Multi", "https://www.wikipedia.org"),
    ]
    
    for site_name, site_url in test_sites:
        if st.button(site_name, use_container_width=True, key=f"test_{site_name}"):
            success, message = browser.navigate_to(site_url)
            if success:
                st.success(f"✅ تم الانتقال إلى {site_name}")
            else:
                st.error(f"❌ {message}")
            st.rerun()
    
    st.subheader("🔧 أدوات Unicode")
    
    if st.button("🔄 إعادة تعيين الترميز", use_container_width=True):
        browser.session.headers.update({
            'Accept-Charset': 'UTF-8, *'
        })
        st.success("تم إعادة تعيين إعدادات الترميز")
    
    if st.button("🧹 تنظيف الذاكرة", use_container_width=True):
        browser.session.cookies.clear()
        import gc
        gc.collect()
        st.success("تم تنظيف الذاكرة")
    
    st.subheader("ℹ️ معلومات الترميز")
    if active_tab:
        st.info(f"""
        **معلومات الصفحة الحالية:**
        
        - 🔤 الترميز: {active_tab.get('encoding', 'غير معروف')}
        - 🌐 العنوان: {active_tab['title']}
        - 🔗 الرابط: {active_tab['url']}
        - 📊 حجم المحتوى: {len(active_tab['content']) if active_tab['content'] else 0} حرف
        """)

# تذييل الصفحة
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p style='font-size: 16px; font-weight: bold; color: #0078d4;'>🖥️ متصفح ديسكتوب - دعم Unicode كامل</p>
    <p style='font-size: 14px;'>يدعم جميع اللغات: العربية • Français • Deutsch • Español • 中文 • 日本語 • Русский • और भी बहुत कुछ</p>
</div>
""", unsafe_allow_html=True)
