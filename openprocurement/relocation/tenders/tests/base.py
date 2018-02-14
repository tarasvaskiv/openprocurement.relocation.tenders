# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from datetime import datetime, timedelta

from openprocurement.relocation.core.tests.base import BaseWebTest, now

from openprocurement.api.utils import apply_data_patch
from openprocurement.tender.belowthreshold.tests.base import test_organization, test_tender_data
try:
    from openprocurement.tender.openua.tests.base import test_tender_data as test_ua_tender_data
except ImportError:
    test_ua_tender_data = None
try:
    from openprocurement.tender.openuadefense.tests.base import test_tender_data as test_uadefense_tender_data
except ImportError:
    test_uadefense_tender_data = None
try:
    from openprocurement.tender.openeu.tests.base import test_tender_data as test_eu_tender_data
except ImportError:
    test_eu_tender_data = None

from openprocurement.tender.limited.tests.base import (test_tender_data as test_tender_reporting_data,
                                                       test_tender_negotiation_data,
                                                       test_tender_negotiation_quick_data,
                                                       skipNegotiation)


test_bid_data = {'tenderers': [test_organization], "value": {"amount": 500, 'valueAddedTaxIncluded': False}}
test_ua_bid_data = deepcopy(test_bid_data)
test_ua_bid_data.update({'selfEligible': True, 'selfQualified': True})
test_uadefense_bid_data = deepcopy(test_ua_bid_data)
test_eu_bid_data = deepcopy(test_ua_bid_data)


class OwnershipWebTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)
    resource = 'tenders'

    def setUp(self):
        super(OwnershipWebTest, self).setUp()
        self.create_tender()

    def create_tender(self):
        data = deepcopy(self.initial_tender_data)
        response = self.app.post_json('/tenders', {'data': data})
        tender = response.json['data']
        self.tender_token = response.json['access']['token']
        self.tender_transfer = response.json['access']['transfer']
        self.tender_id = tender['id']

    def set_tendering_status(self):
        data = {
            "status": "active.tendering",
            "enquiryPeriod": {
                "startDate": (now - timedelta(days=10)).isoformat(),
                "endDate": (now).isoformat()
            },
            "tenderPeriod": {
                "startDate": (now).isoformat(),
                "endDate": (now + timedelta(days=7)).isoformat()
            }
        }

        tender = self.db.get(self.tender_id)
        tender.update(apply_data_patch(tender, data))
        self.db.save(tender)

    def set_qualification_status(self):
        data = {
            "status": 'active.qualification',
            "enquiryPeriod": {
                "startDate": (now - timedelta(days=18)).isoformat(),
                "endDate": (now - timedelta(days=8)).isoformat()
            },
            "tenderPeriod": {
                "startDate": (now - timedelta(days=8)).isoformat(),
                "endDate": (now - timedelta(days=1)).isoformat()
            },
            "auctionPeriod": {
                "startDate": (now - timedelta(days=1)).isoformat(),
                "endDate": (now).isoformat()
            },
            "awardPeriod": {
                "startDate": (now).isoformat()
            }
        }

        tender = self.db.get(self.tender_id)
        tender.update(apply_data_patch(tender, data))
        self.db.save(tender)


class OpenUAOwnershipWebTest(OwnershipWebTest):
    """
    OpenUA Web Test to test openprocurement.relocation.api.
    """

    def set_tendering_status(self):
        data = {
            "status": "active.tendering",
            "enquiryPeriod": {
                "startDate": (now - timedelta(days=15)).isoformat(),
                "endDate": (now).isoformat()
            },
            "tenderPeriod": {
                "startDate": (now).isoformat(),
                "endDate": (now + timedelta(days=30)).isoformat()
            }
        }

        tender = self.db.get(self.tender_id)
        tender.update(apply_data_patch(tender, data))
        self.db.save(tender)

    def set_qualification_status(self):
        data = {
            "status": 'active.qualification',
            "enquiryPeriod": {
                "startDate": (now - timedelta(days=46)).isoformat(),
                "endDate": (now - timedelta(days=31)).isoformat()
            },
            "tenderPeriod": {
                "startDate": (now - timedelta(days=31)).isoformat(),
                "endDate": (now - timedelta(days=1)).isoformat()
            },
            "auctionPeriod": {
                "startDate": (now - timedelta(days=1)).isoformat(),
                "endDate": (now).isoformat()
            },
            "awardPeriod": {
                "startDate": (now).isoformat()
            }
        }

        tender = self.db.get(self.tender_id)
        tender.update(apply_data_patch(tender, data))
        self.db.save(tender)


class OpenEUOwnershipWebTest(OpenUAOwnershipWebTest):
    """
    OpenEU Web Test to test openprocurement.relocation.api.
    """


    def set_auction_status(self, extra=None):
        data = {
            "enquiryPeriod": {
                "startDate": (now - timedelta(days=46)).isoformat(),
                "endDate": (now - timedelta(days=31)).isoformat()
            },
            "tenderPeriod": {
                "startDate": (now - timedelta(days=31)).isoformat(),
                "endDate": (now - timedelta(days=1)).isoformat()
            },
            "qualificationPeriod": {
                "startDate": (now - timedelta(days=1)).isoformat(),
                "endDate": (now).isoformat()
            },
            "auctionPeriod": {
                "startDate": now.isoformat()
            }
        }
        if extra:
            data.update(extra)

        tender = self.db.get(self.tender_id)
        tender.update(apply_data_patch(tender, data))
        self.db.save(tender)

    def set_pre_qualification_status(self, extra=None):
        data = {
            "enquiryPeriod": {
                "startDate": (now - timedelta(days=45)).isoformat(),
                "endDate": (now - timedelta(days=30)).isoformat()
            },
            "tenderPeriod": {
                "startDate": (now - timedelta(days=30)).isoformat(),
                "endDate": (now).isoformat(),
            },
            "qualificationPeriod": {
                "startDate": (now).isoformat(),
            }
        }
        if extra:
            data.update(extra)

        tender = self.db.get(self.tender_id)
        tender.update(apply_data_patch(tender, data))
        self.db.save(tender)


class ContractOwnershipWebTest(BaseWebTest):

    def setUp(self):
        super(ContractOwnershipWebTest, self).setUp()
        self.create_contract()

    def create_contract(self):
        data = deepcopy(self.initial_tender_data)

        orig_auth = self.app.authorization
        self.app.authorization = ('Basic', ('contracting', ''))
        response = self.app.post_json('/contracts', {'data': data})
        self.contract = response.json['data']
        # self.contract_token = response.json['access']['token']
        self.contract_id = self.contract['id']
        self.app.authorization = orig_auth
