# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models


class ReportKardexReportWiz(models.TransientModel):
    _name = "report.kardex.report.wiz"
    _description = "Wizard to create kardex reports of stock moves"

    date_from = fields.Datetime(string="From", required=True, default=fields.Datetime.now)
    date_to = fields.Datetime(string="To", required=True, default=fields.Datetime.now)

    # pylint: disable=no-search-all
    def open_table(self):
        self.env["kardex.report.real"].search([]).unlink()
        query = """
SELECT
svl.id,
svl.id AS stock_valuation_layer_id,
svl.account_move_id,
spt.name ->> 'es_MX' AS name,
svl.product_id,
CASE WHEN svl.value > 0
THEN svl.value
ELSE 0 END AS incoming,
CASE WHEN svl.value < 0
THEN svl.value
ELSE 0 END AS outgoing,
svl.create_date AS date,
svl.accounting_date
FROM stock_valuation_layer AS svl
LEFT JOIN stock_picking_type AS spt ON spt.id = svl.picking_type_id
WHERE
svl.create_date >= %(date_from)s AND
svl.create_date <= %(date_to)s AND
spt.id IS NOT NULL

UNION

SELECT
svl.id,
svl.id AS stock_valuation_layer_id,
svl.account_move_id,
CASE WHEN (
    SELECT
    sm.name
    FROM stock_move AS sm
    WHERE svl.stock_move_id = sm.id
) IS NOT NULL THEN (
    SELECT
    CASE WHEN SUBSTRING(sm.name, 1, 4) LIKE '%%DES%%' THEN 'Desecho'
    ELSE 'Ajuste de Inventario'
    END
    FROM stock_move AS sm
    WHERE svl.stock_move_id = sm.id
) ELSE 'Recalculo de costo' END AS name,
svl.product_id,
CASE WHEN
svl.value > 0
THEN svl.value
ELSE 0 END AS incoming,
CASE WHEN
svl.value < 0
THEN svl.value
ELSE 0 END AS outgoing,
svl.create_date AS date,
svl.accounting_date
FROM stock_valuation_layer AS svl
WHERE
svl.create_date >= %(date_from)s AND
svl.create_date <= %(date_to)s AND
(svl.stock_move_id IS NULL OR (
    SELECT
    sm.picking_type_id
    FROM stock_move AS sm
    WHERE sm.id = svl.stock_move_id) IS NULL)
"""
        params = {
            "date_from": self.date_from,
            "date_to": self.date_to,
        }
        self.env.cr.execute(query, params)
        data = self._cr.dictfetchall()
        self.env["kardex.report.real"].create(data)
        action = {
            "type": "ir.actions.act_window",
            "view_mode": "pivot,tree",
            "name": _("Report Kardex"),
            "res_model": "kardex.report.real",
        }
        return action
