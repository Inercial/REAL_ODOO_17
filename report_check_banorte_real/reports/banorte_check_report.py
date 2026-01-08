# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL.html).

from odoo import _, models
from odoo.tools.misc import format_date, formatLang


class BanorteCheckReport(models.AbstractModel):
    _name = "report.report_check_banorte_real.banorte_check_xlsx"
    _description = "Check XLSX Report for Banorte"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, payments):
        for payment in payments:
            date = format_date(self.env, payment.date, date_format="long")
            sheet = workbook.add_worksheet(_("Check"))
            sheet.write_string("E3", date)
            partner_name = payment.partner_id.name
            if payment.l10n_edi_employee_id:
                partner_name = payment.l10n_edi_employee_id.name
            sheet.write_string("B6", partner_name)
            sheet.write_string("J6", formatLang(self.env, payment.amount, currency_obj=payment.currency_id))
            sheet.write_string("A8", payment.check_amount_in_words)
            sheet.write_string("A19", payment.ref or "*")
            for row_num, line in enumerate(payment.move_id.line_ids):
                sheet.write_string(row_num + 24, 0, line.account_id.code)
                sheet.write_string(row_num + 24, 1, line.account_id.name)
                sheet.write_string(
                    row_num + 24,
                    8,
                    line.debit and formatLang(self.env, line.debit, currency_obj=payment.currency_id) or "",
                )
                sheet.write_string(
                    row_num + 27,
                    9,
                    line.credit and formatLang(self.env, line.credit, currency_obj=payment.currency_id) or "",
                )
            sheet.write_string(
                "I35",
                formatLang(self.env, sum(payment.mapped("move_id.line_ids.debit")), currency_obj=payment.currency_id),
            )
            sheet.write_string(
                "J35",
                formatLang(self.env, sum(payment.mapped("move_id.line_ids.credit")), currency_obj=payment.currency_id),
            )
            sheet.write_string("A37", date)
            sheet.write_string("D41", "CR")
            sheet.write_string("F41", "FCR")
            sheet.write_string("J41", payment.check_number or "-")
