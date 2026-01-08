# Copyright 2022, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    client_location = fields.Selection(
        selection=[
            ("local", "Local"),
            ("foreigner", "Foreigner"),
        ],
    )
