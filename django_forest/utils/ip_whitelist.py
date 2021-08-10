from django_forest.utils.forest_api_requester import ForestApiRequester


class IpWhitelist:

    fetched = False
    use_ip_whitelist = False
    rules = []

    @classmethod
    def get_rules(cls):
        try:
            response = ForestApiRequester.get('/liana/v1/ip-whitelist-rules')
        except Exception:
            raise Exception('Unable to retrieve ip whitelist rules')
        else:
            data = response.json()
            cls.fetched = True
            cls.use_ip_whitelist = data['data']['attributes']['use_ip_whitelist']
            cls.rules = data['data']['attributes']['rules']
