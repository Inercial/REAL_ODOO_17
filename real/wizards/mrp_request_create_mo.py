# Copyright 2017-19 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MrpProductionRequestCreateMo(models.TransientModel):
    _inherit = "mrp.request.create.mo"

    equipment_id = fields.Many2one(
        comodel_name="mrp.equipment",
    )
    order_qty = fields.Integer(string="No. of Orders")
    alternative_bom_id = fields.Many2one(
        comodel_name="mrp.bom",
        string="Bill of Materials",
    )
    product_id = fields.Many2one(related="mrp_request_id.product_id")
    product_tmpl_id = fields.Many2one(related="mrp_request_id.product_tmpl_id")

    @api.constrains("order_qty")
    def _check_order_qty(self):
        for rec in self:
            if rec.order_qty < 0:
                raise ValidationError(_("The order quantity cannot be negative."))

    def _prepare_product_line(self, product_line):
        vals = super()._prepare_product_line(product_line)
        vals["required_qty"] = self.order_qty * product_line[0].product_qty
        return vals

    def _prepare_manufacturing_order(self):
        res = super()._prepare_manufacturing_order()
        res.update(
            {
                "location_dest_id": 19,
                "equipment_id": self.equipment_id.id,
                "bom_id": self.alternative_bom_id.id,
            }
        )
        return res

    def create_mo(self):
        self.ensure_one()
        orders = self.env["mrp.production"]
        count = self.order_qty
        while count:
            vals = self._prepare_manufacturing_order()
            mo = self.env["mrp.production"].create(vals)
            mo.action_confirm()
            mo.action_assign()
            orders |= mo
            count -= 1
        # Open resulting MO:
        action = self.env.ref("mrp.mrp_production_action").read()[0]
        action.update(
            {
                "domain": [("id", "in", orders.ids)],
            }
        )
        return action

    def _prepare_lines(self):
        """Get the components (product_lines) needed for manufacturing the
        given a BoM.
        :return: boms_done, lines_done
        """
        bom_point = self.alternative_bom_id
        factor = self.mrp_request_id.product_uom_id._compute_quantity(self.pending_qty, bom_point.product_uom_id)
        return bom_point.explode(self.mrp_request_id.product_id, factor / bom_point.product_qty)

    @api.model
    def default_get(self, list_fields):
        rec = super().default_get(list_fields)
        active_ids = self._context.get("active_ids")
        active_model = self._context.get("active_model")
        request = self.env[active_model].browse(active_ids)
        rec.update(
            {
                "alternative_bom_id": request.bom_id,
                "mo_qty": request.bom_id.product_qty or 0.0,
            }
        )
        return rec

    def _get_mo_qty(self):
        for rec in self:
            rec.mo_qty = rec.alternative_bom_id.product_qty


class MrpProductionRequestCreateMoLine(models.TransientModel):
    _inherit = "mrp.request.create.mo.line"

    required_qty = fields.Float()

    def _compute_bottle_neck_factor(self):
        nonzero_qty_lines = self.filtered("product_qty")
        zero_qty_lines = self - nonzero_qty_lines

        for line in zero_qty_lines:
            line.bottle_neck_factor = 0.0

        if nonzero_qty_lines:
            super(
                MrpProductionRequestCreateMoLine,
                nonzero_qty_lines,
            )._compute_bottle_neck_factor()
