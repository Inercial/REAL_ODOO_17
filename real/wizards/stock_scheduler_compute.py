from odoo import models


class StockSchedulerCompute(models.TransientModel):
    _inherit = "stock.scheduler.compute"

    def procure_calculation(self):
        self.env["mrp.request"].search([("state", "=", "to_approve")]).unlink()
        finished = self.env["mrp.request"].search(
            [
                ("state", "=", "approved"),
                ("location_dest_id", "in", [19, 9]),
            ]
        )
        if finished:
            finished.button_done()
        return super().procure_calculation()
