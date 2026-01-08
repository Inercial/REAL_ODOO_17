# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountPaymentMethod(models.Model):
    _inherit = "account.payment.method"

    generate_payment_file = fields.Boolean(
        default=False,
        help="Activate this option if this payment method will generate a payment file to be uploaded to the bank.",
    )
    filename_prefix = fields.Char(size=2)
