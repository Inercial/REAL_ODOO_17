# Copyright 2017-19 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


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
