from tools.facebooks.get_link import process_crawl
from sql.domain import Domain
response = Domain().get_link_by_domain(2)
url = [item['link'] for item in response]

process_crawl(url)