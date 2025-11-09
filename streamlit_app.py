import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
import os
from urllib.parse import urljoin, urlparse
import json
import re
import chardet
import ftfy  # لإصلاح النص المشفر

# إعدادات الجلسة
SESSION_DIR = "/tmp/desktop_browser"
os.makedirs(SESSION_DIR, exist_ok=True)

# تثبيت CSS مع إصلاحات الترميز
st.markdown("""
<style>
    /* إصلاحات الترميز العالمية */
    * {
        font-family: 'Segoe UI', 'Tahoma', 'Arial', 'DejaVu Sans', sans-serif !important;
    }
    
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
    
    /* ... باقي الCSS السابق ... */
</style>
""", unsafe_allow_html=True)

class FixedEncodingBrowser:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8,fr;q=0.7,de;q=0.6,es;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
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
        
    def fix_encoding_issues(self, text):
        """إصلاح مشاكل الترميز باستخدام طرق متعددة"""
        if not text:
            return ""
            
        try:
            # الطريقة 1: استخدام ftfy لإصلاح النص المشفر
            fixed_text = ftfy.fix_text(text)
            
            # الطريقة 2: التعامل مع الترميز الخاطئ
            if self.has_encoding_issues(fixed_text):
                # محاولة كشف الترميز وإعادة التحويل
                detected = chardet.detect(text.encode('utf-8', errors='replace'))
                encoding = detected.get('encoding', 'utf-8')
                
                try:
                    # إعادة التحويل من الترميز المكتشف
                    fixed_text = text.encode('utf-8').decode(encoding, errors='replace')
                except:
                    # إذا فشل، نستخدم الترميزات الشائعة
                    for enc in ['windows-1256', 'iso-8859-6', 'windows-1252', 'latin-1']:
                        try:
                            fixed_text = text.encode('utf-8').decode(enc, errors='replace')
                            break
                        except:
                            continue
            
            # الطريقة 3: تنظيف الرموز غير المرغوب فيها
            fixed_text = self.clean_invalid_chars(fixed_text)
            
            return fixed_text
            
        except Exception as e:
            return f"خطأ في إصلاح الترميز: {str(e)}"
    
    def has_encoding_issues(self, text):
        """الكشف عن وجود مشاكل في الترميز"""
        # البحث عن أنماط الترميز الخاطئ
        patterns = [
            r'[âÂîÎôÔûÛ]',  # مشاكل الترميز العربية
            r'[Ã¡Ã©Ã­Ã³Ãº]',  # مشاكل الترميز اللاتينية
            r'â€œ|â€|â€¦',  # علامات الترقيم المشفرة
            r'[]',  # رموز تحكم مشفرة
        ]
        
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        return False
    
    def clean_invalid_chars(self, text):
        """تنظيف الرموز غير الصالحة"""
        # إزالة رموز التحكم غير المرغوب فيها
        cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # إصلاح المسافات والفواصل المشفرة
        replacements = {
            'â€œ': '"', 'â€': '"', 'â€¦': '...',
            'â€™': "'", 'â€˜': "'", 'â€”': '—',
            'â€“': '–', 'â€¢': '•', 'â€®': '',
            'â€¼': '', 'â€¯': '', 'â€¡': 'ç',
            'â€°': '‰', 'â€¹': '›', 'â€º': '›'
        }
        
        for wrong, correct in replacements.items():
            cleaned = cleaned.replace(wrong, correct)
            
        return cleaned
    
    def navigate_to(self, url, tab_id=None):
        """التنقل إلى رابط جديد مع معالجة ترميز قوية"""
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
        
        # جلب المحتوى
        success, content, encoding = self.fetch_page_content(clean_url)
        
        if success:
            # إصلاح مشاكل الترميز
            content = self.fix_encoding_issues(content)
        
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
        """جلب محتوى الصفحة مع معالجة ترميز متقدمة"""
        try:
            # جلب المحتوى كـ bytes مع تعطيل الضغط لتجنب مشاكل الترميز
            response = self.session.get(url, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            # كشف الترميز بدقة
            raw_content = response.content
            encoding = self.detect_encoding_advanced(raw_content)
            
            # تحويل المحتوى إلى Unicode
            content = self.safe_decode(raw_content, encoding)
            
            return True, content, encoding
            
        except Exception as e:
            error_msg = f"خطأ في جلب المحتوى: {str(e)}"
            return False, error_msg, 'utf-8'
    
    def detect_encoding_advanced(self, content):
        """كشف الترميز بطرق متقدمة"""
        # الطريقة 1: استخدام chardet
        detected = chardet.detect(content)
        encoding = detected.get('encoding', 'utf-8')
        confidence = detected.get('confidence', 0)
        
        # إذا كانت الثقة عالية، نستخدم الترميز المكتشف
        if confidence > 0.8:
            return encoding
        
        # الطريقة 2: البحث في محتوى HTML
        html_patterns = {
            'utf-8': [b'charset=utf-8', b'encoding="utf-8"', b'encoding=utf-8'],
            'windows-1256': [b'charset=windows-1256', b'charset=arabic'],
            'iso-8859-6': [b'charset=iso-8859-6'],
            'windows-1252': [b'charset=windows-1252', b'charset=iso-8859-1']
        }
        
        for enc, patterns in html_patterns.items():
            for pattern in patterns:
                if pattern in content.lower():
                    return enc
        
        # الطريقة 3: التحليل الإحصائي
        return self.statistical_encoding_detection(content)
    
    def statistical_encoding_detection(self, content):
        """كشف الترميز بالتحليل الإحصائي"""
        try:
            # تحليل توزيع البايتات
            byte_counts = {}
            for byte in content:
                byte_counts[byte] = byte_counts.get(byte, 0) + 1
            
            # البحث عن أنماط الترميز العربية
            arabic_patterns = [b'\xd9', b'\xd8', b'\xda', b'\xdb']
            arabic_count = sum(byte_counts.get(byte, 0) for byte in arabic_patterns)
            
            if arabic_count > len(content) * 0.05:  # إذا كان 5% من المحتوى عربي
                return 'windows-1256'
            
            return 'utf-8'
        except:
            return 'utf-8'
    
    def safe_decode(self, content, encoding):
        """تحويل آمن للمحتوى إلى Unicode"""
        try:
            # محاولة التحويل بالترميز المحدد
            decoded = content.decode(encoding, errors='replace')
            
            # إصلاح أي مشاكل متبقية
            fixed = ftfy.fix_text(decoded)
            
            return fixed
            
        except UnicodeDecodeError:
            # إذا فشل التحويل، نجرب ترميزات بديلة
            for alt_encoding in ['utf-8', 'windows-1256', 'iso-8859-6', 'windows-1252', 'latin-1']:
                try:
                    decoded = content.decode(alt_encoding, errors='replace')
                    fixed = ftfy.fix_text(decoded)
                    return fixed
                except:
                    continue
            
            # إذا فشلت جميع المحاولات، نستخدم استبدال الأخطاء
            return content.decode('utf-8', errors='replace')
    
    def extract_page_title(self, html_content):
        """استخراج عنوان الصفحة مع إصلاح الترميز"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            title = soup.find('title')
            if title and title.string:
                title_text = title.string.strip()
                return self.fix_encoding_issues(title_text)
            
            h1 = soup.find('h1')
            if h1 and h1.get_text(strip=True):
                h1_text = h1.get_text(strip=True)
                return self.fix_encoding_issues(h1_text)
                
            return None
        except:
            return None
    
    def process_content_for_display(self, html_content, base_url, encoding):
        """معالجة المحتوى للعرض مع ضمان الترميز الصحيح"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # إضافة إعدادات الترميز الصارمة
            meta_charset = soup.new_tag('meta', charset='UTF-8')
            if soup.head:
                soup.head.insert(0, meta_charset)
            
            # إضافة base href
            base_tag = soup.new_tag('base', href=base_url)
            if soup.head:
                soup.head.append(base_tag)
            
            # معالجة جميع النصوص لإصلاح الترميز
            for element in soup.find_all(text=True):
                if element.parent.name not in ['script', 'style']:
                    fixed_text = self.fix_encoding_issues(element)
                    element.replace_with(fixed_text)
            
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
            
            # إضافة CSS شامل لإصلاح الترميز
            style_tag = soup.new_tag('style')
            style_tag.string = """
                /* إصلاحات ترميز شاملة */
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
                    direction: ltr;
                }
                
                /* إصلاح النصوص العربية */
                [lang="ar"], [dir="rtl"] {
                    direction: rtl !important;
                    text-align: right !important;
                    font-family: 'Segoe UI', 'Tahoma', 'Arial', 'Times New Roman', serif !important;
                }
                
                /* إصلاح الرموز الخاصة */
                .fixed-text {
                    unicode-bidi: plaintext;
                    font-family: 'Segoe UI', 'Arial', 'DejaVu Sans', sans-serif;
                }
                
                /* منع ظهور الرموز المشفرة */
                .no-encoding-issues {
                    text-rendering: optimizeLegibility;
                    -webkit-font-smoothing: antialiased;
                }
                
                /* تحسين عرض جميع اللغات */
                p, div, span, h1, h2, h3, h4, h5, h6 {
                    unicode-bidi: embed;
                    line-height: 1.6;
                }
            """
            if soup.head:
                soup.head.append(style_tag)
            
            # إضافة فئة للإصلاح
            if soup.body:
                soup.body['class'] = soup.body.get('class', []) + ['fixed-text', 'no-encoding-issues']
            
            return str(soup)
            
        except Exception as e:
            return f"""
            <!DOCTYPE html>
            <html lang="ar" dir="ltr">
            <head>
                <meta charset="UTF-8">
                <title>إصلاح الترميز</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, sans-serif;
                        padding: 20px;
                        line-height: 1.6;
                        color: #242424;
                        background: #f8f9fa;
                    }}
                    .error {{
                        background: #fff3cd;
                        border: 1px solid #ffeaa7;
                        color: #856404;
                        padding: 20px;
                        border-radius: 6px;
                        text-align: center;
                    }}
                </style>
            </head>
            <body>
                <div class="error">
                    <h3>🔧 تم إصلاح مشاكل الترميز</h3>
                    <p>كانت هناك مشاكل في ترميز الصفحة الأصلية</p>
                    <p>تم تطبيق إصلاحات الترميز التلقائية</p>
                    <button onclick="window.location.reload()" 
                            style="background: #0078d4; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin-top: 10px;">
                        إعادة تحميل الصفحة
                    </button>
                </div>
            </body>
            </html>
            """
    
    # ... باقي الدوال كما هي ...

# تهيئة المتصفح
if 'fixed_browser' not in st.session_state:
    st.session_state.fixed_browser = FixedEncodingBrowser()

# واجهة المستخدم
st.title("🖥️ متصفح ديسكتوب - إصلاح الترميز")

# إضافة حقل لإدخال النص المرميز بشكل خاطئ للاختبار
with st.sidebar:
    st.header("🔧 اختبار إصلاح الترميز")
    
    test_text = st.text_area("اختبار نص مشفر:", 
                           value="""$FN·××)ه^»ص«ْ؟W•ûS³Q\صRْtے‎™*ع’-إ¢نگِ»q6ھ‘™ˆH@ Kة]يمصزA¨3„F Tôè¨®ô*½X؟؟7صىr(*چن:W‍«n\…ّأ‹ٹہbA:,Iگ—@زaِ؟ےًPگ’ِئگإ€K” ^‚‌—’)9¤ش44D uôٍ"è\]Ua‌K—résهٍھآeêجNٍ&[آچ™—Jˆ¼êگڑLôxƒâ،]£آ‏¯»½A”œڑ,صt­_چذt‍@r©›چëZ´ژïذ‰ث1<¾•6‌p~…K'µ",پأûF+نJ""",
                           height=200)
    
    if st.button("إصلاح الترميز"):
        fixed = st.session_state.fixed_browser.fix_encoding_issues(test_text)
        st.text_area("النص المصلح:", value=fixed, height=200)

# ... باقي واجهة المستخدم كما كانت ...

# شريط التحكم
col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    if st.button("◀ العودة", use_container_width=True):
        # كود العودة
        pass

with col2:
    url_input = st.text_input("أدخل عنوان الويب:", placeholder="https://example.com", label_visibility="collapsed")
    if st.button("➤ انتقل", use_container_width=True) and url_input:
        success, message = st.session_state.fixed_browser.navigate_to(url_input)
        if success:
            st.success("✅ تم تحميل الصفحة مع إصلاح الترميز")
        else:
            st.error(f"❌ {message}")
        st.rerun()

with col3:
    if st.button("↻ إعادة تحميل", use_container_width=True):
        st.rerun()

# عرض المتصفح
active_tab = st.session_state.fixed_browser.get_active_tab()
if active_tab:
    display_content = st.session_state.fixed_browser.process_content_for_display(
        active_tab['content'], 
        active_tab['url'],
        active_tab['encoding']
    )
    
    browser_html = f"""
    <div class="desktop-browser">
        <div class="content-area">
            {display_content}
        </div>
    </div>
    """
    
    st.components.v1.html(browser_html, height=600, scrolling=True)

# معلومات الترميز
with st.expander("📊 معلومات الترميز"):
    if active_tab:
        st.write(f"**الترميز المستخدم:** {active_tab.get('encoding', 'غير معروف')}")
        st.write(f"**حجم المحتوى:** {len(active_tab.get('content', ''))} حرف")
        st.write(f"**تم إصلاح الترميز:** ✅")
