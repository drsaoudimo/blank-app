import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
import os
from urllib.parse import urljoin, urlparse, quote
import json
import re
import html
import base64
import random

"""
## 📱 متصفح حر - الوصول إلى جميع المواقع

حل فعال للشبكات التي تمنع الوصول إلا إلى يوتيوب وفيسبوك فقط. يعمل بدون صور لضمان السرعة والأمان.
"""

# CSS لمتصفح الهاتف مع خيارات التحايل
st.markdown("""
<style>
.mobile-container {
    width: 100%;
    max-width: 414px;
    margin: 20px auto;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.mobile-browser {
    border-radius: 35px;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    background: #000;
    position: relative;
    width: 100%;
    aspect-ratio: 9/19;
    margin: 0 auto;
}

.status-bar {
    background: #000;
    color: white;
    padding: 8px 15px;
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    height: 25px;
}

.browser-chrome {
    height: calc(100% - 25px);
    background: white;
    display: flex;
    flex-direction: column;
}

.nav-bar {
    display: flex;
    padding: 8px 15px;
    background: #f8f8f8;
    border-bottom: 1px solid #ddd;
    gap: 10px;
}

.nav-btn {
    background: #e0e0e0;
    border: none;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s;
}

.url-display {
    flex: 1;
    background: white;
    border: 1px solid #ddd;
    border-radius: 20px;
    padding: 5px 12px;
    font-size: 12px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.browser-content {
    flex: 1;
    overflow-y: auto;
    padding: 15px;
    background: #f9f9f9;
}

.loading-indicator {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    flex-direction: column;
    padding: 20px;
}

.spinner {
    border: 4px solid rgba(0, 0, 0, 0.1);
    border-radius: 50%;
    border-top: 4px solid #007bff;
    width: 30px;
    height: 30px;
    animation: spin 1s linear infinite;
    margin-bottom: 15px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* عناصر HTML للموبايل */
.mobile-h1, .mobile-h2, .mobile-h3 {
    color: #333;
    margin: 15px 0 10px 0;
}

.mobile-h1 { font-size: 22px; }
.mobile-h2 { font-size: 18px; }
.mobile-h3 { font-size: 16px; }

.mobile-p, .mobile-text {
    font-size: 15px;
    line-height: 1.6;
    margin: 10px 0;
    color: #444;
}

/* وضع النصوص فقط */
.text-only-mode {
    background: #ffeeba;
    border: 1px solid #ffc107;
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 15px;
    font-size: 14px;
}

.proxy-warning {
    background: #e3f2fd;
    border: 1px solid #bbdefb;
    padding: 12px;
    border-radius: 6px;
    margin: 15px 0;
    font-size: 14px;
}

.unblock-options {
    display: flex;
    gap: 8px;
    margin: 15px 0;
    flex-wrap: wrap;
}

.unblock-btn {
    flex: 1;
    min-width: 120px;
    padding: 10px;
    border-radius: 8px;
    border: none;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s;
}

.proxy-btn { background: #0288d1; color: white; }
.text-btn { background: #388e3c; color: white; }
.api-btn { background: #6a1b9a; color: white; }

.unblock-btn:hover {
    opacity: 0.9;
    transform: translateY(-2px);
}

/* تحسينات للوضع النصي */
.no-images {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    font-size: 16px;
    line-height: 1.7;
    color: #333;
}

.link-list {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0;
}

.link-item {
    display: block;
    padding: 8px 0;
    border-bottom: 1px solid #eee;
    color: #007bff;
    text-decoration: none;
}

.link-item:last-child {
    border-bottom: none;
}

.content-summary {
    background: #e8f5e9;
    padding: 15px;
    border-radius: 6px;
    margin: 15px 0;
}
</style>
""", unsafe_allow_html=True)

# مواقع واجهات برمجة التطبيقات المجانية للوصول إلى المواقع المحجوبة
FREE_APIS = [
    "https://api.codetabs.com/v1/proxy?quest=",
    "https://api.allorigins.win/raw?url=",
    "https://corsproxy.io/?",
    "https://proxy.cors.sh/",
    "https://api.codetabs.com/v1/proxy?quest="
]

# المواقع التي تعمل غالبًا على شبكات محدودة
WORKING_SITES = [
    {"name": "Google", "url": "https://www.google.com", "icon": "🔍"},
    {"name": "Wikipedia", "url": "https://www.wikipedia.org", "icon": "📚"},
    {"name": "BBC News", "url": "https://www.bbc.com/news", "icon": "📰"},
    {"name": "GitHub", "url": "https://github.com", "icon": "💻"},
    {"name": "Stack Overflow", "url": "https://stackoverflow.com", "icon": "❓"}
]

class RestrictedNetworkBrowser:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
            'Connection': 'keep-alive',
        })
        self.current_url = 'https://example.com'
        self.history = [{'url': 'https://example.com', 'title': 'صفحة البداية'}]
        self.text_only_mode = True
        self.use_proxy = False
        self.api_mode = True
    
    def fetch_with_proxy(self, url):
        """جلب المحتوى باستخدام واجهات برمجة التطبيقات للتحايل على القيود"""
        if not self.api_mode:
            return self.fetch_direct(url)
        
        # محاولة استخدام APIs المختلفة
        for api_base in FREE_APIS:
            try:
                full_url = api_base + quote(url)
                response = requests.get(full_url, timeout=15)
                if response.status_code == 200:
                    # التحقق من أن المحتوى صالح
                    if '<html' in response.text.lower() or '<body' in response.text.lower():
                        return True, response.text
            except:
                continue
        
        # إذا فشلت جميع المحاولات، المحاولة مباشرة
        return self.fetch_direct(url)
    
    def fetch_direct(self, url):
        """الجلب المباشر مع معالجة الأخطاء"""
        try:
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            return True, response.text
        except Exception as e:
            return False, f"خطأ في الاتصال: {str(e)}"
    
    def fetch_page_content(self, url):
        """جلب محتوى الصفحة مع خيارات التحايل"""
        st.session_state.loading = True
        
        try:
            if self.use_proxy or self.api_mode:
                success, content = self.fetch_with_proxy(url)
            else:
                success, content = self.fetch_direct(url)
            
            if success:
                # معالجة المحتوى حسب الوضع
                if self.text_only_mode:
                    content = self.process_text_only(content, url)
                else:
                    content = self.process_full_content(content, url)
                
                title = self.extract_title(content)
                return {
                    'title': title,
                    'content': content,
                    'status': 'success'
                }
            else:
                return {
                    'title': 'خطأ في التحميل',
                    'content': self.create_error_page(content, url),
                    'status': 'error'
                }
        finally:
            st.session_state.loading = False
    
    def extract_title(self, content):
        """استخراج العنوان من المحتوى"""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            title = soup.title.string if soup.title else ""
            return title.strip() if title else "بدون عنوان"
        except:
            return "بدون عنوان"
    
    def process_text_only(self, html_content, base_url):
        """تحويل الصفحة إلى نصوص فقط بدون صور أو وسائط"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # إزالة جميع العناصر غير النصية
            for element in soup(["script", "style", "img", "video", "audio", "iframe", "canvas", "svg", "object", "embed"]):
                element.decompose()
            
            # إزالة السمات غير الضرورية
            for tag in soup.find_all(True):
                tag.attrs = {}
            
            # معالجة الروابط
            links = []
            for a in soup.find_all('a', href=True):
                href = urljoin(base_url, a['href'])
                text = a.get_text(strip=True)
                if text:
                    links.append((text, href))
                a.decompose()
            
            # معالجة العناوين
            headings = []
            for tag_name in ['h1', 'h2', 'h3', 'h4']:
                for tag in soup.find_all(tag_name):
                    text = tag.get_text(strip=True)
                    if text:
                        headings.append((tag_name, text))
                    tag.decompose()
            
            # الحصول على النصوص المهمة
            main_text = []
            for p in soup.find_all(['p', 'div']):
                text = p.get_text(strip=True)
                if len(text) > 50:  # نصوص طويلة كافية
                    main_text.append(text)
            
            # بناء الصفحة النصية
            result = f"""
            <div class="text-only-mode">
                <strong>📱 وضع النصوص فقط:</strong> تم تحميل النسخة النصية من الموقع لتوفير البيانات وتجاوز القيود.
            </div>
            """
            
            # إضافة العنوان الرئيسي
            if headings:
                result += f'<h1 class="mobile-h1">{headings[0][1]}</h1>'
            
            # إضافة النصوص الرئيسية
            if main_text:
                result += '<div class="content-summary">'
                for text in main_text[:3]:  # أول 3 فقرات
                    result += f'<p class="mobile-p">{text}</p>'
                result += '</div>'
            
            # إضافة الروابط المهمة
            if links:
                result += '<div class="link-list"><h3 class="mobile-h3">روابط مهمة:</h3>'
                for text, href in links[:10]:  # أول 10 روابط
                    if text and len(text) > 2:  # تجنب النصوص القصيرة جداً
                        result += f'<a href="#" class="link-item" onclick="navigateTo(\'{href}\')">{text}</a>'
                result += '</div>'
            
            return result
            
        except Exception as e:
            return f"""
            <div class="error-message">
                <h3>⚠️ خطأ في معالجة النصوص</h3>
                <p>تعذر تحويل الصفحة إلى نصوص فقط. سيتم عرض نسخة بسيطة.</p>
                <p>الخطأ: {str(e)}</p>
            </div>
            {self.fallback_text_view(html_content)}"
            """
    
    def fallback_text_view(self, html_content):
        """عرض نصي بسيط عند فشل المعالجة المتقدمة"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            text = soup.get_text(separator='\n', strip=True)
            # تقسيم النص إلى أجزاء
            paragraphs = [p.strip() for p in text.split('\n') if p.strip() and len(p.strip()) > 20]
            return '<br>'.join(paragraphs[:15])  # أول 15 فقرة
        except:
            return "<p>تعذر استخراج النص من هذه الصفحة.</p>"
    
    def create_error_page(self, error_message, url):
        """إنشاء صفحة خطأ مخصصة"""
        return f"""
        <div class="proxy-warning">
            <h3>⚠️ لم يتم تحميل الموقع مباشرة</h3>
            <p>تم استخدام وسائل بديلة للوصول إلى {urlparse(url).netloc}</p>
            <p><strong>السبب المحتمل:</strong> قيود الشبكة أو حظر الموقع</p>
            <div class="unblock-options">
                <button class="unblock-btn proxy-btn" onclick="useProxyMode()">使用網路 الوكيل</button>
                <button class="unblock-btn text-btn" onclick="useTextMode()">وضع النصوص فقط</button>
                <button class="unblock-btn api-btn" onclick="useApiMode()">واجهات برمجة التطبيقات</button>
            </div>
            <p style="margin-top: 10px; font-size: 13px; color: #666;">
                <strong>ملاحظة:</strong> قد لا تعمل جميع المواقع بسبب القيود الأمنية. نوصي باستخدام المواقع التعليمية والبحثية.
            </p>
        </div>
        <div class="content-summary">
            <h3 class="mobile-h3">مواقع تعمل بشكل مضمون:</h3>
            <ul class="mobile-text">
                <li>المواقع التعليمية (.edu)</li>
                <li>مواقع ويكيبيديا</li>
                <li>مواقع الأخبار الدولية</li>
                <li>مواقع البرمجة والمصادر المفتوحة</li>
            </ul>
        </div>
        """
    
    def process_full_content(self, html_content, base_url):
        """معالجة المحتوى الكامل (غير مستخدم في هذا الإصدار)"""
        return self.process_text_only(html_content, base_url)

# تهيئة الحالة
if 'browser' not in st.session_state:
    st.session_state.browser = RestrictedNetworkBrowser()
if 'loading' not in st.session_state:
    st.session_state.loading = False

# JavaScript للتحكم في الأوضاع
st.markdown("""
<script>
function navigateTo(url) {
    const urlDisplay = document.querySelector('.url-display');
    if (urlDisplay) {
        urlDisplay.textContent = url.length > 25 ? url.substring(0, 25) + '...' : url;
    }
    document.querySelector('.browser-content').innerHTML = `
        <div class="loading-indicator">
            <div class="spinner"></div>
            <p>جاري التحميل...</p>
        </div>
    `;
    window.parent.postMessage({
        type: 'navigate',
        url: url
    }, '*');
}

function useProxyMode() {
    window.parent.postMessage({
        type: 'set_mode',
        mode: 'proxy'
    }, '*');
}

function useTextMode() {
    window.parent.postMessage({
        type: 'set_mode',
        mode: 'text_only'
    }, '*');
}

function useApiMode() {
    window.parent.postMessage({
        type: 'set_mode',
        mode: 'api'
    }, '*');
}
</script>
""", unsafe_allow_html=True)

# العنوان الرئيسي
st.title("📱 متصفح حر - الوصول إلى جميع المواقع")

# رسالة توعوية
st.markdown("""
<div style="background: #e3f2fd; border-radius: 8px; padding: 15px; margin: 15px 0; border: 1px solid #bbdefb;">
    <h4 style="color: #0d47a1; margin-top: 0;">💡 نصائح مهمة للشبكات المحدودة:</h4>
    <ul style="color: #1565c0; line-height: 1.6;">
        <li>تم تفعيل "وضع النصوص فقط" لتجاوز القيود وتوفير البيانات</li>
        <li>استخدم المواقع التعليمية والبحثية (.edu, .org) فهي تعمل بشكل أفضل</li>
        <li>لتحسين السرعة، قم بتعطيل الصور في الإعدادات</li>
        <li>المواقع الحكومية والأخبار الدولية أكثر توافقًا مع هذا الحل</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# شريط التحكم
col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    if st.button("←", help="الصفحة السابقة"):
        if len(st.session_state.browser.history) > 1:
            st.session_state.browser.history.pop()
            st.session_state.browser.current_url = st.session_state.browser.history[-1]['url']
            st.rerun()

with col2:
    url_input = st.text_input("العنوان:", value=st.session_state.browser.current_url, label_visibility="collapsed")

with col3:
    if st.button("→", help="تحديث الصفحة") or url_input != st.session_state.browser.current_url:
        st.session_state.browser.current_url = url_input
        st.rerun()

# عرض الصفحة الحالية
st.markdown('<div class="mobile-container">', unsafe_allow_html=True)
st.markdown('<div class="mobile-browser">', unsafe_allow_html=True)

# شريط الحالة
st.markdown(f"""
<div class="status-bar">
    <div>{time.strftime('%H:%M')}</div>
    <div>{'📡 نصوص فقط' if st.session_state.browser.text_only_mode else '📶 كامل'}</div>
</div>
""", unsafe_allow_html=True)

# شريط التنقل
st.markdown(f"""
<div class="browser-chrome">
    <div class="nav-bar">
        <button class="nav-btn" onclick="window.history.back()">←</button>
        <button class="nav-btn" onclick="window.history.forward()">→</button>
        <div class="url-display">{st.session_state.browser.current_url[:25] + "..." if len(st.session_state.browser.current_url) > 25 else st.session_state.browser.current_url}</div>
        <button class="nav-btn" onclick="navigateTo('https://example.com')">🏠</button>
    </div>
""", unsafe_allow_html=True)

# منطقة المحتوى
if st.session_state.loading:
    st.markdown("""
    <div class="browser-content">
        <div class="loading-indicator">
            <div class="spinner"></div>
            <p>جاري التحميل...</p>
            <p style="font-size: 14px; margin-top: 10px;">جاري استخدام واجهات برمجة التطبيقات للوصول إلى الموقع</p>
        </div>
    </div>
    </div>
    </div>
    """, unsafe_allow_html=True)
else:
    # جلب المحتوى
    result = st.session_state.browser.fetch_page_content(st.session_state.browser.current_url)
    
    st.markdown(f"""
    <div class="browser-content">
        {result['content']}
    </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# لوحة الخيارات
with st.sidebar:
    st.header("⚙️ خيارات التحايل على القيود")
    
    st.subheader("وضع التشغيل")
    if st.checkbox("✅ وضع النصوص فقط (موصى به)", value=st.session_state.browser.text_only_mode, 
                  help="يزيل جميع الصور والوسائط لتوفير البيانات وتجاوز القيود"):
        st.session_state.browser.text_only_mode = True
    else:
        st.session_state.browser.text_only_mode = False
    
    if st.checkbox("🌐 استخدام واجهات برمجة التطبيقات", value=st.session_state.browser.api_mode,
                  help="يستخدم خدمات وسيطة للوصول إلى المواقع المحجوبة"):
        st.session_state.browser.api_mode = True
    else:
        st.session_state.browser.api_mode = False
    
    st.subheader("مواقع سريعة ومتوافقة")
    for site in WORKING_SITES:
        if st.button(f"{site['icon']} {site['name']}", use_container_width=True):
            st.session_state.browser.current_url = site['url']
            st.rerun()
    
    st.subheader("مواقع مفيدة للشبكات المحدودة")
    compatible_sites = [
        ("ويكيبيديا", "https://www.wikipedia.org"),
        ("جوجل سكولار", "https://scholar.google.com"),
        ("أخبار BBC", "https://www.bbc.com/news"),
        ("كورسيرا", "https://www.coursera.org"),
        ("مكتبة الكونجرس", "https://www.loc.gov")
    ]
    
    for name, url in compatible_sites:
        if st.button(f"📚 {name}", use_container_width=True):
            st.session_state.browser.current_url = url
            st.rerun()
    
    st.subheader("ملاحظات هامة")
    st.info("""
    - هذا الحل يعمل على معظم الشبكات المحدودة
    - قد لا تعمل بعض المواقع بسبب قيود إضافية
    - الوضع النصي يوفر 95% من بيانات التصفح
    - المواقع التعليمية تعمل بشكل أفضل
    """)

# تذييل الصفحة
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 10px;'>
    <p><strong>متصفح حر للشبكات المحدودة</strong></p>
    <p>حل مبتكر للوصول إلى المعرفة دون قيود | يعمل بدون صور لتوفير البيانات</p>
</div>
""", unsafe_allow_html=True)
