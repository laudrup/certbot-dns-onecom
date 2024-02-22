"""DNS Authenticator for One.com."""
import logging

import requests
import zope.interface
from bs4 import BeautifulSoup
from certbot import interfaces
from certbot.plugins import dns_common

logger = logging.getLogger(__name__)


@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for One.com

    This Authenticator uses the One.com web interface to fulfill
    a dns-01 challenge.
    """

    description = (
        "Obtain certificates using a DNS TXT record (if you are using One.com for DNS)."
    )
    ttl = 600

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None

    @classmethod
    def add_parser_arguments(cls, add):
        super(Authenticator, cls).add_parser_arguments(
            add, default_propagation_seconds=120
        )
        add("credentials", help="One.com credentials file.")

    def more_info(self):
        return (
            "This plugin configures a DNS TXT record to respond to a dns-01 challenge using "
            + "the One.com web interface."
        )

    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            "credentials",
            "One.com credentials file",
            {
                "username": "One.com username",
                "password": "One.com password",
            },
        )

    def _perform(self, domain, validation_domain_name, validation):
        self._get_onecom_client().add_txt_record(
            domain, validation_domain_name, validation
        )

    def _cleanup(self, domain, validation_domain_name, validation):
        self._get_onecom_client().del_txt_record(
            domain, validation_domain_name, validation
        )

    def _get_onecom_client(self):
        return _OneComClient(
            self.credentials.conf("username"),
            self.credentials.conf("password"),
            self.ttl,
        )


class _OneComClient(object):
    """
    Encapsulates all communication with One.com.
    """

    def __init__(self, username, password, ttl):
        super(_OneComClient, self).__init__()

        self.username = username
        self.password = password
        self.ttl = ttl
        self.session = requests.Session()

    def login(self):
        data = {
            'username': self.username,
            'password': self.password,
        }
        login_page = self.session.get('https://www.one.com/admin').text
        soup = BeautifulSoup(login_page, 'html.parser')
        login_form = soup.find('form', id='kc-form-login')
        login_url = login_form['action']

        res = self.session.post(login_url, data=data)
        if res.status_code != 200 or "Invalid username or password." in res.text:
            raise Exception(f'Login failed for {self.username}: {res.text}')

    def get_root_domain(self, start_domain):
        domain = start_domain
        # Loop over the subdomains
        while domain.count('.') > 0:
            # Get request, join list to string
            res = self.session.get(f'https://www.one.com/admin/api/domains/{domain}/dns/custom_records')
            if res.status_code == 200:
                # Domain found
                return domain
            else:
                # Domain does not exist, remove first subdomain and try again
                domain = '.'.join(domain.split(".")[1:])

        # We reached a top-level domain, raise an Exception
        raise Exception(f'Failed to find root domain for {start_domain}')


    def add_txt_record(self, full_domain, validation_domain_name, validation):
        logger.debug(f'add_txt_record: {full_domain}, {validation_domain_name}, {validation}')
        self.login()
        root_domain = self.get_root_domain(full_domain)
        prefix = validation_domain_name.removesuffix(f'.{root_domain}')
        payload = {
            "type": "dns_custom_records",
            "attributes": {
                "priority": 0,
                "ttl": self.ttl,
                "type": "TXT",
                "prefix": prefix,
                "content": validation
            }
        }
        res = self.session.post(f'https://www.one.com/admin/api/domains/{root_domain}/dns/custom_records', json=payload)
        if res.status_code != 200:
            raise Exception(f'Failed to add TXT record for {full_domain}: {res.text}')

    def del_txt_record(self, full_domain, validation_domain_name, validation):
        logger.debug(f'del_txt_record: {full_domain}, {validation_domain_name}, {validation}')
        self.login()
        root_domain = self.get_root_domain(full_domain)
        prefix = validation_domain_name.removesuffix(f'.{root_domain}')
        custom_records = self.session.get(f'https://www.one.com/admin/api/domains/{root_domain}/dns/custom_records').json()
        validation_record_ids = [rec["id"] for rec in custom_records['result']['data']
                                 if rec["attributes"]["type"] == "TXT"
                                 and rec["attributes"]["prefix"] == prefix]

        for record_id in validation_record_ids:
            res = self.session.delete(f'https://www.one.com/admin/api/domains/{root_domain}/dns/custom_records/{record_id}')
            if res.status_code != 200:
                logger.warn(f'Failed to remove TXT {validation_domain_name}: {res.text}')
