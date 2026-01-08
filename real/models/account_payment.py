# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    reonciliation_date = fields.Date(
        compute="_compute_stat_buttons_from_reconciliation",
        store=True,
        string="Bank Reconciliation Date",
        compute_sudo=False,
    )

    @api.depends(
        "move_id.line_ids.matched_debit_ids",
        "move_id.line_ids.matched_credit_ids",
    )
    def _compute_stat_buttons_from_reconciliation(self):
        res = super()._compute_stat_buttons_from_reconciliation()
        count = 0
        for rec in self:
            count += 1
            rec.reonciliation_date = False
            if not rec.reconciled_statement_line_ids:
                continue
            statements = self.env["account.bank.statement.line"].browse(rec.reconciled_statement_line_ids.ids)
            rec.reonciliation_date = max(statements.mapped("date"))
        return res

    def action_post(self):
        self.check_invs()
        return super().action_post()

    def check_invs(self):
        for rec in self:
            am = self.env["account.move"].search([("partner_id", "=", rec.partner_id.id), ("stop_inv", "=", True)])
            if am:
                names = [move.name for move in am]
                msg = _("This supplier has invoices blocked for payment. \nBlocked invoices: %s ", names)
                raise ValidationError(msg)
