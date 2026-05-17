import logging
from typing import Optional

logger = logging.getLogger(__name__)

YANDEX_STATIC_MAPS_URL = 'https://static-maps.yandex.ru/1.x/'
YANDEX_MAPS_URL = 'https://yandex.ru/maps/'


def get_static_map_url(
    latitude: float,
    longitude: float,
    city_name: str = '',
    zoom: int = 10,
    size: str = '450,450',
) -> Optional[str]:

    try:
        pt = f'{longitude},{latitude},pm2rdm'
        url = (
            f'{YANDEX_STATIC_MAPS_URL}'
            f'?ll={longitude},{latitude}'
            f'&z={zoom}'
            f'&size={size}'
            f'&pt={pt}'
            f'&l=map'
        )
        logger.info(f'Карта для «{city_name}»: {url}')
        return url
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
