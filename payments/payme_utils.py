import base64
from decimal import Decimal

import requests
from django.conf import settings

# checking if everything is ok
# assert settings.PAYME_SETTINGS.get('PAYME_ENV') != None
# assert settings.PAYME_SETTINGS.get('TOKEN') != None
# assert settings.PAYME_SETTINGS.get('ACCOUNTS') != None
# assert settings.PAYME_SETTINGS['ACCOUNTS'].get('KEY_1') != None
# end of checking

# initializing variables
PAYME_ENV = settings.PAYME_SETTINGS['PAYME_ENV']
TOKEN = settings.PAYME_SETTINGS['TOKEN']
AUTHORIZATION = {'X-Auth': settings.PAYME_SETTINGS['TOKEN']}
SECRET_KEY = settings.PAYME_SETTINGS['SECRET_KEY']
KEY_1 = settings.PAYME_SETTINGS['ACCOUNTS']['KEY_1']
KEY_2 = settings.PAYME_SETTINGS['ACCOUNTS'].get('KEY_2', 'order_type')
# end of initializing variables

AUTH_RECEIPT = {'X-Auth': f'{TOKEN}:{SECRET_KEY}'}


class Response:
    TEST_URL = 'https://checkout.test.payme.uz/api'
    PRODUCTION_URL = 'https://checkout.payme.uz/api'
    INITIALIZATION_URL = 'https://checkout.payme.uz/'
    TEST_INITIALIZATION_URL = 'https://checkout.test.payme.uz'
    URL = PRODUCTION_URL if PAYME_ENV else TEST_URL
    LINK = INITIALIZATION_URL if PAYME_ENV else TEST_INITIALIZATION_URL

    def create_transaction(self, token, order_id, amount, order_type=None) -> dict:
        """
        documentation : https://help.payme.uz/ru/metody-subscribe-api/receipts.create
        documentation : https://help.payme.uz/ru/metody-subscribe-api/receipts.pay
        >>> self.create_transaction(token='token', order_id=1, amount=5000.00)
        """
        data = dict(
            method='receipts.create',
            params=dict(
                amount=float(amount),
                account={
                    KEY_1: order_id,
                    KEY_2: order_type
                }
            )
        )
        response = requests.post(
            url=self.URL,
            json=data,
            headers=AUTH_RECEIPT
        )
        result = response.json()

        if 'error' in result:
            return result

        data = dict(
            method='receipts.pay',
            params=dict(
                id=result['result']['receipt']['_id'],
                token=token
            )
        )

        response = requests.post(
            url=self.URL, json=data, headers=AUTH_RECEIPT)
        print(response.json())
        return response.json()

    def create_initialization(self, amount: Decimal, order_id: str, return_url: str, order_type: str = None) -> str:
        """
        documentation : https://help.payme.uz/ru/initsializatsiya-platezhey/otpravka-cheka-po-metodu-get
        >>> self.create_initialization(amount=Decimal(5000.00), order_id='1', return_url='https://example.com/success/')
        """

        params = f"m={TOKEN};ac.{KEY_1}={order_id};a={amount};c={return_url}"
        if order_type:
            params += f"ac.{KEY_2}"
        encode_params = base64.b64encode(params.encode("utf-8"))
        encode_params = str(encode_params, 'utf-8')
        url = f"{self.LINK}/{encode_params}"
        return url

    def create_cards(self, card_number, expire, save=False) -> dict:
        '''
        documentation : https://help.payme.uz/ru/metody-subscribe-api/cards.create
        '''
        data = dict(
            method='cards.create',
            params=dict(
                card=dict(number=card_number, expire=expire),
                save=save
            )
        )

        response = requests.post(
            url=self.URL, json=data, headers=AUTHORIZATION)
        return response.json()

    def cards_get_verify_code(self, token) -> dict:
        '''
        documentation : https://help.payme.uz/ru/metody-subscribe-api/cards.get_verify_code
        '''
        data = dict(
            method='cards.get_verify_code',
            params=dict(token=token)
        )
        response = requests.post(
            url=self.URL, json=data, headers=AUTHORIZATION)
        result = response.json()
        result.update(token=token)

        return result

    def cards_verify(self, code, token):
        '''
        documentation : https://help.payme.uz/ru/metody-subscribe-api/cards.verify
        '''
        data = dict(
            method='cards.verify',
            params=dict(
                token=token,
                code=str(code)
            )
        )

        response = requests.post(
            url=self.URL, json=data, headers=AUTHORIZATION)
        print(response.json())
        return response.json()

    def delete_receipt(self, id):
        data = dict(
            method="receipts.cancel",
            params=dict(
                id=id
            )
        )

        response = requests.post(url=self.URL, json=data, headers=AUTH_RECEIPT)
        return response.json()


class Payme(Response):
    ORDER_FOUND = 200
    ORDER_NOT_FOND = -31050
    INVALID_AMOUNT = -31001
