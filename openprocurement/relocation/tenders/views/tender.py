# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
    opresource,
    APIResource,
    ROUTE_PREFIX,
    context_unpack
)
from openprocurement.tender.core.utils import save_tender, optendersresource
from openprocurement.relocation.core.utils import change_ownership
from openprocurement.relocation.core.validation import validate_ownership_data
from openprocurement.relocation.tenders.validation import validate_tender_accreditation_level


@optendersresource(name='Tender ownership',
            path='/tenders/{tender_id}/ownership',
            description="Tenders Ownership")
class TenderResource(APIResource):

    @json_view(permission='create_tender',
               validators=(validate_tender_accreditation_level,
                           validate_ownership_data,))
    def post(self):
        tender = self.request.validated['tender']
        location = self.request.route_path('{}:Tender'.format(tender['procurementMethodType']), tender_id=tender.id)
        location = location[len(ROUTE_PREFIX):]  # strips /api/<version>

        if change_ownership(self.request, location) and save_tender(self.request):
            self.LOGGER.info('Updated ownership of tender {}'.format(tender.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_ownership_update'}))

            return {'data': tender.serialize('view')}
