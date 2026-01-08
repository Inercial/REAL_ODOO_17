# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Report Account Move Payment Receipt Real",
    "summary": "Modify report to adapt real requirements",
    "version": "17.0.1.0.1",
    "category": "Accounting",
    "author": "Jarsa",
    "website": "https://www.jarsa.com",
    "license": "LGPL-3",
    "depends": [
        "account",
    ],
    "data": [
        "views/account_report.xml",
        "reports/report_account_move_payment_receipt.xml",
    ],
    "installable": True,
}
