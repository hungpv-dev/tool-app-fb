# import sys
from tools.driver import Browser
import logging
from selenium.webdriver.common.by import By
# from tools.facebooks.browser_pages import BrowserFanpage
from time import sleep
# from main.fanpage import get_fanpage_process_instance
# from sql.errors import Error
# from bot import send
# from helpers.global_value import get_global_theard_event
# global_theard_event = get_global_theard_event()
# fanpage_process_instance = get_fanpage_process_instance()

def process_crawl():
    try:
        manager = Browser('/crawl',loadContent=True)
        browser = manager.start(False) # Khởi tạo trình duyệt
        browser.get("https://insursafe.com/2024/12/24/dna-test-results-reveal-shocking-truth-about-prince-harrys-parentage") # Chuyển hướng
        h1 = browser.find_element(By.CSS_SELECTOR,'h1')
        print(h1.text)
        sleep(1000) # Đợi 10s 
    except Exception as e:
        logging.error(f"Lỗi: {e}")
        print(f"Lỗi: {e}")
    finally:
        if browser:
            browser.quit() # Đóng trình duyệt


