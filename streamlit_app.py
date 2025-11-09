
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import os
import json
import time

"""
## Web Scraping على Streamlit Cloud - الحل النهائي

تم التحديث للعمل على أحدث إصدار من بيئة Streamlit Cloud باستخدام WebDriverManager.
"""

# اسم الملف لحفظ الكوكيز
COOKIES_FILE = "/mount/src/cookies/session_cookies.json"
os.makedirs(os.path.dirname(COOKIES_FILE), exist_ok=True)

@st.cache_resource
def get_driver():
    """تهيئة المتصفح باستخدام WebDriverManager"""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-breakpad")
    options.add_argument("--disable-notifications")
    options.add_argument("--mute-audio")
    options.add_argument("--no-first-run")
    options.add_argument("--no-service-autorun")
    options.add_argument("--password-store=basic")
    
    # استخدام Chromium على Streamlit Cloud
    try:
        # المحاولة الأولى: استخدام WebDriverManager لتنزيل السائق تلقائيًا
        service = Service(
            ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
        )
        st.success("✓ تم تحميل السائق تلقائيًا باستخدام WebDriverManager")
    except Exception as e:
        st.warning(f"⚠️ فشل تحميل السائق تلقائيًا: {e}")
        st.info("جاري المحاولة باستخدام المسارات الافتراضية...")
        
        # المحاولة الثانية: استخدام المسارات الشائعة في Streamlit Cloud
        chrome_path = None
        driver_path = None
        
        # التحقق من المسارات المحتملة
        possible_chrome_paths = [
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
            "/usr/bin/google-chrome",
            "/app/.apt/usr/bin/google-chrome"
        ]
        
        possible_driver_paths = [
            "/usr/bin/chromedriver",
            "/usr/local/bin/chromedriver",
            "/app/.apt/usr/bin/chromedriver"
        ]
        
        for path in possible_chrome_paths:
            if os.path.exists(path):
                chrome_path = path
                break
        
        for path in possible_driver_paths:
            if os.path.exists(path):
                driver_path = path
                break
        
        if chrome_path and driver_path:
            options.binary_location = chrome_path
            service = Service(executable_path=driver_path)
            st.success(f"✓ تم العثور على Chromium في: {chrome_path}")
            st.success(f"✓ تم العثور على chromedriver في: {driver_path}")
        else:
            # الخيار الأخير: استخدام الإعدادات الافتراضية مع محاولة أفضل
            st.warning("⚠️ استخدام الإعدادات الافتراضية للمتصفح")
            options.add_argument("--remote-debugging-port=9222")
    
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
                problematic_keys = ['expiry', 'sameSite', 'secure', 'httpOnly']
                for key in problematic_keys:
                    cookie.pop(key, None)
                
                # ضمان وجود القيم الإلزامية
                if 'domain' not in cookie:
                    cookie['domain'] = base_url.replace('https://', '').replace('http://', '').split('/')[0]
                
                driver.add_cookie(cookie)
                success_count += 1
            except Exception as e:
                st.warning(f"⚠️ لم يتم تحميل كوكي: {cookie.get('name', 'غير معروف')} - {str(e)}")
        
        driver.refresh()
        time.sleep(3)
        
        st.success(f"✓ تم تحميل {success_count} كوكي بنجاح من {filename}")
        return True
    except Exception as e:
        st.error(f"✗ فشل تحميل الكوكيز: {str(e)}")
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
    
    if st.button("🗑️ مسح الجلسة المحفوظة"):
        try:
            if os.path.exists(COOKIES_FILE):
                os.remove(COOKIES_FILE)
                st.success(f"✓ تم مسح ملف الجلسة: {COOKIES_FILE}")
                st.rerun()
            else:
                st.info("ⓘ لا يوجد ملف جلسة محفوظة للمسح.")
        except Exception as e:
            st.error(f"✗ خطأ في مسح ملف الجلسة: {str(e)}")

# --- مناطق العرض ---
result_container = st.empty()
source_container = st.empty()

# --- الدخول المباشر ---
if direct_access:
    with st.spinner("جاري تشغيل المتصفح..."):
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
            # معلومات استكشاف الأخطاء
            st.subheader("معلومات استكشاف الأخطاء:")
            st.code(f"""
            - الإصدار الحالي لـ Selenium: {webdriver.__version__}
            - الموقع المستهدف: {site_url}
            - ملف الكوكيز: {COOKIES_FILE}
            """)
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
        finally:
            try:
                driver.quit()
            except:
                pass
