import streamlit as st
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import os
import json
import time
import stat

"""
## Web Scraping باستخدام Firefox على Streamlit Cloud

حل بديل باستخدام Firefox (GeckoDriver) لتجنب مشاكل Chrome/Chromium.
"""

# اسم الملف لحفظ الكوكيز
COOKIES_FILE = "/mount/src/cookies/session_cookies.json"
os.makedirs(os.path.dirname(COOKIES_FILE), exist_ok=True)

@st.cache_resource
def get_driver():
    """تهيئة متصفح Firefox المتوافق مع Streamlit Cloud"""
    st.info("جاري إعداد متصفح Firefox...")
    
    # إعدادات Firefox للوضع الخفي والبيئات المقيدة
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-setuid-sandbox")
    
    # إعدادات خاصة بـ Firefox
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.dir", "/tmp")
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream")
    options.set_preference("devtools.jsonview.enabled", False)
    
    try:
        # المحاولة الأولى: استخدام WebDriverManager لـ Firefox
        st.info("جاري تحميل GeckoDriver باستخدام WebDriverManager...")
        driver_path = GeckoDriverManager().install()
        
        # ضمان أذونات التنفيذ
        if os.path.exists(driver_path):
            current_permissions = os.stat(driver_path).st_mode
            os.chmod(driver_path, current_permissions | stat.S_IEXEC)
            st.success(f"✓ تم تعيين أذونات التنفيذ لـ geckodriver")
        
        service = Service(executable_path=driver_path)
        driver = webdriver.Firefox(service=service, options=options)
        st.success("✓ تم تشغيل Firefox بنجاح")
        return driver
        
    except Exception as e1:
        st.warning(f"⚠️ فشل المحاولة الأولى: {str(e1)}")
        
        try:
            # المحاولة الثانية: استخدام مسار GeckoDriver الافتراضي في Streamlit Cloud
            st.info("جاري المحاولة باستخدام المسار الافتراضي لـ Firefox...")
            
            # مسارات Firefox المحتملة في Streamlit Cloud
            firefox_path = None
            driver_path = None
            
            possible_firefox_paths = [
                "/usr/bin/firefox",
                "/usr/bin/firefox-esr",
                "/snap/bin/firefox"
            ]
            
            possible_driver_paths = [
                "/usr/bin/geckodriver",
                "/usr/local/bin/geckodriver",
                "/snap/bin/geckodriver"
            ]
            
            for path in possible_firefox_paths:
                if os.path.exists(path):
                    firefox_path = path
                    break
            
            for path in possible_driver_paths:
                if os.path.exists(path):
                    driver_path = path
                    break
            
            if firefox_path:
                options.binary_location = firefox_path
                st.success(f"✓ تم العثور على Firefox في: {firefox_path}")
            else:
                st.warning("ⓘ لم يتم العثور على Firefox، سيتم استخدام الافتراضي")
            
            if driver_path:
                service = Service(executable_path=driver_path)
                st.success(f"✓ تم العثور على geckodriver في: {driver_path}")
            else:
                service = Service()
            
            driver = webdriver.Firefox(service=service, options=options)
            st.success("✓ تم تشغيل Firefox باستخدام المسارات الافتراضية")
            return driver
            
        except Exception as e2:
            st.error(f"✗ فشلت جميع المحاولات: {str(e2)}")
            st.error("يرجى التحقق من إعدادات التطبيق")
            raise

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
        failed_count = 0
        for cookie in cookies:
            try:
                # معالجة الكوكيز لـ Firefox
                cookie.pop('expiry', None)
                cookie.pop('sameSite', None)
                
                # ضمان وجود domain صالح
                if 'domain' not in cookie:
                    base_domain = base_url.replace('https://', '').replace('http://', '').split('/')[0]
                    cookie['domain'] = base_domain
                
                driver.add_cookie(cookie)
                success_count += 1
            except Exception as e:
                failed_count += 1
                st.warning(f"⚠️ لم يتم تحميل كوكي: {cookie.get('name', 'غير معروف')} - {str(e)}")
        
        driver.refresh()
        time.sleep(3)
        
        if success_count > 0:
            st.success(f"✓ تم تحميل {success_count} كوكي بنجاح من {filename}")
            if failed_count > 0:
                st.warning(f"⚠️ فشل تحميل {failed_count} كوكي")
        return True
    except Exception as e:
        st.error(f"✗ فشل تحميل الكوكيز: {str(e)}")
        return False

# --- الواجهة الرئيسية ---
st.title("مدير جلسات Firefox")

col1, col2 = st.columns(2)

with col1:
    direct_access = st.button("🦊 الدخول المباشر إلى Firefox", use_container_width=True, 
                             help="افتح Firefox جديد بدون استخدام أي جلسات محفوظة")

with col2:
    session_access = st.button("🍪 استخدام الجلسة المحفوظة", use_container_width=True,
                              help="استخدم الجلسة المحفوظة مسبقًا (إذا كانت متوفرة)")

# --- الإعدادات ---
with st.expander("⚙️ إعدادات Firefox"):
    site_url = st.text_input("رابط الموقع", "https://www.google.com", key="site_url")
    
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
    with st.spinner("جاري تشغيل Firefox..."):
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
