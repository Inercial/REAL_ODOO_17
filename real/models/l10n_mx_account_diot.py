# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
# pylint: disable=too-complex

from odoo import _, api, models


class MxReportPartnerLedger(models.AbstractModel):
    _inherit = "l10n_mx.account.diot"

    @api.model
    def _get_lines(self, options, line_id=None):
        lines = []
        if line_id:
            line_id = line_id.replace("partner_", "")
        grouped_partners = self._group_by_partner_id(options, line_id)
        # Aml go back to the beginning of the user chosen range but the
        # amount on the partner line should go back to either the beginning of
        # the fy or the beginning of times depending on the partner
        sorted_partners = sorted(grouped_partners, key=lambda p: p.name or "")
        unfold_all = self._context.get("print_mode") and not options.get("unfolded_lines")
        tag_16 = self.env.ref("l10n_mx.tag_diot_16")
        tag_non_cre = (
            self.env.ref("l10n_mx.tag_diot_16_non_cre", raise_if_not_found=False) or self.env["account.account.tag"]
        )
        tag_8 = self.env.ref("l10n_mx.tag_diot_8", raise_if_not_found=False) or self.env["account.account.tag"]
        tag_8_non_cre = (
            self.env.ref("l10n_mx.tag_diot_8_non_cre", raise_if_not_found=False) or self.env["account.account.tag"]
        )
        tag_imp = self.env.ref("l10n_mx.tag_diot_16_imp")
        tag_0 = self.env.ref("l10n_mx.tag_diot_0")
        tag_ret = self.env.ref("l10n_mx.tag_diot_ret")
        tag_exe = self.env.ref("l10n_mx.tag_diot_exento")
        rep_line_obj = self.env["account.tax.repartition.line"].with_context(active_test=False)

        purchase_tax_ids = (
            self.env["account.tax"].with_context(active_test=False).search([("type_tax_use", "=", "purchase")]).ids
        )
        diot_common_domain = [
            "|",
            ("invoice_tax_id", "in", purchase_tax_ids),
            ("refund_tax_id", "in", purchase_tax_ids),
        ]

        company = self.env.company.id
        tax16 = rep_line_obj.search(
            [("tag_ids", "in", tag_16.ids), ("company_id", "=", company)] + diot_common_domain
        ).mapped("tax_id")
        taxnoncre = self.env["account.tax"]
        if tag_non_cre:
            taxnoncre = rep_line_obj.search(
                [("tag_ids", "in", tag_non_cre.ids), ("company_id", "=", company)] + diot_common_domain
            ).mapped("tax_id")
        tax8 = self.env["account.tax"]
        if tag_8:
            tax8 = rep_line_obj.search(
                [("tag_ids", "in", tag_8.ids), ("company_id", "=", company)] + diot_common_domain
            ).mapped("tax_id")
        tax8_noncre = self.env["account.tax"]
        if tag_8_non_cre:
            tax8_noncre = rep_line_obj.search(
                [("tag_ids", "in", tag_8_non_cre.ids), ("company_id", "=", company)] + diot_common_domain
            ).mapped("tax_id")
        taximp = rep_line_obj.search(
            [("tag_ids", "in", tag_imp.ids), ("company_id", "=", company)] + diot_common_domain
        ).mapped("tax_id")
        tax0 = rep_line_obj.search(
            [("tag_ids", "in", tag_0.ids), ("company_id", "=", company)] + diot_common_domain
        ).mapped("tax_id")
        tax_ret = rep_line_obj.search(
            [("tag_ids", "in", tag_ret.ids), ("company_id", "=", company)] + diot_common_domain
        ).mapped("tax_id")
        tax_exe = rep_line_obj.search(
            [("tag_ids", "in", tag_exe.ids), ("company_id", "=", company)] + diot_common_domain
        ).mapped("tax_id")
        grouped_taxes = (
            self.env["account.tax"]
            .with_context(active_test=False)
            .search([("type_tax_use", "=", "purchase"), ("company_id", "=", company), ("amount_type", "=", "group")])
        )
        taxes_in_groups = self.env["account.tax"].with_context(active_test=False)
        if grouped_taxes:
            self.env.cr.execute(
                """
                SELECT child_tax
                FROM account_tax_filiation_rel
                WHERE parent_tax IN %s
                """,
                [tuple(grouped_taxes.ids)],
            )
            taxes_in_groups = taxes_in_groups.browse([x[0] for x in self.env.cr.fetchall()])
        for partner in sorted_partners:
            amls = grouped_partners[partner]["lines"]
            if not amls:
                continue
            if not partner:
                for line in amls:
                    lines.append(
                        {"id": str(line.id), "name": "", "columns": [{"name": ""}], "level": 1, "colspan": 10}
                    )
                continue
            p_columns = [
                partner.l10n_mx_type_of_third or "",
                partner.l10n_mx_type_of_operation or "",
                partner.vat or "",
                partner.country_id.code or "",
                self.str_format(partner.l10n_mx_nationality, True),
            ]
            partner_data = grouped_partners[partner]
            total_tax16 = total_taximp = total_tax8 = 0
            total_tax0 = total_taxnoncre = total_tax8_noncre = 0
            exempt = 0
            withh = 0
            for tax in tax16:
                if tax in taxes_in_groups:
                    diff = 16 - tax.amount
                    withh += diff * partner_data.get(tax.id, 0) / 100
                total_tax16 += partner_data.get(tax.id, 0)
            p_columns.append(total_tax16)
            for tax in taxnoncre.ids:
                total_taxnoncre += partner_data.get(tax, 0)
            p_columns.append(total_taxnoncre)
            for tax in tax8.ids:
                total_tax8 += partner_data.get(tax, 0)
            p_columns.append(total_tax8)
            for tax in tax8_noncre.ids:
                total_tax8_noncre += partner_data.get(tax, 0)
            p_columns.append(total_tax8_noncre)
            for tax in taximp.ids:
                total_taximp += partner_data.get(tax, 0)
            p_columns.append(total_taximp)
            total_tax0 += sum(partner_data.get(tax, 0) for tax in tax0.ids)
            p_columns.append(total_tax0)
            exempt += sum(partner_data.get(exem, 0) for exem in tax_exe.ids)
            p_columns.append(exempt)
            withh += sum(abs(partner_data.get(ret.id, 0) / (100 / ret.amount)) for ret in tax_ret)
            p_columns.append(withh)
            unfolded = "partner_" + str(partner.id) in options.get("unfolded_lines") or unfold_all
            lines.append(
                {
                    "id": "partner_" + str(partner.id),
                    "name": self.str_format(partner.name)[:45],
                    "columns": [{"name": v if index < 5 else int(round(v, 0))} for index, v in enumerate(p_columns)],
                    "level": 2,
                    "unfoldable": True,
                    "unfolded": unfolded,
                }
            )
            if not unfolded:
                continue
            progress = 0
            domain_lines = []
            amls = grouped_partners[partner]["lines"]
            too_many = False
            if len(amls) > 80 and not self._context.get("print_mode"):
                amls = amls[:80]
                too_many = True
            for line in amls:
                line_debit = line.debit
                line_credit = line.credit
                progress = progress + line_debit - line_credit
                name = line.display_name
                name = name[:32] + "..." if len(name) > 35 else name
                columns = ["", "", "", ""]
                columns.append("")
                total_tax16 = total_taximp = total_tax8 = 0
                total_tax0 = total_taxnoncre = total_tax8_noncre = 0
                exempt = 0
                withh = 0
                for tax in tax16.filtered(lambda t: t in line.tax_ids):
                    if tax in taxes_in_groups:
                        diff = 16 - tax.amount
                        withh += diff / 100 * (line.debit or line.credit * -1)
                    total_tax16 += line.debit or line.credit * -1
                columns.append(self.format_value(total_tax16))
                total_taxnoncre += sum(
                    line.debit or line.credit * -1 for tax in taxnoncre.ids if tax in line.tax_ids.ids
                )
                columns.append(self.format_value(total_taxnoncre))
                total_tax8 += sum(line.debit or line.credit * -1 for tax in tax8.ids if tax in line.tax_ids.ids)
                columns.append(self.format_value(total_tax8))
                total_tax8_noncre += sum(
                    line.debit or line.credit * -1 for tax in tax8_noncre.ids if tax in line.tax_ids.ids
                )
                columns.append(self.format_value(total_tax8_noncre))
                total_taximp += sum(line.debit or line.credit * -1 for tax in taximp.ids if tax in line.tax_ids.ids)
                columns.append(self.format_value(total_taximp))
                total_tax0 += sum(line.debit or line.credit * -1 for tax in tax0.ids if tax in line.tax_ids.ids)
                columns.append(self.format_value(total_tax0))
                exempt += sum(line.debit or line.credit * -1 for exem in tax_exe.ids if exem in line.tax_ids.ids)
                columns.append(self.format_value(exempt))
                withh += sum(
                    (line.debit or line.credit * -1) / (100 / ret.amount) * -1
                    for ret in tax_ret.filtered(lambda t: t in line.tax_ids)
                )
                columns.append(self.format_value(withh))
                if line.payment_id:
                    caret_type = "account.payment"
                else:
                    caret_type = "account.move"
                domain_lines.append(
                    {
                        "id": str(line.id),
                        "parent_id": "partner_" + str(partner.id),
                        "name": name,
                        "columns": [{"name": v} for v in columns],
                        "caret_options": caret_type,
                        "level": 1,
                    }
                )
            domain_lines.append(
                {
                    "id": "total_" + str(partner.id),
                    "parent_id": "partner_" + str(partner.id),
                    "class": "o_account_reports_domain_total",
                    "name": _("Total") + " " + partner.name,
                    "columns": [
                        {"name": v if index < 5 else self.format_value(v)} for index, v in enumerate(p_columns)
                    ],
                    "level": 1,
                }
            )
            if too_many:
                domain_lines.append(
                    {
                        "id": "too_many_" + str(partner.id),
                        "parent_id": "partner_" + str(partner.id),
                        "name": _("There are more than 80 items in this list, click here to see all of them"),
                        "colspan": 10,
                        "columns": [{}],
                        "level": 3,
                    }
                )
            lines += domain_lines
        return lines
