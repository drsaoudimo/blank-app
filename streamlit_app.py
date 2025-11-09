import streamlit as st
from playwright.sync_api import sync_playwright, Error as PlaywrightError
import os
import json
import time
import subprocess
import sys

"""
## Web Scraping باستخدام Playwright + Chromium على Streamlit Cloud

حل يعمل بدون أخطاء في بيئة Streamlit Cloud مع تحميل تلقائي للمتصفح.
"""

# إعداد مجلد لتخزين الجلسات
SESSION_DIR = "/mount/src/sessions"
os.makedirs(SESSION_DIR, exist_ok=True)
COOKIES_FILE = os.path.join(SESSION_DIR, "cookies.json")

def install_playwright_browsers():
    """تثبيت متصفحات Playwright تلقائيًا في بيئة Streamlit Cloud"""
    try:
        st.info("جاري تثبيت متصفح Chromium...")
        
        # محاولة تثبيت المتصفح باستخدام الأمر المناسب
        result = subprocess.run(
            [sys.executable, "-c", "from playwright.sync_api import sync_playwright; playwright=sync_playwright().start(); playwright.chromium.install()"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            st.success("✓ تم تثبيت Chromium بنجاح")
            return True
        else:
            st.warning(f"⚠️ تحذير أثناء التثبيت: {result.stderr}")
            return False
            
    except Exception as e:
        st.error(f"✗ فشل تثبيت المتصفح: {str(e)}")
        return False

@st.cache_resource
def get_browser():
    """تهيئة متصفح Chromium باستخدام Playwright مع حلول بديلة"""
    try:
        # المحاولة الأولى: استخدام Playwright مع التثبيت التلقائي
        st.info("جاري تشغيل Playwright...")
        
        # محاولة استيراد Playwright
        with sync_playwright() as p:
            # إعداد المتصفح مع خيارات متوافقة مع Streamlit Cloud
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-setuid-sandbox',
                    '--disable-software-rasterizer',
                    '--disable-background-networking',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--mute-audio',
                    '--no-first-run',
                    '--no-service-autorun',
                ]
            )
            st.success("✓ تم تشغيل Chromium بنجاح")
            return browser
            
    except PlaywrightError as e:
        error_msg = str(e).lower()
        
        # معالجة حالة عدم وجود المتصفح
        if "executable doesn't exist" in error_msg or "browser was not found" in error_msg:
            st.warning("⚠️ لم يتم العثور على متصفح Chromium. جاري التثبيت التلقائي...")
            
            if install_playwright_browsers():
                # إعادة المحاولة بعد التثبيت
                with sync_playwright() as p:
                    browser = p.chromium.launch(
                        headless=True,
                        args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
                    )
                    st.success("✓ تم تشغيل Chromium بعد التثبيت")
                    return browser
            else:
                st.error("✗ فشل التثبيت التلقائي. جاري المحاولة باستخدام المتصفح النظامي...")
                return get_system_browser()
                
        else:
            st.error(f"✗ خطأ في Playwright: {str(e)}")
            return get_system_browser()
            
    except Exception as e:
        st.error(f"✗ خطأ غير متوقع: {str(e)}")
        return get_system_browser()

def get_system_browser():
    """المحاولات البديلة باستخدام متصفح النظام"""
    st.info("جاري المحاولة باستخدام متصفح النظام...")
    
    try:
        # البحث عن مسارات المتصفحات المحتملة في Streamlit Cloud
        possible_paths = [
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
            "/usr/bin/google-chrome",
            "/snap/bin/chromium"
        ]
        
        browser_path = None
        for path in possible_paths:
            if os.path.exists(path):
                browser_path = path
                break
        
        if browser_path:
            st.success(f"✓ تم العثور على Chromium في: {browser_path}")
            
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    executable_path=browser_path,
                    headless=True,
                    args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
                )
                return browser
        else:
            st.error("✗ لم يتم العثور على أي متصفح في النظام")
            st.info("الرجاء التأكد من أن ملف requirements.txt يحتوي على:")
            st.code("playwright==1.42.0")
            return None
            
    except Exception as e:
        st.error(f"✗ فشل جميع المحاولات: {str(e)}")
        raise

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
st.title("متصفح آمن وسريع على Streamlit Cloud")

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
            if not browser:
                st.error("✗ فشل تهيئة المتصفح")
                st.stop()
                
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
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
            if not browser:
                st.error("✗ فشل تهيئة المتصفح")
                st.stop()
                
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
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
