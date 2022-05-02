import json
import re
import time
import urllib.parse
from decimal import Decimal

from bs4 import BeautifulSoup

from storescraper.categories import CELL, WEARABLE, TELEVISION, \
    STEREO_SYSTEM, NOTEBOOK, MONITOR, EXTERNAL_STORAGE_DRIVE, TABLET, \
    HEADPHONES, MOUSE, GAMING_CHAIR, WASHING_MACHINE, REFRIGERATOR, OVEN, \
    AIR_CONDITIONER
from storescraper.product import Product
from storescraper.store import Store
from storescraper.utils import session_with_proxy


class TravelTienda(Store):
    @classmethod
    def categories(cls):
        return [
            CELL,
            WEARABLE,
            STEREO_SYSTEM,
            TELEVISION,
            NOTEBOOK,
            MONITOR,
            EXTERNAL_STORAGE_DRIVE,
            TABLET,
            HEADPHONES,
            MOUSE,
            GAMING_CHAIR,
            WASHING_MACHINE,
            REFRIGERATOR,
            OVEN,
            AIR_CONDITIONER
        ]

    @classmethod
    def discover_urls_for_category(cls, category, extra_args=None):
        category_paths = [
            ('3842720512', CELL),
            ('444586937', WEARABLE),
            ('2234300147', STEREO_SYSTEM),
            ('2722336774', TELEVISION),
            ('3415774358', NOTEBOOK),
            ('375810843', MONITOR),
            ('2306324657', EXTERNAL_STORAGE_DRIVE),
            ('2934181475', TABLET),
            ('1226813193', HEADPHONES),
            ('2547146328', MOUSE),
            ('714969430', GAMING_CHAIR),
            ('326296390', STEREO_SYSTEM),
            ('3121709090', HEADPHONES),
            ('1345767085', STEREO_SYSTEM),
            ('1095159098', STEREO_SYSTEM),
            ('3514911626', STEREO_SYSTEM),
            ('3551610308', STEREO_SYSTEM),
            ('2620100069', WASHING_MACHINE),
            ('306745319', REFRIGERATOR),
            ('394354836', WASHING_MACHINE),
            ('831669398', OVEN),
            ('628735343', AIR_CONDITIONER),
        ]

        session = session_with_proxy(extra_args)
        product_urls = []

        print(category)

        for category_path, local_category in category_paths:
            if local_category != category:
                continue

            url_webpage = 'https://tienda.travel.cl/ccstore/v1/assembler/' \
                          'pages/Default/osf/catalog/_/N-{}?Nrpp=1000' \
                          '&Nr=AND%28sku.availabilityStatus%3AINSTOCK%29' \
                          ''.format(category_path)
            response = session.get(url_webpage)
            json_data = response.json()
            for product_entry in json_data['results']['records']:
                product_path = product_entry['attributes']['product.route'][0]
                product_url = 'https://tienda.travel.cl' + product_path
                print(product_url)
                product_urls.append(product_url)
        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        session.headers['user-agent'] = \
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ' \
            '(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
        response = session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        script_tag = soup.find('script', {'data-name': 'occ-structured-data'})

        if not script_tag:
            if extra_args:
                retries = extra_args.get('retries', 5)
                if retries > 0:
                    retries -= 1
                    extra_args['retries'] = retries
                    time.sleep(2)
                    return cls.products_for_url(url, category, extra_args)
                else:
                    raise Exception('Empty product page: ' + url)
            else:
                extra_args = {'retries': 5}
                time.sleep(2)
                return cls.products_for_url(url, category, extra_args)

        product_json = json.loads(script_tag.text)[0]
        data = soup.find('body').find('script').text

        data_clean = urllib.parse.unquote(
            re.search(r'window.state = JSON.parse\(decodeURI\((.+)\)\)',
                      data).groups()[0])
        json_container = list(
            json.loads(data_clean[1:-1])['catalogRepository'][
                'products'].values())[0]
        name = product_json['name']
        sku = product_json['sku']
        stock = -1
        normal_price = Decimal(product_json['offers']['price'])

        offer_price_text = json_container['listPrices']['tiendaBancoDeChile']
        if offer_price_text:
            offer_price = Decimal(offer_price_text)
        else:
            offer_price = normal_price

        picture_urls = ['https://tienda.travel.cl' +
                        picture.replace(' ', '%20') for picture in
                        json_container['fullImageURLs']]

        p = Product(
            name,
            cls.__name__,
            category,
            url,
            url,
            sku,
            stock,
            normal_price,
            offer_price,
            'CLP',
            sku=sku,
            picture_urls=picture_urls
        )

        return [p]
