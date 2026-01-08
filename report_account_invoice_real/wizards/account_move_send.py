from odoo import api, models


class AccountMoveSend(models.TransientModel):
    _inherit = "account.move.send"

    @api.model
    def _prepare_invoice_pdf_report(self, invoice, invoice_data):
        """Prepare the pdf report for the invoice passed as parameter.
        :param invoice:         An account.move record.
        :param invoice_data:    The collected data for the invoice so far.
        """
        if invoice.invoice_pdf_report_id:
            return

        if invoice.move_type == "out_refund":
            report_name = "report_account_invoice_real.report_invoice_credit_memo_real"
        else:
            report_name = "report_account_invoice_real.action_report_invoice_original"

        content, _report_format = (
            self.env["ir.actions.report"]
            .with_company(invoice.company_id)
            .with_context(from_account_move_send=True)
            ._render(report_name, invoice.ids)
        )

        invoice_data["pdf_attachment_values"] = {
            "raw": content,
            "name": invoice._get_invoice_report_filename(),
            "mimetype": "application/pdf",
            "res_model": invoice._name,
            "res_id": invoice.id,
            "res_field": "invoice_pdf_report_file",  # Binary field
        }
