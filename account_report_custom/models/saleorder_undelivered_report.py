# -*- coding: utf-8 -*-

from odoo import models, api, _, fields

import logging

_logger = logging.getLogger(__name__)


class ReportSaleOrderUndelivered(models.Model):
    _name = "account.saleorder.undelivered"
    _description = "Undelivered"
    _inherit = "account.aged.partner"
    _auto = False

    product_code = fields.Char()
    quantity = fields.Float()
    shipped_quantity = fields.Float()
    outstanding_quantity = fields.Float()
    unit_price = fields.Monetary()
    currency_name = fields.Char()
    currency_symbol = fields.Char()
    amount = fields.Monetary()
    english_name = fields.Char()

    def _get_options(self, previous_options=None):
        # OVERRIDE
        options = super(ReportSaleOrderUndelivered, self)._get_options(previous_options=previous_options)
        # options['filter_account_type'] = 'receivable'
        return options

    @api.model
    def _get_report_name(self):
        return _("Undelivered")

    @api.model
    def _get_sql(self):
        options = self.env.context['report_options']
        query = ("""
            SELECT
                sale_order_line.id, 
                sale_order_line.order_id,
                sale_order_line.product_id,                
                sale_order_line.product_uom_qty AS quantity,
                sale_order_line.qty_delivered AS shipped_quantity,
                sale_order_line.price_unit AS unit_price,
                sale_order_line.price_total AS amount_currency,
                
                CASE WHEN curr_rate.rate > 0
                    THEN (sale_order_line.price_total/curr_rate.rate)
                    ELSE sale_order_line.price_total END AS amount,
                
                (sale_order_line.product_uom_qty - sale_order_line.qty_delivered) AS outstanding_quantity,
                
                prod.default_code AS product_code,
                
                so.name AS order_no,
                so.partner_id AS partner_id,
                so.currency_id AS currency_id,
                
                curr_rate.name AS currency_name,
                curr_rate.symbol AS currency_symbol,
                curr_rate.rate AS currency_rate,
                
                customer.display_name AS partner_name,
                customer.name AS english_name
            FROM sale_order_line
            JOIN sale_order so ON sale_order_line.order_id = so.id
            JOIN res_partner customer ON so.partner_id = customer.id
            JOIN product_product prod ON sale_order_line.product_id = prod.id 
            LEFT JOIN LATERAL (
                    SELECT cr_c1.currency_id, cr_c1.rate, c_c1.name, c_c1.symbol
                    FROM res_currency_rate cr_c1
                    JOIN res_currency c_c1 ON c_c1.id = cr_c1.currency_id
                    WHERE cr_c1.currency_id = so.currency_id
                    ORDER BY cr_c1.name DESC 
                    LIMIT 1
                ) curr_rate ON so.currency_id = curr_rate.currency_id           
            GROUP BY sale_order_line.id, prod.default_code, so.name, so.partner_id, so.currency_id, 
                curr_rate.rate, curr_rate.name, curr_rate.symbol,
                customer.display_name, customer.name
        """)

        params = {}
        return self.env.cr.mogrify(query, params).decode(self.env.cr.connection.encoding)

    @api.model
    def _get_column_details(self, options):
        columns = [
            self._field_column('order_no', name=_("Order No."), ellipsis=True),
            self._field_column('partner_name', name=_("Customer")),
            self._field_column('english_name', name=_("Customer English Name")),
            self._field_column('product_code', name=_("Product Code")),
            self._field_column('quantity', name=_("Quantity")),
            self._field_column('shipped_quantity', name=_("Shipped Quantity")),
            self._field_column('outstanding_quantity', name=_("Outstanding Quantity")),
            self._field_column('currency_symbol', name=_("Currency")),
            self._field_column('unit_price', name=_("Unit Price")),
            self._field_column('amount_currency'),
            self._field_column('amount', name=_("Amount")),
        ]

        return columns
