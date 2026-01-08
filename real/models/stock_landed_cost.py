# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockLandedCostLines(models.Model):
    _inherit = "stock.landed.cost.lines"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("split_method") != "by_quantity":
                vals["split_method"] = "by_quantity"
        return super().create(vals_list)

    @api.onchange("product_id")
    def _onchange_product_id(self):
        self.split_method = "by_quantity"

    @api.constrains("split_method")
    def _validate_split_method(self):
        for rec in self:
            if rec.split_method != "by_quantity":
                raise ValidationError(_("You can not select a split method different of By Quantity"))
