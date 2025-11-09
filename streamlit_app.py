import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
import os
from urllib.parse import urljoin, urlparse
import json
import re
import chardet
from collections import Counter

# إعدادات الجلسة
SESSION_DIR = "/tmp/desktop_browser"
os.makedirs(SESSION_DIR, exist_ok=True)

# تثبيت CSS مع تحسينات كشف الروابط
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
    
    /* لوحة كشف الروابط */
    .links-panel {
        background: #f8f9fa;
        border-left: 1px solid #dee2e6;
        width: 300px;
        height: 100%;
        overflow-y: auto;
        position: absolute;
        right: 0;
        top: 0;
        z-index: 100;
        transition: transform 0.3s ease;
    }
    
    .links-panel.hidden {
        transform: translateX(100%);
    }
    
    .links-header {
        background: #0078d4;
        color: white;
        padding: 12px 15px;
        display: flex;
        justify-content: between;
        align-items: center;
    }
    
    .links-list {
        padding: 10px;
    }
    
    .link-item {
        padding: 8px 10px;
        margin: 5px 0;
        background: white;
        border: 1px solid #e9ecef;
        border-radius: 5px;
        cursor: pointer;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .link-item:hover {
        background: #e3f2fd;
        border-color: #0078d4;
    }
    
    .link-icon {
        width: 16px;
        height: 16px;
        flex-shrink: 0;
    }
    
    .link-text {
        flex: 1;
        font-size: 12px;
        line-height: 1.3;
        word-break: break-word;
    }
    
    .link-url {
        font-size: 10px;
        color: #666;
        margin-top: 2px;
    }
    
    .link-badge {
        background: #28a745;
        color: white;
        padding: 1px 6px;
        border-radius: 10px;
        font-size: 10px;
        margin-left: auto;
    }
    
    /* فئات الروابط */
    .link-internal { border-left: 3px solid #28a745; }
    .link-external { border-left: 3px solid #dc3545; }
    .link-pdf { border-left: 3px solid #e74c3c; }
    .link-image { border-left: 3px solid #3498db; }
    .link-document { border-left: 3px solid #9b59b6; }
    
    /* زر تبديل لوحة الروابط */
    .links-toggle {
        position: absolute;
        right: 10px;
        top: 50%;
        transform: translateY(-50%);
        background: #0078d4;
        color: white;
        border: none;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        cursor: pointer;
        z-index: 101;
        display: flex;
        align-items: center;
        justify-content: center;
    }
</style>
""", unsafe_allow_html=True)

class AdvancedDesktopBrowser:
    def __init__(self):
        self.session = requests.Session()
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
            "encoding": "utf-8",
            "links": [],
            "links_analysis": {}
        }]
        self.active_tab = 1
        self.history = []
        self.future = []
        self.show_links_panel = True
        
    def detect_encoding(self, content):
        """كشف الترميز التلقائي للمحتوى"""
        try:
            detected = chardet.detect(content)
            encoding = detected.get('encoding', 'utf-8')
            confidence = detected.get('confidence', 0)
            
            if confidence < 0.7:
                encoding = 'utf-8'
            
            encoding_map = {
                'iso-8859-1': 'windows-1252',
                'iso-8859-2': 'windows-1250',
                'iso-8859-6': 'windows-1256',
                'iso-8859-8': 'windows-1255',
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
                try:
                    return content.decode(encoding, errors='replace')
                except:
                    for alt_encoding in ['windows-1256', 'iso-8859-6', 'windows-1252', 'latin-1']:
                        try:
                            return content.decode(alt_encoding, errors='replace')
                        except:
                            continue
                    return content.decode('utf-8', errors='replace')
        except Exception as e:
            try:
                return str(content, errors='replace')
            except:
                return "تعذر تحويل المحتوى إلى Unicode"
    
    def extract_links(self, html_content, base_url):
        """استخراج وتحليل جميع الروابط من الصفحة"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            links = []
            domains_counter = Counter()
            
            # استخراج جميع الروابط
            for link in soup.find_all('a', href=True):
                href = link['href']
                link_text = link.get_text(strip=True)
                
                if not href or href.startswith(('javascript:', 'mailto:', 'tel:')):
                    continue
                
                # تحويل الرابط إلى رابط مطلق
                absolute_url = urljoin(base_url, href)
                parsed_url = urlparse(absolute_url)
                domain = parsed_url.netloc
                
                # تحديد نوع الرابط
                link_type = self.classify_link(absolute_url, base_url)
                
                # إعداد بيانات الرابط
                link_data = {
                    'url': absolute_url,
                    'text': link_text or 'رابط بدون نص',
                    'domain': domain,
                    'type': link_type,
                    'icon': self.get_link_icon(link_type)
                }
                
                links.append(link_data)
                domains_counter[domain] += 1
            
            # تحليل إضافي للروابط
            analysis = {
                'total_links': len(links),
                'internal_links': len([l for l in links if l['type'] == 'internal']),
                'external_links': len([l for l in links if l['type'] == 'external']),
                'top_domains': domains_counter.most_common(5),
                'link_types': Counter([l['type'] for l in links]),
                'links_by_domain': dict(domains_counter)
            }
            
            return links, analysis
            
        except Exception as e:
            return [], {
                'total_links': 0,
                'internal_links': 0,
                'external_links': 0,
                'top_domains': [],
                'link_types': {},
                'links_by_domain': {}
            }
    
    def classify_link(self, link_url, base_url):
        """تصنيف الروابط حسب النوع"""
        base_domain = urlparse(base_url).netloc
        link_domain = urlparse(link_url).netloc
        
        if link_domain == base_domain:
            return 'internal'
        elif link_url.lower().endswith(('.pdf', '.PDF')):
            return 'pdf'
        elif link_url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')):
            return 'image'
        elif link_url.lower().endswith(('.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx')):
            return 'document'
        elif link_url.lower().endswith(('.zip', '.rar', '.7z', '.tar', '.gz')):
            return 'archive'
        else:
            return 'external'
    
    def get_link_icon(self, link_type):
        """الحصول على أيقونة مناسبة لنوع الرابط"""
        icons = {
            'internal': '🔗',
            'external': '🌐',
            'pdf': '📄',
            'image': '🖼️',
            'document': '📎',
            'archive': '📦'
        }
        return icons.get(link_type, '🔗')
    
    def navigate_to(self, url, tab_id=None):
        """التنقل إلى رابط جديد مع استخراج الروابط"""
        if not url or url.strip() == "":
            return False, "الرابط فارغ"
            
        if tab_id is None:
            tab_id = self.active_tab
            
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
        
        # جلب المحتوى واستخراج الروابط
        success, content, encoding = self.fetch_page_content(clean_url)
        
        if success:
            # استخراج وتحليل الروابط
            links, analysis = self.extract_links(content, clean_url)
        else:
            links, analysis = [], {}
        
        # تحديث علامة التبويب
        for tab in self.tabs:
            if tab['id'] == tab_id:
                tab['loading'] = False
                tab['content'] = content
                tab['encoding'] = encoding
                tab['links'] = links
                tab['links_analysis'] = analysis
                if success:
                    tab['title'] = self.extract_page_title(content) or parsed.netloc
                else:
                    tab['title'] = "خطأ في التحميل"
                break
                
        return success, "تم التحميل بنجاح" if success else content
    
    def fetch_page_content(self, url):
        """جلب محتوى الصفحة مع دعم Unicode"""
        try:
            response = self.session.get(url, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            encoding = self.detect_encoding(response.content)
            if response.encoding:
                encoding = response.encoding
            
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
        """استخراج عنوان الصفحة"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            title = soup.find('title')
            if title and title.string:
                return title.string.strip()
            
            h1 = soup.find('h1')
            if h1 and h1.get_text(strip=True):
                return h1.get_text(strip=True)
                
            return None
        except:
            return None
    
    def process_content_for_display(self, html_content, base_url, encoding):
        """معالجة المحتوى لعرض تفاعلي"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # إضافة meta charset
            meta_charset = soup.new_tag('meta', charset='UTF-8')
            if soup.head:
                soup.head.insert(0, meta_charset)
            else:
                head = soup.new_tag('head')
                head.append(meta_charset)
                soup.insert(0, head)
            
            # إضافة base href
            base_tag = soup.new_tag('base', href=base_url)
            if soup.head:
                soup.head.append(base_tag)
            
            # جعل الروابط قابلة للنقر
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = urljoin(base_url, href)
                
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
            
            # إضافة CSS شامل
            style_tag = soup.new_tag('style')
            style_tag.string = """
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
                
                [dir="rtl"], .arabic, :lang(ar) {
                    direction: rtl !important;
                    text-align: right !important;
                    font-family: 'Segoe UI', 'Tahoma', 'Arial', 'Times New Roman', serif !important;
                }
                
                .latin, :lang(fr), :lang(de), :lang(es), :lang(it) {
                    font-family: 'Segoe UI', 'Tahoma', 'Arial', 'DejaVu Sans', sans-serif !important;
                }
                
                p, div, span, li, td, th {
                    unicode-bidi: embed;
                    line-height: 1.6;
                }
                
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
                
                img {
                    max-width: 100%;
                    height: auto;
                    border-radius: 4px;
                }
                
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
                
                @media (max-width: 768px) {
                    body {
                        padding: 15px;
                        font-size: 14px;
                    }
                }
            """
            if soup.head:
                soup.head.append(style_tag)
            
            if soup.body:
                soup.body['class'] = soup.body.get('class', []) + ['unicode-content']
            
            return str(soup)
            
        except Exception as e:
            return f"""
            <div style="background: #fef2f2; border: 1px solid #fecaca; color: #dc2626; padding: 20px; border-radius: 6px; text-align: center;">
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
            "loading": False,
            "encoding": "utf-8",
            "links": [],
            "links_analysis": {}
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
    st.session_state.desktop_browser = AdvancedDesktopBrowser()

if 'show_links_panel' not in st.session_state:
    st.session_state.show_links_panel = True

# JavaScript للتفاعل
browser_js = """
<script>
// التعامل مع التنقل من المحتوى
window.addEventListener('message', function(event) {
    if (event.data.type === 'BROWSER_NAVIGATE') {
        const url = event.data.url;
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: url
        }, '*');
    }
    
    if (event.data.type === 'TOGGLE_LINKS_PANEL') {
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: 'toggle_links_panel'
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
        
        if (/[\u0600-\u06FF]/.test(text)) {
            element.style.direction = 'rtl';
            element.style.textAlign = 'right';
            element.classList.add('arabic-text');
        }
        
        if (/[éèêëïîíìôöóòûüùúÿýñç]/.test(text)) {
            element.classList.add('european-text');
        }
    });
}

document.addEventListener('DOMContentLoaded', detectLanguageAndApplyStyles);
setTimeout(detectLanguageAndApplyStyles, 1000);
</script>
"""

# واجهة المستخدم الرئيسية
st.title("🖥️ متصفح ديسكتوب - مع كشف الروابط المتقدم")

# شريط التحكم العلوي
col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 4, 1, 1, 1])

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
    if st.button("🔍", help="كشف الروابط", use_container_width=True):
        st.session_state.show_links_panel = not st.session_state.show_links_panel
        st.rerun()

with col6:
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
            <div style="max-width: 800px; margin: 0 auto;">
                <h1 style="color: #0078d4; font-size: 48px; margin-bottom: 20px;">🌐</h1>
                <h2 style="color: #242424; margin-bottom: 15px;">مرحباً بك في المتصفح المتقدم</h2>
                <p style="color: #666; margin-bottom: 30px; font-size: 16px; line-height: 1.6;">
                    متصفح ديسكتوب متكامل مع نظام كشف الروابط الذكي<br>
                    يعرض جميع الروابط في الصفحة ويصنفها لتسهيل التصفح
                </p>
                
                <div class="feature-grid">
                    <div class="feature">
                        <h3>🔍 كشف الروابط</h3>
                        <p>اكتشاف تلقائي لجميع الروابط في الصفحة</p>
                    </div>
                    <div class="feature">
                        <h3>📊 تحليل متقدم</h3>
                        <p>إحصائيات مفصلة عن أنواع الروابط</p>
                    </div>
                    <div class="feature">
                        <h3>⚡ تصفح سريع</h3>
                        <p>انتقال فوري لأي رابط بنقرة واحدة</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

# بناء لوحة الروابط
links_panel_html = ""
if active_tab and active_tab.get('links') and st.session_state.show_links_panel:
    links = active_tab['links']
    analysis = active_tab.get('links_analysis', {})
    
    links_panel_html = f"""
    <div class="links-panel">
        <div class="links-header">
            <strong>🔗 روابط الصفحة ({analysis.get('total_links', 0)})</strong>
        </div>
        <div class="links-list">
            {"".join([f'''
            <div class="link-item link-{link['type']}" 
                 onclick="window.parent.postMessage({{type: 'BROWSER_NAVIGATE', url: '{link['url']}'}}, '*')">
                <span class="link-icon">{link['icon']}</span>
                <div class="link-text">
                    {link['text']}
                    <div class="link-url">{link['domain']}</div>
                </div>
            </div>
            ''' for link in links[:50]])}  {/* عرض أول 50 رابط فقط */}
            {f'<div style="text-align: center; color: #666; font-size: 12px; padding: 10px;">... وعرض {len(links) - 50} روابط إضافية</div>' if len(links) > 50 else ''}
        </div>
    </div>
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
            <div class="window-title">{active_tab['title'] if active_tab else 'متصفح ديسكتوب - كشف الروابط'}</div>
        </div>
        
        <div class="toolbar">
            <button class="toolbar-btn" onclick="window.history.back()">◀ عودة</button>
            <button class="toolbar-btn" onclick="window.history.forward()">▶ تقدم</button>
            <button class="toolbar-btn" onclick="window.location.reload()">↻ إعادة تحميل</button>
            
            <div class="url-container">
                <div class="security-badge">🔒 آمن</div>
                <input type="text" class="url-bar" value="{active_tab['url'] if active_tab else ''}" readonly>
            </div>
            
            <button class="toolbar-btn" onclick="window.parent.postMessage({{type: 'TOGGLE_LINKS_PANEL'}}, '*')">
                🔍 كشف الروابط
            </button>
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
            {links_panel_html}
        </div>
    </div>
</body>
</html>
"""

# عرض المتصفح
st.components.v1.html(desktop_html, height=600, scrolling=True)

# لوحة التحكم الجانبية مع تحليل الروابط
with st.sidebar:
    st.header("📊 تحليل الروابط")
    
    if active_tab and active_tab.get('links_analysis'):
        analysis = active_tab['links_analysis']
        links = active_tab.get('links', [])
        
        # إحصائيات سريعة
        col1, col2 = st.columns(2)
        with col1:
            st.metric("إجمالي الروابط", analysis.get('total_links', 0))
        with col2:
            st.metric("روابط داخلية", analysis.get('internal_links', 0))
        
        col3, col4 = st.columns(2)
        with col3:
            st.metric("روابط خارجية", analysis.get('external_links', 0))
        with col4:
            pdf_count = len([l for l in links if l['type'] == 'pdf'])
            st.metric("ملفات PDF", pdf_count)
        
        # أنواع الروابط
        st.subheader("📈 توزيع أنواع الروابط")
        if analysis.get('link_types'):
            for link_type, count in analysis['link_types'].items():
                col1, col2 = st.columns([2, 1])
                with col1:
                    type_names = {
                        'internal': '🔗 داخلية',
                        'external': '🌐 خارجية', 
                        'pdf': '📄 PDF',
                        'image': '🖼️ صور',
                        'document': '📎 مستندات',
                        'archive': '📦 أرشيف'
                    }
                    st.write(type_names.get(link_type, link_type))
                with col2:
                    st.write(f"**{count}**")
        
        # النطاقات الرئيسية
        st.subheader("🌐 النطاقات الرئيسية")
        if analysis.get('top_domains'):
            for domain, count in analysis['top_domains'][:5]:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(domain)
                with col2:
                    st.write(f"**{count}**")
        
        # تصفية الروابط
        st.subheader("🔍 تصفية الروابط")
        link_types = list(set([link['type'] for link in links]))
        selected_types = st.multiselect(
            "اختر أنواع الروابط:",
            options=link_types,
            default=link_types,
            format_func=lambda x: {
                'internal': '🔗 داخلية',
                'external': '🌐 خارجية',
                'pdf': '📄 PDF', 
                'image': '🖼️ صور',
                'document': '📎 مستندات',
                'archive': '📦 أرشيف'
            }.get(x, x)
        )
        
        # عرض الروابط المصفاة
        filtered_links = [link for link in links if link['type'] in selected_types]
        
        st.subheader(f"🔗 الروابط ({len(filtered_links)})")
        for i, link in enumerate(filtered_links[:20]):  # عرض أول 20 رابط فقط
            with st.container():
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.write(link['icon'])
                with col2:
                    if st.button(link['text'][:50] + "..." if len(link['text']) > 50 else link['text'], 
                               key=f"side_link_{i}", use_container_width=True):
                        browser.navigate_to(link['url'])
                        st.rerun()
                    st.caption(link['domain'])
                st.divider()
    
    else:
        st.info("🔍 لا توجد بيانات تحليل للرواق بعد. قم بزيارة موقع أولاً.")
    
    st.header("⚙️ أدوات متقدمة")
    
    if st.button("🔄 إعادة تحليل الروابط", use_container_width=True):
        if active_tab and active_tab['content']:
            links, analysis = browser.extract_links(active_tab['content'], active_tab['url'])
            active_tab['links'] = links
            active_tab['links_analysis'] = analysis
            st.success("✅ تم إعادة تحليل الروابط")
            st.rerun()
    
    if st.button("📋 تصدير قائمة الروابط", use_container_width=True):
        if active_tab and active_tab.get('links'):
            links_data = []
            for link in active_tab['links']:
                links_data.append({
                    'النص': link['text'],
                    'الرابط': link['url'],
                    'النوع': link['type'],
                    'النطاق': link['domain']
                })
            st.download_button(
                label="⬇️ تحميل كـ JSON",
                data=json.dumps(links_data, ensure_ascii=False, indent=2),
                file_name=f"links_{urlparse(active_tab['url']).netloc}.json",
                mime="application/json"
            )

# معلومات إضافية
with st.expander("📋 ملخص تحليل الروابط"):
    if active_tab and active_tab.get('links_analysis'):
        analysis = active_tab['links_analysis']
        st.write(f"**إجمالي الروابط المكتشفة:** {analysis.get('total_links', 0)}")
        st.write(f"**الروابط الداخلية:** {analysis.get('internal_links', 0)}")
        st.write(f"**الروابط الخارجية:** {analysis.get('external_links', 0)}")
        
        if analysis.get('top_domains'):
            st.write("**أهم النطاقات:**")
            for domain, count in analysis['top_domains'][:3]:
                st.write(f"- {domain}: {count} روابط")
    else:
        st.info("لا توجد بيانات تحليل متاحة")

# تذييل الصفحة
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p style='font-size: 16px; font-weight: bold; color: #0078d4;'>🖥️ متصفح ديسكتوب - نظام كشف الروابط المتقدم</p>
    <p style='font-size: 14px;'>اكتشاف ذكي • تحليل متقدم • تصفح أسهل</p>
</div>
""", unsafe_allow_html=True)
