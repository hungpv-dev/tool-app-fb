from helpers.global_value import get_global_theard_event
from main.link import get_link_process_instance
from time import sleep
from tools.driver import Browser
import logging
import requests
from selenium.webdriver.common.by import By
from sql.posts import Post
from bs4 import BeautifulSoup
from helpers.fb import clean_facebook_url_redirect

link_process = get_link_process_instance()
global_theard_event = get_global_theard_event()

def start_crawl_web(tab_id, stop_event):
    try:
        manager = Browser('/crawl')
        browser = manager.start(False)
        link_process.update_process(tab_id, 'Đang chuẩn bị cào dữ liệu....')
        post = Post()
        while not stop_event.is_set() and not global_theard_event.is_set():
            try:
                # Extract the link from the provided API object
                data = post.get_url_by_post()
                url = data.get('link')
                if not url:
                    print("Không tìm thấy URL trong object API")
                    link_process.stop_process(tab_id)
                    break
                url = clean_facebook_url_redirect(url)
                response = requests.head(url)
                if response.status_code >= 400:
                    logging.error(f"Lỗi HTTP {response.status_code} khi truy cập {url}")
                    link_process.update_process(tab_id, f'Lỗi HTTP {response.status_code} khi truy cập {url}')
                    post.put_url_by_post(data.get('id'))
                    continue  # Bỏ qua và tiếp tục với URL tiếp theo
                browser.get(url)
                link_process.update_process(tab_id, f'Đang cào dữ liệu {url}')
                try:
                    h1_element = browser.find_element(By.XPATH, '//h1[not(.//a)]')
                    title = h1_element.text
                except Exception as e:
                    logging.error(f"Lỗi khi tìm thẻ <h1> từ {url}: {e}")
                    link_process.update_process(tab_id, f'Lỗi khi cào dữ liệu {url}')
                    post.put_url_by_post(data.get('id'))
                    continue  # Bỏ qua và tiếp tục với URL tiếp theo
                html = browser.page_source
                error_indicators = ["404", "Page Not Found", "not found","Sorry, you have been blocked",'Connection timed out Error code 522','Loading…']
                found_errors = [indicator for indicator in error_indicators if indicator.lower() in html.lower()]
                
                if found_errors:
                    error_message = "Error: The requested URL was not found on the server. Indicators: " + ", ".join(found_errors)
                    link_process.update_process(tab_id, error_message)
                    post.put_url_by_post(data.get('id'))
                    continue  # Bỏ qua và tiếp tục với URL tiếp theo
       
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
                    link_process.update_process(tab_id, f'Cào dữ liệu thành công {url}')
                else:
                    post.put_url_by_post(data.get('id'))
                    link_process.update_process(tab_id, f'Cào dữ liệu thất bại {url}')
                sleep(3)  # Đợi 5s trước khi tiếp tục
            except Exception as e:
                logging.error(f"Lỗi khi cào dữ liệu từ {url}: {e}")
                print(f"Lỗi khi cào dữ liệu từ {url}: {e}")
                if browser:
                    browser.quit()
                browser = manager.start(False)
    except Exception as e:
        logging.error(f"Lỗi: {e}")
        print(f"Lỗi: {e}")
    finally:
        if browser:
            browser.quit()
def extract_div_with_p_tags(html):
    soup = BeautifulSoup(html, 'html.parser')
    div_blocks = []

    def find_parent_div_or_article(tag):
        parent = tag.find_parent(['div', 'article'])
        while parent and parent.find('form'):
            parent = parent.find_parent('div')
        return parent

    def add_div_blocks(tag):
        parent = find_parent_div_or_article(tag)
        if parent:
            # Nếu thẻ cha là <div> và chứa <article>, sử dụng <article>
            if parent.name == 'div' and parent.find('article'):
                article = parent.find('article')
                div_blocks.append(article)
            else:
                div_blocks.append(parent)

    # Tìm tất cả các thẻ <p> và thẻ cha <div> hoặc <article> của chúng
    for p in soup.find_all('p'):
        add_div_blocks(p)

    # Đệ quy tìm các thẻ <p> trong các thẻ <div> lồng nhau
    for div in soup.find_all('div'):
        for p in div.find_all('p'):
            add_div_blocks(p)

    return div_blocks

def find_div_with_most_p_tags(div_blocks):
    if not div_blocks:
        return None, 0 
    div_p_counts = [(div, len(div.find_all('p'))) for div in div_blocks]
    
    main_div, num_p_tags = max(div_p_counts, key=lambda x: x[1])
    for div, p_count in div_p_counts:
        if p_count > 2:
            return div, p_count  # Nếu thẻ <div> hoặc <article> chứa nhiều hơn 2 thẻ <p>, chọn luôn thẻ này làm parent
        
        parent_div = div.find_parent(['div', 'article'])
        if parent_div:
            parent_p_count = len(parent_div.find_all('p'))
            if parent_p_count > num_p_tags:
                main_div = parent_div
                num_p_tags = parent_p_count
    
    return main_div, num_p_tags

def extract_relevant_tags(main_div):
    if main_div:
        for div in main_div.find_all('div'):
            for script in div.find_all(['script', 'button']):
                script.decompose()
        for video_tag in main_div.find_all(['video', 'iframe']):
            video_tag.decompose()
        for tag in main_div.find_all(['script', 'style', 'a', 'ins', 'iframe', 'canvas']):
            tag.decompose()
        ad_classes = ['ad', 'advertisement', 'ads', 'adv', 'Ad-Container', 'Ad-Container AdvInTextBuilder_slot-wrapper___Oz3G', 'code-block']
        for ad_class in ad_classes:
            for ad_tag in main_div.find_all(class_=ad_class):
                ad_tag.decompose()
        for div in main_div.find_all('div'):
            if not div.get_text(strip=True) and not div.find_all():
                div.decompose()
        return main_div.decode_contents()
    return ""