# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError


class Lead(models.Model):
    _inherit = "crm.lead"

    def _compute_can_win_opportunities(self):
        for rec in self:
            rec.current_user_can_win_opportunities = self.env.user.has_group("real.res_groups_allow_win_opportunities")

    current_user_can_win_opportunities = fields.Boolean(compute="_compute_can_win_opportunities")

    def write(self, values):
        for rec in self:
            if values.get("stage_id"):
                if self.env.user.has_group("real.res_groups_can_change_lead_stages"):
                    continue
                if rec.stage_id.sequence > values.get("stage_id"):
                    raise UserError(_("You can't go back to a previous stage."))
                if rec.stage_id.is_won:
                    raise UserError(_("You cannot change the stage of an opportunity that is already won."))
                won_stages = self.env["crm.stage"].search([("is_won", "=", True)])
                can_win = self.env.user.has_group("real.res_groups_allow_win_opportunities")
                if not can_win and values.get("stage_id") in won_stages.ids:
                    raise UserError(_("You are not allowed to mark an opportunity as won."))
        return super().write(values)
