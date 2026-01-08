# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
# pylint: disable=too-complex

import datetime

from odoo import _, models
from odoo.exceptions import UserError


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    def generate_payment_file(self):
        self.ensure_one()
        if self.payment_method_id.code != "banorte_credit_transfer":
            return super().generate_payment_file()
        payment_line = self._process_payment_lines()
        return (
            payment_line.encode("ascii"),
            "PP" + "401903" + datetime.datetime.today().strftime("%y%m%d") + self.name.lstrip("PAY0") + ".TXT",
        )

    def _process_payment_lines(self):
        """Method used to generate payment lines, this is based on layout
        located in data folder of this module.
        Each line will contain description of the field, type and the leght of
        a  field.
        """
        errors = []
        payment_line = ""
        for line in self.payment_ids:
            partner = line.partner_id
            # Operación
            # 01 - Propias
            # 02 - Terceros
            # 04 - SPEI
            # 05 - TEF
            # 09 - TdeC Empresariales Banorte
            # 10 - Pago de TdC Banorte
            # 11 - Pago de TdC Otros Bancos
            # 12 - Pago de TdC AMEX
            # Numérico
            if not line.partner_bank_id.operation_type:
                errors.append(_("Operation type of supplier %(name)s is not defined", name=partner.name))
            payment_line += line.partner_bank_id.operation_type
            # Clave ID
            # El ID del proveedor debe previamente existir en el catálogo de
            # proveedores.
            # Alfanumerico 13 carácteres.
            if line.partner_bank_id.operation_type != "01" and not line.partner_bank_id.id_supplier:
                errors.append(_("ID Supplier for %(name)s is not defined", name=partner.name))
            elif line.partner_bank_id.operation_type == "01":
                payment_line += " " * 13
            else:
                payment_line += self._format_witdth_value(
                    value=self._format_characters(line.partner_bank_id.id_supplier), width=13
                )
            # Cuenta Origen
            # Numérico 20 dígitos.
            # si cuenta origen < 20 llenar con ceros a la izquierda
            # Obligatorio.
            payment_line += self._format_witdth_value(self.company_partner_bank_id.acc_number, 20, "0", True)
            # Cuenta / CLABE Destino
            # Obligatorio
            # Cuentas Banorte deben contener 20 dígitos.
            # si TdC Amex = 15 digitos y llenar con ceros a la izquierda hasta llegar a 20
            # si TdC Banorte = 16 digitos y llenar con ceros a la izquierda hasta llegar a 20
            if line.partner_bank_id.operation_type in ["01", "02", "04", "05", "09"]:
                payment_line += self._format_witdth_value(line.partner_bank_id.acc_number, 20, "0", True)
            elif line.partner_bank_id.operation_type in ["10", "11"]:
                if len(line.partner_bank_id.l10n_mx_edi_clabe) != 18:
                    errors.append(
                        _(
                            "The CLABE for %(partner)s must be 18 digits and is %(count)d",
                            partner=partner.name,
                            count=len(line.partner_bank_id.l10n_mx_edi_clabe),
                        )
                    )
                payment_line += self._format_witdth_value(line.partner_bank_id.l10n_mx_edi_clabe, 20, "0", True)
            else:
                if len(line.partner_bank_id.l10n_mx_edi_clabe) != 15:
                    errors.append(
                        _(
                            "The CLABE for %(partner)s must be 15 digits and is %(count)d",
                            partner=partner.name,
                            clabe=len(line.partner_bank_id.l10n_mx_edi_clabe),
                        )
                    )
                payment_line += self._format_witdth_value(line.partner_bank_id.l10n_mx_edi_clabe, 20, "0", True)
            # Importe
            # Obligatorio
            # Sin punto decimal físico, los 2 útimos dígitos son los decimales; rellenar con ceros a la izquierda;
            payment_line += self._format_witdth_value(
                self._format_characters(str("%.2f" % line.amount)), 14, "0", True
            )
            # Referencia
            # Obligatorio
            # Numérico 10 carácteres.
            if line.partner_bank_id.operation_type == "01":
                payment_line += "\t"
            else:
                payment_line += self._format_witdth_value(str(line.id), 10, "0", True)
            # Descripción
            # Obligatorio
            # Alfanumérico 30 carácteres
            payment_reference = line.payment_reference
            if line.partner_bank_id.supplier_reference:
                payment_reference = line.partner_bank_id.supplier_reference
            payment_line += self._format_witdth_value(self._format_characters(payment_reference), 30)
            # Moneda origen 1 - PESOS (MXP)
            # Obligatorio
            if self.company_id.currency_id.id == 33:
                payment_line += "1"
            # Moneda destino PESOS (MXP); Siempre deberá ser la misma moneda que la origen.
            # Obligatorio
            if line.payment_line_ids.currency_id.id == 33:
                payment_line += "1"
            # RFC Ordenante
            # Obligatorio
            # 12 digitos de RFC persona moral o 13 digitos de RFC persona física
            # si no se tiene RFC, debe dejar en blanco los 13 caracteres
            if line.partner_bank_id.operation_type in ["04", "05"]:
                vat = self.company_id.vat
                if len(vat) == 13:
                    payment_line += vat
                else:
                    if len(vat) == 12:
                        payment_line += vat + " "
            else:
                payment_line += " " * 13
            # IVA (Se ignora por requerimiento del cliente.)
            # 14 caracteres
            payment_line += "0" * 14
            # e-mail beneficiario
            payment_line += " " * 39
            # Fecha aplicación
            # Obligatorio
            # Formato DDMMAAAA
            # 8 caracteres
            if line.partner_bank_id.operation_type in ["01", "02", "04"] and not self.date_scheduled.strftime(
                "%d%m%Y"
            ):
                payment_line += datetime.datetime.today().strftime("%d%m%Y")
            elif line.partner_bank_id.operation_type in ["01", "02", "04"]:
                payment_line += self.date_scheduled.strftime("%d%m%Y")
            elif line.partner_bank_id.operation_type == "05":
                payment_line += self.date_scheduled.strftime("%d%m%Y")
            # Instrucción de pago
            # Obligatorio
            if line.partner_bank_id.operation_type == "04":
                payment_line += (
                    self._format_witdth_value(self._format_characters(line.partner_id.name), 70, " ", False) + "\n"
                )
            elif line.partner_bank_id.operation_type == "05":
                payment_line += self._format_witdth_value("(no valida 3ros)", 70, " ", False) + "\n"
            else:
                payment_line += " " * 70 + "\n"
        if errors:
            raise UserError(_("You have the following errors: \n%(errors)s", errors="\n".join(errors)))
        return payment_line

    def _format_witdth_value(self, value, width, fillchar=" ", rjust=False):
        if rjust:
            value = value.rjust(width, fillchar)
        else:
            value = value.ljust(width, fillchar)
        if len(value) > width:
            value = value[:width]
        return value

    def _format_characters(self, text):
        special_chars = "!\"#$%/()=?¡¨*[];:_'¿´+{},.-><°|@¬\\~`^ñÑ"
        for char in special_chars:
            text = text.replace(char, "")
        return text
