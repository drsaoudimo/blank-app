import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import os
import json
import time

"""
## Web Scraping with Session Management on Streamlit Cloud

تطبيق يدعم جلسات التصفح مع إمكانية الدخول المباشر أو استخدام جلسة محفوظة.
"""

# اسم الملف لحفظ الكوكيز
COOKIES_FILE = "/mount/src/cookies/session_cookies.json"
os.makedirs(os.path.dirname(COOKIES_FILE), exist_ok=True)

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
                cookie.pop('sameSite', None)
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

@st.cache_resource
def get_driver():
    """إنشاء مثيل المتصفح المناسب لبيئة Streamlit Cloud"""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-setuid-sandbox")
    options.binary_location = "/usr/bin/chromium-browser"
    service = Service(executable_path="/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# --- الواجهة الرئيسية مع الزرين ---
st.title("مدير جلسات التصفح")

st.markdown("""
### اختر طريقة الدخول:
اختر بين الدخول المباشر أو استخدام جلسة محفوظة (إذا كانت متوفرة)
""")

col1, col2 = st.columns(2)

with col1:
    direct_access = st.button("🖥️ الدخول المباشر إلى المتصفح", use_container_width=True, 
                             help="افتح متصفح جديد بدون استخدام أي جلسات محفوظة")

with col2:
    session_access = st.button("🍪 استخدام الجلسة المحفوظة", use_container_width=True,
                              help="استخدم الجلسة المحفوظة مسبقًا (إذا كانت متوفرة)")

# --- الإعدادات المتقدمة (قابلة للطي) ---
with st.expander("⚙️ الإعدادات المتقدمة"):
    site_url = st.text_input("رابط الموقع الافتراضي", "https://example.com")
    
    st.subheader("إعدادات تسجيل الدخول")
    login_url = st.text_input("رابط صفحة تسجيل الدخول", "https://example.com/login")
    username = st.text_input("اسم المستخدم للتسجيل")
    password = st.text_input("كلمة المرور", type="password")
    
    st.subheader("إدارة الجلسات")
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

# --- نتيجة التنفيذ ---
result_container = st.empty()
source_container = st.empty()

# --- معالجة زر الدخول المباشر ---
if direct_access:
    with st.spinner("جاري فتح المتصفح..."):
        driver = get_driver()
        try:
            driver.get(site_url)
            time.sleep(3)
            
            result_container.success(f"✓ تم الدخول بنجاح إلى {site_url}")
            
            # خيار حفظ الجلسة بعد التصفح
            if st.button("حفظ هذه الجلسة"):
                save_cookies_to_file(driver)
                st.rerun()
            
            # عرض مصدر الصفحة
            page_source = driver.page_source
            source_container.text_area("مصدر الصفحة", page_source[:2000] + "...", height=300)
        except Exception as e:
            result_container.error(f"✗ حدث خطأ: {e}")
        finally:
            driver.quit()

# --- معالجة زر استخدام الجلسة المحفوظة ---
if session_access:
    with st.spinner("جاري تحميل الجلسة المحفوظة..."):
        driver = get_driver()
        try:
            if load_cookies_from_file(driver, site_url):
                driver.get(site_url)
                time.sleep(3)
                
                result_container.success(f"✓ تم الدخول باستخدام الجلسة المحفوظة إلى {site_url}")
                
                # عرض مصدر الصفحة
                page_source = driver.page_source
                source_container.text_area("مصدر الصفحة", page_source[:2000] + "...", height=300)
            else:
                # إذا لم توجد جلسة محفوظة، اعرض رسالة وخيارات بديلة
                result_container.warning("⚠️ لم يتم العثور على جلسة محفوظة")
                
                if username and password:
                    if st.button("تسجيل الدخول وحفظ الجلسة الجديدة"):
                        with st.spinner("جاري تسجيل الدخول..."):
                            try:
                                driver.get(login_url)
                                time.sleep(3)
                                
                                # محاولة العثور على حقول تسجيل الدخول (تحتاج للتخصيص حسب الموقع)
                                try:
                                    username_field = driver.find_element(By.NAME, "username") or \
                                                    driver.find_element(By.ID, "username") or \
                                                    driver.find_element(By.CSS_SELECTOR, "input[type='text']")
                                    
                                    password_field = driver.find_element(By.NAME, "password") or \
                                                    driver.find_element(By.ID, "password") or \
                                                    driver.find_element(By.CSS_SELECTOR, "input[type='password']")
                                    
                                    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
                                    
                                    username_field.send_keys(username)
                                    password_field.send_keys(password)
                                    submit_button.click()
                                    time.sleep(5)
                                    
                                    # حفظ الكوكيز بعد تسجيل الدخول
                                    save_cookies_to_file(driver)
                                    
                                    # إعادة تحميل الصفحة الرئيسية
                                    driver.get(site_url)
                                    time.sleep(3)
                                    
                                    result_container.success("✓ تم تسجيل الدخول وحفظ الجلسة الجديدة")
                                    
                                    # عرض مصدر الصفحة
                                    page_source = driver.page_source
                                    source_container.text_area("مصدر الصفحة", page_source[:2000] + "...", height=300)
                                    
                                except Exception as e:
                                    st.error(f"✗ فشل عملية تسجيل الدخول: {e}")
                                    source_container.text_area("مصدر صفحة تسجيل الدخول", driver.page_source[:2000] + "...", height=300)
                            except Exception as e:
                                st.error(f"✗ حدث خطأ أثناء تسجيل الدخول: {e}")
                else:
                    st.info("ⓘ يرجى إدخال بيانات تسجيل الدخول في الإعدادات المتقدمة لحفظ جلسة جديدة")
        except Exception as e:
            result_container.error(f"✗ حدث خطأ: {e}")
        finally:
            driver.quit()
