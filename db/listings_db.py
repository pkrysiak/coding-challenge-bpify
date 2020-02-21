import shelve, uuid

class ListingsDB:
    DB_FILE = 'listings-flat.db'

    def __init__(self, test=False):
        self.test = test
        db = self.__establish_connection()
        if db.get('listings') == None:
            db['listings'] = []
        db.close()
    
    def __establish_connection(self):
        return shelve.open(self.DB_FILE, writeback=True)

    def find_by_id(self, listing_id):
        db = self.__establish_connection()
        listing = next((listing for listing in db['listings'] if listing['id'] == listing_id), None)
        db.close()
        return listing

    def find_all(self):
        db = self.__establish_connection()
        listings = db['listings']
        db.close()
        return listings

    def create(self, listing_model):
        listing_model.id = str(uuid.uuid1())
        db = self.__establish_connection()
        db['listings'].append(listing_model.to_dict())
        db.close()
        return listing_model

    def update(self, listing_model):
        db = self.__establish_connection()            
        for index, listing in enumerate(db['listings']):
            if listing['id'] == listing_model.id:
                db['listings'][index] = listing_model.to_dict()
                db.close()
                return listing_model
    
    def delete(self, listing_model):
        db = self.__establish_connection()            
        for index, listing in enumerate(db['listings']):
            if listing['id'] == listing_model.id:
                del db['listings'][index]
                db.close()
                return listing_model