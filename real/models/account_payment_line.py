# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountPaymentLine(models.Model):
    _inherit = "account.payment.line"

    @api.onchange("move_line_id")
    def move_line_id_change(self):
        if self.move_line_id.move_id.stop_inv:
            msg = _("Invoice blocked for payment: \n%s ", self.move_line_id.move_id.name)
            raise ValidationError(msg)
        return super().move_line_id_change()
