# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from datetime import timedelta

from odoo import models
from odoo.fields import Datetime


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_mo_vals(
        self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values, bom
    ):
        res = super()._prepare_mo_vals(
            product_id, product_qty, product_uom, location_id, name, origin, company_id, values, bom
        )
        # date_start and date_finished must equal the current datetime plus one day
        res["date_start"] = Datetime.now() + timedelta(days=1)
        res["date_finished"] = res["date_start"]
        if res.get("bom_id"):
            bom = self.env["mrp.bom"].browse(res.get("bom_id"))
            if bom.picking_type_id:
                res["picking_type_id"] = bom.picking_type_id.id
        return res
