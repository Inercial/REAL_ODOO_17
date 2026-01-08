# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    id_supplier = fields.Char(
        size=13, help="Supplier ID that must exist in the supplier database.", string="ID Supplier"
    )
    operation_type = fields.Selection(
        [
            ("01", "Own"),
            ("02", "Third parties"),
            ("04", "SPEI"),
            ("05", "TEF"),
            ("09", "TdeC Empresariales Banorte"),
            ("10", "Pago de TdC Banorte"),
            ("11", "Pago de TdC Otros Bancos"),
            ("12", "Pago de TdC AMEX"),
        ]
    )
    supplier_reference = fields.Char(
        help="Field used to define reference of supplier, if it's not used the"
        " reference must be the invoices that are paid."
    )

    @api.depends("acc_number", "acc_holder_name")
    def _compute_name(self):
        for rec in self:
            rec.name = " - ".join([rec.acc_number, rec.acc_holder_name]) if rec.acc_holder_name else rec.acc_number
