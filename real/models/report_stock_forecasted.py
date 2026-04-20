from odoo import models
from odoo.tools.misc import format_datetime


class StockForecasted(models.AbstractModel):
    _inherit = 'stock.forecasted_product_product'


    def _prepare_report_line(self, quantity, move_out=None, move_in=None, replenishment_filled=True, product=False, reserved_move=False, in_transit=False, read=True):
        line = super()._prepare_report_line(quantity, move_out=move_out, move_in=move_in, replenishment_filled=replenishment_filled, product=product, reserved_move=reserved_move, in_transit=in_transit, read=read)
        if move_in:
            line.update({'receipt_date': format_datetime(self.env, move_in.date)})
        if move_out:
            line.update({'delivery_date': format_datetime(self.env, move_out.date)})
        return line
