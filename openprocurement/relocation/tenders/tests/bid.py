# -*- coding: utf-8 -*-
import unittest
import random

from openprocurement.relocation.core.tests.mixins import OwnershipChangeTestMixin

from openprocurement.relocation.tenders.tests.base import (
    OwnershipWebTest,
    OpenUAOwnershipWebTest,
    OpenEUOwnershipWebTest,
    test_tender_data,
    test_ua_tender_data,
    test_uadefense_tender_data,
    test_eu_tender_data,
    test_bid_data,
    test_ua_bid_data,
    test_uadefense_bid_data,
    test_eu_bid_data
)


class BidOwnershipChangeTest(OwnershipWebTest, OwnershipChangeTestMixin):
    initial_tender_data = test_tender_data
    initial_bid = test_bid_data
    first_owner = 'broker'
    second_owner = 'broker2'
    test_owner = 'broker2t'
    invalid_owner = 'broker4'
    initial_auth = ('Basic', (first_owner, ''))

    def prepare_ownership_change(self):
        self.set_tendering_status()

        self.initial_data =  self.initial_bid

        self.app.authorization = ('Basic', (self.first_owner, ''))
        response = self.app.post_json('/{}/{}/bids'.format(self.resource,
            self.tender_id), {'data': self.initial_data})
        self.assertEqual(response.status, '201 Created')

        self.bid_id = response.json['data']['id']
        self.transfer = self.bid_transfer = response.json['access']['transfer']
        self.first_owner_token = self.bid_token = response.json['access']['token']
        self.request_path = '/{}/{}/bids/{}'.format(self.resource, self.tender_id, self.bid_id)

    def check_permission(self, path, token):
        return self.app.patch_json('{}?acc_token={}'.format(path, token),
            {"data": {'value': {'amount': self.initial_bid['value']['amount']*random.random()}}}, status="*")


class OpenUABidOwnershipChangeTest(OpenUAOwnershipWebTest, BidOwnershipChangeTest):
    initial_tender_data = test_ua_tender_data
    initial_bid = test_ua_bid_data

    second_owner = 'broker4'
    test_owner = 'broker4t'
    invalid_owner = 'broker2'


class OpenUADefenseBidOwnershipChangeTest(OpenUABidOwnershipChangeTest):
    initial_tender_data = test_uadefense_tender_data
    initial_bid = test_uadefense_bid_data


class OpenEUBidOwnershipChangeTest(OpenEUOwnershipWebTest, OpenUABidOwnershipChangeTest):
    initial_tender_data = test_eu_tender_data
    initial_bid = test_eu_bid_data


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BidOwnershipChangeTest))
    suite.addTest(unittest.makeSuite(OpenUABidOwnershipChangeTest))
    suite.addTest(unittest.makeSuite(OpenUADefenseBidOwnershipChangeTest))
    suite.addTest(unittest.makeSuite(OpenEUBidOwnershipChangeTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
