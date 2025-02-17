import requests
from bs4 import BeautifulSoup

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
# Ví dụ sử dụng
def main(url):
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    html = response.text
   
    div_blocks = extract_div_with_p_tags(html)
   
    main_div, num_p_tags = find_div_with_most_p_tags(div_blocks)

    relevant_html = extract_relevant_tags(main_div)
    print(relevant_html)
# Truyền URL vào hàm main
url = "https://news.megos.online/326004?utm_source=My1107&utm_medium=RappersMusic&utm_campaign=MediGo"  # Thay thế bằng URL bạn muốn phân tích
main(url)