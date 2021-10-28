import logging

from bs4 import BeautifulSoup

from storescraper.categories import REFRIGERATOR
from storescraper.store import Store
from storescraper.utils import session_with_proxy


class TiendasAmal(Store):
    @classmethod
    def categories(cls):
        return [
            REFRIGERATOR
        ]

    @classmethod
    def discover_urls_for_category(cls, category, extra_args=None):
        local_categories = [
            REFRIGERATOR
        ]
        session = session_with_proxy(extra_args)
        session.headers['User-Agent'] = \
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, ' \
            'like Gecko) Chrome/66.0.3359.117 Safari/537.36'
        product_urls = []
        for local_category in local_categories:
            if local_category != category:
                continue
            page = 1
            while True:
                if page > 10:
                    raise Exception('page overflow: ' + local_category)

                url_webpage = 'https://tiendasamal.com/ve/busqueda?' \
                              'controller=search&s=lg&page={}'.format(page)

                print(url_webpage)
                response = session.get(url_webpage)
                soup = BeautifulSoup(response.text, 'html.parser')
                import ipdb
                ipdb.set_trace()
                product_containers = soup.findAll('article',
                                                  'product-miniature')

                if not product_containers:
                    if page == 1:
                        logging.warning('empty category: ' + local_category)
                    break

                for container in product_containers:
                    product_url = container.find('a')['href']
                    if 'lg' in product_url.lower():
                        product_url.append(product_url)
                page += 1
            return product_urls
