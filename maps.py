import logging
import os
from typing import Optional
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

YANDEX_STATIC_MAPS_URL = 'https://enterprise.static-maps.yandex.ru/1.x/'
YANDEX_MAPS_URL = 'https://yandex.ru/maps/'


def get_static_map_url(
    latitude: float,
    longitude: float,
    city_name: str = '',
    zoom: int = 10,
    size: str = '450,450',
) -> Optional[str]:

    try:
        api_key = (
            os.environ.get('YANDEX_STATIC_MAPS_API_KEY')
            or os.environ.get('YANDEX_MAPS_API_KEY')
        )
        if not api_key:
            logger.warning(
                'YANDEX_STATIC_MAPS_API_KEY or YANDEX_MAPS_API_KEY is required '
                'to request Static API map images.'
            )
            return None

        params = {
            'key': api_key,
            'll': f'{longitude},{latitude}',
            'z': zoom,
            'size': size,
            'pt': f'{longitude},{latitude},pm2rdm',
            'l': 'map',
        }
        logger.info('Static API map URL created for «%s».', city_name)
        return f'{YANDEX_STATIC_MAPS_URL}?{urlencode(params)}'
    except Exception as e:
        logger.error(f'Ошибка при формировании URL карты: {e}')
        return None


def get_yandex_maps_url(
    latitude: float,
    longitude: float,
    city_name: str = '',
    zoom: int = 10,
) -> Optional[str]:
    try:
        url = (
            f'{YANDEX_MAPS_URL}'
            f'?ll={longitude}%2C{latitude}'
            f'&z={zoom}'
            f'&pt={longitude}%2C{latitude}%2Cpm2rdm'
        )
        logger.info(f'Место на карте для «{city_name}»: {url}')
        return url
    except Exception as e:
        logger.error(f'Ошибка при формировании URL Яндекс.Карт: {e}')
        return None
