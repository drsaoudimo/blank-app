import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os
import json
import time

"""
## Web Scraping with Session Management on Streamlit Cloud

حل نهائي لمشكلة السائق (Driver) مع دعم كامل لحفظ الجلسات واستعادتها.
"""

# اسم الملف لحفظ الكوكيز
COOKIES_FILE = "/mount/src/cookies/session_cookies.json"
os.makedirs(os.path.dirname(COOKIES_FILE), exist_ok=True)

@st.cache_resource
def get_driver():
    """تهيئة المتصفح بطريقة متوافقة مع Streamlit Cloud"""
    # التحقق من وجود chromedriver في النظام
    driver_path = "/usr/bin/chromedriver"
    browser_path = "/usr/bin/chromium-browser"
    
    # التأكد من وجود الملفات المطلوبة
    if not os.path.exists(driver_path):
        st.error(f"⚠️ chromedriver غير موجود في: {driver_path}")
        st.info("جاري محاولة استخدام مسار بديل...")
        # مسار بديل محتمل
        driver_path = "/usr/local/bin/chromedriver"
    
    if not os.path.exists(browser_path):
        st.error(f"⚠️ chromium-browser غير موجود في: {browser_path}")
    
    # إعداد خيارات المتصفح
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-background-networking")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    # تحديد مسار المتصفح يدويًا
    options.binary_location = browser_path
    
    # إنشاء خدمة chromedriver
    service = Service(executable_path=driver_path)
    
    # إنشاء المتصفح
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def save_cookies_to_file(driver, filename=COOKIES_FILE):
    """تحفظ الكوكيز الحالية من المتصفح إلى ملف محلي."""
    try:
        cookies = driver.get_cookies()
        with open(filename, 'w') as f:
            json.dump(cookies, f, indent=2)
        st.success(f"✓ تم حفظ {len(cookies)} كوكي في {filename}")
        return True
    except Exception as e:
        st.error(f"✗ فشل حفظ الكوكيز: {e}")
        return False

def load_cookies_from_file(driver, base_url, filename=COOKIES_FILE):
    """تحمّل الكوكيز من ملف محلي إلى المتصفح."""
    if not os.path.exists(filename):
        st.info(f"ⓘ ملف الكوكيز غير موجود: {filename}")
        return False
    
    try:
        with open(filename, 'r') as f:
            cookies = json.load(f)
        
        driver.get(base_url)
        time.sleep(2)
        
        success_count = 0
        for cookie in cookies:
            try:
                # إزالة الخصائص التي قد تسبب مشاكل
                for key in ['expiry', 'sameSite']:
                    cookie.pop(key, None)
                driver.add_cookie(cookie)
                success_count += 1
            except Exception as e:
                st.warning(f"⚠️ لم يتم تحميل كوكي: {cookie.get('name', 'غير معروف')} - {e}")
        
        driver.refresh()
        time.sleep(3)
        
        st.success(f"✓ تم تحميل {success_count} كوكي بنجاح من {filename}")
        return True
    except Exception as e:
        st.error(f"✗ فشل تحميل الكوكيز: {e}")
        return False

# --- الواجهة الرئيسية ---
st.title("مدير جلسات التصفح")

col1, col2 = st.columns(2)

with col1:
    direct_access = st.button("🖥️ الدخول المباشر إلى المتصفح", use_container_width=True, 
                             help="افتح متصفح جديد بدون استخدام أي جلسات محفوظة")

with col2:
    session_access = st.button("🍪 استخدام الجلسة المحفوظة", use_container_width=True,
                              help="استخدم الجلسة المحفوظة مسبقًا (إذا كانت متوفرة)")

# --- الإعدادات ---
with st.expander("⚙️ الإعدادات"):
    site_url = st.text_input("رابط الموقع", "https://example.com", key="site_url")
    login_url = st.text_input("رابط تسجيل الدخول", "https://example.com/login", key="login_url")
    
    if st.button("🗑️ مسح الجلسة المحفوظة"):
        try:
            if os.path.exists(COOKIES_FILE):
                os.remove(COOKIES_FILE)
                st.success(f"✓ تم مسح ملف الجلسة: {COOKIES_FILE}")
                st.rerun()
            else:
                st.info("ⓘ لا يوجد ملف جلسة محفوظة للمسح.")
        except Exception as e:
            st.error(f"✗ خطأ في مسح ملف الجلسة: {e}")

# --- مناطق العرض ---
result_container = st.empty()
source_container = st.empty()

# --- الدخول المباشر ---
if direct_access:
    with st.spinner("جاري تحميل المتصفح... (قد يستغرق بضع ثوانٍ)"):
        try:
            driver = get_driver()
            driver.get(site_url)
            time.sleep(3)
            
            result_container.success(f"✓ تم التحميل بنجاح: {site_url}")
            
            # زر حفظ الجلسة بعد التصفح
            if st.button("حفظ هذه الجلسة الحالية"):
                save_cookies_to_file(driver)
            
            # عرض جزء من مصدر الصفحة
            page_source = driver.page_source
            source_container.text_area("مصدر الصفحة", page_source[:1500] + "...", height=300)
        except Exception as e:
            result_container.error(f"✗ خطأ أثناء التحميل: {str(e)}")
            st.code(str(e))
        finally:
            try:
                driver.quit()
            except:
                pass

# --- استخدام الجلسة المحفوظة ---
if session_access:
    with st.spinner("جاري تحميل الجلسة المحفوظة..."):
        try:
            driver = get_driver()
            if load_cookies_from_file(driver, site_url):
                driver.get(site_url)
                time.sleep(3)
                
                result_container.success(f"✓ تم التحميل باستخدام الجلسة المحفوظة: {site_url}")
                page_source = driver.page_source
                source_container.text_area("مصدر الصفحة", page_source[:1500] + "...", height=300)
            else:
                result_container.warning("ⓘ لم يتم العثور على جلسة محفوظة. يرجى محاولة الدخول المباشر ثم حفظ الجلسة.")
        except Exception as e:
            result_container.error(f"✗ خطأ أثناء تحميل الجلسة: {str(e)}")
            st.code(str(e))
        finally:
            try:
                driver.quit()
            except:
                pass
