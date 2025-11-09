import streamlit as st
import os
import json
import time
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import base64
from PIL import Image
import io

# إعدادات المسارات
SESSION_DIR = "/tmp/sessions"
os.makedirs(SESSION_DIR, exist_ok=True)
COOKIES_FILE = os.path.join(SESSION_DIR, "cookies.json")

# تخصيص CSS لتحسين المظهر
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .url-input {
        border: 2px solid #1f77b4;
        border-radius: 10px;
        padding: 15px;
        background-color: #f0f8ff;
    }
    .browser-window {
        border: 2px solid #ddd;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px 0;
        background: white;
    }
    .browser-header {
        background: #f5f5f5;
        padding: 10px 15px;
        border-bottom: 1px solid #ddd;
        border-radius: 10px 10px 0 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .browser-controls {
        display: flex;
        gap: 5px;
    }
    .browser-button {
        width: 12px;
        height: 12px;
        border-radius: 50%;
    }
    .close { background: #ff5f57; }
    .minimize { background: #ffbd2e; }
    .maximize { background: #28ca42; }
    .browser-url-bar {
        flex: 1;
        background: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.8rem;
        color: #666;
        border: 1px solid #ddd;
    }
    .browser-content {
        padding: 20px;
        min-height: 400px;
        max-height: 600px;
        overflow-y: auto;
    }
    .tab-container {
        display: flex;
        background: #f5f5f5;
        border-bottom: 1px solid #ddd;
    }
    .tab {
        padding: 10px 20px;
        background: #e0e0e0;
        border-right: 1px solid #ddd;
        cursor: pointer;
    }
    .tab.active {
        background: white;
        border-bottom: 2px solid #1f77b4;
    }
    .content-tab {
        display: none;
    }
    .content-tab.active {
        display: block;
    }
    .website-preview {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        background: #fafafa;
    }
    .link-item {
        padding: 8px;
        margin: 5px 0;
        background: white;
        border-left: 3px solid #1f77b4;
        border-radius: 4px;
    }
    .image-preview {
        max-width: 100%;
        border-radius: 8px;
        margin: 10px 0;
    }
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 5px;
    }
</style>
""", unsafe_allow_html=True)

class AdvancedBrowserSimulator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        self.history = []
        self.current_url = ""
        
    def navigate(self, url):
        """التنقل إلى رابط مع حفظ التاريخ"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            response = self.session.get(url, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            self.current_url = response.url
            self.history.append({
                'url': response.url,
                'timestamp': time.time(),
                'title': self.extract_title(response.text)
            })
            
            return {
                'success': True,
                'content': response.text,
                'url': response.url,
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', ''),
                'size': len(response.content)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'content': '',
                'url': url
            }
    
    def extract_title(self, html_content):
        """استخراج عنوان الصفحة"""
        soup = BeautifulSoup(html_content, 'html.parser')
        title = soup.title
        return title.string if title else "بدون عنوان"
    
    def extract_detailed_info(self, html_content, base_url):
        """استخراج معلومات مفصلة عن الصفحة"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # العنوان والوصف
        title = soup.title.string if soup.title else "بدون عنوان"
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc['content'] if meta_desc else "لا يوجد وصف"
        
        # جميع الروابط
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            links.append({
                'text': link.get_text(strip=True) or "رابط بدون نص",
                'url': full_url,
                'is_external': not full_url.startswith(base_url)
            })
        
        # الصور
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            full_src = urljoin(base_url, src)
            images.append({
                'src': full_src,
                'alt': img.get('alt', 'لا يوجد نص بديل'),
                'title': img.get('title', '')
            })
        
        # النصوص الرئيسية
        texts = []
        for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            text = element.get_text(strip=True)
            if text and len(text) > 10:
                texts.append({
                    'text': text,
                    'tag': element.name
                })
        
        # النماذج
        forms = []
        for form in soup.find_all('form'):
            forms.append({
                'action': form.get('action', ''),
                'method': form.get('method', 'GET'),
                'inputs': len(form.find_all('input'))
            })
        
        return {
            'title': title,
            'description': description,
            'links_count': len(links),
            'images_count': len(images),
            'texts_count': len(texts),
            'forms_count': len(forms),
            'links': links[:20],  # عرض أول 20 رابط فقط
            'images': images[:10],  # عرض أول 10 صور فقط
            'texts': texts[:15],  # عرض أول 15 نص فقط
            'forms': forms
        }

# --- واجهة Streamlit المحسنة ---
st.set_page_config(
    page_title="🌐 المتصفح المتقدم - عرض الصفحات",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# الشريط الجانبي
with st.sidebar:
    st.markdown('<div class="main-header">🌐 المتصفح المتقدم</div>', unsafe_allow_html=True)
    
    st.subheader("🔗 إدخال الرابط")
    url_input = st.text_input(
        "أدخل رابط الموقع:",
        value="https://www.google.com",
        placeholder="https://example.com",
        key="url_input"
    )
    
    st.subheader("🛠️ خيارات التصفح")
    col1, col2 = st.columns(2)
    with col1:
        auto_save = st.checkbox("حفظ تلقائي", value=True)
    with col2:
        follow_redirects = st.checkbox("متابعة التوجيه", value=True)
    
    st.subheader("📊 إحصائيات سريعة")
    if 'browser' in st.session_state and st.session_state.browser.history:
        st.metric("الصفحات المفتوحة", len(st.session_state.browser.history))
        st.metric("آخر زيارة", st.session_state.browser.history[-1]['title'][:20] + "...")
    
    st.subheader("💾 إدارة الجلسات")
    if st.button("💾 حفظ الجلسة الحالية", use_container_width=True):
        if 'browser' in st.session_state:
            try:
                session_data = {
                    'cookies': dict(st.session_state.browser.session.cookies),
                    'history': st.session_state.browser.history,
                    'current_url': st.session_state.browser.current_url,
                    'timestamp': time.time()
                }
                with open(COOKIES_FILE, 'w', encoding='utf-8') as f:
                    json.dump(session_data, f, indent=2, ensure_ascii=False)
                st.success("✅ تم حفظ الجلسة")
            except Exception as e:
                st.error(f"❌ خطأ في الحفظ: {e}")
    
    if st.button("🗑️ مسح الكل", use_container_width=True, type="secondary"):
        try:
            if os.path.exists(COOKIES_FILE):
                os.remove(COOKIES_FILE)
            st.session_state.clear()
            st.success("✅ تم المسح")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"❌ خطأ في المسح: {e}")

# المنطقة الرئيسية
st.markdown("""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            padding: 20px; border-radius: 15px; color: white; margin-bottom: 20px;'>
    <h1 style='margin:0; text-align: center;'>🌐 مساحة عرض الصفحات المتقدمة</h1>
    <p style='text-align: center; margin: 10px 0 0 0;'>تصميم احترافي لعرض وتحليل صفحات الويب</p>
</div>
""", unsafe_allow_html=True)

# تهيئة المتصفح في session state
if 'browser' not in st.session_state:
    st.session_state.browser = AdvancedBrowserSimulator()

# شريط التحكم بالمتصفح
col_controls1, col_controls2, col_controls3, col_controls4 = st.columns([2, 1, 1, 1])

with col_controls1:
    if st.button("🚀 تصفح الآن", use_container_width=True, type="primary"):
        with st.spinner("جاري تحميل الصفحة..."):
            result = st.session_state.browser.navigate(url_input)
            
            if result['success']:
                st.success(f"✅ تم تحميل {result['url']} بنجاح")
                st.session_state.last_result = result
                st.session_state.page_info = st.session_state.browser.extract_detailed_info(
                    result['content'], result['url']
                )
            else:
                st.error(f"❌ فشل في التحميل: {result['error']}")

with col_controls2:
    if st.button("🔄 إعادة تحميل", use_container_width=True):
        if st.session_state.browser.current_url:
            result = st.session_state.browser.navigate(st.session_state.browser.current_url)
            if result['success']:
                st.success("✅ تم إعادة التحميل")
                st.session_state.last_result = result
                st.rerun()

with col_controls3:
    if st.button("📊 تحليل الصفحة", use_container_width=True):
        if 'last_result' in st.session_state:
            st.info("🔍 جاري تحليل الصفحة...")
            st.rerun()

with col_controls4:
    if st.button("🧹 تنظيف العرض", use_container_width=True):
        if 'last_result' in st.session_state:
            del st.session_state.last_result
        st.rerun()

# عرض نتائج التصفح
if 'last_result' in st.session_state and st.session_state.last_result['success']:
    result = st.session_state.last_result
    page_info = st.session_state.page_info
    
    # نافذة المتصفح المحاكاة
    st.markdown("""
    <div class='browser-window'>
        <div class='browser-header'>
            <div class='browser-controls'>
                <div class='browser-button close'></div>
                <div class='browser-button minimize'></div>
                <div class='browser-button maximize'></div>
            </div>
            <div class='browser-url-bar'>📍 {}</div>
        </div>
    </div>
    """.format(result['url']), unsafe_allow_html=True)
    
    # تبويبات العرض
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📄 محتوى الصفحة", "🔗 الروابط", "🖼️ الصور", "📊 الإحصائيات", "📝 النصوص"])
    
    with tab1:
        st.subheader("📄 محتوى الصفحة الرئيسي")
        
        col_content1, col_content2 = st.columns([3, 1])
        
        with col_content1:
            # عرض محتوى HTML مع تنسيق
            with st.expander("📋 عرض مصدر HTML", expanded=True):
                st.code(result['content'][:5000] + ("..." if len(result['content']) > 5000 else ""), 
                       language='html')
        
        with col_content2:
            st.metric("حجم الصفحة", f"{result['size']:,} بايت")
            st.metric("حالة التحميل", result['status_code'])
            st.metric("نوع المحتوى", result['content_type'].split(';')[0])
    
    with tab2:
        st.subheader(f"🔗 الروابط ({page_info['links_count']})")
        
        if page_info['links']:
            # تصفية الروابط
            col_filter1, col_filter2 = st.columns(2)
            with col_filter1:
                show_external = st.checkbox("عرض الروابط الخارجية", value=True)
            with col_filter2:
                search_links = st.text_input("🔍 بحث في الروابط")
            
            filtered_links = page_info['links']
            if not show_external:
                filtered_links = [link for link in filtered_links if not link['is_external']]
            if search_links:
                filtered_links = [link for link in filtered_links if search_links.lower() in link['text'].lower()]
            
            for i, link in enumerate(filtered_links[:30]):  # عرض أول 30 رابط فقط
                with st.container():
                    col_link1, col_link2 = st.columns([3, 1])
                    with col_link1:
                        st.markdown(f"**{i+1}. {link['text']}**")
                        st.caption(link['url'])
                    with col_link2:
                        if st.button("➡️ انتقل", key=f"link_{i}", use_container_width=True):
                            st.session_state.url_input = link['url']
                            st.rerun()
                    st.divider()
        else:
            st.info("ℹ️ لم يتم العثور على روابط في هذه الصفحة")
    
    with tab3:
        st.subheader(f"🖼️ الصور ({page_info['images_count']})")
        
        if page_info['images']:
            cols = st.columns(3)
            for i, img in enumerate(page_info['images'][:9]):  # عرض أول 9 صور
                with cols[i % 3]:
                    try:
                        # محاولة عرض الصورة
                        st.markdown(f"**الصورة {i+1}**")
                        st.markdown(f"النص البديل: {img['alt']}")
                        st.markdown(f"[رابط الصورة]({img['src']})")
                    except:
                        st.info("🖼️ لا يمكن عرض هذه الصورة")
        else:
            st.info("ℹ️ لم يتم العثور على صور في هذه الصفحة")
    
    with tab4:
        st.subheader("📊 إحصائيات الصفحة")
        
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        with col_stat1:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.metric("الروابط", page_info['links_count'])
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_stat2:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.metric("الصور", page_info['images_count'])
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_stat3:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.metric("النصوص", page_info['texts_count'])
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_stat4:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.metric("النماذج", page_info['forms_count'])
            st.markdown('</div>', unsafe_allow_html=True)
        
        # مخطط تفصيلي
        st.subheader("📈 تحليل المحتوى")
        chart_data = {
            'نوع المحتوى': ['روابط', 'صور', 'نصوص', 'نماذج'],
            'العدد': [page_info['links_count'], page_info['images_count'], 
                     page_info['texts_count'], page_info['forms_count']]
        }
        st.bar_chart(chart_data, x='نوع المحتوى', y='العدد')
    
    with tab5:
        st.subheader(f"📝 النصوص الرئيسية ({page_info['texts_count']})")
        
        if page_info['texts']:
            for i, text_item in enumerate(page_info['texts'][:20]):  # عرض أول 20 نص
                with st.expander(f"{text_item['tag'].upper()}: {text_item['text'][:50]}...", expanded=False):
                    st.write(text_item['text'])
                    st.caption(f"علامة: {text_item['tag']}")
        else:
            st.info("ℹ️ لم يتم العثور على نصوص رئيسية في هذه الصفحة")

else:
    # الشاشة الافتراضية عندما لا يكون هناك صفحة مفتوحة
    st.markdown("""
    <div style='text-align: center; padding: 100px 20px; background: #f8f9fa; border-radius: 15px; margin: 50px 0;'>
        <h2 style='color: #6c757d;'>🌐 مرحباً في المتصفح المتقدم</h2>
        <p style='color: #6c757d; font-size: 1.2rem;'>أدخل رابطاً في الشريط الجانبي وابدأ التصفح!</p>
        <div style='font-size: 4rem; margin: 30px 0;'>🚀</div>
        <p style='color: #6c757d;'>استخدم الزر "🚀 تصفح الآن" لتحميل أول صفحة</p>
    </div>
    """, unsafe_allow_html=True)

# قسم التاريخ في الأسفل
if st.session_state.browser.history:
    with st.expander("📚 سجل التصفح", expanded=False):
        st.subheader("الصفحات التي تم زيارتها")
        for i, visit in enumerate(reversed(st.session_state.browser.history[-10:])):  # آخر 10 زيارات
            col_hist1, col_hist2, col_hist3 = st.columns([3, 2, 1])
            with col_hist1:
                st.write(f"**{visit['title']}**")
                st.caption(visit['url'])
            with col_hist2:
                st.caption(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(visit['timestamp'])))
            with col_hist3:
                if st.button("🔄 فتح", key=f"hist_{i}", use_container_width=True):
                    st.session_state.url_input = visit['url']
                    st.rerun()

# تذييل الصفحة
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>مساحة عرض الصفحات المتقدمة</strong> | تصميم متكامل لعرض وتحليل محتوى الويب</p>
    <p>⚡ سريع • 🛡️ آمن • 📊 متعدد الخيارات</p>
</div>
""", unsafe_allow_html=True)
