import streamlit as st
import os
import json
import time
import sys
from playwright.sync_api import sync_playwright
from contextlib import contextmanager

"""
## حل مشكلة "Event loop is closed" في Playwright

الحل النهائي للتعامل مع أخطاء الإغلاق في بيئة Streamlit Cloud.
"""

# مجلد الجلسات
SESSION_DIR = "/mount/src/sessions"
os.makedirs(SESSION_DIR, exist_ok=True)
COOKIES_FILE = os.path.join(SESSION_DIR, "cookies.json")

@contextmanager
def safe_browser():
    """مدير سياق آمن للمتصفح يتعامل مع أخطاء الإغلاق تلقائيًا"""
    browser = None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-setuid-sandbox',
                    '--disable-software-rasterizer'
                ]
            )
            yield browser
    except Exception as e:
        st.error(f"✗ خطأ في تشغيل المتصفح: {str(e)}")
        yield None
    finally:
        try:
            if browser is not None:
                # محاولة إغلاق المتصفح بأمان
                browser.close()
        except Exception as close_error:
            # تجاهل أخطاء الإغلاق المحددة
            if "Event loop is closed" not in str(close_error) and "is already stopped" not in str(close_error):
                st.warning(f"⚠️ تحذير أثناء إغلاق المتصفح: {str(close_error)}")

def save_cookies(context, filename=COOKIES_FILE):
    """حفظ ملفات تعريف الارتباط"""
    try:
        cookies = context.cookies()
        with open(filename, 'w') as f:
            json.dump(cookies, f, indent=2)
        st.success(f"✓ تم حفظ {len(cookies)} كوكي")
        return True
    except Exception as e:
        st.error(f"✗ خطأ في حفظ الكوكيز: {e}")
        return False

def load_cookies(context, filename=COOKIES_FILE):
    """تحميل ملفات تعريف الارتباط"""
    if not os.path.exists(filename):
        st.info("ⓘ لا يوجد جلسة محفوظة")
        return False
    
    try:
        with open(filename, 'r') as f:
            cookies = json.load(f)
        
        context.add_cookies(cookies)
        st.success(f"✓ تم تحميل {len(cookies)} كوكي")
        return True
    except Exception as e:
        st.error(f"✗ خطأ في تحميل الكوكيز: {e}")
        return False

# --- الواجهة ---
st.title("متصفح ويب مستقر على Streamlit Cloud")

col1, col2 = st.columns(2)

with col1:
    direct_btn = st.button("🟢 دخول مباشر", use_container_width=True)

with col2:
    session_btn = st.button("💾 استخدام جلسة محفوظة", use_container_width=True)

with st.expander("⚙️ الإعدادات"):
    url = st.text_input("رابط الموقع", "https://www.google.com")
    
    if st.button("🗑️ مسح الجلسة المحفوظة"):
        try:
            if os.path.exists(COOKIES_FILE):
                os.remove(COOKIES_FILE)
                st.success("✓ تم مسح الجلسة")
                st.rerun()
        except Exception as e:
            st.error(f"✗ خطأ: {e}")

result_area = st.empty()
content_area = st.empty()

# --- الدخول المباشر ---
if direct_btn:
    with st.spinner("جاري التحميل..."):
        with safe_browser() as browser:
            if browser:
                try:
                    context = browser.new_context(
                        viewport={'width': 1920, 'height': 1080},
                        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    )
                    page = context.new_page()
                    page.goto(url, timeout=60000)
                    time.sleep(2)
                    
                    result_area.success(f"✓ تم تحميل {url}")
                    
                    if st.button("حفظ الجلسة", key="save_direct"):
                        save_cookies(context)
                    
                    content = page.content()[:1500] + "..."
                    content_area.text_area("مصدر الصفحة", content, height=300)
                    
                except Exception as e:
                    result_area.error(f"✗ خطأ أثناء التصفح: {str(e)}")
            else:
                result_area.error("✗ فشل تشغيل المتصفح")

# --- استخدام الجلسة المحفوظة ---
if session_btn:
    with st.spinner("جاري تحميل الجلسة..."):
        with safe_browser() as browser:
            if browser:
                try:
                    context = browser.new_context(
                        viewport={'width': 1920, 'height': 1080},
                        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    )
                    
                    cookies_loaded = load_cookies(context)
                    
                    page = context.new_page()
                    page.goto(url, timeout=60000)
                    time.sleep(3)
                    
                    result_area.success(f"✓ تم التحميل باستخدام {'الجلسة المحفوظة' if cookies_loaded else 'متصفح جديد'}")
                    
                    content = page.content()[:1500] + "..."
                    content_area.text_area("مصدر الصفحة", content, height=300)
                    
                except Exception as e:
                    result_area.error(f"✗ خطأ أثناء التصفح: {str(e)}")
            else:
                result_area.error("✗ فشل تشغيل المتصفح")
