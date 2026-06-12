# account_payment_order_banorte — Account Payment Order Banorte

> **Version:** 17.0.1.0.1 | **License:** LGPL-3 | **Author:** Jarsa

<!-- ============================================================ -->
<!-- ENGLISH SECTION — Technical Reference                        -->
<!-- ============================================================ -->

## Overview

This module extends Odoo's payment infrastructure (`account.payment`, `account.payment.order`, `account.payment.method`, `res.partner.bank`, `res.partner`, and `account.journal`) to generate Banorte-compatible TXT payment layout files for outbound supplier payments. It supports multiple operation types (Own transfers, Third parties, SPEI, TEF, credit card payments) following Banorte's proprietary flat-file format. The module also enables importing Banorte bank statements in TXT format, automatically parsing fixed-width records to create reconcilable bank statement lines.

## Dependencies

### Odoo / OCA Modules

- `account_payment` — Base payment model (`account.payment`) required for outbound payment handling and method registration
- `account_payment_order` — Provides `account.payment.order` and `account.payment.line.create` wizard, which are the core batch payment objects extended by this module
- `l10n_mx` — Mexican localization base; provides currency (MXN) and company RFC (VAT) structures
- `l10n_mx_edi` — Mexican EDI localization; provides `l10n_mx_edi_clabe` field on `res.partner.bank` and `l10n_mx_edi_payment_method_id` on bank statement lines
- `account_statement_import_file` — Enables the TXT bank statement import mechanism via `_import_bank_statement` and `_get_bank_statements_available_import_formats`

### Python Libraries

- `re` — Used in `account_journal.py` and `account_payment.py` for RFC extraction and reference formatting via regular expressions
- `base64` — Used in `account_payment.py` to encode the generated TXT file as a binary attachment
- `datetime` — Used in `account_payment.py`, `account_payment_order.py`, and `account_journal.py` for date formatting in filenames and payment records

## Installation

1. Place the module in your addons path.
2. Update the module list: **Settings → Activate Developer Mode → Update Apps List**
3. Search for `account_payment_order_banorte` and click **Install**.
4. After installation, two payment methods are automatically created (`Banorte Credit Transfer to suppliers` and `Banorte Service Payment`) and one payment mode (`Banorte Transfer to Suppliers`) is created linked to the main company. Verify these records under **Accounting → Configuration → Payment Methods** and **Accounting → Configuration → Payment Modes**.

## Models Reference

### `account.payment.order` — Payment Order

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| *(All native fields inherited)* | — | — | No new fields added; behavior extended via methods only |

**Key methods:**
- `generate_payment_file()`: Overrides the OCA method to produce a Banorte-format TXT file when `payment_method_id.code == 'banorte_credit_transfer'`; returns the encoded file bytes and a filename with prefix `PP`, company code `401903`, date, and order name.
- `_process_payment_lines()`: Iterates over all payment lines in the order and builds a fixed-width ASCII record per line, including operation type, supplier ID, source account, destination account/CLABE, amount (no decimal point), reference, description, currency codes, RFC, IVA (zeroed), email (blank), scheduled date, and payment instruction. Raises `UserError` if validation errors accumulate.
- `_format_witdth_value(value, width, fillchar, rjust)`: Pads or truncates a string to the required fixed width, left- or right-justified.
- `_format_characters(text)`: Strips special characters that are not supported in the Banorte ASCII layout.

---

### `res.partner.bank` — Bank Account

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `id_supplier` | `Char(size=13)` | ID Supplier | Supplier ID that must exist in the Banorte supplier database; required for all operation types except Own (01) |
| `operation_type` | `Selection` | Operation Type | Banorte operation code: 01=Own, 02=Third parties, 04=SPEI, 05=TEF, 09=TdeC Empresariales Banorte, 10=Pago de TdC Banorte, 11=Pago de TdC Otros Bancos, 12=Pago de TdC AMEX |
| `supplier_reference` | `Char` | Supplier Reference | Fixed reference string to include in the payment description; if empty, invoice references are used instead |

**Key methods:**
- `_compute_display_name()`: Overrides display name computation for company-owned bank accounts to append `acc_holder_name` after the account number, improving readability in internal transfer dropdowns.

---

### `account.payment` — Payment

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `state_txt` | `Boolean` | *(hidden)* | Internal flag set to `True` once the TXT payment file has been generated; default `False` |
| `create_payment_file` | `Boolean` | *(hidden, related)* | Stored related field from `payment_method_id.generate_payment_file`; controls visibility of the "Generate Payment File" button |
| `expiration_date` | `Date` | Expiration Date | Optional expiration date for the payment; editable only in draft state |
| `ref_1` | `Char(size=40)` | Ref 1 | Auxiliary reference field 1; editable only in draft state |
| `ref_2` | `Char(size=40)` | Ref 2 | Auxiliary reference field 2; editable only in draft state |

**Key methods:**
- `_compute_available_partner_bank_ids()`: Extends native method so that internal transfers to journals without a bank account (e.g., cash) still display the company's internal bank accounts as selectable options.
- `action_post()`: Overrides posting to validate that a partner bank account is selected when the payment method is `banorte_credit_transfer`; raises `UserError` if missing.
- `_get_method_codes_using_bank_account()`: Registers `banorte_credit_transfer` as a payment method code that requires a bank account selection.
- `open2generated()`: Calls `generate_payment_file()`, creates an `ir.attachment` with the resulting TXT binary, and opens a simplified form view of the attachment; sets `state_txt = True`.
- `generate_payment_file()`: Delegates to `_process_payment_lines()` and returns the ASCII-encoded TXT bytes plus a filename composed of the method's `filename_prefix`, `401903`, today's date (YYMMDD), and the payment name suffix.
- `_process_payment_lines()`: Builds the Banorte fixed-width record for a single payment, applying the same field layout as in `account.payment.order` but scoped to one payment record. Validates operation type, supplier ID, source account, destination account, amount, reference, description, and currency.

---

### `account.payment.method` — Payment Method

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `generate_payment_file` | `Boolean` | Generate Payment File | When enabled, the payment method will generate a TXT file to be uploaded to the bank; default `False` |
| `filename_prefix` | `Char(size=2)` | Filename Prefix | Two-character prefix prepended to the generated TXT filename (e.g., `PP` for credit transfers, `PC` for service payments) |

---

### `res.partner` — Contact

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `banorte_biller_id` | `Char(size=6)` | Banorte Biller ID | Six-character Banorte biller identifier for the partner; used in service payment contexts |

---

### `account.journal` — Journal

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| *(No new fields added)* | — | — | Behavior extended via methods only |

**Key methods:**
- `_get_bank_statements_available_import_formats()`: Adds `"TXT"` to the list of importable bank statement formats.
- `_check_file_format(filename)`: Returns `True` if the filename ends with `.txt` (case-insensitive).
- `_search_partner(ref)`: Parses a transaction narration string using regex to extract an RFC value, then searches for a matching `res.partner` by VAT; returns partner ID or `False`.
- `_search_method(ref)`: Detects the string `"SPEI"` in the narration to identify the payment method; returns method ID `3` if found.
- `_import_bank_statement(attachments)`: Parses Banorte TXT bank statement files with fixed-width record types (`11` = account header, `22` = movement record, `23` = complementary concept). Constructs `account.bank.statement` records and their line items. Redirects to native handler for non-TXT files or multiple attachments.
- `process_date(date)`: Converts a 6-character date string in `YYMMDD` format to a Python `date` object.

---

### `account.payment.line.create` *(Wizard)* — Create Payment Lines

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `operation_type` | `Selection` | Operation Type | Filter lines by Banorte operation type: 01=Own, 02=Third parties, 04=SPEI, 05=TEF |

**Key methods:**
- `_prepare_move_line_domain()`: Extends the native domain to filter move lines by the selected `operation_type` on the partner's bank account when creating payment order lines.

---

## Security Groups

No custom security groups or `ir.model.access.csv` file is defined in this module. Access control relies on the native groups provided by `account_payment` and `account_payment_order`.

## Menus & Actions

This module does not register new top-level menus or actions. It extends existing views in:

- **Accounting → Customers / Vendors → Payments** — Adds "Generate Payment File" button, `Expiration Date`, `Ref 1`, `Ref 2` fields to the native payment form
- **Accounting → Configuration → Payment Methods** (via `account_payment_mode`) — Adds `Generate Payment File` checkbox and `Filename Prefix` field to the payment method form
- **Contacts → [Partner form] → Accounting tab → Bank Accounts section** — Adds `Banorte Biller ID` field
- **Bank Account form** (accessible from partner or journal) — Adds `Operation Type` (required), `ID Supplier`, and `Supplier Reference` fields

## Wizards

### Create Payment Lines Wizard

Accessed from an open **Payment Order** via the standard "Add Payment Lines" button provided by `account_payment_order`. The Banorte extension adds an **Operation Type** filter field so users can restrict which move lines are pulled into the payment order based on the Banorte operation type configured on the partner's bank account.

---

<!-- ============================================================ -->
<!-- SECCIÓN EN ESPAÑOL — Documentación Funcional                 -->
<!-- ============================================================ -->

## Descripción General

Este módulo fue diseñado para empresas mexicanas que realizan pagos masivos a proveedores a través del banco **Banorte**. Su función principal es generar automáticamente los archivos de pago en formato TXT que Banorte exige para procesar transferencias electrónicas, pagos SPEI, TEF y pagos de tarjetas de crédito, todo desde la interfaz de Odoo sin necesidad de capturar manualmente cada operación en el portal bancario.

El módulo se integra de forma transparente con los procesos contables existentes en Odoo: una vez que se tienen las facturas de proveedores aprobadas, el equipo de pagos puede agruparlas en una **Orden de Pago** o procesarlas como **Pagos Individuales**, seleccionar el método de pago Banorte correspondiente, y con un solo clic obtener el archivo listo para subir al banco.

Adicionalmente, el módulo permite **importar los estados de cuenta bancarios de Banorte** en formato TXT, reconociendo automáticamente los movimientos, identificando a los socios por su RFC incluido en el concepto, y asociando el método de pago (SPEI u otro) para facilitar la conciliación bancaria.

En conjunto, este módulo elimina la doble captura de información entre Odoo y el portal de Banorte, reduce errores humanos en la elaboración de archivos de dispersión y acelera el ciclo de pago a proveedores.

## Objetivo de Negocio

- **Automatizar la generación de archivos de dispersión Banorte** para reducir el tiempo y los errores en el proceso de pago a proveedores.
- **Soportar múltiples tipos de operación bancaria** (transferencias propias, a terceros, SPEI, TEF y pagos de tarjetas de crédito) desde una sola interfaz.
- **Mantener trazabilidad completa** de qué pagos han sido procesados y cuándo se generó el archivo bancario, mediante el indicador interno de estado del TXT.
- **Facilitar la conciliación bancaria** al importar automáticamente los estados de cuenta de Banorte en TXT, identificando socios por RFC y métodos de pago por concepto.
- **Centralizar la configuración bancaria** de proveedores (tipo de operación, ID en catálogo Banorte, referencia fija) directamente en la ficha de cuenta bancaria del contacto en Odoo.
- **Garantizar cumplimiento del layout Banorte** mediante validaciones automáticas que alertan al usuario antes de generar el archivo si faltan datos obligatorios.

## Flujos de Negocio Principales

### Flujo 1: Pago Masivo a Proveedores mediante Orden de Pago

**Descripción:** El equipo de cuentas por pagar agrupa varias facturas de proveedores en una Orden de Pago y genera un único archivo TXT para cargarlo al portal Banorte y dispersar todos los pagos en una sola operación bancaria.

**Pasos:**
1. El usuario navega a **Contabilidad → Proveedores → Órdenes de Pago** y crea una nueva orden.
2. Selecciona el modo de pago **Banorte Transfer to Suppliers** (o el modo Banorte correspondiente).
3. Utiliza el botón **Agregar líneas de pago** para abrir el asistente. Puede filtrar las líneas por **Tipo de Operación** (Propias, Terceros, SPEI, TEF) para segmentar el archivo.
4. Confirma las líneas a incluir y aprueba la orden de pago.
5. Hace clic en el botón de generación de archivo provisto por `account_payment_order` (integrado con la lógica Banorte).
6. El sistema valida cada línea: tipo de operación, ID de proveedor en catálogo Banorte, número de cuenta origen, cuenta/CLABE destino, importe, referencia y descripción.
7. Si no hay errores, se descarga el archivo TXT con el nombre en formato `PP401903AAMMDD<folio>.TXT`.
8. El usuario sube el archivo al portal corporativo de Banorte para procesar la dispersión.

**Reglas de negocio importantes:**
- Si falta el **Tipo de Operación** en la cuenta bancaria del proveedor, el sistema no genera el archivo y muestra el error específico.
- Para operaciones tipo **01 (Propias)**, no se requiere ID de proveedor en el catálogo Banorte; los 13 caracteres se rellenan con espacios.
- Para operaciones **04 (SPEI)** y **05 (TEF)**, se incluye el RFC del ordenante (empresa) en el registro.
- El importe se formatea sin punto decimal físico; los últimos dos dígitos representan los centavos.
- Las cuentas para pagos de tarjetas AMEX (operación 12) deben tener exactamente 15 dígitos; para otras tarjetas (09, 10, 11) deben tener 16 dígitos.

---

### Flujo 2: Pago Individual a Proveedor con Generación de Archivo TXT

**Descripción:** El usuario procesa un pago individual a un proveedor usando el método de pago Banorte y genera el archivo TXT directamente desde el formulario de pago.

**Pasos:**
1. El usuario crea o accede a un pago en **Contabilidad → Proveedores → Pagos**.
2. Selecciona el método de pago **Banorte Credit Transfer to suppliers**.
3. Completa los campos **Fecha de Vencimiento**, **Ref 1** y **Ref 2** si aplica (editables solo en estado borrador).
4. Verifica que el proveedor tenga una cuenta bancaria seleccionada con el **Tipo de Operación** correcto.
5. Hace clic en **Confirmar** (Publicar). El sistema valida que exista una cuenta bancaria del proveedor; si no, muestra un error.
6. Una vez confirmado el pago (estado "Publicado"), aparece el botón **Generar Archivo de Pago**.
7. El usuario hace clic en el botón; el sistema genera el archivo TXT y lo guarda como adjunto del pago.
8. Se abre automáticamente la vista del adjunto para descargar el archivo y cargarlo al banco.

**Reglas de negocio importantes:**
- El botón **Generar Archivo de Pago** solo es visible cuando el pago está en estado **Publicado**, es de tipo **salida (pago a proveedor)** y el método de pago tiene activada la opción **Genera Archivo de Pago**.
- Una vez generado el archivo, el campo interno `state_txt` se marca como `True` para trazabilidad.
- El nombre del archivo sigue el patrón `<prefijo>401903<AAMMDD><sufijo_folio>.TXT`.

---

### Flujo 3: Importación de Estado de Cuenta Banorte TXT

**Descripción:** El equipo de tesorería importa el estado de cuenta bancario descargado de Banorte en formato TXT para registrar automáticamente los movimientos y facilitar la conciliación.

**Pasos:**
1. El usuario accede al diario bancario correspondiente y utiliza la opción de importar estado de cuenta.
2. Selecciona el archivo TXT descargado del portal Banorte.
3. El sistema detecta el formato TXT y procesa los registros: lee el encabezado de cuenta (tipo 11), los movimientos principales (tipo 22) y los conceptos complementarios (tipo 23).
4. Por cada movimiento, el sistema intenta identificar al socio buscando el RFC en el concepto de la transacción.
5. Si el concepto contiene la palabra "SPEI", el sistema asigna automáticamente el método de pago SPEI a la línea.
6. Se crean los registros de estado de cuenta con todas las líneas de movimiento listas para conciliar.
7. El sistema redirige al usuario a la vista de líneas del estado de cuenta importado.

**Reglas de negocio importantes:**
- Solo se puede importar un archivo TXT a la vez; si se seleccionan múltiples archivos, el sistema redirige al proceso estándar de Odoo.
- La fecha de todos los movimientos se toma del encabezado del archivo (fecha final del período), no de cada registro individual.
- Los importes negativos (débitos) y positivos (créditos) se determinan por el dígito de posición 27 del registro tipo 22 (1 = débito, 2 = crédito).
- El RFC extraído del concepto se busca en la base de datos de socios usando coincidencia insensible a mayúsculas/minúsculas.

---

### Flujo 4: Configuración de Cuenta Bancaria de Proveedor para Banorte

**Descripción:** El administrador o el equipo de pagos registra o actualiza la información bancaria de un proveedor con los datos requeridos por Banorte para incluirlo en los archivos de dispersión.

**Pasos:**
1. El usuario accede a la ficha del proveedor en **Contactos** o desde **Contabilidad → Proveedores**.
2. En la pestaña **Contabilidad**, sección **Cuentas Bancarias**, agrega o edita una cuenta bancaria.
3. Selecciona el **Tipo de Operación** (obligatorio): Propias, Terceros, SPEI, TEF, TdeC Empresariales Banorte, Pago de TdC Banorte, Pago de TdC Otros Bancos, o Pago de TdC AMEX.
4. Si el tipo de operación es diferente a **Propias (01)**, ingresa el **ID Proveedor** (hasta 13 caracteres) que corresponde al catálogo de proveedores de Banorte.
5. Opcionalmente, ingresa una **Referencia de Proveedor** fija que se usará como descripción en todos los pagos a esa cuenta.
6. Si aplica, registra el **ID Facturador Banorte** en la ficha principal del contacto (campo de 6 caracteres en la pestaña Contabilidad).
7. Guarda los cambios.

**Reglas de negocio importantes:**
- El campo **Tipo de Operación** es obligatorio en el formulario de cuenta bancaria.
- El **ID Proveedor** es obligatorio para todos los tipos excepto **Propias (01)**; el formulario lo oculta y omite su requerimiento cuando se selecciona el tipo 01.
- Si se define una **Referencia de Proveedor**, esta sobreescribe la referencia automática (número de factura) en el archivo de pago.

---

## Guía de Configuración

1. **Verificar métodos de pago instalados:** Ir a **Contabilidad → Configuración → Métodos de Pago**. Confirmar que existen:
   - *Banorte Credit Transfer to suppliers* (código: `banorte_credit_transfer`, prefijo: `PP`)
   - *Banorte Service Payment* (código: `banorte_service_payment`, prefijo: `PC`)
   Si no aparecen, actualizar el módulo.

2. **Verificar el modo de pago:** Ir a **Contabilidad → Configuración → Modos de Pago**. Confirmar que existe *Banorte Transfer to Suppliers* vinculado a la compañía principal. Ajustar la cuenta bancaria de la compañía en el modo de pago si es necesario.

3. **Configurar la cuenta bancaria de la empresa:** En el diario bancario de Banorte, verificar que tenga configurada una **Cuenta Bancaria** con el número de cuenta de 20 dígitos. Este número se usará como **Cuenta Origen** en todos los archivos generados.

4. **Configurar cuentas bancarias de proveedores:** Para cada proveedor que se pagará vía Banorte, acceder a su ficha → pestaña **Contabilidad** → **Cuentas Bancarias** y completar:
   - Número de cuenta o CLABE
   - **Tipo de Operación** (obligatorio)
   - **ID Proveedor** (obligatorio si no es tipo 01)
   - **Referencia de Proveedor** (opcional)
   > ⚠️ **Advertencia:** Si el proveedor no tiene configurado el **Tipo de Operación**, el sistema no podrá generar el archivo de pago y mostrará un error.

5. **Configurar el RFC de la empresa:** Verificar que la empresa tenga el RFC registrado en **Ajustes → Empresas → [su empresa]**. Este dato se incluye en los pagos SPEI y TEF.

6. **Para importar estados de cuenta:** Asegurarse de que el diario bancario tenga habilitada la importación de archivos. El módulo registra automáticamente el formato TXT como disponible para ese diario.

---

## Campos y Pantallas Clave

### Cuenta Bancaria (de Contacto)

| Campo en pantalla | Para qué sirve | Valores posibles / Notas |
|---|---|---|
| Tipo de Operación | Define el tipo de transferencia Banorte que se usará al pagar a esta cuenta | 01-Propias, 02-Terceros, 04-SPEI, 05-TEF, 09-TdeC Empresariales Banorte, 10-Pago de TdC Banorte, 11-Pago de TdC Otros Bancos, 12-Pago de TdC AMEX. **Campo obligatorio.** |
| ID Proveedor | Identificador del proveedor en el catálogo interno de Banorte | Alfanumérico, máximo 13 caracteres. Obligatorio para todos los tipos excepto 01-Propias. |
| Referencia de Proveedor | Texto fijo que aparecerá como descripción en el archivo de pago | Si se deja vacío, se usa la referencia de la factura o del pago. Máximo 30 caracteres efectivos en el archivo. |

### Contacto (Pestaña Contabilidad)

| Campo en pantalla | Para qué sirve | Valores posibles / Notas |
|---|---|---|
| Banorte Biller ID | Identificador de facturador Banorte asignado a este contacto | Texto de hasta 6 caracteres. Usado en contextos de pago de servicios. |

### Pago (Formulario de Pago)

| Campo en pantalla | Para qué sirve | Valores posibles / Notas |
|---|---|---|
| Fecha de Vencimiento | Fecha límite opcional para el pago | Fecha. Solo editable en estado Borrador. |
| Ref 1 | Campo de referencia auxiliar 1 | Texto, máximo 40 caracteres. Solo editable en estado Borrador. |
| Ref 2 | Campo de referencia auxiliar 2 | Texto, máximo 40 caracteres. Solo editable en estado Borrador. |
| Generar Archivo de Pago *(botón)* | Genera y descarga el archivo TXT para subir a Banorte | Visible solo cuando el pago está Publicado, es saliente y el método de pago soporta generación de archivo. |

### Método de Pago (Formulario)

| Campo en pantalla | Para qué sirve | Valores posibles / Notas |
|---|---|---|
| Genera Archivo de Pago | Indica si este método produce un archivo TXT para el banco | Casilla de verificación (Sí/No). Activada por defecto para los métodos Banorte. |
| Prefijo de Nombre de Archivo | Dos caracteres que inician el nombre del archivo generado | Texto, máximo 2 caracteres. Ejemplos: `PP` (pagos a proveedores), `PC` (pagos de servicios). |

### Asistente: Crear Líneas de Pago

| Campo en pantalla | Para qué sirve | Valores posibles / Notas |
|---|---|---|
| Tipo de Operación | Filtra las facturas/movimientos por el tipo de operación Banorte configurado en la cuenta bancaria del proveedor | 01-Propias, 02-Terceros, 04-SPEI, 05-TEF. Si se deja vacío, no se aplica filtro adicional. |

---

## Automatizaciones y Reglas

- **Validación al confirmar pago (Banorte):** Se ejecuta cuando el usuario hace clic en **Confirmar** en un pago con método `banorte_credit_transfer`. Resultado: si no hay cuenta bancaria del proveedor seleccionada, el sistema bloquea la confirmación y muestra el mensaje *"You need to select a partner bank account"*.

- **Validación al generar archivo de pago:** Se ejecuta al procesar las líneas de pago (individual u orden). Resultado: el sistema verifica tipo de operación, ID proveedor, longitud de cuenta/CLABE, importe y descripción. Si hay errores, los acumula todos y los muestra en un único mensaje antes de cancelar la generación.

- **Marcado de estado TXT:** Se ejecuta automáticamente cuando se genera exitosamente un archivo de pago individual. Resultado: el campo interno `state_txt` del pago se establece en `True`, registrando que el archivo fue generado.

- **Registro de formato TXT para importación:** Al instalar el módulo, el formato `TXT` queda disponible automáticamente como opción de importación en todos los diarios bancarios, sin configuración adicional.

---

## Preguntas Frecuentes (FAQ)

**P: ¿Por qué no aparece el botón "Generar Archivo de Pago" en mi pago?**
R: El botón solo es visible cuando se cumplen las tres condiciones simultáneamente: (1) el pago está en estado **Publicado** (no borrador ni cancelado), (2) es un pago **saliente** (a proveedor, no cobro), y (3) el método de pago seleccionado tiene activada la opción **Genera Archivo de Pago**. Verifique que el método de pago sea uno de los métodos Banorte instalados por este módulo.

**P: El sistema me muestra un error al generar el archivo que dice "Operation type of supplier X is not defined". ¿Qué debo hacer?**
R: Debe ir a la ficha del proveedor indicado, entrar a la pestaña **Contabilidad**, editar su cuenta bancaria y seleccionar el **Tipo de Operación** correspondiente (SPEI, TEF, Terceros, etc.). Este campo es obligatorio para generar el archivo Banorte.

**P: ¿Puedo incluir proveedores con diferentes tipos de operación (SPEI y TEF) en la misma Orden de Pago?**
R: Sí, la Orden de Pago puede contener líneas con distintos tipos de operación. El asistente **Crear Líneas de Pago** tiene un filtro de **Tipo de Operación** que le permite agregar líneas de un tipo a la vez, pero el archivo final puede contener mezcla de tipos. Sin embargo, es recomendable consultar con Banorte si el archivo mixto es aceptado en su configuración específica de banca empresarial.

**P: ¿Qué pasa si el número de CLABE del proveedor no tiene 18 dígitos para una operación tipo 10 u 11?**
R: El sistema mostrará un error al intentar generar el archivo, indicando cuántos dígitos tiene la CLABE y cuántos se esperan (18). No se generará ningún archivo hasta que se corrija el número de CLABE en la cuenta bancaria del proveedor.

**P: ¿Cómo importo el estado de cuenta de Ban
<!-- odoo-docs: last-commit=8e71b5dbe6264665fc32329f2b4a2ff809c24057 | updated=2026-05-11 -->
