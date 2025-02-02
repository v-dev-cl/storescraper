import json
from collections import defaultdict

from decimal import Decimal
import validators

from storescraper.product import Product
from storescraper.store import Store
from storescraper.utils import session_with_proxy, check_ean13


class Jumbo(Store):
    @classmethod
    def categories(cls):
        return [
            'Groceries'
        ]

    @classmethod
    def discover_entries_for_category(cls, category, extra_args=None):
        url_extensions = [
            ['despensa', ['Groceries'], 'Despensa', 1],
        ]

        session = session_with_proxy(extra_args)
        session.headers['x-api-key'] = 'IuimuMneIKJd3tapno2Ag1c1WcAES97j'
        product_entries = defaultdict(lambda: [])

        for url_extension, local_categories, section_name, category_weight in \
                url_extensions:

            if category not in local_categories:
                continue

            page = 1

            while True:
                if page >= 75:
                    raise Exception('Page overflow: ' + url_extension)

                api_url = 'https://apijumboweb.smdigital.cl/catalog/api/v2/' \
                          'products/{}?page={}'.format(
                              url_extension, page)
                print(api_url)

                response = session.get(api_url)

                json_data = json.loads(response.text)

                if "status" in json_data and (json_data["status"] == 500
                                              or json_data["status"] == 400):
                    break

                for idx, product in enumerate(json_data['products']):
                    product_url = 'https://www.jumbo.cl/{}/p' \
                        .format(product['linkText'])

                    product_entries[product_url].append({
                        'category_weight': category_weight,
                        'section_name': section_name,
                        'value': 40 * (page - 1) + idx + 1
                    })

                page += 1

        return product_entries

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        api_url = 'https://apijumboweb.smdigital.cl/catalog/api/v1' \
                  '/catalog_system/pub/products/search/{}/p?sc=11'. \
            format(url.split('/')[3])
        session.headers['x-api-key'] = 'IuimuMneIKJd3tapno2Ag1c1WcAES97j'
        api_request = session.get(api_url)
        data = api_request.json()

        if len(data) == 0:
            return []

        api_json = data[0]
        name = api_json['brand'] + ' - ' + api_json['productName']
        sku = api_json['productReference']
        description = api_json['categories'][0]

        product_item = api_json['items'][0]
        seller_info = product_item['sellers'][0]['commertialOffer']
        ean = product_item.get('ean', None)

        if ean and not check_ean13(ean):
            ean = None

        price = Decimal(seller_info['Price'])

        if seller_info['AvailableQuantity'] == 0:
            return []

        picture_urls = []
        for i in product_item['images']:
            image = i['imageUrl'].split('?')[0]
            if validators.url(image):
                picture_urls.append(image)

        p = Product(
            name,
            cls.__name__,
            category,
            url,
            url,
            sku,
            -1,
            price,
            price,
            'CLP',
            sku=sku,
            ean=ean,
            picture_urls=picture_urls,
            description=description
        )

        return [p]
