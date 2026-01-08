# Copyright 2022, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import pytz

from odoo import _, fields, models
from odoo.exceptions import UserError


class WizardReportMrpRequest(models.TransientModel):
    _name = "wizard.report.mrp.request"
    _description = "Wizard to view report of MRP Request"

    date_to_foreing = fields.Datetime(string="Foreing", required=True, default=fields.Date.context_today)
    date_to = fields.Datetime(string="Local", required=True, default=fields.Date.context_today)

    # pylint: disable=no-search-all
    def confirm_report(self):
        # location_id = 8 Stock Location
        # picking_type_id = 3 Preparacion
        self.env["report.stock.quant.real"].search([]).unlink()
        date_to_foreing = self._get_localzone_convert(self.date_to_foreing)
        date_to = self._get_localzone_convert(self.date_to)

        self._cr.execute(
            """
            SELECT
                sm.product_id AS id,
                sm.product_id AS product_id,
                (SELECT
                    SUM(sm2.product_qty)
                    FROM stock_move AS sm2
                    INNER JOIN stock_picking AS sp ON sp.id = sm2.picking_id
                    WHERE
                    sm2.location_id = 8 AND
                    sm2.picking_type_id = 3 AND
                    sm2.state IN ('partially_available','confirmed') AND
                    sm2.date <= %(date_to_foreing)s AND
                    sm2.client_location = 'foreigner' AND
                    sp.state='assigned' AND
                    sm2.product_id = sm.product_id
                ) AS product_uom_qty_foreign,
                (SELECT
                    SUM(sml.product_qty)
                    FROM stock_move AS sm2
                    INNER JOIN stock_move_line AS sml ON sml.picking_id = sm2.picking_id AND
                    sml.product_id = sm2.product_id
                    WHERE
                    sm2.location_id = 8 AND
                    sm2.picking_type_id = 3 AND
                    sm2.state NOT IN ('draft', 'cancel', 'done') AND
                    sm2.date <= %(date_to_foreing)s AND
                    sm2.client_location = 'foreigner' AND
                    sm2.product_id = sm.product_id AND
                    sml.state != 'assigned'
                ) AS reserved_availability_foreign,
                (SELECT
                    SUM(sm2.product_qty)
                    FROM stock_move AS sm2
                    INNER JOIN stock_picking AS sp ON sp.id = sm2.picking_id
                    WHERE
                    sm2.location_id = 8 AND
                    sm2.picking_type_id = 3 AND
                    sm2.state IN ('partially_available','confirmed') AND
                    sm2.date <= %(date_to)s AND
                    sm2.client_location = 'local' AND
                    sp.state='assigned' AND
                    sm2.product_id = sm.product_id
                ) AS product_uom_qty_local,
                (SELECT
                    SUM(sml.product_qty)
                    FROM stock_move AS sm2
                    INNER JOIN stock_move_line AS sml ON sml.picking_id = sm2.picking_id AND
                    sml.product_id = sm2.product_id
                    WHERE
                    sm2.location_id = 8 AND
                    sm2.picking_type_id = 3 AND
                    sm2.state NOT IN ('draft', 'cancel', 'done') AND
                    sm2.date <= %(date_to)s AND
                    sm2.client_location = 'local' AND
                    sm2.product_id = sm.product_id AND
                    sml.state != 'assigned'
                ) AS reserved_availability_local,
                AVG(swo.product_max_qty) - (AVG(sq.quantity)- AVG(sq.reserved_quantity)) AS available_space,
                AVG(bom.product_qty) AS batch_size
            FROM stock_move AS sm
            LEFT JOIN stock_quant AS sq ON sq.product_id = sm.product_id AND sq.location_id = 8
            LEFT JOIN stock_warehouse_orderpoint AS swo ON swo.product_id = sm.product_id AND swo.location_id = 8
            LEFT JOIN product_product AS pp ON pp.id = sm.product_id
            LEFT JOIN mrp_bom AS bom ON bom.product_tmpl_id = pp.product_tmpl_id
            WHERE
                sm.location_id = 8 AND
                sm.picking_type_id = 3 AND
                sm.state NOT IN ('draft', 'cancel', 'done') AND
                sm.client_location in ('local','foreigner')
            GROUP BY sm.product_id
            """,
            {
                "date_to_foreing": date_to_foreing,
                "date_to": date_to,
            },
        )
        result = self._cr.dictfetchall()
        if not result:
            raise UserError(_("No records found"))

        self.env["report.stock.quant.real"].sudo().create(result)
        action = {
            "type": "ir.actions.act_window",
            "name": _("Report Sale "),
            "res_model": "report.stock.quant.real",
            "view_mode": "tree",
        }
        return action

    def _get_localzone_convert(self, date):
        time_zone = self.env.user.partner_id.tz
        if time_zone:
            date_to_convert = date
            local = pytz.timezone(time_zone)
            validation_time = pytz.utc.localize(date_to_convert)
            validation_time = validation_time.astimezone(local)
            date_convert = validation_time.strftime("%Y-%m-%d %H:%M:%S")
            return date_convert
        raise UserError(_("has no defined time zone"))
