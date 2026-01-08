# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, models
from odoo.tools.misc import format_date, formatLang


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def do_print_checks(self):
        mx_check_layout = self[0].journal_id.mx_check_layout
        banorte_ref = "l10n_mx_check_printing.action_print_check_banorte"
        if mx_check_layout == banorte_ref:
            self.write({"state": "posted"})
            module = __name__.split("addons.")[1].split(".")[0]
            report_name = "{}.banorte_check_xlsx".format(module)
            return {
                "type": "ir.actions.report",
                "report_type": "xlsx",
                "report_name": report_name,
                "context": dict(self.env.context, report_file=_("Banorte Check")),
                "data": {"dynamic_report": True},
            }
        return super().do_print_checks()

    def get_pages(self):
        """Returns the data structure used by the template : a list of dicts
        containing what to print on pages.
        """
        pages = []
        pages.append(
            {
                "sequence_number": self.check_number,
                "date": format_date(self.env, self.date, date_format="long"),
                "partner_id": self.partner_id,
                "partner_name": (self.partner_id.name or "").upper(),
                "currency": self.currency_id,
                "state": self.state,
                "amount": formatLang(self.env, self.amount, currency_obj=self.currency_id),
                "amount_in_word": "(* " + self.check_amount_in_words.upper() + " *)",  # noqa
            }
        )
        return pages
