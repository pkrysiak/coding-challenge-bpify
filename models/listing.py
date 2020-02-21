import re
from dataclasses import dataclass, asdict, field
from currencies import Currency
from db.listings_db import ListingsDB
from markets import MARKETS
from currencies import CURRENCIES

class RecordNotFound(Exception):
    pass

class ValidationError(ValueError):
    pass

@dataclass
class Listing:
    title: str
    base_price: int
    currency: Currency
    market: str
    host_name: str = field(default='')
    id: str = field(default=None)

    def __post_init__(self):
        self.__validationErrors = []

    ### Validations

    def is_valid(self):
        return self.__validate_required_fields() and self.__validate_market() and self.__validate_currency()

    def __validate_required_fields(self):
        all_required_fields_present = None not in [self.title, self.base_price, self.currency, self.market]
        if not all_required_fields_present:
            self.__validationErrors.append('title, base_price, currency, market are required fields')
            return False
        return True
    
    def __validate_market(self):
        try:
            MARKETS.get_by_code(self.market)
            return True
        except Exception as e:
            self.__validationErrors.append(e.args[0])
            return False

    def __validate_currency(self):
        try:
            CURRENCIES.get_by_code(self.currency.upper())
            return True
        except Exception as e:
            self.__validationErrors.append(e.args[0])
            return False

    ### Instance methods

    def to_dict(self):
        return asdict(self)
    
    def save(self):
        if self.is_valid():
            db = ListingsDB()
            if self.__is_persisted():
                return db.update(self)
            else:
                return db.create(self)
        else:
            raise ValidationError(self.__validationErrors)

    def update(self, attrs):
        self.title = attrs.get('title')
        self.base_price = attrs.get('base_price')
        self.currency = attrs.get('currency')
        self.market = attrs.get('market')
        self.host_name = attrs.get('host_name')
        self.save()

    def delete(self):
        db = ListingsDB()
        return db.delete(self)

    def __is_persisted(self):
        return self.id != None

    ### Class methods

    @classmethod
    def filter(cls, attrs):
        filtered = []
        for listing in cls.all():
            if cls.__listings_comparator(listing, attrs):
                filtered.append(listing)
        return filtered

    @classmethod
    def all(cls):
        db = ListingsDB()
        return [cls.new(listing) for listing in db.find_all()]

    @classmethod
    def find_by_id(cls, id):
        db = ListingsDB()
        listing = db.find_by_id(id)
        if listing:
            return cls.new(listing)
        else:
            raise RecordNotFound('Record not found')

    @classmethod
    def new(cls, attrs):
        return cls(
            id=attrs.get('id'),
            title=attrs.get('title'), 
            base_price=attrs.get('base_price'), 
            currency=attrs.get('currency'), 
            market=attrs.get('market'), 
            host_name=attrs.get('host_name')
        )

    @classmethod
    def __listings_comparator(cls, listing, filter_attrs):

        def base_price_comparator(listing, filter_attrs):
            comparators_map = {
                'e': '==',
                'gt': '>',
                'gte': '>=',
                'lt': '<',
                'lte': '<='  
            }
            for filter_argument, filter_value in filter_attrs.items():
                regex = re.compile(r'base_price\.(?P<comparator>e|gte|gt|lte|lt)')
                match = regex.match(filter_argument)
                if match:
                    comparator = comparators_map.get(match.group('comparator'))
                    return eval('{listing_base_price} {comparator} {filtered_price}'.format(listing_base_price=listing.base_price, comparator=comparator, filtered_price=filter_value))

        market = filter_attrs.get('market')
        currency = filter_attrs.get('currency')

        if market and listing.market not in market.split(','):
            return False
        if currency and listing.currency != currency:
            return False
        if base_price_comparator(listing, filter_attrs) == False:
            return False
        return True
