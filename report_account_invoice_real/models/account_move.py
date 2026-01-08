from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_name_invoice_report(self):
        self.ensure_one()
        if self.l10n_mx_edi_cfdi_state == "sent" and self.l10n_mx_edi_cfdi_attachment_id:
            return "report_account_invoice_real.report_invoice_original_real"
        return super()._get_name_invoice_report()
