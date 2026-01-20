# Copyright 2021, Jarsa Sistemas
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from datetime import date, datetime

from odoo import _, fields, models
from odoo.exceptions import UserError


class ReportCancelledInvoices(models.TransientModel):
    _name = "report.cancelled.invoices"

    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)

    def report_query(self):
        query = """
                    SELECT
                        am.name AS x_folio,
                        CASE
                            WHEN am.move_type = 'out_invoice' THEN 'F'
                            ELSE 'NC'
                        END AS x_tipo_doc,
                        TO_CHAR(am.invoice_date, 'DD/MM/YYYY') AS x_fecha_doc,
                        TO_CHAR(mc.fecha_cancelacion, 'DD/MM/YYYY') AS x_fecha_cancelacion,
                        rp.name AS x_cliente,
                        rpui.name AS x_vendedor,
                        SUM(
                            CASE
                                WHEN am.move_type = 'out_refund'
                                    THEN COALESCE(ABS(val.costo), 0) * -1
                                ELSE
                                    COALESCE(ABS(val.costo), 0)
                            END
                        ) AS x_costo_linea,
                        SUM(
                            CASE
                                WHEN am.move_type = 'out_refund'
                                    THEN ROUND(
                                        GREATEST(aml.price_subtotal, ABS(aml.credit), ABS(aml.debit)) * 1.16,
                                        2
                                    ) * -1
                                ELSE
                                    ROUND(
                                        GREATEST(aml.price_subtotal, ABS(aml.credit), ABS(aml.debit)) * 1.16,
                                        2
                                    )
                            END
                        ) AS x_precio_con_iva_linea,
                        SUM(
                            CASE
                                WHEN am.move_type = 'out_refund'
                                    THEN aml.tons_display * -1
                                ELSE
                                    aml.tons_display
                            END
                        ) AS x_tons
                    FROM account_move_line aml
                    JOIN account_move am ON am.id = aml.move_id
                    JOIN account_account aa ON aa.id = aml.account_id
                    LEFT JOIN res_partner rp ON rp.id = am.partner_id
                    LEFT JOIN res_users ru ON ru.id = am.invoice_user_id
                    LEFT JOIN res_partner rpui ON rpui.id = ru.partner_id
                    LEFT JOIN LATERAL (
                        SELECT
                            (mtv.create_date AT TIME ZONE 'utc' AT TIME ZONE 'america/mexico_city')::date AS fecha_cancelacion
                        FROM mail_tracking_value mtv
                        JOIN mail_message mm ON mm.id = mtv.mail_message_id
                        WHERE
                            mtv.old_value_char IN ('Borrador', 'Registrado')
                            AND mtv.new_value_char = 'Cancelado'
                            AND mm.res_id = am.id
                        ORDER BY mtv.create_date DESC
                        LIMIT 1
                    ) mc ON TRUE
                    LEFT JOIN LATERAL (
                        SELECT ROUND(svl.value, 2) AS costo
                        FROM stock_valuation_layer svl
                        JOIN stock_move sm ON sm.id = svl.stock_move_id
                        JOIN sale_order_line_invoice_rel solir ON solir.order_line_id = sm.sale_line_id
                        WHERE
                            solir.invoice_line_id = aml.id
                            AND svl.product_id = aml.product_id
                            AND sm.picking_type_id IN (2, 13)
                            AND ABS(svl.quantity) = ABS(aml.quantity)
                            AND (sm.location_id = 5 OR sm.location_dest_id = 5)
                        ORDER BY svl.create_date ASC
                        LIMIT 1
                    ) val ON TRUE
                    WHERE
                        am.state = 'cancel'
                        AND mc.fecha_cancelacion BETWEEN %s AND %s
                        AND am.move_type IN ('out_invoice', 'out_refund')
                        AND aml.price_subtotal > 0
                        AND aa.account_type IN ('income', 'income_other')
                        AND aml.product_id NOT IN (671, 856)
                        AND aml.account_id IN (32, 172, 171, 173, 441, 442, 174, 175, 176, 177)
                        AND am.name NOT IN ('/', 'F20012')
                        AND NOT (
                            date_trunc('month', am.invoice_date)
                            = date_trunc('month', mc.fecha_cancelacion)
                        )
                    GROUP BY
                        am.name,
                        am.move_type,
                        am.invoice_date,
                        mc.fecha_cancelacion,
                        rp.name,
                        rpui.name
                    ORDER BY rpui.name;
                """

        self.env.cr.execute(query, (self.date_start, self.date_end))
        return self.env.cr.fetchall()

    def action_print_report(self):
        if self.date_start > self.date_end:
            raise UserError(_("The start date cannot be greater than the end date."))

        data = {
            "date_start": self.date_start.strftime("%Y-%m-%d"),
            "date_end": self.date_end.strftime("%Y-%m-%d"),
            "query": self.report_query(),
        }

        return (
            self.env.ref("real_reports.action_report_cancelled_invoices_template")
            .with_context(landscape=True)
            .report_action(self, data=data)
        )


class ReportCancelledInvoicesTemplate(models.AbstractModel):
    _name = "report.real_reports.report_cancelled_invoices_template"
    _description = "Report cancelled invoices template"

    def _get_report_values(self, docids, data):
        query = data.get("query", [])

        sum_precio_con_iva_linea = sum(line[7] or 0 for line in query)
        sum_costo_linea = sum(line[6] or 0 for line in query)

        return {
            "docs": self.env["account.fcr.report"].search([]),
            "today": date.today().strftime("%d-%m-%Y"),
            "query": query,
            "date_start": datetime.strptime(data["date_start"], "%Y-%m-%d").strftime(
                "%d-%m-%Y"
            ),
            "date_end": datetime.strptime(data["date_end"], "%Y-%m-%d").strftime(
                "%d-%m-%Y"
            ),
            "sum_precio_con_iva_linea": round(sum_precio_con_iva_linea, 2),
            "sum_costo_linea": round(sum_costo_linea, 2),
        }
