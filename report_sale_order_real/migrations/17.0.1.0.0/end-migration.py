import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, installed_version):
    """Update mail templates to use custom reports during migration"""

    templates = {
        "sale.mail_template_sale_confirmation": "report_sale_order_real.action_report_saleorder_order",
        "sale.email_template_edi_sale": "report_sale_order_real.action_report_saleorder_quotation",
        "sale.mail_template_sale_payment_executed": "report_sale_order_real.action_report_saleorder_quotation",
    }

    for template_xmlid, report_xmlid in templates.items():
        template = env.ref(template_xmlid, raise_if_not_found=False)
        report = env.ref(report_xmlid, raise_if_not_found=False)
        if template and report:
            template.write(
                {
                    "report_template_ids": [(6, 0, [report.id])],
                }
            )
            _logger.info("Changed %s to use %s", template_xmlid, report_xmlid)
        else:
            _logger.warning("Template %s or report %s not found", template_xmlid, report_xmlid)
