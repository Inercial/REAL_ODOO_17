# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
# pylint: disable=self-cls-assignment
# pylint: disable=super-with-arguments

from odoo import models


class AccountResequenceWizard(models.TransientModel):
    _inherit = "account.resequence.wizard"

    def resequence(self):
        context = self._context.copy()
        context["skip_account_move_synchronization"] = True
        self = self.with_context(**context)
        return super().resequence()
