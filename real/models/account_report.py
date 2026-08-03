from odoo import models, fields
import re
import io

class TrialBalanceCustomHandler(models.AbstractModel):
    _inherit = "account.trial.balance.report.handler"

    def _custom_options_initializer(self, report, options, previous_options=None):
        super()._custom_options_initializer(report, options, previous_options)
        if not options.get("hide_columns"):
            return

        if main_headers := options.get("column_headers", [[]])[0]:
            last_hdr = len(main_headers) - 1
            for i, header in enumerate(main_headers):
                header["colspan"] = 1 if i in (0, last_hdr) else 2

        cols = options.get("columns", [])
        comp = options.get("comparison", {})
        comp_periods = 0 if comp.get("filter") == "no_comparison" else comp.get("number_period", 0)
        total_cols = len(cols) - (comp_periods + 6)

        if total_cols > 0:
            for i, col in enumerate(cols):
                if i == 0 or i == total_cols:
                    col["name"] = "Saldo"
                elif 0 < i < total_cols:
                    col["name"] = "Débito" if i % 2 != 0 else "Crédito"
                else:
                    col["name"] = ""

    def _dynamic_lines_generator(self, report, options, all_column_groups_expression_totals, warnings=None):
        lines = super()._dynamic_lines_generator(report, options, all_column_groups_expression_totals, warnings)
        if options.get("hide_columns"):# and options.get("comparison").get("filter") == "no_comparison":
            for line_tuple in lines:
                line = line_tuple[1]
                if 'columns' in line and len(line['columns']) > 8:
                    line_len = len(line["columns"])
                    to_remove = {0, 1, line_len - 3, line_len - 2}
                    to_remove.update(range(5, line_len - 3, 3))
                    line["columns"] = [
                        col for i, col in enumerate(line["columns"])
                        if i not in to_remove
                    ]
        return lines


class AccountReport(models.Model):
    _inherit = "account.report"

    filter_hide_columns = fields.Boolean(
        string="Hide Columns",
        compute=lambda x: x._compute_report_option_filter("filter_hide_columns"), readonly=False, store=True, depends=["root_report_id", "section_main_report_ids"],
    )

    def _init_options_hide_columns(self, options, previous_options=None):
        if previous_options is None:
            previous_options = {}
        previous_section_source_id = previous_options.get("sections_source_id")
        if previous_options and (not previous_section_source_id or previous_section_source_id == options["sections_source_id"]):
            options["hide_columns"] = previous_options.get("hide_columns", True)
        else:
            options["hide_columns"] = True

    def export_to_pdf(self, options):
        if not options.get("hide_columns"):
            return super().export_to_pdf(options)
        self.ensure_one()
        action_report = self.env["ir.actions.report"]
        files_stream = []
        for (bodies, footer, is_landscape) in self._get_html_data_for_pdf_export(options):
            modified_bodies = []
            for body in bodies:
                body = re.sub(r'class="o_overflow_name"\s+colspan="3"', "class='o_overflow_name' colspan='1'", body, count=1)
                body = re.sub(r'class="o_overflow_name"\s+colspan="3"', "class='o_overflow_name' colspan='2'", body, count=1)
                body = re.sub(r'class="o_overflow_name"\s+colspan="3"', "class='o_overflow_name' colspan='1'", body, count=1)
                modified_bodies.append(body)
            files_stream.append(
                io.BytesIO(action_report._run_wkhtmltopdf(
                    modified_bodies,
                    footer=footer.decode() if isinstance(footer, bytes) else footer,
                    landscape=is_landscape or self._context.get("force_landscape_printing"),
                    specific_paperformat_args={
                        "data-report-margin-top": 10,
                        "data-report-header-spacing": 10,
                        "data-report-margin-bottom": 15,
                    }
                )
            ))
        if len(files_stream) > 1:
            result_stream = action_report._merge_pdfs(files_stream)
            result = result_stream.getvalue()
            result_stream.close()
            for file_stream in files_stream:
                file_stream.close()
        else:
            result = files_stream[0].read()

        return {
            "file_name": self.get_default_report_filename(options, "pdf"),
            "file_content": result,
            "file_type": "pdf",
        }
        
