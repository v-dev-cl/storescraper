import re
import time
import json
import requests

from bs4 import BeautifulSoup
from decimal import Decimal

from storescraper.store import Store
from storescraper.product import Product
from storescraper.flixmedia import flixmedia_video_urls
from storescraper.utils import get_cf_session, HeadlessChrome, \
    load_driver_cf_cookies, session_with_proxy, html_to_markdown, \
    CF_REQUEST_HEADERS
from storescraper import banner_sections as bs

from selenium.common.exceptions import NoSuchElementException


class Ripley(Store):
    @classmethod
    def categories(cls):
        return [
            'Notebook',
            'Television',
            'Tablet',
            'Refrigerator',
            'Printer',
            'Oven',
            'Stove',
            'DishWasher'
            'VacuumCleaner',
            'WashingMachine',
            'Cell',
            'Camera',
            'StereoSystem',
            'OpticalDiskPlayer',
            'ExternalStorageDrive',
            'UsbFlashDrive',
            'MemoryCard',
            'Projector',
            'VideoGameConsole',
            'Monitor',
            'AllInOne',
            'AirConditioner',
            'WaterHeater',
            'SolidStateDrive',
            'SpaceHeater',
            'Wearable',
            'Mouse',
            'Keyboard',
            'KeyboardMouseCombo',
            'Headphones',
        ]

    @classmethod
    def discover_urls_for_category(cls, category, extra_args=None):
        return [category]

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        category_paths = [
            ['tecno/computacion/notebooks', ['Notebook'],
             'Tecno > Computación > Notebooks', 1],
            ['tecno/computacion/notebooks-gamer', ['Notebook'],
             'Tecno > Computación > Notebooks gamer', 1],
            ['tecno/computacion/tablets-y-e-readers', ['Tablet'],
             'Tecno > Computación > Tablets y E-readers', 1],
            ['tecno/impresoras-y-tintas', ['Printer'],
             'Tecno > Computación > Impresoras y Tintas', 1],
            ['tecno/computacion/almacenamiento',
             ['UsbFlashDrive', 'ExternalStorageDrive'],
             'Tecno > Computación > Almacenamiento', 0.5],
            ['tecno/computacion/pc-all-in-one', ['AllInOne'],
             'Tecno > Computación > PC/All in one', 1],
            ['tecno/computacion/proyectores-y-monitores',
             ['Monitor', 'Projector'],
             'Tecno > Computación > Proyectores y monitores', 0.5],
            ['tecno/television', ['Television'],
             'Tecno > Televisión', 1],
            ['tecno/television/smart-tv', ['Television'],
             'Tecno > Televisión > Smart TV', 1],
            ['electro/refrigeracion', ['Refrigerator'],
             'Electro > Refrigeración', 1],
            ['electro/refrigeracion/side-by-side', ['Refrigerator'],
             'Electro > Refrigeración > Side by Side', 1],
            ['electro/refrigeracion/refrigeradores', ['Refrigerator'],
             'Electro > Refrigeración > Refrigeradores', 1],
            ['electro/refrigeracion/freezers-y-congeladores', ['Refrigerator'],
             'Electro > Refrigeración > Freezers y congeladores', 1],
            ['electro/refrigeracion/frigobar', ['Refrigerator'],
             'Electro > Refrigeración > Frigobar', 1],
            ['electro/refrigeracion/door-in-door', ['Refrigerator'],
             'Electro > Refrigeración > Door in Door', 1],
            ['electro/cocina/cocinas', ['Stove'],
             'Electro > Cocina > Cocinas', 1],
            ['electro/electrodomesticos/hornos-y-microondas', ['Oven'],
             'Electro > Electrodomésticos > Hornos y Microondas', 1],
            ['electro/cocina/lavavajillas', ['DishWasher'],
             'Electro > Cocina > Lavavajillas', 1],
            ['electro/aseo/aspiradoras-y-enceradoras', ['VacuumCleaner'],
             'Electro > Aseo > Aspiradoras y enceradoras', 1],
            ['electro/lavanderia', ['WashingMachine'],
             'Electro > Lavandería', 1],
            ['electro/lavanderia/lavadoras', ['WashingMachine'],
             'Electro > Lavandería > Lavadoras', 1],
            ['electro/lavanderia/secadoras', ['WashingMachine'],
             'Electro > Lavandería > Secadoras', 1],
            ['electro/lavanderia/lavadora-secadora', ['WashingMachine'],
             'Electro > Lavandería > Lavadora-secadora', 1],
            ['electro/lavanderia/doble-carga', ['WashingMachine'],
             'Electro > Lavandería > Doble carga', 1],
            ['tecno/telefonia/iphone', ['Cell'],
             'Tecno > Telefonía > iPhone', 1],
            ['tecno/telefonia/samsung', ['Cell'],
             'Tecno > Telefonía > Samsung', 1],
            ['tecno/telefonia/huawei', ['Cell'],
             'Tecno > Telefonía > Huawei', 1],
            ['tecno/telefonia/xiaomi', ['Cell'],
             'Tecno > Telefonía > Xiaomi', 1],
            ['tecno/telefonia/motorola', ['Cell'],
             'Tecno > Telefonía > Motorola', 1],
            ['tecno/telefonia/basicos', ['Cell'],
             'Tecno > Telefonía > Básicos', 1],
            ['tecno/fotografia-y-video/camaras-reflex', ['Camera'],
             'Tecno > Fotografía y Video > Camaras reflex', 1],
            ['tecno/fotografia-y-video/semi-profesionales', ['Camera'],
             'Tecno > Fotografía y Video > Semi profesionales', 1],
            ['tecno/audio-y-musica/equipos-de-musica', ['StereoSystem'],
             'Tecno > Audio y Música > Equipos de música', 1],
            ['tecno/audio-y-musica/parlantes-portables', ['StereoSystem'],
             'Tecno > Audio y Música > Parlantes Portables', 1],
            ['tecno/audio-y-musica/soundbar-y-home-theater', ['StereoSystem'],
             'Tecno > Audio y Música > Soundbar y Home theater', 1],
            ['tecno/television/bluray-dvd-y-tv-portatil',
             ['OpticalDiskPlayer'],
             'Tecno > Televisión > Bluray -DVD y TV Portátil', 1],
            ['tecno/playstation/consolas', ['VideoGameConsole'],
             'Tecno > PlayStation > Consolas', 1],
            ['tecno/nintendo/consolas', ['VideoGameConsole'],
             'Tecno > Nintendo > Consolas', 1],
            ['electro/climatizacion/aire-acondicionado',
             ['AirConditioner'],
             'Electro > Climatización > Ventiladores y aire acondicionado', 1],
            ['electro/climatizacion/purificadores-y-humificadores',
             ['AirConditioner'],
             'Electro > Climatización > Purificadores y humidificadores', 1],
            ['electro/climatizacion/estufas-y-calefactores',
             ['SpaceHeater'],
             'Electro > Climatización > Estufas y calefactores', 1],
            ['tecno/corner-smartwatch/garmin', ['Wearable'],
             'Tecno > Telefonía > Smartwatches y Wearables > Garmin', 1],
            ['tecno/corner-smartwatch/polar', ['Wearable'],
             'Tecno > Telefonía > Smartwatches y Wearables > Polar', 1],
            ['tecno/corner-smartwatch/apple-watch', ['Wearable'],
             'Tecno > Telefonía > Smartwatches y Wearables > Apple Watch', 1],
            ['tecno/corner-smartwatch/samsung', ['Wearable'],
             'Tecno > Telefonía > Smartwatches y Wearables > Samsung', 1],
            ['tecno/corner-smartwatch/huawei', ['Wearable'],
             'Tecno > Telefonía > Smartwatches y Wearables > Huawei', 1],
            ['tecno/especial-audifonos', ['Headphones'],
             'Tecno > Audio y Música > Audífonos', 1],
        ]

        if extra_args is None:
            extra_args = {}

        if 'PROXY_USERNAME' in extra_args:
            session = get_cf_session(extra_args)
        else:
            session = session_with_proxy(extra_args)

        fast_mode = extra_args.pop('fast_mode', False)

        url_base = 'https://simple.ripley.cl/{}?page={}'
        product_dict = {}

        for e in category_paths:
            category_path, local_categories, section_name, category_weight = e

            if category not in local_categories:
                continue

            page = 1
            position = 1

            while True:
                if page > 100:
                    raise Exception('Page overflow')

                category_url = url_base.format(category_path, page)
                print(category_url)
                response = session.get(category_url, allow_redirects=False)

                if response.status_code != 200 and page == 1:
                    raise Exception('Invalid section: ' + category_url)

                soup = BeautifulSoup(response.text, 'html.parser')
                products_data = soup.find('script',
                                          {'type': 'application/ld+json'})

                products_soup = soup.find('div', 'catalog-container')

                if not products_data or not products_soup:
                    if page == 1:
                        raise Exception('Empty path: {}'.format(url))
                    else:
                        break

                products_elements = products_soup.findAll(
                    'div', 'ProductItem__Row')

                if not products_elements:
                    products_elements = products_soup.findAll(
                        'a', 'catalog-product-item')

                products_json = json.loads(products_data.text)[
                    'itemListElement']

                assert (len(products_elements) == len(products_json))

                for product_json in products_json:
                    product_element = products_elements[
                        int(product_json['position']) - 1]
                    product_data = product_json['item']

                    brand = product_data.get('brand', '').upper()

                    # If the product is LG or Samsung and is sold directly by
                    # Ripley (not marketplace) obtain the full data
                    if brand in ['LG', 'SAMSUNG'] and 'MPM' not in \
                            product_data['sku'] and not fast_mode:

                        product = product_dict.get(product_data['sku'], None)
                        if not product:
                            url = cls._get_entry_url(product_element)
                            product = cls._assemble_full_product(
                                url, category, extra_args)
                    else:
                        product = cls._assemble_product(
                            product_data, product_element, category)

                    if product:
                        if product.sku in product_dict:
                            product_to_update = product_dict[product.sku]
                        else:
                            product_dict[product.sku] = product
                            product_to_update = product

                        product_to_update.positions[section_name] = position

                    position += 1

                page += 1

        products_list = [p for p in product_dict.values()]

        return products_list

    @classmethod
    def _get_entry_url(cls, element):
        # Element Data (Varies by page)
        if element.name == 'div':
            url_extension = element.find('a')['href']
        else:
            url_extension = element['href']

        url = 'https://simple.ripley.cl{}'.format(url_extension)
        return url

    @classmethod
    def _assemble_full_product(cls, url, category, extra_args, retries=5):
        if 'PROXY_USERNAME' not in extra_args:
            session = session_with_proxy(extra_args)
        else:
            session = get_cf_session(extra_args)

        print(url)
        page_source = session.get(url).text

        soup = BeautifulSoup(page_source, 'html.parser')

        if soup.find('div', 'error-page'):
            return []

        product_data = re.search(r'window.__PRELOADED_STATE__ = (.+);',
                                 page_source)
        if not product_data:
            if retries:
                return cls._assemble_full_product(url, category, extra_args, retries=retries-1)
            else:
                return []

        product_json = json.loads(product_data.groups()[0])
        specs_json = product_json['product']['product']

        sku = specs_json['partNumber']
        name = specs_json['name'].encode('ascii', 'ignore').decode('ascii')
        short_description = specs_json.get('shortDescription', '')

        # If it's a cell sold by Ripley directly (not Mercado Ripley) add the
        # "Prepago" information in its description
        if category in ['Cell', 'Unknown'] and 'MPM' not in sku:
            name += ' ({})'.format(short_description)

        if specs_json['isOutOfStock'] or specs_json['isUnavailable']:
            stock = 0
        else:
            stock = -1

        if 'offerPrice' in specs_json['prices']:
            normal_price = Decimal(specs_json['prices']['offerPrice'])
        elif 'listPrice' in specs_json['prices']:
            normal_price = Decimal(specs_json['prices']['listPrice'])
        else:
            return []

        offer_price = Decimal(specs_json['prices'].get('cardPrice',
                                                       normal_price))

        if offer_price > normal_price:
            offer_price = normal_price

        description = ''

        refurbished_notice = soup.find('div', 'emblemaReaccondicionados19')

        if refurbished_notice:
            description += html_to_markdown(str(refurbished_notice))

        if 'longDescription' in specs_json:
            description += html_to_markdown(specs_json['longDescription'])

        description += '\n\nAtributo | Valor\n-- | --\n'

        for attribute in specs_json['attributes']:
            if 'name' in attribute and 'value' in attribute:
                description += '{} | {}\n'.format(attribute['name'],
                                                  attribute['value'])

        description += '\n\n'
        condition = 'https://schema.org/NewCondition'

        if 'reacondicionado' in description.lower() or \
                'reacondicionado' in name.lower() or \
                'reacondicionado' in short_description.lower():
            condition = 'https://schema.org/RefurbishedCondition'

        if soup.find('img', {'src': '//home.ripley.cl/promo-badges/'
                                    'reacondicionado.png'}):
            condition = 'https://schema.org/RefurbishedCondition'

        picture_urls = []
        for path in specs_json['images']:
            picture_url = path

            if 'file://' in picture_url:
                continue

            if not picture_url.startswith('http'):
                picture_url = 'https:' + picture_url

            picture_urls.append(picture_url)

        if not picture_urls:
            picture_urls = None

        flixmedia_id = None
        video_urls = []

        flixmedia_urls = [
            '//media.flixfacts.com/js/loader.js',
            'https://media.flixfacts.com/js/loader.js'
        ]

        for flixmedia_url in flixmedia_urls:
            flixmedia_tag = soup.find(
                'script', {'src': flixmedia_url})
            if flixmedia_tag and flixmedia_tag.has_attr('data-flix-mpn'):
                flixmedia_id = flixmedia_tag['data-flix-mpn']
                video_urls = flixmedia_video_urls(flixmedia_id)
                break

        review_count = int(specs_json['powerReview']['fullReviews'])

        if review_count:
            review_avg_score = float(
                specs_json['powerReview']['averageRatingDecimal'])
        else:
            review_avg_score = None

        if 'shopName' in specs_json['marketplace']:
            seller = specs_json['marketplace']['shopName']
        elif specs_json['isMarketplaceProduct']:
            seller = 'Mercado R'
        else:
            seller = None

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
            description=description,
            picture_urls=picture_urls,
            condition=condition,
            flixmedia_id=flixmedia_id,
            review_count=review_count,
            review_avg_score=review_avg_score,
            video_urls=video_urls,
            seller=seller
        )

        return p

    @classmethod
    def _assemble_product(cls, data, element, category):
        # Element Data (Varies by page)
        if element.name == 'div':
            element_name = element.find(
                'a', 'ProductItem__Name').text.replace('  ', ' ').strip()
        else:
            element_name = element.find(
                'div', 'catalog-product-details__name') \
                .text.replace('  ', ' ').strip()

        # Common

        # This is removing extra white spaces in between words
        # If not done, sometimes it will not be equal to element name
        data_name = " ".join([a for a in data['name'].split(' ') if a != '']) \
            .strip()

        assert (element_name == data_name)

        # Remove weird characters, e.g.
        # https://simple.ripley.cl/tv-portatil-7-negro-mpm00003032468
        name = data_name.encode('ascii', 'ignore').decode('ascii')
        sku = data['sku']
        url = cls._get_entry_url(element)

        if 'image' in data:
            picture_urls = ['https:{}'.format(data['image'])]
        else:
            picture_urls = None

        if data['offers']['price'] == 'undefined':
            return None

        offer_price = Decimal(data['offers']['price'])
        normal_price_container = element.find(
            'li', 'catalog-prices__offer-price')

        if normal_price_container:
            normal_price = Decimal(
                element.find('li', 'catalog-prices__offer-price')
                    .text.replace('$', '').replace('.', ''))
        else:
            normal_price = offer_price

        if normal_price < offer_price:
            offer_price = normal_price

        stock = 0
        if data['offers']['availability'] == 'http://schema.org/InStock':
            stock = -1

        if '-mpm' in url:
            seller = 'External seller'
        else:
            seller = None

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
            picture_urls=picture_urls,
            seller=seller
        )

        return p

    @classmethod
    def discover_urls_for_keyword(cls, keyword, threshold, extra_args=None):
        session = get_cf_session(extra_args)
        product_urls = []

        page = 1

        while True:
            if page > 40:
                raise Exception('Page overflow')

            search_url = 'https://simple.ripley.cl/search/{}?page={}'\
                .format(keyword, page)
            response = session.get(search_url, allow_redirects=False)

            if response.status_code != 200:
                raise Exception('Invalid search: ' + keyword)

            soup = BeautifulSoup(response.text, 'html.parser')

            products_container = soup.find('div', 'catalog-container')

            if not products_container:
                break

            products = products_container.findAll('a', 'catalog-product-item')

            for product in products:
                product_url = 'https://simple.ripley.cl' + product['href']
                product_urls.append(product_url)
                if len(product_urls) == threshold:
                    return product_urls

            page += 1

        return product_urls

    @classmethod
    def preflight(cls, extra_args=None):
        # Obtain Cloudflare bypass cookie
        if extra_args is None:
            raise Exception("extra_args should contain the parameters to "
                            "obtain the Cloudflare session cookie or the "
                            "'debug' flag if testing locally")
        if 'PROXY_USERNAME' not in extra_args:
            return {}

        proxy = 'http://{}:{}@{}:{}'.format(
            extra_args['PROXY_USERNAME'],
            extra_args['PROXY_PASSWORD'],
            extra_args['PROXY_IP'],
            extra_args['PROXY_PORT'],
        )
        with HeadlessChrome(images_enabled=True, proxy=proxy,
                            headless=True) as driver:
            driver.get('https://simple.ripley.cl')
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            hcaptcha_script_tag = soup.find('script', {'data-type': 'normal'})
            website_key = hcaptcha_script_tag['data-sitekey']

            # Anti captcha request
            request_body = {
                "clientKey": extra_args['KEY'],
                "task":
                    {
                        "type": "HCaptchaTask",
                        "websiteURL": "https://simple.ripley.cl/",
                        "websiteKey": website_key,
                        "proxyType": "http",
                        "proxyAddress": extra_args['PROXY_IP'],
                        "proxyPort": extra_args['PROXY_PORT'],
                        "proxyLogin": extra_args['PROXY_USERNAME'],
                        "proxyPassword": extra_args['PROXY_PASSWORD'],
                        "userAgent": CF_REQUEST_HEADERS['User-Agent']
                    }
            }
            print('Sending anti-captcha task')
            print(json.dumps(request_body, indent=2))
            anticaptcha_session = requests.Session()
            anticaptcha_session.headers['Content-Type'] = 'application/json'
            response = json.loads(anticaptcha_session.post(
                'http://api.anti-captcha.com/createTask',
                json=request_body).text)

            print('Anti-captcha task request response')
            print(json.dumps(response, indent=2))

            assert response['errorId'] == 0

            task_id = response['taskId']
            print('TaskId', task_id)

            # Wait until the task is ready...
            get_task_result_params = {
                "clientKey": extra_args['KEY'],
                "taskId": task_id
            }
            print(
                'Querying for anti-captcha response (wait 10 secs per retry)')
            print(json.dumps(get_task_result_params, indent=4))
            retries = 1
            hcaptcha_response = None
            while not hcaptcha_response:
                if retries > 60:
                    raise Exception('Failed to get a token in time')
                print('Retry #{}'.format(retries))
                time.sleep(10)
                res = json.loads(anticaptcha_session.post(
                    'https://api.anti-captcha.com/getTaskResult',
                    json=get_task_result_params).text)

                assert res['errorId'] == 0, res
                assert res['status'] in ['processing', 'ready'], res
                if res['status'] == 'ready':
                    print('Solution found')
                    hcaptcha_response = res['solution']['gRecaptchaResponse']
                    break
                retries += 1

            print(hcaptcha_response)
            for field in ['g-recaptcha-response', 'h-captcha-response']:
                driver.execute_script("document.querySelector('[name=\""
                                      "{0}\"]').remove(); "
                                      "var foo = document.createElement('"
                                      "input'); foo.setAttribute('name', "
                                      "'{0}'); "
                                      "foo.setAttribute('value','{1}'); "
                                      "document.getElementsByTagName('form')"
                                      "[0].appendChild(foo);".format(
                    field, hcaptcha_response))
            driver.execute_script("document.getElementsByTagName('form')"
                                  "[0].submit()")

            d = {
                "proxy": proxy,
                "cf_clearance": driver.get_cookie('cf_clearance')['value'],
                "__cfduid": driver.get_cookie('__cfduid')['value']
            }
            return d

    @classmethod
    def banners(cls, extra_args=None):
        extra_args = cls._extra_args_with_preflight(extra_args)
        base_url = 'https://simple.ripley.cl/{}'

        sections_data = [
            [bs.HOME, 'Home', bs.SUBSECTION_TYPE_HOME, ''],
            [bs.ELECTRO_RIPLEY, 'Electro Ripley',
             bs.SUBSECTION_TYPE_CATEGORY_PAGE, 'electro/'],
            [bs.TECNO_RIPLEY, 'Tecno Ripley',
             bs.SUBSECTION_TYPE_CATEGORY_PAGE, 'tecno/'],
            [bs.REFRIGERATION, 'Refrigeración',
             bs.SUBSECTION_TYPE_MOSAIC, 'electro/refrigeracion/'],
            [bs.REFRIGERATION, 'Refrigeradores', bs.SUBSECTION_TYPE_MOSAIC,
             'electro/refrigeracion/refrigeradores/'],
            [bs.WASHING_MACHINES, 'Lavandería',
             bs.SUBSECTION_TYPE_MOSAIC, 'electro/lavanderia'],
            [bs.WASHING_MACHINES, 'Lavadoras',
             bs.SUBSECTION_TYPE_MOSAIC, 'electro/lavanderia/lavadoras'],
            [bs.WASHING_MACHINES, 'Lavadora-secadora',
             bs.SUBSECTION_TYPE_MOSAIC,
             'electro/lavanderia/lavadora-secadora'],
            [bs.WASHING_MACHINES, 'Doble Carga',
             bs.SUBSECTION_TYPE_MOSAIC, 'electro/lavanderia/doble-carga'],
            [bs.TELEVISIONS, 'Televisión',
             bs.SUBSECTION_TYPE_MOSAIC, 'tecno/television'],
            [bs.TELEVISIONS, 'Smart TV',
             bs.SUBSECTION_TYPE_MOSAIC, 'tecno/television/smart-tv'],
            [bs.TELEVISIONS, '4K – UHD - NanoCell',
             bs.SUBSECTION_TYPE_MOSAIC, 'tecno/television/4k-uhd-nanocell'],
            [bs.TELEVISIONS, 'Premium - OLED - QLED - 8K',
             bs.SUBSECTION_TYPE_MOSAIC,
             'tecno/television/premium-oled-qled-8k'],
            [bs.TELEVISIONS, 'HD - Full HD',
             bs.SUBSECTION_TYPE_MOSAIC, 'tecno/television/hd-full-hd'],
            [bs.AUDIO, 'Audio y Música',
             bs.SUBSECTION_TYPE_MOSAIC, 'tecno/audio-y-musica'],
            # [AUDIO, 'Parlantes y Subwoofer', SUBSECTION_TYPE_MOSAIC,
            #  'tecno/audio-y-musica/parlantes-y-subwoofer'],
            # [AUDIO, 'Microcomponentes',
            #  SUBSECTION_TYPE_MOSAIC,
            #  'tecno/audio-y-musica/microcomponentes'],
            [bs.AUDIO, 'Soundbar y Home theater',
             bs.SUBSECTION_TYPE_MOSAIC,
             'tecno/audio-y-musica/soundbard-y-home-theater'],
            [bs.AUDIO, 'Parlantes Portables',
             bs.SUBSECTION_TYPE_MOSAIC,
             'tecno/audio-y-musica/parlantes-portables'],
            [bs.CELLS, 'Telefonía',
             bs.SUBSECTION_TYPE_MOSAIC, 'tecno/telefonia'],
            [bs.CELLS, 'Android',
             bs.SUBSECTION_TYPE_MOSAIC, 'tecno/telefonia/android'],
            [bs.CELLS, 'iPhone',
             bs.SUBSECTION_TYPE_MOSAIC, 'tecno/telefonia/iphone']
        ]

        if 'PROXY_USERNAME' not in extra_args:
            session = session_with_proxy(extra_args)
        else:
            session = get_cf_session(extra_args)
        banners = []

        for section, subsection, subsection_type, url_suffix in sections_data:
            url = base_url.format(url_suffix)
            response = session.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            if subsection_type == bs.SUBSECTION_TYPE_HOME:
                banners = banners + cls.get_owl_banners(
                    url, section, subsection, subsection_type, extra_args)

            elif subsection_type == bs.SUBSECTION_TYPE_CATEGORY_PAGE:
                if soup.find('div', 'owl-carousel'):
                    banners = banners + cls.get_owl_banners(
                        url, section, subsection, subsection_type, extra_args)
                else:
                    images = soup.findAll('a', 'item')

                    if not images:
                        print('No banners')

                    for index, image in enumerate(images):
                        picture = image.find('span', 'bg-item')
                        picture_url = re.search(
                            r'url\((.*?)\)', picture['style']).group(1)

                        destination_urls = [image['href']]

                        banners.append({
                            'url': url,
                            'picture_url': picture_url,
                            'destination_urls': destination_urls,
                            'key': picture_url,
                            'position': index + 1,
                            'section': section,
                            'subsection': subsection,
                            'type': subsection_type
                        })
            elif subsection_type == bs.SUBSECTION_TYPE_MOSAIC:
                picture_container = soup.find('section', 'catalog-top-banner')

                if not picture_container:
                    print('No banners')
                    continue

                picture_url = picture_container.find('img')

                if not picture_url:
                    continue

                destination = soup.find(
                    'section', 'catalog-top-banner').find('a')
                destination_urls = []

                if destination:
                    destination_urls = [destination['href']]

                banners.append({
                    'url': url,
                    'picture_url': picture_url.get('src') or
                    picture_url.get('data-src'),
                    'destination_urls': destination_urls,
                    'key': picture_url.get('src') or
                    picture_url.get('data-src'),
                    'position': 1,
                    'section': section,
                    'subsection': subsection,
                    'type': subsection_type
                })
            else:
                raise Exception('Invalid subsection type')

        return banners

    @classmethod
    def get_owl_banners(cls, url, section, subsection, subsection_type, extra_args):
        with HeadlessChrome(images_enabled=True, timeout=60,
                            proxy=extra_args['proxy']) as driver:
            print(url)
            banners = []
            driver.set_window_size(1920, 1080)
            driver.set_page_load_timeout(240)
            # Open the page first so that the CF cookies can be loaded in
            # this domain
            driver.get(url)
            # Then set the sesion cookies
            load_driver_cf_cookies(driver, extra_args, '.ripley.cl')
            # Then re-open the page
            driver.get(url)
            driver.execute_script("scrollTo(0, 0);")

            pictures = []

            banner_container = driver \
                .find_element_by_class_name('owl-carousel')

            controls = banner_container \
                .find_elements_by_class_name('owl-page')

            for control in controls:
                control.click()
                time.sleep(1)
                pictures.append(
                    banner_container.screenshot_as_base64)

            images = banner_container.find_elements_by_class_name('owl-item')

            assert len(images) == len(pictures)

            for index, image in enumerate(images):
                try:
                    image_style = image.find_element_by_tag_name(
                        'span').get_attribute('style')
                    key = re.search(r'url\((.*?)\)', image_style) \
                        .group(1)
                except NoSuchElementException:
                    key = image.find_element_by_tag_name(
                        'source').get_attribute('srcset')

                destinations = image.find_elements_by_tag_name('a')
                destination_urls = [a.get_attribute('href')
                                    for a in destinations]
                destination_urls = list(set(destination_urls))

                destination_urls = list(set(destination_urls))

                banners.append({
                    'url': url,
                    'picture': pictures[index],
                    'destination_urls': destination_urls,
                    'key': key,
                    'position': index + 1,
                    'section': section,
                    'subsection': subsection,
                    'type': subsection_type
                })

            return banners

