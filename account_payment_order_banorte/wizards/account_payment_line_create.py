# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class AccountPaymentLineCreate(models.TransientModel):
    _inherit = "account.payment.line.create"

    operation_type = fields.Selection(
        [
            ("01", "Own"),
            ("02", "Third parties"),
            ("04", "SPEI"),
            ("05", "TEF"),
        ]
    )

    def _prepare_move_line_domain(self):
        domain = super()._prepare_move_line_domain()
        if self.operation_type:
            domain += [("move_id.partner_bank_id.operation_type", "=", self.operation_type)]
        return domain
