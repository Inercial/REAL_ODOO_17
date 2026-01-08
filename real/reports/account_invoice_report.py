# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    price_unit_without_freight = fields.Float()

    def _select(self):
        select_str = super()._select()
        select_str += """
            ,line.price_unit_without_freight
        """
        return select_str
