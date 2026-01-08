# Copyright 2021, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from num2words import num2words

from odoo import models, tools


class ResCurrency(models.Model):
    _inherit = "res.currency"

    def amount_to_text(self, amount):
        self.ensure_one()

        def _num2words(number, lang):
            try:
                return num2words(number, lang=lang).title()
            except NotImplementedError:
                return num2words(number, lang="en").title()

        formatted = "%.{}f".format(self.decimal_places) % amount
        parts = formatted.partition(".")
        integer_value = int(parts[0])
        fractional_value = int(parts[2] or 0)

        lang = tools.get_lang(self.env)
        amount_words = tools.ustr("{amt_value} {amt_word}").format(
            amt_value=_num2words(integer_value, lang=lang.iso_code),
            amt_word=self.currency_unit_label,
        )
        amount_words += " %s/100 M.N." % str(fractional_value).zfill(2)
        return amount_words
