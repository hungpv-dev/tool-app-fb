from tools.driver import Browser
import logging
from selenium.webdriver.common.by import By
from time import sleep
from sql.posts import Post
from bs4 import BeautifulSoup

def extract_div_with_p_tags(html):
    soup = BeautifulSoup(html, 'html.parser')
    div_blocks = []

    # Lọc tất cả các thẻ <p> và tìm thẻ <div> gần nhất chứa thẻ <p>
    for p in soup.find_all('p'):
        div = p.find_parent('div')
        if div:
            div_blocks.append(div)
    
    return div_blocks

def find_div_with_most_p_tags(div_blocks):
    if not div_blocks:
        return None, 0  # Nếu không tìm thấy thẻ <div> nào có thẻ <p>
    
    # Đếm số lượng thẻ <p> trong từng thẻ <div>
    div_p_counts = [(div, len(div.find_all('p'))) for div in div_blocks]
    
    # Sắp xếp các thẻ <div> theo số lượng thẻ <p> chứa trong đó
    main_div, num_p_tags = max(div_p_counts, key=lambda x: x[1])
    return main_div, num_p_tags

def extract_relevant_tags(main_div):
    relevant_html = ""
    if (main_div):
        for tag in main_div.find_all(recursive=False):
            if tag.name not in ['div', 'script']:
                relevant_html += str(tag)
            elif tag.name == 'div':
                for sub_tag in tag.find_all(recursive=False):
                    if sub_tag.name not in ['div', 'script']:
                        relevant_html += str(sub_tag)
    return relevant_html

def process_crawl(urls):
    try:
        manager = Browser('/crawl', loadContent=True)
        browser = manager.start(False)  # Khởi tạo trình duyệt
        for url in urls:
            browser.get(url)  # Chuyển hướng
            h1 = browser.find_element(By.CSS_SELECTOR, 'h1')
            title = h1.text
            html = browser.page_source

            # Phân tích HTML và tìm thẻ <div> chứa nhiều thẻ <p> nhất
            div_blocks = extract_div_with_p_tags(html)
            main_div, num_p_tags = find_div_with_most_p_tags(div_blocks)
            relevant_html = extract_relevant_tags(main_div)
            print(relevant_html)
            response = Post().insert_post_web({'post': {
                'content': relevant_html,
                'link_facebook': url,
                "title": title,
                'images': []
            }})
            if response.get("status_code") == 200:
                print("Bài viết đã được thêm vào database")
            else:
                print("Lỗi khi thêm bài viết vào database")
            sleep(10)  # Đợi 4s
    except Exception as e:
        logging.error(f"Lỗi: {e}")
        print(f"Lỗi: {e}")
    finally:
        if browser:
            browser.quit()
