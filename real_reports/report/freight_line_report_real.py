# Copyright 2021, Jarsa Sistemas
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError


class FreightLineReport(models.Model):
    _name = "freight.line.report"
    _description = "Freight Line Report"

    date_start = fields.Date()
    date_end = fields.Date()

    def action_print_report(self):
        if self.date_start > self.date_end:
            raise UserError(_("The start date cannot be greater than the end date."))

        self.env.cr.execute(
            """
            SELECT
                rpui.name,
                SUM(
                    CASE
                        WHEN am.move_type = 'out_refund'
                        THEN ((aml.freight_cost * coalesce(pp.freight_weight,0)) * aml.quantity) * -1
                        ELSE (aml.freight_cost * coalesce(pp.freight_weight,0)) * aml.quantity END
                )
            FROM
                account_move_line AS aml
                LEFT JOIN account_move am ON am.id = aml.move_id
                LEFT JOIN account_account aa ON aa.id = aml.account_id
                LEFT JOIN res_users AS ruui ON ruui.id = am.invoice_user_id
                LEFT JOIN res_partner AS rpui ON rpui.id = ruui.partner_id
                LEFT JOIN product_product pp ON pp.id = aml.product_id
            WHERE
                am.state IN ('posted')
                AND am.move_type IN ('out_invoice','out_refund')
                AND aml.price_subtotal > 0
                AND aa.account_type IN ('income', 'income_other')
                AND aml.product_id NOT IN (671, 856)
                AND aml.account_id IN (32, 172, 171, 173, 441, 442, 174, 175, 176, 177)
                AND am.invoice_date BETWEEN %s AND %s
            GROUP BY
                rpui.name
            """,
            (self.date_start, self.date_end),
        )

        query = {"query": self.env.cr.fetchall(), "date_start": self.date_start, "date_end": self.date_end}
        return self.env.ref("real_reports.action_freight_line_report_template").report_action(self, data=query)


class TemplateFreightLine(models.AbstractModel):
    _name = "report.real_reports.freight_line_template"
    _description = "Freight Line Template"

    def _get_report_values(self, docids, data=None):
        total = 0

        for line in data.get("query"):
            if line[0] in ("REAL", "Claudia Lorena Garcia Rodriguez"):
                data.get("query").remove(line)

            line[1] = round(line[1])
            total += line[1]

        data.get("query").append(["TOTAL", total])
        return {"lines": data.get("query"), "date_start": data.get("date_start"), "date_end": data.get("date_end")}
