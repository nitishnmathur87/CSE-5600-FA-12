CSE-5600-FA-12
==============

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


*******************************
More detailed readme to follow
*******************************

