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
    for p in soup.find_all('p'):
        div = p.find_parent(['div', 'article'])
        while div and div.find('form'):
            div = div.find_parent('div')
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
    if main_div:
        for div in main_div.find_all('div'):
            for script in div.find_all(['script', 'button']):
                script.decompose()
        for video_tag in main_div.find_all(['video', 'iframe']):
            parent_div = video_tag.find_parent('div')
            if parent_div:
                parent_div.decompose()
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