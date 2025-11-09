import streamlit as st

"""
## Web scraping on Streamlit Cloud with Selenium

This is a minimal, reproducible example of how to scrape the web with Selenium and Chrome on Streamlit's Community Cloud.
"""

with st.echo():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.core.os_manager import ChromeType
    import subprocess
    import time

    @st.cache_resource
    def get_driver():
        # تثبيت chromedriver باستخدام webdriver_manager
        driver_path = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
        
        # إعداد خيارات التشغيل
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")
        options.add_argument("--disable-javascript")  # قم بإزالة هذا إذا كنت بحاجة لجافا سكريبت
        
        # إعداد السيرفر
        service = Service(driver_path)
        
        # إنشاء السائق
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    try:
        driver = get_driver()
        driver.get("http://example.com")
        
        # عرض مصدر الصفحة
        st.code(driver.page_source[:500])  # عرض أول 500 حرف فقط
        
        driver.quit()
    except Exception as e:
        st.error(f"حدث خطأ: {e}")
