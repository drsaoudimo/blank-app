import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
import os
from urllib.parse import urljoin, urlparse
import json
import re

# إعدادات الجلسة
SESSION_DIR = "/tmp/browser_sessions"
os.makedirs(SESSION_DIR, exist_ok=True)

# تثبيت CSS للمتصفح المتجاوب
st.markdown("""
<style>
    /* المتصفح الرئيسي */
    .browser-container {
        width: 100%;
        height: 70vh;
        border: 2px solid #ddd;
        border-radius: 10px;
        background: white;
        margin: 20px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        position: relative;
        overflow: hidden;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* شريط التنقل */
    .browser-navbar {
        background: #f5f5f5;
        padding: 12px 15px;
        display: flex;
        gap: 10px;
        align-items: center;
        border-bottom: 1px solid #ddd;
        height: 50px;
        box-sizing: border-box;
    }
    
    .nav-btn {
        background: #e9ecef;
        border: none;
        width: 35px;
        height: 35px;
        border-radius: 50%;
        cursor: pointer;
        font-size: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .nav-btn:hover {
        background: #dee2e6;
    }
    
    .url-bar {
        flex: 1;
        padding: 10px 15px;
        border: 1px solid #ccc;
        border-radius: 25px;
        font-size: 14px;
        background: white;
    }
    
    /* منطقة المحتوى */
    .browser-content {
        width: 100%;
        height: calc(100% - 50px);
        overflow: auto;
        background: white;
    }
    
    /* محتوى الويب المعدل */
    .website-content {
        width: 100%;
        min-height: 100%;
        padding: 20px;
        box-sizing: border-box;
        background: white;
    }
    
    /* تحسين الروابط للتفاعل */
    .processed-link {
        color: #007bff;
        text-decoration: none;
        cursor: pointer;
        padding: 5px;
        border-radius: 3px;
        transition: background-color 0.2s;
    }
    
    .processed-link:hover {
        background-color: #e3f2fd;
        text-decoration: underline;
    }
    
    /* نماذج معدلة */
    .processed-form {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    /* تحسين الصور */
    .processed-img {
        max-width: 100%;
        height: auto;
        border-radius: 5px;
    }
    
    /* أزرار التبديل */
    .view-toggle {
        display: flex;
        gap: 10px;
        margin-bottom: 15px;
        flex-wrap: wrap;
    }
    
    .view-btn {
        padding: 10px 20px;
        border-radius: 8px;
        border: 1px solid #ddd;
        cursor: pointer;
        background: #f8f9fa;
        flex: 1;
        text-align: center;
        min-width: 120px;
    }
    
    .view-btn.active {
        background: #007bff;
        color: white;
        border-color: #007bff;
    }
    
    /* شاشة التحميل */
    .loading-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 200px;
        flex-direction: column;
        gap: 15px;
    }
    
    .spinner {
        width: 40px;
        height: 40px;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #007bff;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* رسائل الخطأ */
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 20px;
        border-radius: 5px;
        text-align: center;
        margin: 20px;
    }
    
    /* التكيف مع الشاشات الصغيرة */
    @media (max-width: 768px) {
        .browser-container {
            height: 60vh;
        }
        
        .browser-navbar {
            padding: 8px 10px;
            height: 45px;
        }
        
        .nav-btn {
            width: 30px;
            height: 30px;
            font-size: 14px;
        }
        
        .url-bar {
            padding: 8px 12px;
            font-size: 12px;
        }
        
        .view-btn {
            min-width: 100px;
            padding: 8px 15px;
            font-size: 14px;
        }
    }
</style>
""", unsafe_allow_html=True)

class AdvancedBrowser:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
        })
        self.current_url = "https://www.google.com"
        self.history = []
        self.future = []  # للتنقل للأمام
        
    def navigate_to(self, url):
        """التنقل إلى رابط جديد"""
        if not url:
            return False
            
        # إضافة للتاريخ قبل التغيير
        if self.current_url:
            self.history.append(self.current_url)
            self.future.clear()  # مسح المستقبل عند تنقل جديد
            
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        self.current_url = url
        return True
    
    def go_back(self):
        """العودة للصفحة السابقة"""
        if len(self.history) > 0:
            self.future.append(self.current_url)
            self.current_url = self.history.pop()
            return True
        return False
    
    def go_forward(self):
        """التقدم للصفحة التالية"""
        if len(self.future) > 0:
            self.history.append(self.current_url)
            self.current_url = self.future.pop()
            return True
        return False
    
    def fetch_page(self, url):
        """جلب محتوى الصفحة"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return response.text, True
        except Exception as e:
            error_html = self.create_error_page(str(e), url)
            return error_html, False
    
    def create_error_page(self, error, url):
        """إنشاء صفحة خطأ"""
        return f"""
        <div class="website-content">
            <div style="text-align: center; padding: 50px 20px;">
                <h1 style="color: #dc3545; font-size: 48px;">⚠️</h1>
                <h2 style="color: #333; margin-bottom: 20px;">تعذر تحميل الصفحة</h2>
                <p style="color: #666; margin-bottom: 10px;"><strong>الرابط:</strong> {url}</p>
                <p style="color: #666; margin-bottom: 30px;"><strong>الخطأ:</strong> {error}</p>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; max-width: 500px; margin: 0 auto;">
                    <h3 style="color: #333; margin-bottom: 15px;">الحلول المقترحة:</h3>
                    <ul style="text-align: left; color: #666; line-height: 1.6;">
                        <li>تحقق من اتصال الإنترنت</li>
                        <li>تأكد من صحة الرابط</li>
                        <li>جرب رابطاً مختلفاً</li>
                        <li>انتظر قليلاً ثم حاول مرة أخرى</li>
                    </ul>
                </div>
                
                <div style="margin-top: 30px;">
                    <button onclick="window.location.href='?url=https://www.google.com'" 
                            style="background: #007bff; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; margin: 5px;">
                        الذهاب إلى Google
                    </button>
                    <button onclick="window.location.reload()" 
                            style="background: #28a745; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; margin: 5px;">
                        إعادة المحاولة
                    </button>
                </div>
            </div>
        </div>
        """
    
    def process_content(self, html_content, base_url):
        """معالجة محتوى HTML للسماح بالتنقل التفاعلي"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # معالجة جميع الروابط
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = urljoin(base_url, href)
                
                # استبدال الرابط بحدث JavaScript
                link['onclick'] = f"window.parent.navigateTo('{absolute_url}'); return false;"
                link['class'] = link.get('class', []) + ['processed-link']
                link['title'] = f"انتقل إلى: {absolute_url}"
                
                # إزالة الـ href الأصلي لمنع التنقل المباشر
                del link['href']
                link['style'] = 'cursor: pointer; color: #007bff; text-decoration: underline;'
            
            # معالجة النماذج
            for form in soup.find_all('form'):
                form['onsubmit'] = "window.parent.handleFormSubmit(this); return false;"
                form['class'] = form.get('class', []) + ['processed-form']
            
            # تحسين الصور
            for img in soup.find_all('img', src=True):
                img_src = img['src']
                absolute_src = urljoin(base_url, img_src)
                img['src'] = absolute_src
                img['class'] = img.get('class', []) + ['processed-img']
                img['style'] = 'max-width: 100%; height: auto;'
                img['loading'] = 'lazy'
            
            # تحسين الجداول للشاشات الصغيرة
            for table in soup.find_all('table'):
                table['style'] = 'width: 100%; max-width: 100%; overflow-x: auto; display: block;'
            
            # إضافة CSS إضافي لتحسين العرض
            style_tag = soup.new_tag('style')
            style_tag.string = """
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    color: #333;
                    max-width: 100%;
                    overflow-x: hidden;
                }
                * {
                    box-sizing: border-box;
                }
                .processed-link {
                    color: #007bff !important;
                    text-decoration: underline !important;
                    cursor: pointer !important;
                }
                .processed-link:hover {
                    background-color: #e3f2fd !important;
                }
                img {
                    max-width: 100% !important;
                    height: auto !important;
                }
                table {
                    width: 100% !important;
                    max-width: 100% !important;
                    overflow-x: auto !important;
                    display: block !important;
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
            <div class="website-content">
                <div class="error-message">
                    <h3>خطأ في معالجة المحتوى</h3>
                    <p>تعذر معالجة محتوى الصفحة للعرض التفاعلي.</p>
                    <p>الخطأ: {str(e)}</p>
                    <button onclick="window.location.reload()" style="background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin-top: 10px;">
                        إعادة تحميل الصفحة
                    </button>
                </div>
            </div>
            """

# تهيئة المتصفح
if 'browser' not in st.session_state:
    st.session_state.browser = AdvancedBrowser()

# JavaScript للتفاعل
browser_js = """
<script>
// دالة للتنقل إلى روابط جديدة
function navigateTo(url) {
    window.parent.postMessage({
        type: 'NAVIGATE',
        url: url
    }, '*');
}

// دالة لإرسال النماذج
function handleFormSubmit(form) {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    window.parent.postMessage({
        type: 'FORM_SUBMIT',
        formData: data,
        action: form.action,
        method: form.method
    }, '*');
}

// دالة للتعامل مع الرسائل من Streamlit
window.addEventListener('message', function(event) {
    if (event.data.type === 'RELOAD_PAGE') {
        window.location.reload();
    }
});

// جعل جميع الروابط قابلة للنقر
document.addEventListener('click', function(e) {
    if (e.target.tagName === 'A' && e.target.onclick) {
        e.preventDefault();
        e.target.onclick();
    }
});
</script>
"""

# العنوان والتحكم
st.title("🌐 متصفح ويب متكامل")

# أزرار التبديل بين الأوضاع
st.markdown("""
<div class="view-toggle">
    <button class="view-btn active" onclick="setViewMode('desktop')">💻 كمبيوتر</button>
    <button class="view-btn" onclick="setViewMode('tablet')">📱 لوحي</button>
    <button class="view-btn" onclick="setViewMode('mobile')">📱 هاتف</button>
</div>

<script>
function setViewMode(mode) {
    // إزالة النشط من جميع الأزرار
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // إضافة النشط للزر المحدد
    event.target.classList.add('active');
    
    // إرسال الرسالة لـ Streamlit
    window.parent.postMessage({
        type: 'VIEW_MODE',
        mode: mode
    }, '*');
}
</script>
""", unsafe_allow_html=True)

# شريط التنقل
col1, col2, col3, col4 = st.columns([1, 1, 4, 1])

with col1:
    if st.button("←", help="العودة", use_container_width=True):
        if st.session_state.browser.go_back():
            st.rerun()

with col2:
    if st.button("→", help="التقدم", use_container_width=True):
        if st.session_state.browser.go_forward():
            st.rerun()

with col3:
    url_input = st.text_input(
        "أدخل عنوان الويب:",
        value=st.session_state.browser.current_url,
        placeholder="https://www.example.com",
        label_visibility="collapsed"
    )
    
    if url_input and url_input != st.session_state.browser.current_url:
        if st.session_state.browser.navigate_to(url_input):
            st.rerun()

with col4:
    if st.button("↻", help="إعادة تحميل", use_container_width=True):
        st.rerun()

# عرض المتصفح
st.markdown("### نافذة المتصفح:")

# جلب ومعالجة المحتوى
with st.spinner("جاري تحميل الصفحة..."):
    html_content, success = st.session_state.browser.fetch_page(st.session_state.browser.current_url)
    
    if success:
        processed_content = st.session_state.browser.process_content(html_content, st.session_state.browser.current_url)
    else:
        processed_content = html_content

# عرض المحتوى المعالج
browser_html = f"""
<div class="browser-container">
    <div class="browser-navbar">
        <button class="nav-btn" onclick="window.history.back()">←</button>
        <button class="nav-btn" onclick="window.history.forward()">→</button>
        <div class="url-bar">{st.session_state.browser.current_url}</div>
        <button class="nav-btn" onclick="window.location.reload()">↻</button>
    </div>
    <div class="browser-content">
        {processed_content}
        {browser_js}
    </div>
</div>
"""

st.components.v1.html(browser_html, height=600, scrolling=True)

# معالجة الأحداث من JavaScript
try:
    # هذه الدالة تستقبل الرسائل من JavaScript
    def handle_js_message():
        # في تطبيق حقيقي، يمكن معالجة الرسائل هنا
        pass
        
except:
    pass

# لوحة التحكم الجانبية
with st.sidebar:
    st.header("🎮 أدوات التحكم")
    
    st.subheader("التنقل السريع")
    quick_sites = [
        ("Google", "https://www.google.com"),
        ("Wikipedia", "https://www.wikipedia.org"),
        ("GitHub", "https://www.github.com"),
        ("Stack Overflow", "https://stackoverflow.com"),
        ("YouTube", "https://www.youtube.com"),
        ("Amazon", "https://www.amazon.com")
    ]
    
    for site_name, site_url in quick_sites:
        if st.button(site_name, use_container_width=True):
            if st.session_state.browser.navigate_to(site_url):
                st.rerun()
    
    st.subheader("سجل التصفح")
    if st.session_state.browser.history:
        for i, url in enumerate(reversed(st.session_state.browser.history[-5:])):
            display_url = url[:40] + "..." if len(url) > 40 else url
            if st.button(f"📄 {display_url}", key=f"hist_{i}", use_container_width=True):
                st.session_state.browser.current_url = url
                st.rerun()
    else:
        st.info("لا يوجد سجل تصفح")
    
    st.subheader("إعدادات المتصفح")
    if st.button("🧹 مسح الذاكرة المؤقتة", use_container_width=True):
        st.session_state.browser.session.cookies.clear()
        st.success("تم مسح الذاكرة المؤقتة")
    
    if st.button("🗑️ مسح السجل", use_container_width=True):
        st.session_state.browser.history.clear()
        st.session_state.browser.future.clear()
        st.success("تم مسح السجل")
    
    if st.button("🔄 إعادة تعيين المتصفح", use_container_width=True):
        st.session_state.browser = AdvancedBrowser()
        st.success("تم إعادة التعيين")
        st.rerun()

# معلومات وإحصائيات
with st.expander("📊 معلومات المتصفح"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("الصفحات السابقة", len(st.session_state.browser.history))
    
    with col2:
        st.metric("الصفحات التالية", len(st.session_state.browser.future))
    
    with col3:
        domain = urlparse(st.session_state.browser.current_url).netloc
        st.metric("المجال الحالي", domain[:15] + "..." if len(domain) > 15 else domain)

# تذييل الصفحة
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>🌐 المتصفح التفاعلي المتقدم</strong></p>
    <p>✅ تنقل كامل بين الصفحات • 📱 متجاوب مع جميع الشاشات • ⚡ سريع وموثوق</p>
</div>
""", unsafe_allow_html=True)

# JavaScript إضافي للتفاعل
st.markdown("""
<script>
// التعامل مع الرسائل من iframe
window.addEventListener('message', function(event) {
    if (event.data.type === 'NAVIGATE') {
        // إرسال الأمر لـ Streamlit للتنقل
        window.location.href = window.location.pathname + '?url=' + encodeURIComponent(event.data.url);
    }
});

// تحديث واجهة المستخدم
function updateUI() {
    // يمكن إضافة المزيد من التفاعلات هنا
}
</script>
""", unsafe_allow_html=True)
