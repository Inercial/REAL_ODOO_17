
from odoo import fields, models


class MrpProductionRequestCreateMo(models.TransientModel):
    _inherit = "mrp.request.create.mo"


    def _prepare_product_line(self, pl):
        sup = super()._prepare_product_line(pl)
        sup["required_qty"] = self.order_qty * pl[0].product_qty
        return sup


class MrpProductionRequestCreateMoLine(models.TransientModel):
    _inherit = "mrp.request.create.mo.line"


    required_qty = fields.Float()

    def _compute_bottle_neck_factor(self):
        for rec in self:
            rec.bottle_neck_factor = 0 if rec.product_qty == 0 else super()._compute_bottle_neck_factor()
