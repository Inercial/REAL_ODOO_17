# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError


class MrpProductionChangeDateWizard(models.TransientModel):
    _name = "mrp.production.change.date.wizard"
    _description = "Wizard to allow to change date to production and related account move."

    date = fields.Datetime(required=True)

    def change_date(self):
        self.ensure_one()
        if self.date.date() > fields.Date.context_today(self):
            raise UserError(_("You cannot define a date in the future."))
        productions = self.env["mrp.production"].browse(self._context.get("active_ids"))
        states = all(state == "done" for state in productions.mapped("state"))
        if not states:
            raise UserError(_("All the productions must be in state 'Done'"))
        scraps = self.env["stock.scrap"].search(
            [
                ("production_id", "in", productions.ids),
            ]
        )
        moves = productions.mapped("move_raw_ids")
        moves |= productions.mapped("move_finished_ids")
        moves |= productions.mapped("move_byproduct_ids")
        moves |= scraps.mapped("move_ids")
        svls = moves.mapped("stock_valuation_layer_ids")
        account_moves = svls.mapped("account_move_id")
        date_tz = fields.Datetime.context_timestamp(self, self.date)
        date_str = fields.Datetime.to_string(date_tz)
        productions.write(
            {
                "date_finished": date_str,
            }
        )
        moves.write(
            {
                "date": date_str,
            }
        )
        moves.mapped("move_line_ids").write(
            {
                "date": date_str,
            }
        )
        # Use of SQL as Odoo don't allow to change create_date field.
        self.env.cr.execute(
            """
            UPDATE stock_valuation_layer
            SET create_date = %s
            WHERE id IN %s
            """,
            (fields.Datetime.to_string(self.date), tuple(svls.ids)),
        )
        account_moves.button_draft()
        account_moves.write(
            {
                "name": "/",
                "date": date_str,
            }
        )
        for move in account_moves:
            move.action_post()
