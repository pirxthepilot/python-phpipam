# PHPIPAM Module
# Handy module for querying the phpipam API

import requests
import urllib
import json
import sys
import re


class PhpIpam:

    def __init__(self, ipam_baseurl, ipam_id, ipam_user, ipam_pw,
                 ca_cert=None):
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
        self.http_error_check(req_auth, exit_on_404=True)
        self.token = req_auth.json()['data']['token']
        self.headers = {'token': self.token}
        return self.headers

    def close(self):
        return requests.delete(self.ipam_root + '/user/',
                               headers=self.headers,
                               verify=self.verify).text

    def get(self, query):
        response = requests.get(self.ipam_root + urllib.quote(query),
                                headers=self.headers,
                                verify=self.verify)
        self.http_error_check(response)
        return response.json()

    def get_subnets(self):
        req = self.get('/sections/' + self.section_id +
                       '/subnets/')
        return self.proper_output(req)

    def get_subnet_id(self, subnet):
        req = self.get('/subnets/cidr/' + subnet)
        if self.proper_output(req):
            return req['data'][0]['id']
        else:
            return False

    def get_subnet_info(self, subnet):
        subnet_id = self.get_subnet_id(subnet)
        if subnet_id:
            req = self.get('/subnets/' + subnet_id + '/')
            return self.proper_output(req)

    def get_subnet_usage(self, subnet):
        subnet_id = self.get_subnet_id(subnet)
        if subnet_id:
            req = self.get('/subnets/' + subnet_id +
                           '/usage/')
            return self.proper_output(req)

    def get_subnet_firstfree(self, subnet):
        subnet_id = self.get_subnet_id(subnet)
        if subnet_id:
            req = self.get('/subnets/' + subnet_id +
                           '/first_free/')
            req_dict = { "code": req['code'],
                         "data": { "first_free": req['data'] }
                       }
            return self.proper_output(req_dict)

    def get_addresses(self, subnet):
        subnet_id = self.get_subnet_id(subnet)
        if subnet_id:
            req = self.get('/subnets/' + subnet_id +
                           '/addresses/')
            return self.proper_output(req)

    def get_address_info(self, address):
        req = self.get('/addresses/search/' + address + '/')
        return self.proper_output(req)

    def http_error_check(self, response, exit_on_404=False):
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # By default, do not treat 404 as an error
            if re.match('404', str(e)) is None:
                print str(e) + ' - ' + (response.json())['message']
                sys.exit(1)
            else:
                if exit_on_404:
                    sys.exit(1)

    def proper_output(self, data):
        """
        Standard output logic:
        If the query response code is 200, send the data
        Otherwise, return False
        """
        if data['code'] == 200:
            return json.dumps(data)
        else:
            return False
