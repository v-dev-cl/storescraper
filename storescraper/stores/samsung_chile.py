from decimal import Decimal

from storescraper.categories import NOTEBOOK, CELL, TABLET, WEARABLE, \
    HEADPHONES, CELL_ACCESORY, TELEVISION, STEREO_SYSTEM, REFRIGERATOR, \
    WASHING_MACHINE, OVEN, DISH_WASHER, VACUUM_CLEANER, AIR_CONDITIONER, \
    MONITOR
from storescraper.product import Product
from storescraper.store import Store
from storescraper.utils import session_with_proxy, remove_words

import json


class SamsungChile(Store):
    @classmethod
    def categories(cls):
        cats = []

        for cat_id, path, cat in cls._category_info():
            if cat not in cats:
                cats.append(cat)

        return cats

    @classmethod
    def discover_urls_for_category(cls, category, extra_args=None):
        category_info = cls._category_info()

        urls = []

        for category_id, category_path, local_category \
                in category_info:
            if local_category != category:
                continue

            url = 'https://www.samsung.com/cl/{}'.format(category_path)
            urls.append(url)

        return urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        category_info = cls._category_info()
        session = session_with_proxy(extra_args)

        api_url = 'https://searchapi.samsung.com/v6/front/b2c/product/' \
                  'finder/newhybris?siteCode=cl&start=0&num=600' \
                  '&onlyFilterInfoYN=N'

        products = []

        for category_id, category_path, category_name in category_info:
            if category_name != category:
                continue

            category_endpoint = api_url + '&type=' + category_id

            json_data = json.loads(
                session.get(category_endpoint).text)['response']
            product_list = json_data['resultData']['productList']

            for product in product_list:
                for model in product['modelList']:
                    name = model['displayName']
                    variant_specs = []

                    for spec_entry in model['fmyChipList']:
                        variant_specs.append(spec_entry['fmyChipName'].strip())

                    if variant_specs:
                        name += ' ({})'.format(' / '.join(variant_specs))

                    if 'www.samsung.com' in model['pdpUrl']:
                        model_url = 'https:{}'.format(model['pdpUrl'])
                    else:
                        model_url = 'https://www.samsung.com{}'\
                            .format(model['pdpUrl'])
                    key = model['modelCode']
                    picture_urls = ['https:' + model['thumbUrl']]

                    for picture in model['galleryImage'] or []:
                        picture_urls.append('https:' + picture)

                    if model['priceDisplay']:
                        price = Decimal(remove_words(model['priceDisplay']))
                    else:
                        price = Decimal(0)

                    products.append(Product(
                        '{} ({})'.format(name, key),
                        cls.__name__,
                        category,
                        model_url,
                        url,
                        key,
                        -1,
                        price,
                        price,
                        'CLP',
                        sku=key,
                        picture_urls=picture_urls
                    ))

        return products

    @classmethod
    def _category_info(cls):
        return [
            ('01010000', 'smartphones/all-smartphones', CELL),
            ('01020000', 'tablets/all-tablets', TABLET),
            ('01030000', 'watches/all-watches', WEARABLE),
            ('01040000', 'audio-sound', HEADPHONES),
            ('01050000', 'mobile-accessories/all-mobile-accessories/',
             CELL_ACCESORY),
            ('04010000', 'tvs/all-tvs', TELEVISION),
            ('05010000', 'audio-devices/all-audio-devices', STEREO_SYSTEM),
            ('08030000', 'refrigerators/all-refrigerators', REFRIGERATOR),
            ('08010000', 'washers-and-dryers/all-washers-and-dryers',
             WASHING_MACHINE),
            ('08110000', 'microwave-ovens/all-microwave-ovens', OVEN),
            ('08090000', 'dishwashers/all-dishwashers', DISH_WASHER),
            ('08070000', 'vacuum-cleaners/all-vacuum-cleaners',
             VACUUM_CLEANER),
            ('08050000', 'air-conditioners/all-air-conditioners',
             AIR_CONDITIONER),
            ('08080000', 'cooking-appliances/all-cooking-appliances', OVEN),
            ('07010000', 'monitors/all-monitors', MONITOR),
            ('03010000', 'computers/all-computers', NOTEBOOK),
        ]
