# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
    opresource,
    APIResource,
    save_tender,
    ROUTE_PREFIX,
    context_unpack
)
from openprocurement.relocation.core.utils import change_ownership
from openprocurement.relocation.core.validation import validate_ownership_data
from openprocurement.relocation.tenders.validation import validate_complaint_accreditation_level


@opresource(name='Award complaint ownership',
            path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/ownership',
            description="Award complaint Ownership")
class AwardComplaintOwnershipResource(APIResource):

    @json_view(permission='create_complaint',
               validators=(validate_complaint_accreditation_level,
                           validate_ownership_data,))
    def post(self):
        complaint = self.request.context
        tender = self.request.validated['tender']
        award_id = self.request.validated['award_id']
        location = self.request.route_path('Tender Award Complaints', tender_id=tender.id, award_id=award_id, complaint_id=complaint.id)
        location = location[len(ROUTE_PREFIX):]  # strips /api/<version>

        if change_ownership(self.request, location) and save_tender(self.request):
            self.LOGGER.info('Updated award {} complaint {} ownership of tender {}'.format(complaint.id, award_id, tender.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'award_complaint_ownership_update'}, {'complaint_id': complaint.id, 'award_id': award_id, 'tender_id': tender.id}))

            return {'data': complaint.serialize('view')}
