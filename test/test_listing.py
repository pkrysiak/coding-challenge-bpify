import unittest, os
from db.listings_db import ListingsDB
from models.listing import Listing, ValidationError, RecordNotFound
from services.get_listing_calendar import GetListingCalendar

class ListingsDBTest(unittest.TestCase):

    def setUp(self):
        ListingsDB.DB_FILE = 'listings-flat-test.db'

    def tearDown(self):
        os.remove(ListingsDB.DB_FILE)

    def testCreateListing(self):
        listing = Listing.new({
            "title": "Comfortable Room In Cozy Neighborhood",
            "base_price": 867,
            "currency": "USD",
            "market": "san-francisco",
            "host_name": "John Smith"
        })
        listing.save()
        assert listing.id != None
        assert listing.title == 'Comfortable Room In Cozy Neighborhood'
        assert listing.base_price == 867
        assert listing.currency == "USD"
        assert listing.market == 'san-francisco'
        assert listing.host_name == 'John Smith'
    
    def testGetListings(self):
        Listing.new({
            "title": "Comfortable Room In Cozy Neighborhood",
            "base_price": 867,
            "currency": "USD",
            "market": "san-francisco",
            "host_name": "John Smith"
        }).save()

        listings = Listing.all()

        assert len(listings) == 1
        assert listings[0].to_dict() == {
            "id" : listings[0].id,
            "title": "Comfortable Room In Cozy Neighborhood",
            "base_price": 867,
            "currency": "USD",
            "market": "san-francisco",
            "host_name": "John Smith"
        }

    def testUpdateListing(self):
        listing = Listing.new({
            "title": "Comfortable Room In Cozy Neighborhood",
            "base_price": 867,
            "currency": "USD",
            "market": "san-francisco",
            "host_name": "John Smith"
        }).save()

        assert listing.id != None
        

        listing.update({
            "title": "title",
            "base_price": 111,
            "currency": "EUR",
            "market": "lisbon",
            "host_name": "Will Smith"
        })

        updated = Listing.find_by_id(listing.id)
        
        assert listing.id == updated.id
        assert updated.title == 'title'
        assert updated.base_price == 111
        assert updated.currency == "EUR"
        assert updated.market == 'lisbon'
        assert updated.host_name == 'Will Smith'
    
    def testFailedUpdate(self):
        listing = Listing.new({
            "title": "Comfortable Room In Cozy Neighborhood",
            "base_price": 867,
            "currency": "USD",
            "market": "san-francisco",
            "host_name": "John Smith"
        }).save()

        with self.assertRaises(ValidationError):
            listing.update({
                "title": "title",
                "base_price": 111,
                "currency": "EUR",
                "market": "jerusalem",
                "host_name": "Will Smith"
            })

    def testFind(self):
        listing = Listing.new({
            "title": "Comfortable Room In Cozy Neighborhood",
            "base_price": 867,
            "currency": "USD",
            "market": "san-francisco",
            "host_name": "John Smith"
        }).save()

        assert Listing.find_by_id(listing.id).to_dict() == {
            "id" : listing.id,
            "title": "Comfortable Room In Cozy Neighborhood",
            "base_price": 867,
            "currency": "USD",
            "market": "san-francisco",
            "host_name": "John Smith"
        }

    def testNotFound(self):
        with self.assertRaises(RecordNotFound):
            Listing.find_by_id("wrong-uuid-offf-thee-object")

    def testFiltering(self):
        listing = Listing.new({
            "title": "Comfortable Room In Cozy Neighborhood",
            "base_price": 867,
            "currency": "USD",
            "market": "san-francisco",
            "host_name": "John Smith"
        }).save()

        assert Listing.filter({'market': 'lisbon'}) == []
        assert Listing.filter({'market': 'san-francisco'}) == [listing]
        assert Listing.filter({'currency': 'USD'}) == [listing]
        assert Listing.filter({'currency': 'USD', 'market': 'san-francisco'}) == [listing]
        assert Listing.filter({'currency': 'USD', 'market': 'lisbon'}) == []
        assert Listing.filter({'base_price.gt': 500}) == [listing]
        assert Listing.filter({'base_price.lt': 500}) == []
        assert Listing.filter({'base_price.gte': 867}) == [listing]
        assert Listing.filter({'base_price.lte': 867}) == [listing]
        assert Listing.filter({'base_price.gte': 868}) == []
        assert Listing.filter({'base_price.lte': 866}) == []
        assert Listing.filter({'base_price.e': 867}) == [listing]
        assert Listing.filter({'base_price.e': 865}) == []
        assert Listing.filter({'base_price.gt': 800, 'currency': 'USD', 'market': 'san-francisco'}) == [listing]

if __name__ == "__main__":
    unittest.main() 