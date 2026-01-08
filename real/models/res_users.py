# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    force_share = fields.Boolean()
    default_analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
    )

    @api.depends("groups_id")
    def _compute_share(self):
        user_group_id = self.env.ref("base.group_user").id
        internal_users = self.filtered_domain(
            [
                "|",
                ("groups_id", "in", [user_group_id]),
                ("force_share", "=", True),
            ]
        )
        internal_users.share = False
        (self - internal_users).share = True
