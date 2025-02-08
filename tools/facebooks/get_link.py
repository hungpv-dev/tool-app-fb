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
from sql.posts import Post   
# fanpage_process_instance = get_fanpage_process_instance()

def process_crawl(urls):
    try:
        manager = Browser('/crawl', loadContent=True)
        browser = manager.start(False)  # Khởi tạo trình duyệt
        for url in urls:
            browser.get(url)  # Chuyển hướng
            h1 = browser.find_element(By.CSS_SELECTOR, 'h1')
            content_div = browser.find_element(By.CSS_SELECTOR, 'div.entry-content')
            elements = content_div.find_elements(By.XPATH, './/p | .//h2 ')
            content = ""
            for element in elements:
                if element.tag_name in ['p', 'h2']:
                    content += element.get_attribute('outerHTML')
            response = Post().insert_post({'post': {
                'content': content,
                'link_facebook': url
            }})
            if response.get("status_code") == 200:
                print("Bài viết đã được thêm vào database")
            else:
                print("Lỗi khi thêm bài viết vào database")
            sleep(4)  # Đợi 4s
    except Exception as e:
        logging.error(f"Lỗi: {e}")
        print(f"Lỗi: {e}")
    finally:
        if browser:
            browser.quit()
