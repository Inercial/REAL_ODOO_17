# Copyright 2021, Jarsa Sistemas
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from collections import defaultdict
from datetime import date

from odoo import _, fields, models
from odoo.exceptions import UserError


class GeneralLedgerAudit(models.Model):
    _name = "general.ledger.audit"
    _description = "General Ledger Audit Report Wizard"

    date_start = fields.Date(string="Fecha Inicial", required=True)
    date_end = fields.Date(string="Fecha Final", required=True)

    def report_query(self, date_start, date_end):
        self.env.cr.execute(
            """
SELECT
    CONCAT(code_name, ' - ', account_name) AS code_full_name,
    group_raw_name,
    TO_CHAR(date_month, 'Month') AS month_name,
    SUM(debit) AS sum_debit,
    SUM(credit) AS sum_credit,
    SUM(balance) AS sum_balance
FROM (
    SELECT
        account_move_line.id,
        CAST(SPLIT_PART(account.code, '.', 3) AS numeric) AS code_name,
        groups.name ->> 'en_US' AS group_raw_name,
        account.name ->> 'en_US' AS account_name,
        DATE_TRUNC('month', account_move_line.date) AS date_month,
        ROUND(account_move_line.debit * currency_table.rate, currency_table.precision) AS debit,
        ROUND(account_move_line.credit * currency_table.rate, currency_table.precision) AS credit,
        ROUND(account_move_line.balance * currency_table.rate, currency_table.precision) AS balance
    FROM account_move_line
    LEFT JOIN account_move am ON am.id = account_move_line.move_id
    LEFT JOIN (VALUES (1, 1.0, 2)) AS currency_table (company_id, rate, precision)
        ON currency_table.company_id = account_move_line.company_id
    LEFT JOIN account_account account ON account.id = account_move_line.account_id
    LEFT JOIN account_group groups ON groups.id = account.group_id
    WHERE account_move_line.company_id = 1
        AND account_move_line.date >= %s
        AND account_move_line.date <= %s
        AND account_move_line.parent_state = 'posted'
) general_ledger
GROUP BY date_month, code_name, account_name, group_raw_name
ORDER BY code_name, date_month
        """,
            (date_start, date_end),
        )
        return [list(row) for row in self.env.cr.fetchall()]

    def _prepare_report_data(self):
        """Prepara los datos y soluciona el KeyError asegurando tipos de datos consistentes"""
        if self.date_start > self.date_end:
            raise UserError(_("The start date cannot be greater than the end date."))

        query = self.report_query(self.date_start, self.date_end)

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

        div_dep = []
        dep_group_dict = defaultdict(set)
        sum_total1 = sum_total2 = sum_total3 = 0.0

        for line in query:
            dep_id = str(line[0])
            line[0] = dep_id
            line[2] = meses.get(line[2].strip().lower(), line[2])

            if dep_id not in div_dep:
                div_dep.append(dep_id)

            dep_group_dict[dep_id].add(line[1])

            sum_total1 += line[3]
            sum_total2 += line[4]
            sum_total3 += line[5]

        div_group = {k: sorted(list(v)) for k, v in dep_group_dict.items()}

        return {
            "today": date.today().strftime("%d-%m-%Y"),
            "query": query,
            "title": "General Ledger Audit Report",
            "div_dep": div_dep,
            "div_group": div_group,
            "sum_total1": sum_total1,
            "sum_total2": sum_total2,
            "sum_total3": sum_total3,
            "date_start": self.date_start.strftime("%d-%m-%Y"),
            "date_end": self.date_end.strftime("%d-%m-%Y"),
        }

    def action_print_report(self):
        data = self._prepare_report_data()
        return self.env.ref("real_reports.action_general_ledger_audit_template").report_action(self, data=data)

    def action_print_excel(self):
        data = self._prepare_report_data()
        return self.env.ref("real_reports.action_report_general_ledger_xlsx").report_action(
            self, data={"query_data": data}
        )


class GeneralLedgerAuditTemplate(models.AbstractModel):
    _name = "report.real_reports.general_ledger_audit_template"
    _description = "Generates PDF values"

    def _get_report_values(self, docids, data=None):
        return data


class GeneralLedgerXlsx(models.AbstractModel):
    _name = "report.real_reports.general_ledger_audit_xlsx"
    _description = "General Ledger Audit Report XLSX"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, records):
        report_data = data.get("query_data")
        sheet = workbook.add_worksheet("Auditoría")

        title_fmt = workbook.add_format({"bold": True, "font_size": 16})
        header_fmt = workbook.add_format({"bold": True, "bg_color": "#D3D3D3", "border": 1, "align": "center"})
        money_fmt = workbook.add_format({"num_format": "$#,##0.00", "border": 1})
        text_fmt = workbook.add_format({"border": 1})
        total_fmt = workbook.add_format({"bold": True, "num_format": "$#,##0.00", "top": 2})

        sheet.write(0, 0, report_data["title"], title_fmt)
        sheet.write(2, 0, f"Fecha impresión: {report_data['today']}")
        sheet.write(3, 0, f"Fecha inicial: {report_data['date_start']}")
        sheet.write(4, 0, f"Fecha final: {report_data['date_end']}")

        row = 6
        for dep in report_data["div_dep"]:
            sheet.write(row, 0, f"GRUPO DE CUENTA: {dep}", workbook.add_format({"bold": True, "font_size": 12}))
            row += 1

            headers = ["NOMBRE", "MES", "DEBE", "HABER", "SALDO"]
            for col, header in enumerate(headers):
                sheet.write(row, col, header, header_fmt)
            row += 1

            grupos = report_data["div_group"].get(dep, [])
            for group in grupos:
                for line in report_data["query"]:
                    if str(line[0]) == str(dep) and str(line[1]) == str(group):
                        sheet.write(row, 0, line[1], text_fmt)
                        sheet.write(row, 1, line[2], text_fmt)
                        sheet.write(row, 2, line[3], money_fmt)
                        sheet.write(row, 3, line[4], money_fmt)
                        sheet.write(row, 4, line[5], money_fmt)
                        row += 1
            row += 1

        row += 1
        sheet.write(row, 3, "TOTAL DEBE:", total_fmt)
        sheet.write(row, 4, report_data["sum_total1"], total_fmt)
        row += 1
        sheet.write(row, 3, "TOTAL HABER:", total_fmt)
        sheet.write(row, 4, report_data["sum_total2"], total_fmt)
        row += 1
        sheet.write(row, 3, "TOTAL SALDO:", total_fmt)
        sheet.write(row, 4, report_data["sum_total3"], total_fmt)
