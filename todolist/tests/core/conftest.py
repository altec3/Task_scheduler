import random
import string

import pytest
from django.contrib.auth.password_validation import (
    CommonPasswordValidator, MinimumLengthValidator, NumericPasswordValidator
)


@pytest.fixture(params=['min length validation', 'common password validation', 'numeric password validation'])
def invalid_password(request, faker) -> str:
    match request.param:
        case 'min length validation':
            return faker.password(length=random.randrange(4, MinimumLengthValidator().min_length))
        case 'common password validation':
            return CommonPasswordValidator().passwords.pop()
        case 'numeric password validation':
            return ''.join(faker.random.sample(string.digits, MinimumLengthValidator().min_length))
        case _:
            raise NotImplementedError
