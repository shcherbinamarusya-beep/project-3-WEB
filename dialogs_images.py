import logging
import os
from typing import Optional

import requests

logger = logging.getLogger(__name__)

YANDEX_DIALOGS_API_URL = 'https://dialogs.yandex.net/api/v1'
_IMAGE_CACHE = {}


def upload_image_by_url(image_url: str) -> Optional[str]:
    skill_id = os.environ.get('YANDEX_SKILL_ID') or os.environ.get('ALICE_SKILL_ID')
    oauth_token = (
        os.environ.get('YANDEX_DIALOGS_OAUTH_TOKEN')
        or os.environ.get('YANDEX_OAUTH_TOKEN')
    )

    if not skill_id or not oauth_token:
        logger.warning(
            'YANDEX_SKILL_ID and YANDEX_DIALOGS_OAUTH_TOKEN are required '
            'to show dynamic map images in Alice.'
        )
        return None

    if image_url in _IMAGE_CACHE:
        return _IMAGE_CACHE[image_url]

    endpoint = f'{YANDEX_DIALOGS_API_URL}/skills/{skill_id}/images'
    try:
        response = requests.post(
            endpoint,
            headers={'Authorization': f'OAuth {oauth_token}'},
            json={'url': image_url},
            timeout=5,
        )
        response.raise_for_status()
        image_id = response.json().get('image', {}).get('id')
        if not image_id:
            logger.error('Dialogs API response does not contain image id: %s', response.text)
            return None

        _IMAGE_CACHE[image_url] = image_id
        return image_id
    except requests.RequestException as e:
        logger.error('Failed to upload image to Dialogs API: %s', e)
        return None
