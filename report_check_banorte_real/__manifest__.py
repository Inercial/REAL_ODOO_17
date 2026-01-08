# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Report Check for Banorte",
    "summary": "Check format in XLSX for Banorte",
    "version": "17.0.1.0.1",
    "category": "Report",
    "author": "Jarsa",
    "website": "https://www.jarsa.com",
    "license": "LGPL-3",
    "depends": [
        "l10n_mx_check_printing",
        "report_xlsx",
    ],
    "data": [
        "reports/banorte_check_report.xml",
    ],
    "external_dependencies": {
        "python": [
            "num2words",
        ],
    },
    "installable": True,
}
