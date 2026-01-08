# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    def _prepare_move(self, bank_lines=None):
        res = super()._prepare_move(bank_lines)
        if bank_lines and len(bank_lines) == 1:
            res["ref"] = bank_lines.communication
        return res
