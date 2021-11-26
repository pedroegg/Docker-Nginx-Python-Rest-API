import os
import requests
import logging

import lib.errors as errors

logger = logging.getLogger('API Imgur')

def UploadImage(base64_image: str, title: str, description: str) -> str:
    try:
        request = requests.post(
            url='https://api.imgur.com/3/upload',
            headers={'authorization': 'Client-ID {}'.format(os.getenv('IMGUR_CLIENT_ID'))},
            data={'title': title, 'description': description, 'type': 'base64', 'image': base64_image},
            files=[],
        )
    
    except Exception as e:
        raise
    
    if request.status_code == 200:
        response = request.json()
    
    else:
        logger.error('could not upload image to imgur. raw response: {}'.format(request.text))
        raise errors.FailedUploadFile()

    return response['data']['link']
