# Copyright 2021, Jarsa Sistemas
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from collections import defaultdict
from datetime import date, datetime

from odoo import _, fields, models
from odoo.exceptions import UserError


class GeneralLedgerAudit(models.Model):
    _name = "general.ledger.audit"

    rep_select = fields.Selection(
        [("Reporte FCR", "A-055"), ("Reporte FCR Complemento", "A-055-B")],
        string="Report",
        default="Reporte FCR",
    )

    date_start = fields.Date()
    date_end = fields.Date()

    def report_query(self, date_start, date_end, rep_select):
        self.env.cr.execute(
            """
SELECT
    code_name,
    group_name,
    TO_CHAR(DATE_TRUNC('month', date_month), 'Month') AS date_month,
    SUM(debit) AS sum_debit,
    SUM(credit) AS sum_credit,
    SUM(balance) AS sum_balance
FROM
    (
        SELECT
            account_move_line.id,
            CAST(SPLIT_PART(account.code, '.', 1) AS numeric) AS code_name,
            groups.name AS group_name,
            DATE_TRUNC('month', account_move_line.date) AS date_month,
            ROUND(account_move_line.debit * currency_table.rate, currency_table.precision) AS debit,
            ROUND(account_move_line.credit * currency_table.rate, currency_table.precision) AS credit,
            ROUND(account_move_line.balance * currency_table.rate, currency_table.precision) AS balance
        FROM
            account_move_line
            LEFT JOIN account_move am ON am.id = account_move_line.move_id
            LEFT JOIN (
                VALUES
                    (1, 1.0, 2)
            ) AS currency_table (company_id, rate, precision) ON currency_table.company_id = account_move_line.company_id
            LEFT JOIN res_company company ON company.id = account_move_line.company_id
            LEFT JOIN res_partner partner ON partner.id = account_move_line.partner_id
            LEFT JOIN account_account account ON account.id = account_move_line.account_id
            LEFT JOIN account_journal journal ON journal.id = account_move_line.journal_id
            LEFT JOIN account_full_reconcile full_rec ON full_rec.id = account_move_line.full_reconcile_id
            LEFT JOIN account_group groups ON groups.id = account.group_id
        WHERE
            (
                account_move_line.display_type NOT IN ('line_section', 'line_note')
                OR account_move_line.display_type IS NULL
            )
            AND (
                account_move_line.parent_state != 'cancel'
                OR account_move_line.parent_state IS NULL
            )
            AND account_move_line.company_id = 1
            AND account_move_line.date >= % s
            AND account_move_line.date <= % s
            AND account_move_line.parent_state = 'posted'
            AND (
                account_move_line.company_id IS NULL
                OR account_move_line.company_id IN (1)
            )
        ORDER BY
            EXTRACT(
                MONTH
                FROM
                    DATE_TRUNC('month', account_move_line.date)
            )
    ) general_ledger
GROUP BY
    date_month,
    code_name,
    group_name
ORDER BY
    code_name,
    EXTRACT(
        MONTH
        FROM
            DATE_TRUNC('month', date_month)
    )
                    """,
            (date_start, date_end),
        )

        return self.env.cr.fetchall()

    def action_print_report(self):
        if self.date_start > self.date_end:
            raise UserError(_("The start date cannot be greater than the end date."))

        data = {
            "data": self.read()[0],
            "date_start": self.date_start,
            "date_end": self.date_end,
            "rep_select": self.rep_select,
            "rep_select_label": self.rep_select_label,
            "query": self.report_query(
                self.date_start.strftime("%Y-%m-%d"), self.date_end.strftime("%Y-%m-%d"), self.rep_select
            ),
        }

        return self.env.ref("real_reports.action_general_ledger_audit_template").report_action(self, data=data)

    @property
    def rep_select_label(self):
        return dict(self._fields["rep_select"].selection).get(self.rep_select, "")


class GeneralLedgerAuditTemplate(models.AbstractModel):
    _name = "report.real_reports.general_ledger_audit_template"
    _description = "FCR template"

    # pylint: disable=no-search-all
    def _get_report_values(self, docids, data=None):
        query = data.get("query")

        meses = {
            "january": "Enero",
            "february": "Febrero",
            "march": "Marzo",
            "april": "Abril",
            "may": "Mayo",
            "june": "Junio",
            "july": "Julio",
            "august": "Agosto",
            "september": "Septiembre",
            "october": "Octubre",
            "november": "Noviembre",
            "december": "Diciembre",
        }

        for div in query:
            div[2] = meses.get(div[2].strip().lower(), "Mes no válido")

        div_dep = []
        for div in query:
            if div[0] not in div_dep:
                div_dep.append(div[0])

        sum_total1 = 0.0
        for amount in query:
            sum_total1 += amount[3]
        sum_total2 = 0.0
        for amount in query:
            sum_total2 += amount[4]
        sum_total3 = 0.0
        for amount in query:
            sum_total3 += amount[5]

        dep_group_dict = defaultdict(set)
        for item in query:
            dep_group_dict[item[0]].add(item[1])

        sorted_keys = sorted(dep_group_dict.keys(), key=lambda x: str(x) if x is not None else "")
        div_group = {key: sorted(dep_group_dict[key]) for key in sorted_keys}

        return {
            "docs": self.env["account.fcr.report"].search([]),
            "today": date.today().strftime("%d-%m-%Y"),
            "query": query,
            "title": "General Ledger Audit Report",
            "code": data.get("rep_select_label", ""),
            "div_dep": div_dep,
            "div_group": div_group,
            "sum_total1": sum_total1,
            "sum_total2": sum_total2,
            "sum_total3": sum_total3,
            "date_start": datetime.strptime(data.get("date_start"), "%Y-%m-%d").strftime("%d-%m-%Y"),
            "date_end": datetime.strptime(data.get("date_end"), "%Y-%m-%d").strftime("%d-%m-%Y"),
        }
