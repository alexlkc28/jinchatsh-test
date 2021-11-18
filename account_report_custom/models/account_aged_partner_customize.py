# -*- coding: utf-8 -*-

from odoo import models, api, _

import logging

_logger = logging.getLogger(__name__)


class ReportAccountAgedPartnerCustomize(models.AbstractModel):
    _inherit = "account.aged.partner"

    @api.model
    def _get_column_details(self, options):
        columns = super()._get_column_details(options)

        columns[4:] = [
            self._custom_column(  # Avoid doing twice the sub-select in the view
                name=_('SO no.'),
                classes=['string'],
                getter=(
                    lambda v: self.x_studio_source_order
                ),
                sortable=True,
            )
        ]

        _logger.info(columns)

        return columns
