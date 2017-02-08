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
    test_organization
)


class ComplaintOwnershipChangeTest(OwnershipWebTest, OwnershipChangeTestMixin):
    initial_tender_data = test_tender_data

    first_owner = 'broker'
    second_owner = 'broker2'
    test_owner = 'broker2t'
    invalid_owner = 'broker4'
    initial_auth = ('Basic', (first_owner, ''))

    def prepare_ownership_change(self):
        self.set_tendering_status()

        self.initial_data =  {'title': 'complaint title', 'description': 'complaint description',
                             'author': test_organization, 'status': 'draft'}

        self.app.authorization = ('Basic', (self.first_owner, ''))
        response = self.app.post_json('/tenders/{}/complaints'.format(
                    self.tender_id), {'data': self.initial_data})
        self.assertEqual(response.status, '201 Created')

        self.complaint_id = response.json['data']['id']
        self.transfer = self.complaint_transfer = response.json['access']['transfer']
        self.first_owner_token = self.complaint_token = response.json['access']['token']
        self.request_path = '/{}/{}/complaints/{}'.format(self.resource, self.tender_id, self.complaint_id)

    def check_permission(self, path, token):
        return self.app.patch_json('{}?acc_token={}'.format(path, token),
            {"data": {'description': "Check permission {}".format(random.random())}}, status="*")



class OpenUAComplaintOwnershipChangeTest(OpenUAOwnershipWebTest, ComplaintOwnershipChangeTest):
    initial_tender_data = test_ua_tender_data

    second_owner = 'broker4'
    test_owner = 'broker4t'
    invalid_owner = 'broker2'


class OpenUADefenseComplaintOwnershipChangeTest(OpenUAComplaintOwnershipChangeTest):
    initial_tender_data = test_uadefense_tender_data


class OpenEUComplaintOwnershipChangeTest(OpenEUOwnershipWebTest, OpenUAComplaintOwnershipChangeTest):
    initial_tender_data = test_eu_tender_data


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ComplaintOwnershipChangeTest))
    suite.addTest(unittest.makeSuite(OpenUAComplaintOwnershipChangeTest))
    suite.addTest(unittest.makeSuite(OpenUADefenseComplaintOwnershipChangeTest))
    suite.addTest(unittest.makeSuite(OpenEUComplaintOwnershipChangeTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
