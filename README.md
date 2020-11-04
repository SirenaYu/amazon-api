# An API to Include Amazon Gift Code in Anonymous Qualtrics Surveys

This API is meant for social scientist who are conducting anonymous Qualtrics surveys and would like to include an Amazon gift card code at the end of the survey to reward respondents. It is first created for JPAL's COVID-19 USA Project.

I am new to open source software, so please excuse any README content that isn't consistent with the format of most open source programs. And if you know anyway that I can improve this, feel free to email me at sirenayu@mit.edu and let me know! Without further ado, here's a step by step instruction to help you set up the program.

## Step 1: Set up an Amazon Incentives API Account
To use the Amazon Incentives API, you must first register for an Amazon Incentives API account [here](https://s3-us-west-2.amazonaws.com/incentives-api-setup/index.html). Upon successful registration, the Amazon team should send you a link to a web portal where you can generate access key and tokens, which you will use to communicate with the Amazon API.


## Step 2: Customize amazon_gift_card_api.py
The next step is to set up the amazon_gift_card_api.py file.  

If you use a different language other than Python, feel free to download a sample Amazon Incentives API file from [here](https://s3.amazonaws.com/AGCOD/tech_spec/AGCODServicePythonClient.zip). I adapted my file from the Python file on Amazon’s website because the one on the website is coded in Python 2, and I personally use Python 3.

The file (in Python 3) contains:
An AppConstants class, in which you define important parameters
Numerous functions that are called in the API call, as well as functions that facilitate these functions (don’t change anything here unless there are bugs)
An example of an API call in the main function

There are a few things that you should set up with your own parameters in the AppConstants class, which I highlighted in the code fragment below:
```python
class AppConstants():
   """
   forbids to overwrite existing variables
   forbids to add new values if 'locked' variable exists
   """
   def __setattr__(self,name,value):
       if("locked" in self.__dict__):
           raise NameError("Class is locked can not add any attributes (%s)" % name)
       if name in self.__dict__:
           raise NameError("Can't rebind const(%s)" % name)
       self.__dict__[name]=value
  
  #Static headers used in the request
   ACCEPT_HEADER = "accept"
   CONTENT_HEADER = "content-type"
   HOST_HEADER = "host"
   XAMZDATE_HEADER = "x-amz-date"
   XAMZTARGET_HEADER = "x-amz-target"
   AUTHORIZATION_HEADER = "Authorization"

   #Static format parameters
   DATE_FORMAT = "%Y%m%dT%H%M%SZ"
   DATE_TIMEZONE = "UTC"
   UTF8_CHARSET = "UTF-8"

   #Signature calculation related parameters
   HMAC_SHA256_ALGORITHM = "HmacSHA256"
   HASH_SHA256_ALGORITHM = "SHA-256"
   AWS_SHA256_ALGORITHM = "AWS4-HMAC-SHA256"
   KEY_QUALIFIER = "AWS4"
   TERMINATION_STRING = "aws4_request"

   #User and instance parameters
   awsKeyID = "" ##### Your KeyID, obtained from Amazon portal ######
   awsSecretKey = "" ##### Your Secret Key, obtained from Amazon portal #####
   #dateTimeString = datetime.datetime.utcnow().strftime(DATE_FORMAT)  #"20140630T224526Z"

   #Service and target (API) parameters
   regionName = "us-east-1" #lowercase!  Ref http://docs.aws.amazon.com/general/latest/gr/rande.html
   serviceName = "AGCODService"

   #Payload parameters
   partnerID = "" ##### Your Partner ID #####
   requestID = "" 
   cardNumber = ""
   amount = "" ##### Your amount #####
   currencyCode = "USD"

   #Additional payload parameters for CancelGiftCard
   gcId = ""

   #Additional payload parameters for GetGiftCardActivityPage
   pageIndex = 0
   pageSize = 1
   utcStartDate = "" #"yyyy-MM-ddTHH:mm:ss eg. 2013-06-01T23:10:10"
   utcEndDate = "" #"yyyy-MM-ddTHH:mm:ss eg. 2013-06-01T23:15:10"
   showNoOps = True

   #Parameters that specify what format the payload should be in and what fields will
   #be in the payload, based on the selected operation.
   msgPayloadType = PayloadType.XML
   #msgPayloadType = PayloadType.JSON
   serviceOperation = AGCODServiceOperation.CreateGiftCard
   #serviceOperation = AGCODServiceOperation.CancelGiftCard
   #serviceOperation = AGCODServiceOperation.ActivateGiftCard
   #serviceOperation = AGCODServiceOperation.DeactivateGiftCard
   #serviceOperation = AGCODServiceOperation.ActivationStatusCheck
   #serviceOperation = AGCODServiceOperation.GetGiftCardActivityPage

   #Parameters used in the message header
   host = "agcod-v2-gamma.amazon.com" #Refer to the AGCOD tech spec for a list of end points based on region/environment
   protocol = "https"
   queryString = ""    # empty
   requestURI = "/" + AGCODServiceOperation.tostring(serviceOperation)
   serviceTarget = "com.amazonaws.agcod.AGCODService" + "." + AGCODServiceOperation.tostring(serviceOperation)
   hostName = protocol + "://" + host + requestURI

```
Note that if you set up the parameters when you create the AppConstants object, these parameters will be universal for all gift cards. If you would like to define some of the parameters at the time of your API call, you can do so. 

When programming, I ran into a time sensitive error. Turned out it was because I made a universal declaration of dateTimeString, which caused all gift card requests to have the same timestamp, despite them being called at different times. As a result, the declaration of dateTimeString should be made at the time of the API call (shown below).

Below is an example API call in the main function, which prints the gift card code and response from Amazon API. In this example, I customized the gift card amount and the request ID at the time of my API call, with the following syntax highlighted in yellow. Note that if you would like to define a parameter at the time of the API call, the parameter should not be defined in AppConstants.

```python

app = AppConstants()
app.amount = 10
app.requestID = app.partnerID + 'your_id' ##### The request ID should be unique for every new request #####
app.dateTimeString = datetime.datetime.utcnow().strftime(app.DATE_FORMAT)

#Initialize whole payload in the specified format for the given operation and set additional headers based on these settings
payload, contentType = setPayload(app)

#Create the URL connection to the host
hostConnection = app.hostName
conn = urllib.request.Request(url=hostConnection)

#Create Authentication signature and set the connection parameters
signRequestAWSv4(conn, payload, contentType, app)
try:
   #Write the output message to the connection, if it errors it will generate an IOException
   conn.data = payload
   print('OUTGOING DATA:')
   print(conn.data)

   req = urllib.request.urlopen(conn)
   response = req.read()
   req.close()

   print("\nRESPONSE:")
   print("Gift card code: ", response.decode('utf-8')[40:56])   # Extracts the gift card code from a response string
   print(response)

except urllib.request.HTTPError as e:
   # If the server returns an unsuccessful HTTP status code, such as 3XX, 4XX and 5XX, an HTTPError exception is thrown.
   response = e.read()
   print("\nERROR RESPONSE:")
   print(response)
   exit(1)

except urllib.request.URLError as e:
   #If any element of the signing, payload creation, or connection throws an exception then terminate since we cannot continue.
   print("URL ERROR")
   print(e)
   exit(1)

```
By the end of this step, you should be able to request some gift card codes from Amazon in the sandbox environment.


## Step 3: Set up the Flask App
This step allows you to create a Flask app, which would later help you host your request to the Amazon API on a server. This is done in api.py.

The first step is to set up Flask:
```python
from flask import Flask, request
from flask_restful import reqparse, Api, Resource
import amazon_gift_card_api as gc
import urllib.request

## set up flask

f_app = Flask(__name__)
api = Api(f_app)

parser = reqparse.RequestParser()
```
Then, create a resource called CreateGiftCard, and within it define a function called get. In get, parse obtain any parameters you will need, then perform the API call.

```python
## set up a token for security purposes
REALTOKEN = ""  # your token here

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
       app.dateTimeString = datetime.datetime.utcnow().strftime(app.DATE_FORMAT)
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
           return {"redeem_code": gc_code}

       except urllib.request.HTTPError:
          # for loop to prevent app from crashing if user enters a different amount with the same request ID
           for i in range(1, 31):
               app = gc.AppConstants()
               app.requestID = app.partnerID + id
               app.amount = i
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
               except urllib.request.URLError as e:
                   pass

           # If the server returns an unsuccessful HTTP status code, return that there has been an error

           return {"redeem_code": "Unsuccessful Amazon Request: HTTPError"}

       except urllib.request.URLError:
            # for loop to prevent app from crashing if user enters a different amount with the same request ID
           for i in range(1, 31):
               app = gc.AppConstants()
               app.requestID = app.partnerID + id
               app.amount = i
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
               except urllib.request.URLError as e:
                   pass

           # If any element of the signing, payload creation, or connection throws an exception then return that there is an error
           return {"redeem_code": "Unsuccessful Amazon Request: URLError"}
```
And at the end, set up the API resource routing for the CreateGiftCard resource.
```python
##
## Actually setup the Api resource routing here
##
api.add_resource(CreateGiftCard, '/creategiftcard')

```
By the end of this step, you should be able host this Flask App on your local host. Try calling 
curl http://127.0.0.1:5000/creategiftcard/id=myid&amount=10&token=mytoken in your terminal, and you should get a response like this:

{"redeem_code": "GUFN-TVYYVD-5ZA5"}


## Step 4: Host Flask App on Heroku
After getting your Flask API to run on your local host, the next step is to get it running on a Heroku server so that you can call the API from Qualtrics. 

Follow the next few steps to get the Flask app running on Heroku:
1) The first step is to create a Heroku account on www.heroku.com if you do not already have one. After creating an account, follow the first 5 sections of this [guide](https://devcenter.heroku.com/articles/getting-started-with-python) to set up Heroku on your machine. 
2) Follow this [guide](https://devcenter.heroku.com/articles/getting-started-with-python#push-local-changes) to push your code onto the Heroku server.

Your app should now be running on Heroku! If your app is named my-first-heroku-app, for example, try calling curl https://my-first-heroku-app.herokuapp.com/creategiftcard/id=myid&amount=10&token=mytoken in your terminal, and you should get a response like this:

{"redeem_code": "GUFN-TVYYVD-5ZA5"}

## Step 5: Call the Flask API from Qualtrics
You’re almost there! The last step is to call the Flask API from Qualtrics and get your Amazon code.

In your Qualtrics survey, open up your survey flow. Once you have done that, create a web service block and fill out the parameters like so:
```python
URL = https://my-first-heroku-app.herokuapp.com/creategiftcard/
Method = GET
id = myid ##### have a unique ID for each request! You can achieve this by setting this to a unique value such as survey ID#####
amount = youramount
token = yourtoken ##### this is any string that you can create for security reasons, remember to match it in your program #####
Set_Embedded_Data:
  amazon_gift_code = redeem_code
```
One important note is that Amazon has a limit on the length of it's request ID's (I believe it's 32 characters). Make sure your choice of ID (coupled with the PartnerID attached at the beginning) doesn't exceed that length!

Now when you view the survey, you will have an embedded data field called amazon_gift_code that contains the gift code requested live from Amazon. Enjoy!



