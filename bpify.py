from flask import Flask, escape, request, jsonify
from markets import MARKETS
from models.listing import Listing, ValidationError, RecordNotFound
from services.currency_converter import CurrencyConverter
from services.get_listing_calendar import GetListingCalendar

app = Flask(__name__)

@app.route("/test_flask", methods=["GET", "POST"])
def test_flask():
    """Example to show how to use Flask and extract information from the incoming request.
    It is not intended to be the only way to do things with Flask, rather more a way to help you not spend too much time on Flask.
    
    Ref: http://flask.palletsprojects.com/en/1.1.x/

    Try to make those requests:
    curl "http://localhost:5000/test_flask?first=beyond&last=pricing"
    curl "http://localhost:5000/test_flask" -H "Content-Type: application/json" -X POST -d '{"first":"beyond", "last":"pricing"}' 
    
    """
    # This contains the method used to access the route, such as GET or POST, etc
    method = request.method

    # Query parameters
    # It is a dict like object
    # Ref: https://flask.palletsprojects.com/en/1.1.x/api/?highlight=args#flask.Request.args
    query_params = request.args
    query_params_serialized = ", ".join(f"{k}: {v}" for k, v in query_params.items())

    # Get the data as JSON directly
    # If the mimetype does not indicate JSON (application/json, see is_json), this returns None.
    # Ref: https://flask.palletsprojects.com/en/1.1.x/api/?highlight=get_json#flask.Request.get_json
    data_json = request.get_json()

    return jsonify(
        {
            "method": method,
            "query_params": query_params_serialized,
            "data_json": data_json,
        }
    )


@app.route("/markets")
def markets():
    return jsonify([market.to_dict() for market in MARKETS.get_all()])

@app.route("/listings", methods=["GET", "POST"])
def listings():
    if request.method == "POST": 
        data = request.get_json()
        listing = Listing.new(data)
        try:
            return jsonify(listing.save())
        except ValidationError as e:
            return jsonify({'errors': e.args[0]}), 422
    elif request.method == 'GET':
        args = dict(request.args)
        return jsonify(Listing.filter(args))

@app.route("/listings/<id>", methods=["GET", "PUT", "DELETE"])
def listing(id):
    try:
        if request.method == "GET":
            return jsonify(Listing.find_by_id(id))
        elif request.method == "PUT":
            data = request.get_json()
            current_listing = Listing.find_by_id(id)
            current_listing.update(data)
            return jsonify(current_listing)
        elif request.method == "DELETE":
            return jsonify(Listing.find_by_id(id).delete())
    except RecordNotFound as e:
        return jsonify({'error': e.args[0]}), 404
    except ValidationError as e:
        return jsonify({'errors': [e.args[0]]}), 422

@app.route("/listings/<id>/calendar", methods=["GET"])
def listing_calendar(id):
    args = dict(request.args)
    currency = args.get('currency')
    try:
        current_listing = Listing.find_by_id(id)
        calendar = GetListingCalendar(current_listing).get_calendar(currency)
        return jsonify(calendar)
    except RecordNotFound as e:
        return jsonify({'error': e.args[0]}), 404



