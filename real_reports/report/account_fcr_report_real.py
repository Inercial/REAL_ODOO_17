# Copyright 2021, Jarsa Sistemas
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from collections import defaultdict
from datetime import date, datetime

from odoo import _, fields, models
from odoo.exceptions import UserError


class AccountFcrReport(models.Model):
    _name = "account.fcr.report"
    _description = "FCR Report"

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
                grupo.x_grupo_padre,
                grupo.x_grupo,
                grupo.x_cuenta_analitica,
                grupo.x_cuenta_contable,
                SUM(x_monto)
            FROM (
                SELECT DISTINCT ON (aml.id)
                    aml.date AS x_fecha,
                    CASE
                        WHEN aa.account_type IN ('income') THEN 'Ingresos'
                        ELSE 'Gastos'
                    END AS x_grupo_tipo,
                    aapp.name ->> 'en_US' AS x_grupo_padre,
                    aap.name ->> 'en_US' AS x_grupo,
                    aaa.name ->> 'en_US' AS x_cuenta_analitica,
                    aa.name ->> 'en_US' AS x_cuenta_contable,
                    aaatg.account_account_tag_id AS x_account_account_tag_id,
                    aa.group_id AS x_group_id,
                    CASE
                        WHEN aml.credit > 0 THEN aml.credit
                        ELSE (aml.debit * -1)
                    END AS x_monto
                FROM
                    account_move_line aml
                    LEFT JOIN account_move am ON am.id = aml.move_id
                    LEFT JOIN account_account aa ON aa.id = aml.account_id
                    LEFT JOIN account_account_account_tag aaatg ON aaatg.account_account_id = aa.id
                    LEFT JOIN account_account_tag aatg ON aatg.id = aaatg.account_account_tag_id
                    -- 1. Expand the JSON into Key/Value pairs
                    CROSS JOIN LATERAL
                        jsonb_each_text(aml.analytic_distribution) AS dist(analytic_id_text, percentage)
                    -- 2. Split "104,226" (for example) into two separate rows: "104" and "226"
                    CROSS JOIN LATERAL
                        unnest(string_to_array(dist.analytic_id_text, ',')) AS split_ids(single_id)
                    -- 3. Join to get account details and FILTER out Plan 78
                    JOIN
                        account_analytic_account aaa ON aaa.id = split_ids.single_id::integer
                        AND aaa.plan_id <> 78
                    LEFT JOIN account_analytic_plan aap ON aap.id = aaa.plan_id
                    LEFT JOIN account_analytic_plan aapp ON aapp.id = aap.parent_id
                WHERE
                    am.state = 'posted'
                    AND aa.account_type IN (
                        'income', 'income_other',
                        'expense', 'expense_depreciation',
                        'expense_direct_cost'
                    )
                    AND aatg.name ->> 'en_US' = %(rep_select)s
                    AND aml.date >= %(date_start)s
                    AND aml.date <= %(date_end)s
                ORDER BY aml.id
            ) grupo
            GROUP BY
                grupo.x_cuenta_contable,
                grupo.x_cuenta_analitica,
                grupo.x_grupo,
                grupo.x_grupo_padre
            ORDER BY
                grupo.x_grupo_padre ASC,
                grupo.x_grupo ASC,
                grupo.x_cuenta_analitica ASC,
                grupo.x_cuenta_contable ASC
            """,
            {
                "rep_select": rep_select,
                "date_start": date_start,
                "date_end": date_end,
            },
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

        return self.env.ref("real_reports.action_account_fcr_template").report_action(self, data=data)

    @property
    def rep_select_label(self):
        return dict(self._fields["rep_select"].selection).get(self.rep_select, "")


class TemplateAccountFcr(models.AbstractModel):
    _name = "report.real_reports.account_fcr_template"
    _description = "FCR template"

    # pylint: disable=no-search-all
    def _get_report_values(self, docids, data=None):
        query = data.get("query")

        div_dep = []
        for div in query:
            if div[0] not in div_dep:
                div_dep.append(div[0])

        sum_total = 0.0
        for amount in query:
            sum_total += amount[4]

        dep_group_dict = defaultdict(set)
        for item in query:
            dep_group_dict[item[0]].add(item[1])

        sorted_keys = sorted(dep_group_dict.keys(), key=lambda x: str(x) if x is not None else "")
        div_group = {key: sorted(dep_group_dict[key]) for key in sorted_keys}

        return {
            "docs": self.env["account.fcr.report"].search([]),
            "today": date.today().strftime("%d-%m-%Y"),
            "query": query,
            "title": "ESTADO DE RESULTADOS",
            "code": data.get("rep_select_label", ""),
            "div_dep": div_dep,
            "div_group": div_group,
            "sum_total": sum_total,
            "date_start": datetime.strptime(data.get("date_start"), "%Y-%m-%d").strftime("%d-%m-%Y"),
            "date_end": datetime.strptime(data.get("date_end"), "%Y-%m-%d").strftime("%d-%m-%Y"),
        }
