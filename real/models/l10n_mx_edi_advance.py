from odoo import fields, models


class L10nMxEdiAdvance(models.Model):
    _inherit = "l10n_mx_edi.advance"

    x_studio_notas = fields.Char(string="Notas")
