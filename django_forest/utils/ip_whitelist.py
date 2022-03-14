import ipaddress

import requests

from django_forest.utils.forest_api_requester import ForestApiRequester


class IpWhitelist:

    fetched = False
    use_ip_whitelist = False
    rules = []

    @classmethod
    def get_rules(cls):
        url = ForestApiRequester.build_url('/liana/v1/ip-whitelist-rules')
        response = ForestApiRequester.get(url)
        if response.status_code != requests.codes.ok:
            raise Exception('Unable to retrieve ip whitelist rules')

        data = response.json()
        cls.fetched = True
        cls.use_ip_whitelist = data['data']['attributes']['use_ip_whitelist']
        cls.rules = data['data']['attributes']['rules']

    @staticmethod
    def same_version(ip1, ip2):
        return isinstance(ip1, type(ip2))

    @staticmethod
    def is_both_loopback(ip1, ip2):
        return ip1.is_loopback and ip2.is_loopback

    @classmethod
    def is_ip_match_ip(cls, ip1, ip2):
        if not cls.same_version(ip1, ip2):
            return cls.is_both_loopback(ip1, ip2)

        if ip1 == ip2:
            return True
        else:
            return cls.is_both_loopback(ip1, ip2)

    @classmethod
    def is_ip_match_range(cls, ip, rule):
        ip_minimum = ipaddress.ip_address(rule['ipMinimum'])
        ip_maximum = ipaddress.ip_address(rule['ipMaximum'])
        if not cls.same_version(ip, ip_minimum):
            return False

        return int(ip_minimum) <= int(ip) <= int(ip_maximum)

    @classmethod
    def is_ip_match_subnet(cls, ip, subnet):
        return ip in list(ipaddress.ip_network(subnet).hosts())

    @classmethod
    def is_ip_matches_rule(cls, ip, rule):
        if rule['type'] == 0:
            return cls.is_ip_match_ip(ipaddress.ip_address(ip), ipaddress.ip_address(rule['ip']))
        elif rule['type'] == 1:
            return cls.is_ip_match_range(ipaddress.ip_address(ip), rule)
        elif rule['type'] == 2:
            return cls.is_ip_match_subnet(ipaddress.ip_address(ip), rule['range'])

    @classmethod
    def is_ip_matches_any_rule(cls, ip):
        for rule in cls.rules:
            if cls.is_ip_matches_rule(ip, rule):
                return True
        else:
            return False
