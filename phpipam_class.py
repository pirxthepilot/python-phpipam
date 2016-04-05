# PHPIPAM Module
# Handy module for querying the phpipam API

import requests
import json
import sys


class PhpIpam:

    def __init__(self, ipam_baseurl, ipam_id, ipam_user, ipam_pw, ca_cert=None):
        self.ipam_root = ipam_baseurl + '/api/' + ipam_id
        self.ipam_id = ipam_id
        self.ipam_user = ipam_user
        self.ipam_pw = ipam_pw
        self.section_id = '1'   # Hard coded section ID (IPv4)
        self.verify = True if ca_cert is None else ca_cert

    def connect(self):
        try:
            req_auth = requests.post(self.ipam_root + '/user/',
                                     auth=(self.ipam_user, self.ipam_pw),
                                     verify=self.verify)
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.TooManyRedirects) as e:
            print 'requests error: ' + str(e)
            sys.exit(1)
        self.http_error_check(req_auth)
        self.token = req_auth.json()['data']['token']
        self.headers = {'token': self.token}
        return self.headers

    def close(self):
        return requests.delete(self.ipam_root + '/user/',
                               headers=self.headers,
                               verify=self.verify).text

    def get(self, query):
        response = requests.get(self.ipam_root + query,
                                headers=self.headers,
                                verify=self.verify)
        self.http_error_check(response)
        return response.json()

    def get_subnets(self):
        req = self.get('/sections/' + self.section_id +
                       '/subnets/')
        return json.dumps(req)

    def get_addresses(self, subnet):
        subnet_id = (self.get('/subnets/cidr/' + subnet))['data'][0]['id']
        req = self.get('/subnets/' + subnet_id +
                       '/addresses/')
        return json.dumps(req)

    def get_address_info(self, address):
        req = self.get('/addresses/search/' + address + '/')
        return json.dumps(req)

    def http_error_check(self, response):
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print str(e) + ' - ' + (response.json())['message']
            sys.exit(1)
