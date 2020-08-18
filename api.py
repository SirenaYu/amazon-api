from flask import Flask, request
from flask_restful import reqparse, Api, Resource
import amazon_gift_card_api as gc
import urllib.request
import datetime

## set up flask

f_app = Flask(__name__)
api = Api(f_app)

parser = reqparse.RequestParser()

## set up token
REALTOKEN = '' # your token here

## create a CreateGiftCard resource
class CreateGiftCard(Resource):

    def get(self):
        # obtain information from query parameters
        id = str(request.args.get('id'))
        amount = str(request.args.get('amount'))
        token = str(request.args.get('token'))
        if token != REALTOKEN:
            return {"error_message": "token does not match"}

        # create amazon app
        app = gc.AppConstants()
        app.dateTimeString = datetime.datetime.utcnow().strftime(app.DATE_FORMAT)  #"20140630T224526Z"
        app.requestID = app.partnerID + id
        app.amount = amount
        payload, contentType = gc.setPayload(app)
        hostConnection = app.hostName
        conn = urllib.request.Request(url=hostConnection)
        gc.signRequestAWSv4(conn, payload, contentType, app)
        conn.data = payload
        try:
            req = urllib.request.urlopen(conn)
            response = req.read()
            req.close()
            gc_code = response.decode('utf-8')[40:56]
            print("\nRESPONSE:")
            print("Gift Card Code", response.decode('utf-8')[40:56])
            print(response)
            return {"redeem_code": gc_code}

        except urllib.request.HTTPError as e:
            # If the server returns an unsuccessful HTTP status code, return that there has been an error
            response = e.read()
            print("\nERROR RESPONSE:")
            print(response)
            print("Error: ", e)
            return {"redeem_code": "Unsuccessful Amazon Request: HTTPError"}

        except urllib.request.URLError as e:
            # If any element of the signing, payload creation, or connection throws an exception then return that there is an error
            response = e.read()
            print("\nERROR RESPONSE:")
            print(response)
            return {"redeem_code": "Unsuccessful Amazon Request: URLError"}


##
## Actually setup the Api resource routing here
##
api.add_resource(CreateGiftCard, '/creategiftcard')


if __name__ == '__main__':
    f_app.run(debug=True)