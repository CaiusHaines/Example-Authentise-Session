import argparse

import requests
import json

from requests.auth import HTTPBasicAuth




class AuthentiseSession:
    # '''
    # Example class to create an API sesssion to a nautilus server for admin use
    # '''

    def __init__(self, host, verify_ssl=True):
        """
        Create an Authentise Session using a persistant API key 
        :param verify_ssl : True/False veirfy SSL Keys to CA's
        :param: host: the site to connect to. For example 'authentise.com' or stage-auth.com' for most customer testing
        """
        self.host = host
        self.session_cookie = None #
        self.api_auth = None
        self.verify_ssl = verify_ssl

    @staticmethod
    def _parse_session_cookie(cookie):
        parts = cookie.split(";")
        return parts[0]


    def _init_session(self, username, password):
        """
        Creates a connection to the system via username/password to get a cookie
        """
        data = {"username": username, "password": password}

        headers = {"content-type": "application/json"}

        response = requests.post(
            "https://users.{}/sessions/".format(self.host), json=data, headers=headers)
        response.raise_for_status()

        cookie_header = response.headers.get("Set-Cookie", None)
        self.session_cookie = self._parse_session_cookie(cookie_header)

    def _get_api_key(self):
        """
        Exaple of fetching the long-term API Key from our api_tokens service.
        Cookie is used to get an API Key (longer term access key) 
        """
        data = {"name": "create-bureau"}

        headers = {"content-type": "application/json",
                   "cookie": self.session_cookie}

        response = requests.post("https://users.{}/api_tokens/".format(
            self.host), json=data, headers=headers, verify=self.verify_ssl)

        if response.ok:
            self.api_auth = response.json()
            #print(self.api_auth)
            print(" We have received an API key we can re-use")

    def init_api(self, username, password):
        """
        Creates a connection to the system. 
        Username / Password to get a Cookie (temporary, expiring key)
        Cookie is used to get an API Key (longer term access key) 
        """
        self._init_session(username, password)
        self._get_api_key()

    def make_request(self, url, data):
        "Example of calling the API using the API Key to request data from an endpoint"
        auth = HTTPBasicAuth(self.api_auth["uuid"], self.api_auth["secret"])
        return requests.post(url.format(self.host), auth=auth, data=data, verify=self.verify_ssl)

    def make_delete_request(self, url, uuid):
        "Example of calling the API using the API Key to delete data from an endpoint"
        auth = HTTPBasicAuth(self.api_auth["uuid"], self.api_auth["secret"])
        return requests.delete(url.format(self.host, uuid), auth=auth)

if __name__ == '__main__':
    print("Running Example AuthSessionExample at the command line")

    parser = argparse.ArgumentParser(description='Example of getting an API Key for Authentise.')
    parser.add_argument("username", help="username to log-in via")
    parser.add_argument("password", help="password to log-in via")

    args = parser.parse_args()
    if 'username' in args and 'password' in args:
        #print(args)
        sesh = AuthentiseSession(host = 'authentise.com', verify_ssl = True)
        sesh.init_api(args.username, args.password)
    # ags should print there error, no else case needed