# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models


class HrExpense(models.Model):
    _inherit = "hr.expense"

    payment_mode = fields.Selection(
        default="petty_account",
    )

    @api.depends("employee_id")
    def _compute_is_editable(self):
        is_account_manager = self.env.user.has_group("account.group_account_user") or self.env.user.has_group(
            "account.group_account_manager"
        )
        for expense in self:
            if expense.state in ["draft", "downloaded"] or expense.sheet_id.state in ["draft", "submit"]:
                expense.is_editable = True
            elif expense.sheet_id.state == "approve":
                expense.is_editable = is_account_manager
            else:
                expense.is_editable = False

    def force_approved(self):
        global_partner = self.env["ir.config_parameter"].sudo().get_param("l10n_edi_hr_expense.global_partner")
        for exp in self.filtered(lambda e: e.payment_mode != "company_account"):
            exp.write(
                {
                    "l10n_edi_functionally_approved": True,
                    "l10n_edi_fiscally_approved": True,
                    "l10n_edi_forced_approved": True,
                    "partner_id": int(global_partner),
                }
            )
            exp.message_post(body=_("Approved was forced"))
        return super().force_approved()
