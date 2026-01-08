# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountPaymentLineCreate(models.TransientModel):
    _inherit = "account.payment.line.create"

    def populate(self):
        sup = super().populate()

        new_list = []
        for lines in self.move_line_ids:
            if not lines.move_id.stop_inv:
                new_list.append(lines.id)

        self.move_line_ids = [(6, 0, new_list)]

        return sup

    @api.onchange("move_line_ids")
    def check_inv_stp(self):
        for lines in self.move_line_ids:
            if lines.move_id.stop_inv:
                msg = _("Invoice blocked for payment: \n%s ", lines.move_id.name)
                raise ValidationError(msg)
