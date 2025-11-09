import streamlit as st
from playwright.sync_api import sync_playwright
import os
import json
import time
import sys

"""
## تشغيل متصفح ويب على Streamlit Cloud

هذا الحل يعمل بشكل موثوق على Streamlit Cloud باستخدام Playwright.
"""

def install_browser():
    """تثبيت المتصفح تلقائيًا في Streamlit Cloud"""
    try:
        st.info("جاري تثبيت Chromium...")
        os.system(f"{sys.executable} -m playwright install chromium")
        st.success("✓ تم تثبيت Chromium بنجاح")
    except Exception as e:
        st.error(f"✗ خطأ في التثبيت: {str(e)}")

@st.cache_resource
def get_browser():
    """تهيئة المتصفح مع حلول للبيئة المقيدة لـ Streamlit Cloud"""
    try:
        # التأكد من تثبيت المتصفح
        install_browser()
        
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
            return browser
    except Exception as e:
        st.error(f"✗ خطأ في تشغيل المتصفح: {str(e)}")
        st.info("جرب إعادة تحميل الصفحة أو تحقق من ملف requirements.txt")
        return None

st.title("متصفح ويب على Streamlit Cloud")

url = st.text_input("أدخل رابط الموقع", "https://example.com")

if st.button("تحميل الصفحة"):
    with st.spinner("جاري التحميل..."):
        browser = get_browser()
        if browser:
            try:
                context = browser.new_context()
                page = context.new_page()
                page.goto(url, timeout=60000)
                time.sleep(2)
                
                st.success(f"✓ تم تحميل {url} بنجاح")
                
                # عرض جزء من مصدر الصفحة
                content = page.content()[:1500] + "..."
                st.text_area("مصدر الصفحة", content, height=300)
                
                # حفظ لقطة شاشة (اختياري)
                screenshot_path = "/mount/src/screenshot.png"
                page.screenshot(path=screenshot_path)
                if os.path.exists(screenshot_path):
                    st.image(screenshot_path, caption="لقطة شاشة للصفحة")
                
            except Exception as e:
                st.error(f"✗ خطأ أثناء التحميل: {str(e)}")
            finally:
                browser.close()
