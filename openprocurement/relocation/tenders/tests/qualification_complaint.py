# -*- coding: utf-8 -*-
import unittest
import random

from openprocurement.relocation.core.tests.mixins import OwnershipChangeTestMixin
from openprocurement.relocation.core.tests.base import test_transfer_data

from openprocurement.relocation.tenders.tests.base import (
    OpenEUOwnershipWebTest,
    test_eu_tender_data,
    test_eu_bid_data,
    test_organization
)


@unittest.skipIf(test_eu_tender_data == None, 'Skip above eu tests')
class QualificationComplaintOwnershipChangeTest(OpenEUOwnershipWebTest, OwnershipChangeTestMixin):
    initial_tender_data = test_eu_tender_data
    initial_bid = test_eu_bid_data

    first_owner = 'broker'
    second_owner = 'broker4'
    test_owner = 'broker4t'
    invalid_owner = 'broker2'
    initial_auth = ('Basic', (first_owner, ''))

    def prepare_ownership_change(self):
        self.set_tendering_status()

        #broker(tender owner)create bid
        response = self.app.post_json('/tenders/{}/bids'.format(
            self.tender_id), {'data': self.initial_bid})
        self.assertEqual(response.status, '201 Created')
        bid1_id = response.json['data']['id']
        bid1_token = response.json['access']['token']

        #broker4 create bid
        auth = self.app.authorization
        self.app.authorization = ('Basic', (self.second_owner, ''))
        response = self.app.post_json('/tenders/{}/bids'.format(
            self.tender_id), {'data': self.initial_bid})
        bid2_id  = response.json['data']['id']
        bid2_token = response.json['access']['token']

        #broker change status to pre-qualification
        self.set_pre_qualification_status()

        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.app.authorization = auth

        #qualifications
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.assertEqual(response.status, "200 OK")
        qualifications = response.json['data']

        for qualification in qualifications:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification['id'], self.tender_token),
                                           {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, "200 OK")

        # active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json['data']['status'], "active.pre-qualification.stand-still")

        qualification_id = qualifications[1]['id']

        # broker create complaint
        self.initial_data = {'title': 'complaint title', 'description': 'complaint description', 'author': test_organization, 'status': 'draft'}

        self.app.authorization = ('Basic', (self.first_owner, ''))
        self.create_token = bid1_token
        response = self.app.post_json('/tenders/{}/qualifications/{}/complaints?acc_token={}'.format(self.tender_id, qualification_id, self.create_token),
                                      {'data': self.initial_data})
        self.assertEqual(response.status, '201 Created')

        self.complaint_id = response.json['data']['id']
        self.transfer = self.complaint_transfer = response.json['access']['transfer']
        self.first_owner_token = self.complaint_token = response.json['access']['token']
        self.request_path = '/{}/{}/qualifications/{}/complaints/{}'.format(self.resource, self.tender_id, qualification_id, self.complaint_id)

    def check_permission(self, path, token):
        return self.app.patch_json('{}?acc_token={}'.format(path, token),
            {"data": {'description': "Check permission {}".format(random.random())}}, status="*")


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(QualificationComplaintOwnershipChangeTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
