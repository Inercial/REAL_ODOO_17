# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from odoo import _, fields, models


class ReportExoenseReportWiz(models.TransientModel):
    _name = "expense.report.real.wiz"
    _description = "Wizard to create expense reports "

    date_from = fields.Date(
        string="From",
        required=True,
        default=fields.Date.context_today,
    )
    date_to = fields.Date(
        string="To",
        required=True,
        default=fields.Date.context_today,
    )

    # pylint: disable=no-search-all
    def open_table(self):
        self.env["expense.report.real"].search([]).unlink()
        self._cr.execute(
            """
            SELECT
                aj.id as journal_id,
                aml.name,
                aml.date,
                aml.account_id,
                aml.debit,
                aml.credit,
                aml.balance,
                aml.ref
            FROM account_move_line AS aml
            LEFT JOIN account_journal AS aj ON aj.id = aml.journal_id
            LEFT JOIN account_account AS aa ON aa.id = aml.account_id
            WHERE aj.is_petty_cash = 'true'
            AND aml.date >= %s
            AND aml.date <= %s
            AND aa.account_type = 'asset_cash'
            GROUP BY aj.id,aml.id
            ORDER BY aj.name
            """,
            (
                self.date_from,
                self.date_to,
            ),
        )
        data = self._cr.dictfetchall()

        self.env["expense.report.real"].create(data)

        return {
            "type": "ir.actions.act_window",
            "view_mode": "pivot,tree",
            "name": _("Report expense"),
            "res_model": "expense.report.real",
        }
