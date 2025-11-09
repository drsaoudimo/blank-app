import streamlit as st
from playwright.sync_api import sync_playwright
import os
import json
import time

"""
## Web Scraping باستخدام Playwright + Chromium

حل مضمون للعمل على Streamlit Cloud مع دعم كامل لـ JavaScript والجلسات المحفوظة.
"""

# إعداد مجلد لتخزين الجلسات
SESSION_DIR = "/mount/src/sessions"
os.makedirs(SESSION_DIR, exist_ok=True)
COOKIES_FILE = os.path.join(SESSION_DIR, "cookies.json")

@st.cache_resource
def get_browser():
    """تهيئة متصفح Chromium باستخدام Playwright"""
    st.info("جاري تشغيل Chromium عبر Playwright...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-setuid-sandbox'
            ]
        )
        st.success("✓ تم تشغيل Chromium بنجاح")
        return browser

def save_cookies(context, filename=COOKIES_FILE):
    """حفظ ملفات تعريف الارتباط إلى ملف"""
    try:
        cookies = context.cookies()
        with open(filename, 'w') as f:
            json.dump(cookies, f, indent=2)
        st.success(f"✓ تم حفظ {len(cookies)} كوكي بنجاح")
        return True
    except Exception as e:
        st.error(f"✗ خطأ في حفظ الكوكيز: {e}")
        return False

def load_cookies(context, filename=COOKIES_FILE):
    """تحميل ملفات تعريف الارتباط من ملف"""
    if not os.path.exists(filename):
        st.info("ⓘ لا يوجد ملف جلسة محفوظة")
        return False
    
    try:
        with open(filename, 'r') as f:
            cookies = json.load(f)
        
        context.add_cookies(cookies)
        st.success(f"✓ تم تحميل {len(cookies)} كوكي بنجاح")
        return True
    except Exception as e:
        st.error(f"✗ خطأ في تحميل الكوكيز: {e}")
        return False

# --- الواجهة الرئيسية ---
st.title("متصفح آمن وسريع")

col1, col2 = st.columns(2)

with col1:
    direct_access = st.button("🟢 دخول مباشر", use_container_width=True, 
                             help="فتح متصفح جديد بدون جلسات")

with col2:
    session_access = st.button("💾 استخدام جلسة محفوظة", use_container_width=True,
                              help="استخدام آخر جلسة تم حفظها")

# --- الإعدادات ---
with st.expander("⚙️ الإعدادات"):
    site_url = st.text_input("رابط الموقع", "https://www.google.com", key="url")
    
    if st.button("🗑️ مسح الجلسة المحفوظة"):
        try:
            if os.path.exists(COOKIES_FILE):
                os.remove(COOKIES_FILE)
                st.success("✓ تم مسح الجلسة المحفوظة")
                st.rerun()
            else:
                st.info("ⓘ لا يوجد جلسة محفوظة للمسح")
        except Exception as e:
            st.error(f"✗ خطأ: {e}")

# --- مناطق العرض ---
result_area = st.empty()
page_content = st.empty()

# --- الدخول المباشر ---
if direct_access:
    with st.spinner("جاري التحميل..."):
        try:
            browser = get_browser()
            context = browser.new_context()
            page = context.new_page()
            
            page.goto(site_url, timeout=60000)
            time.sleep(2)
            
            result_area.success(f"✓ تم تحميل {site_url} بنجاح")
            
            # زر حفظ الجلسة
            if st.button("حفظ الجلسة الحالية"):
                save_cookies(context)
            
            # عرض جزء من مصدر الصفحة
            content = page.content()[:1500] + "..."
            page_content.text_area("مصدر الصفحة", content, height=300)
            
            browser.close()
            
        except Exception as e:
            result_area.error(f"✗ خطأ: {str(e)}")

# --- استخدام الجلسة المحفوظة ---
if session_access:
    with st.spinner("جاري تحميل الجلسة..."):
        try:
            browser = get_browser()
            context = browser.new_context()
            
            # تحميل الكوكيز إذا كانت موجودة
            cookies_loaded = load_cookies(context)
            
            page = context.new_page()
            page.goto(site_url, timeout=60000)
            time.sleep(3)
            
            result_area.success(f"✓ تم التحميل باستخدام {'الجلسة المحفوظة' if cookies_loaded else 'متصفح جديد'}")
            
            content = page.content()[:1500] + "..."
            page_content.text_area("مصدر الصفحة", content, height=300)
            
            browser.close()
            
        except Exception as e:
            result_area.error(f"✗ خطأ: {str(e)}")
