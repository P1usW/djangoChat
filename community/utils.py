from django.core.exceptions import ValidationError

import re


def uniq_name_url_validator(name_url: str):
    name_url = name_url.lower()
    name_url = ''.join(re.findall(r'\w', name_url, re.ASCII))
    if re.match(r'\d', name_url):
        raise ValidationError('Название не должно начнаться с цифры')
    return name_url
