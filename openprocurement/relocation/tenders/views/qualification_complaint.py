# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
    APIResource,
    save_tender,
    ROUTE_PREFIX,
    context_unpack
)
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.relocation.core.utils import change_ownership
from openprocurement.relocation.core.validation import validate_ownership_data
from openprocurement.relocation.tenders.validation import validate_complaint_accreditation_level


@qualifications_resource(name='Qualification complaint ownership',
            path='/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/ownership',
            description="Qualification complaint Ownership")
class QualificationComplaintOwnershipResource(APIResource):

    @json_view(permission='create_complaint',
               validators=(validate_complaint_accreditation_level,
                           validate_ownership_data,))
    def post(self):
        complaint = self.request.context
        tender = self.request.validated['tender']
        qualification_id = self.request.validated['qualification_id']
        location = self.request.route_path('Tender EU Qualification Complaints', tender_id=tender.id, qualification_id=qualification_id, complaint_id=complaint.id)
        location = location[len(ROUTE_PREFIX):]  # strips /api/<version>

        if change_ownership(self.request, location) and save_tender(self.request):
            self.LOGGER.info('Updated qualification {} complaint {} ownership of tender {}'.format(complaint.id, qualification_id, tender.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'qualification_complaint_ownership_update'}, {'complaint_id': complaint.id, 'qualification_id': qualification_id, 'tender_id': tender.id}))

            return {'data': complaint.serialize('view')}
