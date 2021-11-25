# -*- coding: utf-8 -*-

from odoo import models, api, _, fields

import logging

_logger = logging.getLogger(__name__)


class ReportSaleOrderUndelivered(models.Model):
    _name = "account.saleorder.undelivered"
    _description = "Undelivered"
    _inherit = "account.accounting.report"
    _order = "order_no asc"
    _auto = False

    filter_unfold_all = True

    order_id = fields.Many2one('sale.order')
    order_no = fields.Char(group_operator='max')
    partner_id = fields.Many2one('res.partner')
    partner_name = fields.Char(group_operator='max')
    english_name = fields.Char(group_operator='max')
    product_code = fields.Char()
    quantity = fields.Float()
    shipped_quantity = fields.Float()
    outstanding_quantity = fields.Float()
    currency_name = fields.Char()
    currency_rate = fields.Float()
    currency_symbol = fields.Char()
    unit_price = fields.Monetary()
    amount_currency = fields.Monetary()
    amount = fields.Monetary()

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
                0 AS move_id, 
                sale_order_line.name, 
                0 AS account_id, 
                0 AS journal_id, 
                sale_order_line.company_id, 
                sale_order_line.currency_id, 
                0 AS analytic_account_id, 
                sale_order_line.display_type, 
                sale_order_line.create_date AS date, 
                0 AS debit, 
                0 AS credit, 
                0 AS balance,
                
                sale_order_line.id,
                sale_order_line.order_id,
                sale_order_line.currency_id,
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
                
                curr_rate.name AS currency_name,
                curr_rate.symbol AS currency_symbol,
                curr_rate.rate AS currency_rate,
                
                partner.id AS partner_id,
                partner.display_name AS partner_name,
                partner.name AS english_name
            FROM sale_order_line
            JOIN sale_order so ON sale_order_line.order_id = so.id
            JOIN res_partner partner ON so.partner_id = partner.id
            LEFT JOIN ir_property trust_property ON (
                trust_property.res_id = 'res.partner,'|| so.partner_id
                AND trust_property.name = 'trust'
                AND trust_property.company_id = sale_order_line.company_id
            )
            JOIN product_product prod ON sale_order_line.product_id = prod.id 
            LEFT JOIN LATERAL (
                    SELECT cr_c1.currency_id, cr_c1.rate, c_c1.name, c_c1.symbol
                    FROM res_currency_rate cr_c1
                    JOIN res_currency c_c1 ON c_c1.id = cr_c1.currency_id
                    WHERE cr_c1.currency_id = sale_order_line.currency_id
                    ORDER BY cr_c1.name DESC 
                    LIMIT 1
                ) curr_rate ON so.currency_id = curr_rate.currency_id           
            GROUP BY sale_order_line.id, sale_order_line.currency_id,
                prod.default_code, trust_property.id,
                so.id, so.name,
                curr_rate.rate, curr_rate.name, curr_rate.symbol,
                partner.id, partner.display_name, partner.name
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

    @api.model
    def _get_templates(self):
        # OVERRIDE
        templates = super(ReportSaleOrderUndelivered, self)._get_templates()
        templates['main_template'] = 'account_report_custom.template_account_saleorder_undelivered_report'
        templates['line_template'] = 'account_report_custom.line_template_account_saleorder_undelivered_report'
        return templates

    def _get_hierarchy_details(self, options):
        return [
            self._hierarchy_level('order_id', foldable=True, namespan=len(self._get_column_details(options)) - 7),
            self._hierarchy_level('id'),
        ]

    def _show_line(self, report_dict, value_dict, current, options):
        _logger.info(report_dict)
        """Determine if a line should be shown.

        By default, show only children of unfolded lines and children of non unfoldable lines
        :param report_dict: the lines to be displayed or not
        :param value_dict: the raw values of the current line
        :param current (list<tuple>): list of tuple(grouping_key, id)
        :param options (dict): report options.
        :return (bool): True if the line should be shown
        """
        return (report_dict['order_id'] is None
                or report_dict['order_id'] == 'total-None'
                or (report_dict['order_id'] in options.get('unfolded_lines', [])
                    or options.get('unfold_all'))
                or not self._get_hierarchy_details(options)[len(current) - 2].foldable)
