import requests
import logging

class Model:
    def __init__(self):
        self.base_url = "https://htvtonghop.com/api"
        self.headers = {
            'X-CSRF-Token': 'asfytecthungpvphattrien',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        }
        self.proxy = None

    def setProxy(self, proxy):
            try:
                if proxies:
                    proxies = {
                        "http": f"http://{proxy.get('user')}:{proxy.get('pass')}@{proxy.get('ip')}:{proxy.get('port')}",
                        "https": f"http://{proxy.get('user')}:{proxy.get('pass')}@{proxy.get('ip')}:{proxy.get('port')}"
                    }
                    self.proxy = proxies
            except Exception as e:  
                print(f'Lỗi khi set proxy: {e}')
                logging.error(f'Lỗi khi set proxy: {e}')
                pass

    def request(self, method, endpoint, params=None, data=None):
        """
        Hàm chung để xử lý GET, POST, PUT, DELETE với cơ chế fallback nếu proxy lỗi.
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.request(method=method,url=url,params=params,json=data,headers=self.headers,timeout=300,proxies=self.proxy)
            response.raise_for_status()  
            return response.json()
        except (requests.exceptions.ProxyError, requests.exceptions.SSLError):
            print("⚠️ Proxy lỗi! Thử lại không dùng proxy...")
            logging.error("⚠️ Proxy lỗi! Thử lại không dùng proxy...")
            try:
                response = requests.request(method=method,
                    url=url,
                    params=params,
                    json=data,
                    headers=self.headers,
                    timeout=300
                )
                response.raise_for_status()
                return response.json()
            except ValueError:
                return response.text
            except requests.exceptions.RequestException as e:
                print(f"⛔ Request lỗi: {e}")
                logging.error(f"⛔ Request lỗi: {e}")
                return None
        except ValueError:
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"⛔ Request lỗi: {e}")
            logging.error(f"⛔ Request lỗi: {e}")
            return None

    def get(self, endpoint, params=None):
        return self.request("GET", endpoint, params=params)

    def post(self, endpoint, data=None):
        return self.request("POST", endpoint, data=data)

    def put(self, endpoint, data=None):
        return self.request("PUT", endpoint, data=data)

    def delete(self, endpoint, params=None):
        return self.request("DELETE", endpoint, params=params)
