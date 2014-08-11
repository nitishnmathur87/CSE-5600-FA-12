CSE-5600
==============

File: oauth3Hand.py

Function Name: What it does

_CONFIG: details such as app-id, consumer-secret, consumer-key, api-base, app-name, etc are called in this dictionary 

OAuthClient: To start/init the OAuth Dance

absolute_uri: get the absolute URI

get, put, delete, post: Make an OAuth signed request to the server

_requestParams: This function is called to verify if the app-id and record-id are there in the request parameters for get, put, post, delete

update_token: Update the resource token used by the client to sign requests.

_fetchToken: get a request token from the server

authorizationURL: this will redirect the user to the authorization URL so that he/she can authorize an app for that patient

exchangeToken: exchange the clients current token (request token) for an access token

_initoauthClient: initialize the Oauth Dance. Here is where the above function (OAuthClient is called)

_testToken: test whether the access token is valid by testing basic demographics

_requestRecordToken: requests a request token for a given patient id

_exchangeToken: exchanges verifier for an access token and stores it in a session

Procedure for OAuth (3 way hand shake which includes the user authorization phase)

Below is the procedure to call the functions in the app as defined in the oauth3WayShake.py file in the app file.

Firstly, The SMART app should have a root file named as index

The index file should contain the _CONFIG dictionary that contains all the information such as 

_CONFIG = {

"url": "http://sandbox-api.smartplatforms.org", #specific to the smart container, or also known as the api_base

"name": "SMART API",

"app_id": "cse5600@cse.uconn.edu",

"consumer_key": "cse5600@cse.uconn.edu",

"consumer_secret": "secret"

}

Now, the first goal is to define the / URL for that app to respond in the SMART container. First check if there exists a patient id in the session. If not then call the initialization URL where a patient can be chosen by the user. This means that since there was no previously selected patient and since there is no id in the session it means that the app hasn't been used before or there were no patients selected before. For getting this selection page, the procedure behind this is that first it checks for consumer_key and consumer_secret in the _CONFIG that was declared in the file. If it is not found then an error is raised. The next test case is to see whether the api base is defined in the api dictionary. If not found then add and check if valid.

The launch url method is pretty simple. it returns the url appended with the app-id as defined in the _CONFIG which redirects to selecting a patient.

After checking if the patient exists or not in the session of the app, check if access token is there. Initialize the process by calling the _init_oauthclient function. If access token is missing for that particular session then start the OAuth dance by calling the _requestRecordToken function. Else if token is there then call the update_token function. Next step would be to use the _testToken function which would test if it is a valid token or no


*******************************
More detailed readme to follow
*******************************

