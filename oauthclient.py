import urllib
import httplib2 as httplib
import re
import os
import os.path
import hmac
import hashlib
import json
import urlparse
import base64
import oauth2 as oauth
import common.rdf_tools.rdf_ontology
import common.rdf_tools.util
import flask
import logging
from filename import _CONFIG 
from generate_api import SmartResponse, augment
"""Code is reused and refined from the existing repo of SMART platform """
"""Here the filename would be the app file name where the _CONFIG information is written

Something like this would be the SMART Container OAuth Endpoint Configuration
_CONFIG = {
    "url": "http://sandbox-api.smartplatforms.org", #specific to the smart container
    "name": "SMART API",
    "app_id": "cse5600@cse.uconn.edu",
    "consumer_key": "cse5600@cse.uconn.edu",
    "consumer_secret": "secret"
}

"""

API_DICT = {}
"""The API_DICT dictionary is defined so that the api_base from the _CONFIG information can be stored"""

############################################################# HELPER FUNCTIONS #############################################
""" Returns the Oauth client, configured accordingly. """
def _init_oauthClient(rec_id=None):
    
    try:
        """ here the _CONFIG information is coded in the 'filename'"""
        client = OAuthClient(_CONFIG.get('app_id'),
                             _CONFIG.get('url'),
                             _CONFIG)
    except Exception as e:
        logging.critical('Could not init OAuthClient: %s' % e)
        flask.abort(500)
        return

    """initial client setup doesn't require rec_id"""
    rec_id = self.rec_id
    return client

 """ Tests access token by trying to fetch a records basic demographics """
def _testToken(client): """where client is the call in the app file calling the _init_oauthClient() function"""
   
    try:
        demo = get_demographics()
        status = demo.response.get('status')
        if '200' == status:
            return True
        else:
            logging.warning('get_demographics returned non-200 status: ' +
                            demo.response.get('status'))
            return False
    except Exception as e:
        return False

""" Requests a request token for a given rec_id """
def _requestRecordToken(rec_id, client):
    
    logging.debug("Req'd token for %s at %s", rec_id, _CONFIG.get('url'))
    try:
        req_token = _fetchToken()
        sessions = flask.session['sessions']
        sessions[rec_id] = {'req_token': req_token, 'acc_token': None}
        flask.session['sessions'] = sessions
        flask.session['auth_in_progress_rec_id'] = rec_id

    except Exception as e:
        logging.critical('Could not _fetchToken: %s' % e)
        flask.abort(500)

""" Exchanges verifier for an acc_token and stores it in the session """
def _exchangeToken(rec_id, req_token, verifier):
    
    client = _init_oauthClient(rec_id)
    update_token(req_token)

    try:
        acc_token = exchangeToken(verifier)
    except Exception as e:
        logging.critical("Token exchange failed: %s" % e)
        flask.abort(500)

    # success, store it!
    logging.debug("Exchanged req_token for acc_token: %s" % acc_token)
    sessions = flask.session['sessions']
    s = sessions.get(rec_id)
    s['acc_token'] = acc_token
    sessions[rec_id] = s
    flask.session['sessions'] = sessions


####################################### END HELPER FUNCTIONS ##################################################

class CError(Exception)
	pass
	#pass is a null operation -- when it is executed, nothing happens
class OAuthClient(oauth.Client) 
"""In the OAuth library, there is a class Client which is a worker to execute a request. The state_vars 
is a dictionary of parameters which we can supply to override the parameters obtained from the SMART 
context in the API calls executed by this client. The default parameters are defined in the SMART OWL 
file in the common repo of SMART Platforms"""

	def __init__(self, app_id, api_base, consumer_params, **state_vars):
		if consumer_params.get('consumer_key') is None or consumer_params.get('consumer_secret') is None:
			raise CError('Both consumer_secret and consumer_key are needed, only got :-to  %s' %consumer_params)

		""" The OAuth consumer is a third party service that wants to access protected resources 
        from an OAuth service provider on behalf of an end user. It is kind of the OAuth client.
		According to the documentation of the OAuth library, Usually a consumer must be registered 
        with the service provider by the developer of the consumer software. As part of that process, 
        the service provider gives the consumer a *key* and a *secret* with which the consumer 
        software can identify itself to the service. The consumer will include its key in each 
        request to identify itself, but will use its secret only when signing requests, to prove that
        the request is from that particular registered consumer. 
        Once registered, the consumer can then use its consumer credentials to ask the service provider 
        for a request token, kicking off the OAuth authorization process."""

    	consumer = oauth.Consumer(consumer_params['consumer_key'], consumer_params['consumer_secret'])
    	"""use the super keyword to inherit the properties of the consumer class."""
    	super(OAuthClient, self).__init__(consumer)

    	self.app_id = app_id
    	self.api_base = api_base
    	self._rec_id = None


        """If there is a value in a state_vars then just store the values """
    	for var_name, value in state_vars.iteritems():
    		setattr(self, var_name, value)

        """Check if there exists manifest file of the container when the api_base (from _CONFIG) is not in the API_DICT dictionary
         store the api_base in the API_DICT dictionary which matches the api_base in the manifest file (since the manifest file is in 
            JSON format)"""
    	if self.api_base not in API_DICT:
    		resp, content = self.get('manifest')
    		assert resp.status == 200, "Failed to get container manifest"
    		API_DICT[self.api_base] = json.loads(content)

        """Update the manifest file"""
    	self.container_manifest = API_DICT[self.api_base]

    """defines a record id. The property() function returns a special descriptor object. In general a descriptor object is an object 
    attribute with "binding behaviour", one whose attribute access has been overridden by methods in the descriptor protocol. The 
    property object acts as a descriptor object, so it has .__get__(), .__set__() and .__delete__() methods to hook into instance attribute 
    getting, setting and deleting"""
    @property 
    def rec_id(self):
    	return self._rec_id

    """The above is also same as 
    def rec_id(self): return self._rec_id
    rec_id = property(rec_id)
    """

    """set record id, first check if record id
    first check if that record id is already there, if not assign and set the token as None (that is set the resource token as none). A 
    detailed explaination would be The below setter is basically calling the property().setter method, which returns a copy of the same property, but with the setter
    function replaced with the decorated method. Extend the above property with a setter. Below would return a new property which inherits 
    everything from the old rec_id plus the given setter"""
    @rec_id.setter
    def rec_id(self, new_rec_id):
    	if self._rec_id != new_rec_id:
    		self._rec_id = new_rec_id
    		self.token = None


    
    """Returns the start URL where the user can login and select a record  . this URL can be retrieved from the Container Manifest"""
    @property
    def launch_url(self):
       
        url = self.container_manifest.get('launch_urls', {}).get('app_launch')
        if url is None:
            return None
        
        """You now must substitute {{app_id}} with your app id"""
        return re.sub(r"\{\{\s*app_id\s*\}\}", self.app_id, url)
    
    """ Makes sure there is the app-id and record-id in the request parameters for get, put, post and delete"""
    def _requestParams(self, params):
        if params is None:
            params = {}
        if params.get('app_id') is None:
            params['app_id'] = self.app_id
        if params.get('rec_id') is None:
            params['rec_id'] = self.rec_id
        return params

    """To get the absolute URI """
    def absolute_uri(self, uri):
        if uri[:4] == "http":
            return uri
        while '/' == uri[:1]:  # meaning if / is the first element in the uri list then make uri excluding the i elements that is discard the http tag so that it can be joined in next step
            uri = uri[i:]
        return '/'.join([self.api_base, uri]) # join api_base and uri seperated by /


    """ Update the resource token used by the client to sign requests. """
    def update_token(self, resource_token):
        
        if isinstance(resource_token, oauth.Token):
            self.token = resource_token
        else: #from the OAuth library use the Token function to store the new updated token
            token = oauth.Token(resource_token['oauth_token'], resource_token['oauth_token_secret'])
            self.token = token

    """ Get a request token from the server. """
    def _fetchToken(self, params={}):
        
        if self.token:
            raise CError("Client already has a resource token.")

        """make sure we have the record id"""
        if self.rec_id is not None:
            params['rec_id'] = self.rec_id

        # "oauth_callback" can only be "oob"
        params['oauth_callback'] = 'oob'

        resp, content = self.post(self.container_manifest['launch_urls']['request_token'], body=params)
        if resp['status'] != '200':
            raise CError("%s response fetching request token: %s" % (resp['status'], content))
        req_token = dict(urlparse.parse_qsl(content))
        self.update_token(req_token)
        return req_token
    """ Make an OAuth-signed GET request to the Server."""
    def get(self, uri, body={}, headers={}, **uri_params):
        
        """ Append the body data to the querystring"""
        if isinstance(body, dict) and len(body) > 0:
            body = urllib.urlencode(body)
            uri = "%s?%s" % (uri, body) if body else uri
        """check if app_id and rec_id are there"""
        uri_params = self._requestParams(uri_params)
        return self.request(self.absolute_uri(uri), uri_params, method="GET", body='', headers=headers)

    
    """ Make an OAuth-signed PUT request to the Server. """
    def put(self, uri, body='', headers={}, content_type=None, **uri_params):
        
        if content_type:
            headers['Content-Type'] = content_type
        
        """If our body is not plain, set the content type appropriately"""
        if isinstance(body, dict):
            body = urllib.urlencode(body)
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
        """check if app_id and rec_id are there"""
        uri_params = self._requestParams(uri_params)
        return self.request(self.absolute_uri(uri), uri_params, method="PUT", body=body, headers=headers)

    
    """ Make an OAuth-signed POST request to the Server. """
    def post(self, uri, body='', headers={}, content_type=None, **uri_params):
        
        if content_type:
            headers['Content-Type'] = content_type

        """If our body is not plain, set the content type appropriately"""
        if isinstance(body, dict):
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            body = urllib.urlencode(body)
        """check if app_id and rec_id are there"""
        uri_params = self._requestParams(uri_params)
        return self.request(self.absolute_uri(uri), uri_params, method="POST", body=body, headers=headers)

    """ Make an OAuth-signed DELETE request to the Server. """
    def delete(self, uri, headers={}, **uri_params):
        """check if app_id and rec_id are there"""
        uri_params = self._requestParams(uri_params)
        return self.request(self.absolute_uri(uri), uri_params, method="DELETE", headers=headers)

    
    """redirect to authorization URL (since 3way handshake so user is involved)"""
    @property
    def authorizationURL(self):
        if not self.token:
            raise CError("Client must have a token to get a redirect url")
        return self.container_manifest['launch_urls']['authorize_token'] + "?oauth_token=" + self.token.key


    """ Exchange the client's current token (should be a request token) for an access token. """
    def exchangeToken(self, verifier):
        #check if there is a token
        if not self.token:
            raise CError("Client must have a token to exchange.")
        #set the verifier
        self.token.set_verifier(verifier)
        resp, content = self.post(self.container_manifest['launch_urls']['exchangeToken'])
        if resp['status'] != '200':
            raise CError("%s response fetching access token: %s"%(resp['status'], content))
        access_token = dict(urlparse.parse_qsl(content)) 
        #parse_qsl is to parse a query string given as a string argument. Data is returned as a list of name, value pairs
        self.update_token(access_token)

        for var_name, value in access_token.iteritems():
            if not var_name.startswith("oauth_"):
                setattr(self, var_name, value)

        return access_token

if (not common.rdf_tools.rdf_ontology.parsed):
    assert False, "No ontology found"

augment(OAuthClient)

#####################################################################

