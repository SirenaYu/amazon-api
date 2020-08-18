# amazon-api

This is a Flask API which can be used to generate Amazon gift card codes during a session of Qualtrics survey so that survey respondents can retrieve the code at end of survey. 

## Installation
TODO

## amazon_gift_card_api.py
This file is adapted from the Incentives API Samples page from Amazon, and it contains sample API calls to most Amazon Incentives API operations. 
You can download the original files [here](https://s3.amazonaws.com/AGCOD/tech_spec/AGCODServicePythonClient.zip).

Note that the original file from Amazon is coded in Python 2, and I have adpated the code so that it runs in Python 3.

## Setting up Flask

TODO

## Calling the Amazon API

After setting up the Flask API in ```api.py```, this is my actual call to communicate with the Amazon Incentives API. 

```python
# create amazon app
app = gc.AppConstants()
app.requestID = app.partnerID + id # id should be a unique string for each new API call
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
  return {"redeem_code": gc_code}

except urllib.request.HTTPError:
  # If the server returns an unsuccessful HTTP status code, return that there has been an error
  return {"redeem_code": "Unsuccessful Amazon Request: HTTPError"}

except urllib.request.URLError:
           
   # If any element of the signing, payload creation, or connection throws an exception then return that there is an error
   return {"redeem_code": "Unsuccessful Amazon Request: URLError"}
```

The first and most important method to introduce is the ```AppConstants``` method, located in ```amazon_gift_card_api.py```. Think of this as an initilizing method for you API call object.

```python
class AppConstants():
  """
  forbids to overwrite existing variables
  forbids to add new values if 'locked' variable exists
  """
```

AppConstants is where you should define a series of parameters for gift card creation. For example, if you would like to only generate giftcards with 1 dollar value, you can do that by setting ```amount``` to 1 and ```currencyCode``` to "USD". 
Below is a segment from ```AppConstants``` which sets up the parameters for an API call.

```python
    #User and instance parameters
    awsKeyID = "" # Your KeyID
    awsSecretKey = "" # Your Key
    dateTimeString = datetime.datetime.utcnow().strftime(DATE_FORMAT)  #"20140630T224526Z"

    #Service and target (API) parameters
    regionName = "us-east-1" #lowercase!  Ref http://docs.aws.amazon.com/general/latest/gr/rande.html
    serviceName = "AGCODService"

    #Payload parameters
    partnerID = "" # Your Partner ID
    requestID = "" # A unique request ID for every new gift card, can be defined at the time of the call
    cardNumber = ""
    amount = 1 
    currencyCode = "USD"
```

Note: In order to obtain your unique ```awsKeyID```, ```awsSecretKey``` and ```partnerID```, you need to first [register for an Amazon Incentives API account](https://s3-us-west-2.amazonaws.com/incentives-api-setup/index.html).


It is possible to leave certain parameter blank for now and define them at the time of your call. In fact, the parameter ```requestID``` should only be defined at the time of the call because each gift card request needs to have a unique requestID.
In my API call I had defined both the ```requestID``` and the ```amount``` at the time of my call, because I wanted to generate gift cards of various values.

```python
# create amazon app
app = gc.AppConstants()
app.requestID = app.partnerID + id # id should be a unique string for each new API call
app.amount = amount 
```
TODO
