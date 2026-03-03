from odoo import api, models
from datetime import datetime

class PhysicalInventoryCount(models.TransientModel):
    _name = "physical.inventory.count"

class ReportPhysicalInventory(models.AbstractModel):
    _name = 'report.real_reports.report_physical_inventory_count'

    @api.model
    def _get_report_values(self, docids, data=None):
        self.env.cr.execute("""
SELECT
    trim(pt.name ->> 'en_US' || ' ' || COALESCE(pav.name ->> 'en_US', '')) AS product_name,
    trim(replace(split_part(pc.complete_name, '/', 1), 'PT ', '')) AS complete_name,
    COALESCE(sq_sum.total_qty, 0)::integer AS quantity
FROM
    product_product AS pp
    INNER JOIN product_template AS pt ON pt.id = pp.product_tmpl_id
    INNER JOIN product_category AS pc ON pc.id = pt.categ_id
    LEFT JOIN (
        SELECT product_id, SUM(quantity) AS total_qty
        FROM stock_quant
        WHERE location_id IN (8, 19, 11)
        GROUP BY product_id
    ) AS sq_sum ON sq_sum.product_id = pp.id
    LEFT JOIN product_variant_combination AS pvc ON pvc.product_product_id = pp.id
    LEFT JOIN product_template_attribute_value AS ptav ON ptav.id = pvc.product_template_attribute_value_id
    LEFT JOIN product_attribute_value AS pav ON pav.id = ptav.product_attribute_value_id
WHERE
    pt.type = 'product'
    AND pp.active = true
    AND (pc.complete_name ILIKE 'PT POLVOS /%' OR pc.complete_name ILIKE 'PT EMULSIONES /%')
ORDER BY
    pc.complete_name DESC
        """)
        return {
            'doc_ids': docids,
            'doc_model': 'physical.inventory.count',
            'docs': self.env.cr.dictfetchall(),
            'logo': self.env.company.logo,
            'print_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }