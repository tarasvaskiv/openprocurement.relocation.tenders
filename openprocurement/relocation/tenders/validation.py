# -*- coding: utf-8 -*-
from openprocurement.relocation.core.validation import validate_accreditation_level


def validate_tender_accreditation_level(request):
    validate_accreditation_level(request, request.validated['tender'], 'create_accreditation')


def validate_tender_bid_accreditation_level(request):
    validate_accreditation_level(request, request.validated['tender'], 'edit_accreditation')


validate_complaint_accreditation_level = validate_tender_bid_accreditation_level
