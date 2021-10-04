import json
import logging
from decimal import Decimal

import requests.utils
from bs4 import BeautifulSoup

from storescraper.categories import NOTEBOOK, VIDEO_CARD, PROCESSOR, MONITOR, \
    TELEVISION, MOTHERBOARD, RAM, STORAGE_DRIVE, SOLID_STATE_DRIVE, \
    POWER_SUPPLY, COMPUTER_CASE, CPU_COOLER, TABLET, PRINTER, CELL, CAMERA, \
    EXTERNAL_STORAGE_DRIVE, USB_FLASH_DRIVE, MEMORY_CARD, PROJECTOR, \
    VIDEO_GAME_CONSOLE, STEREO_SYSTEM, ALL_IN_ONE, MOUSE, OPTICAL_DRIVE, \
    KEYBOARD, KEYBOARD_MOUSE_COMBO, WEARABLE, UPS, AIR_CONDITIONER, \
    GAMING_CHAIR, REFRIGERATOR, WASHING_MACHINE
from storescraper.product import Product
from storescraper.store import Store
from storescraper.utils import session_with_proxy, remove_words


class PcFactory(Store):
    @classmethod
    def categories(cls):
        return [
            NOTEBOOK,
            VIDEO_CARD,
            PROCESSOR,
            MONITOR,
            TELEVISION,
            MOTHERBOARD,
            RAM,
            STORAGE_DRIVE,
            SOLID_STATE_DRIVE,
            POWER_SUPPLY,
            COMPUTER_CASE,
            CPU_COOLER,
            TABLET,
            PRINTER,
            CELL,
            CAMERA,
            EXTERNAL_STORAGE_DRIVE,
            USB_FLASH_DRIVE,
            MEMORY_CARD,
            PROJECTOR,
            VIDEO_GAME_CONSOLE,
            STEREO_SYSTEM,
            ALL_IN_ONE,
            MOUSE,
            OPTICAL_DRIVE,
            KEYBOARD,
            KEYBOARD_MOUSE_COMBO,
            WEARABLE,
            UPS,
            AIR_CONDITIONER,
            GAMING_CHAIR,
            REFRIGERATOR,
            WASHING_MACHINE
        ]

    @classmethod
    def discover_urls_for_category(cls, category, extra_args=None):
        session = session_with_proxy(extra_args)

        if extra_args and 'cookies' in extra_args:
            session.cookies = requests.utils.cookiejar_from_dict(
                extra_args['cookies'])

        # Productos normales
        url_extensions = [
            ['735', NOTEBOOK],
            ['334', VIDEO_CARD],
            ['272', PROCESSOR],
            ['995', MONITOR],
            ['789', TELEVISION],
            ['292', MOTHERBOARD],
            ['112', RAM],
            ['100', RAM],
            ['266', RAM],
            ['340', STORAGE_DRIVE],
            ['421', STORAGE_DRIVE],
            ['932', STORAGE_DRIVE],
            ['411', STORAGE_DRIVE],
            ['585', SOLID_STATE_DRIVE],
            ['54', POWER_SUPPLY],
            ['16', COMPUTER_CASE],
            ['328', COMPUTER_CASE],
            ['42', CPU_COOLER],
            ['994', TABLET],
            ['262', PRINTER],
            ['432', CELL],
            ['6', CAMERA],
            ['620', CAMERA],
            ['422', EXTERNAL_STORAGE_DRIVE],
            ['904', EXTERNAL_STORAGE_DRIVE],
            ['218', USB_FLASH_DRIVE],
            ['48', MEMORY_CARD],
            ['46', PROJECTOR],
            ['438', VIDEO_GAME_CONSOLE],
            ['889', STEREO_SYSTEM],
            ['890', STEREO_SYSTEM],
            ['798', STEREO_SYSTEM],
            ['700', STEREO_SYSTEM],
            ['831', STEREO_SYSTEM],
            ['34', STEREO_SYSTEM],
            ['797', STEREO_SYSTEM],
            ['748', STEREO_SYSTEM],
            ['475', ALL_IN_ONE],
            ['22', MOUSE],
            ['286', OPTICAL_DRIVE],
            ['36', KEYBOARD],
            ['418', KEYBOARD_MOUSE_COMBO],
            ['685', WEARABLE],
            ['38', UPS],
            ['1026', AIR_CONDITIONER],
            ['1007', GAMING_CHAIR],
            ['1103', REFRIGERATOR],
            ['1104', WASHING_MACHINE],
        ]
        product_urls = []
        for url_extension, local_category in url_extensions:
            if local_category != category:
                continue
            page = 1
            while True:
                if page > 10:
                    raise Exception('page overflow: ' + url_extension)
                url_webpage = 'https://www.pcfactory.cl/a?categoria={}&' \
                              'pagina={}'.format(url_extension, page)
                print(url_webpage)
                response = session.get(url_webpage)
                soup = BeautifulSoup(response.text, 'html.parser')
                product_containers = soup.findAll('div', 'product')

                if not product_containers:
                    if page == 1:
                        logging.warning('Empty category: ' + url_extension)
                    break
                for container in product_containers:
                    product_url = container.find('a')['href']
                    product_urls.append(
                        'https://www.pcfactory.cl' + product_url)
                page += 1

        # Segunda seleccción
        url_extensions = [
            ['liq-celulares', CELL],
            ['liq-tablets', TABLET],
            ['liq-notebook', NOTEBOOK],
            ['liq-aio', ALL_IN_ONE],
            ['liq-tv', TELEVISION],
            ['liq-smart', WEARABLE],
            ['liq-impresoras', PRINTER],
        ]

        for url_extension, local_category in url_extensions:
            if local_category != category:
                continue
            url_webpage = 'https://www.pcfactory.cl/{}'.format(url_extension)
            print(url_webpage)
            response = session.get(url_webpage)
            soup = BeautifulSoup(response.text, 'html.parser')
            product_containers = soup.findAll('div', 'product')

            if not product_containers:
                continue

            for container in product_containers:
                product_url = container.find('a')['href']
                product_urls.append(
                    'https://www.pcfactory.cl' + product_url)

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)

        if extra_args and 'cookies' in extra_args:
            session.cookies = requests.utils.cookiejar_from_dict(
                extra_args['cookies'])

        response = session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        sku_tag = soup.find('input', {'name': 'data_id_producto'})

        if 'value' not in sku_tag.attrs:
            return []

        sku = sku_tag['value']

        body = json.dumps(
            {'requests': [{'indexName': 'productos_sort_price_asc',
                           'params': 'hitsPerPage=1000&query={}'.format(
                               sku)}]})
        api_response = session.post(
            'https://ed3kwid4nw-dsn.algolia.net/1/indexes/*/queries?x'
            '-algolia-api-key=8e5bacd98938c96a0f1d8a50bd86e0cc&x-algolia'
            '-application-id=ED3KWID4NW',
            data=body)
        json_container = json.loads(api_response.text)

        product_json = None

        for product in json_container['results'][0]['hits']:
            if product['idProducto'] == int(sku):
                product_json = product
                break

        if not product_json:
            return []

        part_number = product_json['partno']
        name = product_json['nombre']
        stock = sum(stock['stock'] for stock in product_json['stockSucursal'])
        price_container = soup.find('div', 'product-single__price').findAll(
            'div', 'price-xl')
        normal_price = Decimal(remove_words(price_container[1].text))
        offer_price = Decimal(remove_words(price_container[0].text))
        picture_urls = ['https://www.pcfactory.cl' + tag['src'].split('?t')[0]
                        for tag in
                        soup.find('div', 'product-single__gallery').findAll(
                            'img')]

        if 'LIQ' in name:
            condition = 'https://schema.org/RefurbishedCondition'
        else:
            condition = 'https://schema.org/NewCondition'

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
            part_number=part_number,
            picture_urls=picture_urls,
            condition=condition
        )
        return [p]

    @classmethod
    def preflight(cls, extra_args=None):
        if extra_args and extra_args.get('queueit'):
            session = session_with_proxy(extra_args)
            res = session.get('https://www.pcfactory.cl/', allow_redirects=False)
            assert res.status_code == 302
            url = res.headers['Location']
            fixed_url = url.replace('http%3A', 'https%3A')
            res = session.get(fixed_url)
            assert res.status_code == 200

            cookies = requests.utils.dict_from_cookiejar(res.cookies)
            return {
                'cookies': cookies
            }
        else:
            return {}
