# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Account Move Reversal",
    "summary": "Module that install Account Move Reversal",
    "version": "17.0.1.0.1",
    "category": "Invoice",
    "author": "Jarsa",
    "website": "https://www.jarsa.com",
    "license": "LGPL-3",
    "depends": [
        "l10n_mx_edi_advance",
        "stock",
    ],
    "data": [
        "views/account_move_view.xml",
        "wizard/account_move_reversal_view.xml",
    ],
}
