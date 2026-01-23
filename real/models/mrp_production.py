# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    equipment_id = fields.Many2one(
        "mrp.equipment",
        ondelete="restrict",
    )
    date_planned_start = fields.Datetime(copy=True)
    hide_dump_info = fields.Boolean(default=True)
    driver = fields.Many2one("mrp.dump.truck.driver")
    plate = fields.Many2one("mrp.license.plate")
    qty_of_block = fields.Boolean(default=False)

    def action_confirm(self):
        res = super().action_confirm()
        if self.picking_ids:
            self.picking_ids.move_ids_without_package.write(
                {
                    "equipment_id": self.equipment_id.id,
                }
            )
        return res

    def action_cancel(self):
        if not self.user_has_groups("real.res_groups_can_see_button_action_cancel_in_mrp_production"):
            raise UserError(_("Permission Error: You are not allowed to cancel a production order."))
        return super().action_cancel()

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if self.product_id.driver_commission:
            self.hide_dump_info = False
        else:
            self.hide_dump_info = True
            self.driver = False
            self.plate = False

    # Validación para que cuando el usuario intente agregar una cantidad mayor a 10 a la original, salte un wizard que
    # pregunta si esto es correcto.
    def pre_button_mark_done(self):
        sup = super().pre_button_mark_done()
        if ((self.qty_producing > (self.product_qty + 10)) or (self.qty_producing < (self.product_qty - 10))) and not self.qty_of_block:
            lines = []
            for order in self._get_quantity_produced_issues():
                lines.append((0, 0, {"mrp_production_id": order.id, "to_backorder": True}))
            ctx = self.env.context.copy()
            ctx.update({"default_mrp_production_ids": self.ids, "default_mrp_production_backorder_line_ids": lines})
            action = self.env["ir.actions.actions"]._for_xml_id("real.action_mrp_production_overflow")
            action["context"] = ctx
            return action
        return sup
