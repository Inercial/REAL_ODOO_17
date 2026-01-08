# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class StockRequestOrder(models.Model):
    _inherit = "stock.request.order"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("stock.request.order")
            group = self.env["procurement.group"].create(
                {
                    "name": vals["name"],
                }
            )
            vals["procurement_group_id"] = group.id
            if vals.get("stock_request_ids"):
                for line in vals["stock_request_ids"]:
                    line[2]["procurement_group_id"] = group.id
        return super().create(vals_list)
