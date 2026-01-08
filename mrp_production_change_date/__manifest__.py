# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "MRP Production Change Date",
    "summary": """
        Wizard to allow to change date to producction and related account move.
    """,
    "version": "17.0.1.0.1",
    "category": "MRP",
    "author": "Jarsa",
    "website": "https://www.jarsa.com",
    "license": "LGPL-3",
    "depends": [
        "stock_account",
        "mrp",
    ],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "wizards/mrp_production_change_date_wizard_view.xml",
    ],
    "installable": True,
}
