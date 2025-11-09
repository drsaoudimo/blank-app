import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import json
import time

"""
## Web Scraping with Session Management on Streamlit Cloud

يستخدم هذا التطبيق Chromium الموجود مسبقًا في بيئة Streamlit Cloud مع إمكانية حفظ واستعادة الجلسات (الكوكيز).
"""

# اسم الملف لحفظ الكوكيز (سيتم حفظه في مجلد التطبيق)
COOKIES_FILE = "/mount/src/cookies/session_cookies.json"
# التأكد من وجود مجلد الحفظ
os.makedirs(os.path.dirname(COOKIES_FILE), exist_ok=True)

def save_cookies_to_file(driver, filename=COOKIES_FILE):
    """تحفظ الكوكيز الحالية من المتصفح إلى ملف محلي."""
    try:
        # الحصول على جميع الكوكيز
        cookies = driver.get_cookies()
        
        # حفظ الكوكيز كـ JSON
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
        # فتح الملف وقراءة الكوكيز
        with open(filename, 'r') as f:
            cookies = json.load(f)
        
        # فتح الموقع الأساسي أولاً (ضروري قبل إضافة الكوكيز)
        driver.get(base_url)
        time.sleep(2)  # انتظار تحميل الصفحة
        
        # إضافة كل كوكي
        success_count = 0
        for cookie in cookies:
            try:
                # إزالة الخصائص غير المدعومة
                cookie.pop('sameSite', None)
                # إضافة الكوكي إلى المتصفح
                driver.add_cookie(cookie)
                success_count += 1
            except Exception as e:
                st.warning(f"⚠️ لم يتم تحميل كوكي: {cookie.get('name', 'غير معروف')} - {e}")
        
        # تحديث الصفحة بعد إضافة الكوكيز
        driver.refresh()
        time.sleep(3)  # انتظار تحديث الصفحة
        
        st.success(f"✓ تم تحميل {success_count} كوكي بنجاح من {filename}")
        return True
    except Exception as e:
        st.error(f"✗ فشل تحميل الكوكيز: {e}")
        return False

def check_login_status(driver, check_url, success_indicator):
    """التحقق من حالة تسجيل الدخول"""
    try:
        driver.get(check_url)
        time.sleep(2)
        
        # التحقق من وجود عنصر يشير إلى تسجيل الدخول
        page_source = driver.page_source.lower()
        if success_indicator.lower() in page_source:
            return True
        return False
    except Exception as e:
        st.error(f"✗ خطأ في التحقق من حالة تسجيل الدخول: {e}")
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
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-breakpad")
    options.add_argument("--disable-notifications")
    options.add_argument("--mute-audio")
    
    # تحديد مسار Chromium الموجود مسبقًا على Streamlit Cloud
    options.binary_location = "/usr/bin/chromium-browser"
    
    # استخدام chromedriver الموجود في النظام
    service = Service(executable_path="/usr/bin/chromedriver")
    
    # إنشاء السائق
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# --- واجهة Streamlit ---
st.title("إدارة جلسات المستخدم مع Selenium")

# إعدادات الموقع المستهدف
st.subheader("إعدادات الموقع")
site_url = st.text_input("رابط الموقع الرئيسي", "https://example.com")
login_url = st.text_input("رابط صفحة تسجيل الدخول", "https://example.com/login")
check_login_url = st.text_input("رابط التحقق من تسجيل الدخول", site_url)
success_indicator = st.text_input("نص يشير إلى تسجيل الدخول الناجح", "Welcome")

# إعدادات تسجيل الدخول
st.subheader("بيانات تسجيل الدخول")
username = st.text_input("اسم المستخدم")
password = st.text_input("كلمة المرور", type="password")

col1, col2, col3 = st.columns(3)

with col1:
    login_btn = st.button("تسجيل الدخول وحفظ الجلسة")
with col2:
    load_btn = st.button("تحميل الجلسة المحفوظة")
with col3:
    clear_btn = st.button("مسح الجلسة المحفوظة")

result_container = st.empty()
source_container = st.empty()

# --- تسجيل الدخول وحفظ الكوكيز ---
if login_btn and username and password:
    with st.spinner("جاري تسجيل الدخول..."):
        driver = get_driver()
        try:
            # فتح صفحة تسجيل الدخول
            driver.get(login_url)
            time.sleep(3)
            
            # إدخال اسم المستخدم وكلمة المرور (يجب تعديل العناصر حسب الموقع الفعلي)
            # مثال لطريقة العثور على العناصر:
            try:
                username_field = driver.find_element(By.NAME, "username")
                password_field = driver.find_element(By.NAME, "password")
                submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                
                username_field.send_keys(username)
                password_field.send_keys(password)
                submit_button.click()
                time.sleep(5)  # انتظار عملية تسجيل الدخول
                
                # التحقق من نجاح تسجيل الدخول
                if check_login_status(driver, check_login_url, success_indicator):
                    # حفظ الكوكيز
                    if save_cookies_to_file(driver):
                        result_container.success("✓ تم تسجيل الدخول وحفظ الجلسة بنجاح!")
                        
                        # عرض جزء من مصدر الصفحة
                        page_source = driver.page_source
                        source_container.code(page_source[:1000] + "...")
                else:
                    result_container.error("✗ فشل في تسجيل الدخول. يرجى التحقق من البيانات.")
                    source_container.code(driver.page_source[:1000] + "...")
            except Exception as e:
                result_container.error(f"✗ خطأ في عملية تسجيل الدخول: {e}")
                source_container.code(driver.page_source[:1000] + "...")
        finally:
            driver.quit()

# --- تحميل الجلسة المحفوظة ---
if load_btn:
    with st.spinner("جاري تحميل الجلسة المحفوظة..."):
        driver = get_driver()
        try:
            # محاولة تحميل الكوكيز
            if load_cookies_from_file(driver, site_url):
                # التحقق من حالة تسجيل الدخول
                if check_login_status(driver, check_login_url, success_indicator):
                    result_container.success("✓ تم تحميل الجلسة بنجاح!")
                    
                    # عرض جزء من مصدر الصفحة
                    page_source = driver.page_source
                    source_container.code(page_source[:1000] + "...")
                else:
                    result_container.warning("⚠️ تم تحميل الكوكيز ولكن لم يتم التحقق من تسجيل الدخول.")
                    source_container.code(driver.page_source[:1000] + "...")
            else:
                result_container.error("✗ لم يتم العثور على ملف جلسة محفوظة.")
        finally:
            driver.quit()

# --- مسح ملف الجلسة المحفوظة ---
if clear_btn:
    try:
        if os.path.exists(COOKIES_FILE):
            os.remove(COOKIES_FILE)
            st.success(f"✓ تم مسح ملف الجلسة: {COOKIES_FILE}")
        else:
            st.info("ⓘ لا يوجد ملف جلسة محفوظة للمسح.")
    except Exception as e:
        st.error(f"✗ خطأ في مسح ملف الجلسة: {e}")
