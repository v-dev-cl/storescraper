import logging
from decimal import Decimal

from bs4 import BeautifulSoup

from storescraper.categories import GAMING_CHAIR, HEADPHONES, STEREO_SYSTEM, \
    MOUSE, KEYBOARD, COMPUTER_CASE, MONITOR, SOLID_STATE_DRIVE, \
    STORAGE_DRIVE, POWER_SUPPLY, RAM, MOTHERBOARD, PROCESSOR, VIDEO_CARD, \
    CPU_COOLER
from storescraper.product import Product
from storescraper.store import Store
from storescraper.utils import session_with_proxy, remove_words


class Kessinger(Store):
    @classmethod
    def categories(cls):
        return [
            GAMING_CHAIR,
            HEADPHONES,
            STEREO_SYSTEM,
            MOUSE,
            KEYBOARD,
            COMPUTER_CASE,
            MONITOR,
            SOLID_STATE_DRIVE,
            STORAGE_DRIVE,
            POWER_SUPPLY,
            RAM,
            MOTHERBOARD,
            PROCESSOR,
            VIDEO_CARD,
            CPU_COOLER,
        ]

    @classmethod
    def discover_urls_for_category(cls, category, extra_args=None):
        url_extensions = [
            ['sillas-gamers', GAMING_CHAIR],
            ['audifonos', HEADPHONES],
            ['parlantes', STEREO_SYSTEM],
            ['mouse', MOUSE],
            ['teclados', KEYBOARD],
            ['gabinetes', COMPUTER_CASE],
            ['monitores', MONITOR],
            ['estado-solido-ssd', SOLID_STATE_DRIVE],
            ['disco-duro', STORAGE_DRIVE],
            ['fuentes-de-poder', POWER_SUPPLY],
            ['memorias-ram', RAM],
            ['placas-madre', MOTHERBOARD],
            ['procesadores', PROCESSOR],
            ['tarjetas-graficas', VIDEO_CARD],
            ['refrigeracion-y-ventiladores', CPU_COOLER],
        ]

        session = session_with_proxy(extra_args)
        product_urls = []
        for url_extension, local_category in url_extensions:
            if local_category != category:
                continue
            page = 1
            while True:
                if page > 15:
                    raise Exception('page overflow: ' + url_extension)

                url_webpage = 'https://kessinger.cl/{}/page/{}/'.format(
                    url_extension, page)
                print(url_webpage)
                response = session.get(url_webpage)
                soup = BeautifulSoup(response.text, 'html.parser')
                product_containers = soup.findAll('div', 'product-grid-item')

                if not product_containers:
                    if page == 1:
                        logging.warning('empty category: ' + url_extension)
                    break
                for container in product_containers:
                    product_url = container.find('a')['href']
                    product_urls.append(product_url)
                page += 1
        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        response = session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        name = soup.find('h1', 'product_title').text
        sku = soup.find('link', {'rel': 'shortlink'})['href'].split('p=')[-1]
        if soup.find('p', 'stock').text == 'Sin Stock':
            stock = 0
        else:
            stock_container = soup.find('p', 'stock').text.split()[1]
            stock = int(stock_container) if stock_container.isnumeric() else -1
        if soup.find('p', 'price').text == '':
            return []
        elif len(soup.find('p', 'price').findAll('bdi')) > 1:
            price = Decimal(
                remove_words(soup.find('p', 'price').findAll('bdi')[0].text))

        elif soup.find('p', 'price').find('ins'):
            price = Decimal(
                remove_words(soup.find('p', 'price').find('ins').text))
        else:
            price = Decimal(remove_words(soup.find('p', 'price').text))
        picture_urls = [tag['data-thumb'] for tag in soup.findAll('figure',
                        'woocommerce-product-gallery__image')]
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
            'CLP',
            sku=sku,
            picture_urls=picture_urls
        )
        return [p]
