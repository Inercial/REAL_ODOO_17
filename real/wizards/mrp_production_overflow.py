# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MrpProductionBackorder(models.TransientModel):
    _name = "mrp.production.overflow"
    _description = "Mrp Production Overflow"

    mrp_production_ids = fields.Many2many("mrp.production")

    # Método que se encarga de igualar la cantidad a producir con la cantidad programada como lo hacía originalmente.
    # Si esto no se hace se cicla el código, porque vuelve a validar si las cantidades siguen siendo diferentes.
    def action_overflow(self):
        ctx = dict(self.env.context)
        ctx.pop("default_mrp_production_ids", None)
        self.mrp_production_ids.qty_of_block = True
        return self.mrp_production_ids.with_context(ctx, skip_backorder=True).button_mark_done()
