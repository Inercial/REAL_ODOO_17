# Copyright 2022, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
# pylint: disable=too-complex
import base64
import datetime
import re

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    state_txt = fields.Boolean(default=False)
    create_payment_file = fields.Boolean(related="payment_method_id.generate_payment_file", store=True)
    expiration_date = fields.Date()
    ref_1 = fields.Char(size=40)
    ref_2 = fields.Char(size=40)

    def action_post(self):
        if self.payment_method_id.code == "banorte_credit_transfer" and not self.partner_bank_id:
            raise UserError(_("You need to select a partner bank account"))

        return super().action_post()

    @api.model
    def _get_method_codes_using_bank_account(self):
        res = super()._get_method_codes_using_bank_account()
        res.append("banorte_credit_transfer")
        return res

    def open2generated(self):
        self.ensure_one()
        payment_file_str, filename = self.generate_payment_file()
        action = {}
        if payment_file_str and filename:
            attachment = self.env["ir.attachment"].create(
                {
                    "res_model": "account.payment",
                    "res_id": self.id,
                    "name": filename,
                    "datas": base64.b64encode(payment_file_str),
                }
            )
            simplified_form_view = self.env.ref("account_payment_order.view_attachment_simplified_form")
            action = {
                "name": _("Payment File"),
                "view_mode": "form",
                "view_id": simplified_form_view.id,
                "res_model": "ir.attachment",
                "type": "ir.actions.act_window",
                "target": "current",
                "res_id": attachment.id,
            }
        self.write(
            {
                "state_txt": True,
            }
        )
        return action

    def generate_payment_file(self):
        self.ensure_one()

        if self.payment_method_id.generate_payment_file:
            payment_line = self._process_payment_lines()

            return (
                payment_line.encode("ascii"),
                self.payment_method_id.filename_prefix
                + "401903"
                + datetime.datetime.today().strftime("%y%m%d")
                + self.name[13:]
                + ".TXT",
            )

    def _process_payment_lines(self):
        """Method used to generate payment lines, this is based on layout
        located in data folder of this module.
        Each line will contain description of the field, type and the leght of
        a  field.
        """
        errors = []
        payment_line = ""
        partner = self.partner_id
        contact = self.create_uid.partner_id

        if self.payment_method_id.code == "banorte_credit_transfer":
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
            if not self.partner_bank_id.operation_type:
                errors.append(_("Operation type of supplier %(partner)s is not defined", partner=partner.name))
            else:
                payment_line += self.partner_bank_id.operation_type
            # Clave ID
            # El ID del proveedor debe previamente existir en el catálogo de
            # proveedores.
            # Alfanumerico 13 carácteres.
            if self.partner_bank_id.operation_type != "01" and not self.partner_bank_id.id_supplier:
                errors.append(_("ID Supplier for %(partner)s is not defined", partner=partner.name))
            elif self.partner_bank_id.operation_type == "01":
                payment_line += " " * 13
            else:
                payment_line += self._format_width_value(
                    value=self._format_characters(self.partner_bank_id.id_supplier), width=13
                )
            # Cuenta Origen
            # Numérico 20 dígitos.
            # si cuenta origen < 20 llenar con ceros a la izquierda
            # Obligatorio.
            if not self.journal_id.bank_account_id:
                errors.append(_("The journal %(journal)s has no bank account defined", journal=self.journal_id.name))
            else:
                payment_line += self._format_width_value(self.journal_id.bank_account_id.acc_number, 20, "0", True)
            # Cuenta / CLABE Destino
            # Obligatorio
            # Cuentas Banorte deben contener 20 dígitos.
            # si TdC Amex = 15 digitos y llenar con ceros a la izquierda hasta llegar a 20
            # si TdC Banorte = 16 digitos y llenar con ceros a la izquierda hasta llegar a 20
            if self.partner_bank_id.operation_type in ["09", "10", "11", "12"]:
                if self.partner_bank_id.operation_type == "12" and len(self.partner_bank_id.acc_number) != 15:
                    errors.append(_("The AMEX account number must be 15 digits long"))
                elif self.partner_bank_id.operation_type != "12" and len(self.partner_bank_id.acc_number) != 16:
                    errors.append(_("The bank account number must be 16 digits long"))
                else:
                    payment_line += self._format_width_value(self.partner_bank_id.acc_number, 20, "0", True)
            else:
                if len(self.partner_bank_id.acc_number) > 20:
                    errors.append(_("The bank account number must not exceed 20 digits"))
                else:
                    payment_line += self._format_width_value(self.partner_bank_id.acc_number, 20, "0", True)
            # Importe
            # Obligatorio (máximo 14 dígitos)
            # Sin punto decimal físico, los 2 útimos dígitos son los decimales; rellenar con ceros a la izquierda;
            payment_line += self._format_width_value(self._format_characters(str("%.2f" % self.amount)), 14, "0", True)
            # Referencia
            # Obligatorio
            # Numérico 10 carácteres.
            if self.partner_bank_id.operation_type == "01":
                payment_line += "\t"
            else:
                name = self.name.lstrip("BAF/")
                payment_line += self._format_width_value(str(re.sub("/|", "", name)), 10, "0", True)
            # Descripción
            # Obligatorio
            # Alfanumérico 30 carácteres
            reference = self.ref
            if self.partner_bank_id.supplier_reference:
                reference = self.partner_bank_id.supplier_reference
            if not reference:
                errors.append(_("A description for the payment must be provided"))
            else:
                payment_line += self._format_width_value(self._format_characters(reference), 30)
            # Moneda Origen 1 - PESOS (MXP)
            # Obligatorio
            if self.company_id.currency_id.name == "MXN":
                payment_line += "1"
            else:
                errors.append(_("The system only supports MXN payments"))
            # Moneda Destino PESOS (MXP); Siempre deberá ser la misma moneda que la origen.
            # Obligatorio
            if self.currency_id.name != self.company_id.currency_id.name:
                errors.append(_("The source and destination currency must be the same"))
            else:
                payment_line += "1"
            # RFC Ordenante
            # Obligatorio
            # 12 digitos de RFC persona moral o 13 digitos de RFC persona física
            # si no se tiene RFC, debe dejar en blanco los 13 caracteres
            if self.partner_bank_id.operation_type in ["04", "05"]:
                vat = self.company_id.vat
                if len(vat) == 13:
                    payment_line += vat
                else:
                    if len(vat) == 12:
                        payment_line += vat + " "
            else:
                payment_line += " " * 13
            # IVA (Se ignora por requerimiento del cliente.)
            # 14 caracteres pero se llena con ceros los caracteres
            payment_line += "0" * 14
            # e-mail beneficiario
            payment_line += " " * 39
            # Fecha de Aplicación
            # Obligatorio
            # Formato DDMMAAAA
            # 8 caracteres
            date = self.date + datetime.timedelta(days=1)
            if self.partner_bank_id.operation_type == "05":
                payment_line += date.strftime("%d%m%Y")
            else:
                payment_line += "0" * 8
            # Instrucción de pago
            # Obligatorio
            if self.partner_bank_id.operation_type == "04":
                payment_line += (
                    self._format_width_value(self._format_characters(self.partner_id.name), 70, " ", False) + "\n"
                )
            elif self.partner_bank_id.operation_type == "05":
                payment_line += self._format_width_value("(no valida 3ros)", 70, " ", False) + "\n"
            else:
                payment_line += " " * 70 + "\n"
        else:
            # Pago de Servicios
            # Número de Facturador
            # 6 caracteres, rellenar con ceros a la izquierda
            # Obligatorio
            if not partner.banorte_biller_id:
                errors.append(_("The partner %(partner)s has no Banorte biller ID defined", partner=partner.name))
            else:
                payment_line += self._format_width_value(
                    self._format_characters(partner.banorte_biller_id), 6, "0", True
                )
            # Forma de Pago
            # 2 caracteres, Cargo a cuenta = 04 (pesos), 14 (Dólares)
            # Obligatorio
            if self.company_id.currency_id.name == "MXN":
                payment_line += "04"
            else:
                payment_line += "14"
            # Monto a Pagar
            # 15 caracteres, rellenar con ceros a la izquierda
            # Sin punto decimal físico, los 2 últimos dígitos son los decimales
            # Obligatorio
            payment_line += self._format_width_value(self._format_characters(str("%.2f" % self.amount)), 15, "0", True)
            # Cuenta Cargo
            # 20 caracteres, rellenar con ceros a la izquierda
            # Obligatorio
            if not self.journal_id.bank_account_id:
                errors.append(_("The journal %(journal)s has no bank account defined", journal=self.journal_id.name))
            else:
                payment_line += self._format_width_value(self.journal_id.bank_account_id.acc_number, 20, "0", True)
            # Cuenta Abono
            # 20 caraceres, rellenar con ceros a la izquierda
            payment_line += "0" * 20
            # Referencia 1
            # 40 caracteres, rellenar con espacios a la derecha
            # Obligatorio
            if not self.ref_1:
                errors.append(_("The payment needs a reference of 40 characters maximum"))
            else:
                payment_line += self._format_width_value(self._format_characters(self.ref_1), 40, " ", False)
            # Fecha de Vencimiento
            # 8 caracteres, rellenar con ceros si no se tiene el dato
            if self.expiration_date:
                payment_line += self.expiration_date.strftime("%d%m%Y")
            else:
                payment_line += "0" * 8
            # Correo Electrónico para Notificación
            # 40 caracteres, rellenar con espacios a la derecha
            # Obligatorio
            if not contact.email or not self.is_valid_email(contact.email) or len(contact.email) > 40:
                errors.append(
                    _("The contact %(contact)s needs a valid email account of 40 chars maximum", contact=contact.name)
                )
            else:
                payment_line += self._format_width_value(contact.email, 40, " ", False)
            # Referencia 2
            # 40 caracteres, rellenar con espacios a la derecha
            if self.ref_2:
                payment_line += self._format_width_value(self.ref_2, 40, " ", False)
            else:
                payment_line += " " * 40
            # Referencia 3
            # 40 caracteres, rellenar con espacios a la derecha
            payment_line += " " * 40
            # Referencia 4
            # 40 caracteres, rellenar con espacios a la derecha
            payment_line += " " * 40
            # Referencia 5
            # 40 caracteres, rellenar con espacios a la derecha
            payment_line += " " * 40
            # Referencia 6
            # 40 caracteres, rellenar con espacios a la derecha
            payment_line += " " * 40 + "\n"

        if errors:
            raise UserError(_("You have the following errors: \n%(errors)s", errors="\n".join(errors)))
        return payment_line

    def is_valid_email(self, email):
        return re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email)

    def _format_width_value(self, value, width, fillchar=" ", rjust=False):
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
