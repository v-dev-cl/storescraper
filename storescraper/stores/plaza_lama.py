import json
import logging

from bs4 import BeautifulSoup
from decimal import Decimal

from storescraper.product import Product
from storescraper.store import Store
from storescraper.utils import session_with_proxy
from storescraper.categories import TELEVISION


class PlazaLama(Store):
    @classmethod
    def categories(cls):
        return [
            TELEVISION
        ]

    @classmethod
    def discover_urls_for_category(cls, category, extra_args=None):
        # Only interested in LG products

        session = session_with_proxy(extra_args)
        product_urls = []
        if TELEVISION != category:
            return []

        page = 1
        while True:
            if page >= 15:
                raise Exception('Page overflow')

            url = 'https://www.plazalama.com.do/collections/lg' \
                '?page={}'.format(page)
            print(url)
            response = session.get(url)
            soup = BeautifulSoup(response.text, 'html5lib')
            product_containers = soup.findAll('div', 'product-item')

            if not product_containers:
                if page == 1:
                    logging.warning('Empty category:' + url)
                break

            for container in product_containers:
                product_url = container.find('a')['href']
                product_urls.append(
                    'https://www.plazalama.com.do' + product_url)
            page += 1
        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        response = session.get(url)
        soup = BeautifulSoup(response.text, 'html5lib')

        json_data = json.loads(soup.findAll(
            'script', {'type': 'application/json'})[-1].text)
        json_product = json_data['product']

        description = json_product['description']
        picture_urls = ['https:' + i for i in json_product['images']]

        json_data_variants = json_product['variants']

        products = []
        for v_data in json_data_variants:

            key = str(v_data['id'])
            sku = v_data['sku']
            name = v_data['name']
            if key in json_data['inventories']:
                stock = int(json_data['inventories']
                            [key]['inventory_quantity'])
            else:
                stock = 0
            price = Decimal(v_data['price']) / Decimal(100)

            p = Product(
                name,
                cls.__name__,
                category,
                url,
                url,
                sku,
                stock,
                price,
                price,
                'DOP',
                sku=sku,
                picture_urls=picture_urls,
                description=description
            )
            products.append(p)

        return products
