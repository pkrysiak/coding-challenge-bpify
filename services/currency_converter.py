import requests

class ExternalServiceConnectionError(Exception):
    pass

class CurrencyConverter:
    APP_ID = 'c2f266f554274142a8028740221bf8c3'

    @classmethod
    def convert(cls, from_currency, to_currency, amount):
        response = requests.get('https://openexchangerates.org/api/latest.json', params={'app_id': cls.APP_ID})
        if response:
            rates = response.json().get('rates') 
            return (amount / rates.get(from_currency)) * rates.get(to_currency)
        else:
            raise ExternalServiceConnectionError('There was a problem with the currency exchange service')
