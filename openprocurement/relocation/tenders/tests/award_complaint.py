# -*- coding: utf-8 -*-
import unittest
import random

from openprocurement.relocation.core.tests.mixins import OwnershipChangeTestMixin
from openprocurement.relocation.core.tests.base import test_transfer_data
from openprocurement.relocation.tenders.tests.base import (
    OwnershipWebTest,
    OpenUAOwnershipWebTest,
    OpenEUOwnershipWebTest,
    test_tender_data,
    test_ua_tender_data,
    test_uadefense_tender_data,
    test_eu_tender_data,
    test_tender_negotiation_data,
    test_tender_negotiation_quick_data,
    test_bid_data,
    test_ua_bid_data,
    test_uadefense_bid_data,
    test_eu_bid_data,
    test_organization,
    skipNegotiation
)

class AwardComplaintOwnershipChangeTest(OwnershipWebTest, OwnershipChangeTestMixin):
    initial_tender_data = test_tender_data
    initial_bid = test_bid_data

    first_owner = 'broker'
    second_owner = 'broker2'
    test_owner = 'broker2t'
    invalid_owner = 'broker4'
    initial_auth = ('Basic', (first_owner, ''))

    def check_permission(self, path, token):
        return self.app.patch_json('{}?acc_token={}'.format(path, token),
        {"data": {'description': "Check permission {}".format(random.random())}}, status="*")

    def prepare_ownership_change(self):
        self.set_tendering_status()

        #broker(tender owner)create bid
        response = self.app.post_json('/tenders/{}/bids'.format(
        self.tender_id), {'data': self.initial_bid})
        self.assertEqual(response.status, '201 Created')
        bid1_id = response.json['data']['id']
        self.create_token = bid1_token = response.json['access']['token']

        #broker4 create bid
        self.app.authorization = ('Basic', (self.second_owner, ''))
        response = self.app.post_json('/tenders/{}/bids'.format(
        self.tender_id), {'data': self.initial_bid})
        bid2_id  = response.json['data']['id']
        bid2_token = response.json['access']['token']

        # submit award
        self.set_qualification_status()
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(
            self.tender_id), {'data': {'suppliers': [test_organization], 'status': 'pending', 'bid_id': bid2_token}})
        award = response.json['data']
        self.award_id = award['id']

        # submit complaint from broker
        self.initial_data = {'title': 'complaint title', 'description': 'complaint description', 'author': test_organization, 'status': 'draft'}

        self.app.authorization = ('Basic', (self.first_owner, ''))

        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.create_token), {'data': self.initial_data})
        self.assertEqual(response.status, '201 Created')

        self.complaint_id = response.json['data']['id']
        self.transfer = self.complaint_transfer = response.json['access']['transfer']
        self.first_owner_token = self.complaint_token = response.json['access']['token']
        self.request_path = '/{}/{}/awards/{}/complaints/{}'.format(self.resource, self.tender_id, self.award_id, self.complaint_id)


@unittest.skipIf(test_ua_tender_data == None, 'Skip above ua tests')
class OpenUAAwardComplaintOwnershipChangeTest(OpenUAOwnershipWebTest, AwardComplaintOwnershipChangeTest):
    initial_tender_data = test_ua_tender_data
    initial_bid = test_ua_bid_data

    second_owner = 'broker4'
    test_owner = 'broker4t'
    invalid_owner = 'broker2'


@unittest.skipIf(test_uadefense_tender_data == None, 'Skip above ua defense tests')
class OpenUADefenseAwardComplaintOwnershipChangeTest(OpenUAAwardComplaintOwnershipChangeTest):
    initial_tender_data = test_uadefense_tender_data
    initial_bid = test_uadefense_bid_data


@unittest.skipIf(test_eu_tender_data == None, 'Skip above eu tests')
class OpenEUAwardComplaintOwnershipChangeTest(OpenEUOwnershipWebTest, OpenUAAwardComplaintOwnershipChangeTest):
    initial_tender_data = test_eu_tender_data
    initial_bid = test_eu_bid_data

    def prepare_ownership_change(self):
        self.set_tendering_status()

        #broker(tender owner)create bid
        response = self.app.post_json('/tenders/{}/bids'.format(
        self.tender_id), {'data': self.initial_bid})
        self.assertEqual(response.status, '201 Created')
        bid1_id = response.json['data']['id']
        self.create_token = bid1_token = response.json['access']['token']

        #broker4 create bid
        self.app.authorization = ('Basic', (self.second_owner, ''))
        response = self.app.post_json('/tenders/{}/bids'.format(
        self.tender_id), {'data': self.initial_bid})
        bid2_id  = response.json['data']['id']
        bid2_token = response.json['access']['token']

        # switch to active.pre-qualification
        self.set_pre_qualification_status({"id": self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        # qualify bids
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.app.authorization = ('Basic', (self.first_owner, ''))
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
                self.tender_id, qualification['id'], self.tender_token), {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, "200 OK")

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
            self.tender_id, self.tender_token), {"data": {"status": 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        # switch to active.auction
        self.set_auction_status({"id": self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], "active.auction")

        # submit award
        self.set_qualification_status()
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(
            self.tender_id), {'data': {'suppliers': [test_organization], 'status': 'pending', 'bid_id': bid2_token}})
        award = response.json['data']
        self.award_id = award['id']


        # submit complaint from broker
        self.initial_data = {'title': 'complaint title', 'description': 'complaint description', 'author': test_organization, 'status': 'draft'}

        self.app.authorization = ('Basic', (self.first_owner, ''))

        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.create_token), {'data': self.initial_data})
        self.assertEqual(response.status, '201 Created')

        self.complaint_id = response.json['data']['id']
        self.transfer = self.complaint_transfer = response.json['access']['transfer']
        self.first_owner_token = self.complaint_token = response.json['access']['token']
        self.request_path = '/{}/{}/awards/{}/complaints/{}'.format(self.resource, self.tender_id, self.award_id, self.complaint_id)


@unittest.skipIf(skipNegotiation, 'Skip negotiation tests')
class NegotiationAwardComplaintOwnershipChangeTest(OpenUAAwardComplaintOwnershipChangeTest):
    initial_tender_data = test_tender_negotiation_data

    def prepare_ownership_change(self):
        # Create award
        request_path = '/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.tender_token)
        response = self.app.post_json(request_path, {'data': {'suppliers': [test_organization], 'qualified': True,
                                                              'status': 'pending'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        award = response.json['data']
        self.award_id = award['id']

        # submit complaint from broker
        self.initial_data = {'title': 'complaint title', 'description': 'complaint description', 'author': test_organization, 'status': 'draft'}

        self.app.authorization = ('Basic', (self.first_owner, ''))

        response = self.app.post_json('/tenders/{}/awards/{}/complaints'.format(
            self.tender_id, self.award_id), {'data': self.initial_data})
        self.assertEqual(response.status, '201 Created')

        self.complaint_id = response.json['data']['id']
        self.transfer = self.complaint_transfer = response.json['access']['transfer']
        self.first_owner_token = self.complaint_token = response.json['access']['token']
        self.request_path = '/{}/{}/awards/{}/complaints/{}'.format(self.resource, self.tender_id, self.award_id, self.complaint_id)


@unittest.skipIf(skipNegotiation, 'Skip negotiation tests')
class NegotiationQuickAwardComplaintOwnershipChangeTest(NegotiationAwardComplaintOwnershipChangeTest):
    initial_tender_data = test_tender_negotiation_quick_data



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AwardComplaintOwnershipChangeTest))
    suite.addTest(unittest.makeSuite(OpenUAAwardComplaintOwnershipChangeTest))
    suite.addTest(unittest.makeSuite(OpenUADefenseAwardComplaintOwnershipChangeTest))
    suite.addTest(unittest.makeSuite(OpenEUAwardComplaintOwnershipChangeTest))
    suite.addTest(unittest.makeSuite(NegotiationAwardComplaintOwnershipChangeTest))
    suite.addTest(unittest.makeSuite(NegotiationQuickAwardComplaintOwnershipChangeTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
