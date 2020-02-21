from services.currency_converter import CurrencyConverter
import datetime, calendar

class GetListingCalendar:

    def __init__(self, listing):
        self.listing = listing

    def get_calendar(self, currency):
        monthly_calendar = []

        base_price = self.__get_base_price_in_currency(currency)
        for day in self.__generate_dates_for_current_month():
            price = base_price * self.__multiplier(self.listing, day)
            serialized_day = self.__serialize_day(str(day), price, currency)
            monthly_calendar.append(serialized_day)
        return monthly_calendar

    def __serialize_day(self, date, price, currency):
        return {
           'date': date,
           'price': price,
           'currency': currency or self.listing.currency
        }

    def __get_base_price_in_currency(self, currency):
        if currency == self.listing.currency or currency == None:
            return self.listing.base_price
        else:
            return CurrencyConverter.convert(self.listing.currency, currency, self.listing.base_price)

    def __generate_dates_for_current_month(self):
        today = datetime.date.today()
        num_days = calendar.monthrange(today.year, today.month)[1]
        return [datetime.date(today.year, today.month, day) for day in range(1, num_days+1)]

    def __multiplier(self, listing, date):
        if listing.market in ['paris', 'lisbon'] and date.weekday() in [5,6]:
            return 1.5
        if listing.market == 'san-francisco' and date.weekday() == 2:
            return 0.7
        if listing.market not in ['paris', 'lisbon', 'francisco'] and date.weekday() == 5:
            return 1.25
        return 1
    