from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service  # Sửa lại import
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from helpers.base import config

service = Service(config('driver_path'))
driver = webdriver.Chrome(service=service)

# Mở trang web
driver.get('https://checknews.online/96837?utm_source=L0805&utm_medium=ConorMcGregorFans&utm_campaign=Medibox&utm_content=Facebook')

# Chờ trang tải xong (nếu cần thiết)
time.sleep(3)

# Lấy nội dung của trang sau khi trang đã tải
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Lấy title của trang
title = soup.title.string
print(f"Title: {title}")

# Lấy content (thường là bài viết chính, có thể tìm theo thẻ <article>, <div>, hoặc <section>)
content = soup.find('div', class_='content')  # Tùy thuộc vào cấu trúc trang web, bạn có thể thay đổi selector
if content:
    print(f"Content: {content.text.strip()}")
else:
    print("Không tìm thấy nội dung.")

# Lấy footer (thường có thông tin bản quyền, liên kết, v.v.)
footer = soup.find('footer')
if footer:
    print(f"Footer: {footer.text.strip()}")
else:
    print("Không tìm thấy footer.")

# Đóng trình duyệt
driver.quit()
