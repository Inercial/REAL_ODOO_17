# Branch and Commit Naming Convention

This repository follows a standardized naming convention for branches and commit messages
to ensure consistency, traceability, and a clear change history.

---

## Branch Naming

### Format

<odoo_version>#<task_number>-<short_description>

### Example

git checkout -b 17.0#0006-report_account_invoice_credit_memo

### Description

- <odoo_version>  
  Odoo version under development (e.g. 17.0).

- #<task_number>  
  Sequential task identifier, ranging from 0001 to 9999.

- <short_description>  
  Brief and clear description of the change.  
  Use the main affected file or module name, or a concise summary if multiple files were modified.  
  Must be lowercase and use underscores.

---

## Commit Message Naming

### Format

[TYPE][task#0000] Short description of the change

### Example

git commit -m "[REPORT][task#0006] Replace 'FOLIO ORIGEN' with 'FACTURAS RECTIFICATIVAS' field"

### Description

### Commit Type [TYPE]

Required, uppercase, and enclosed in brackets. Allowed values:

- FIX       – Bug fixes
- REPORT    – Report modifications
- ADD       – New features, fields, or functionality
- UPDATE    – Changes to existing behavior or logic
- REFACTOR  – Code restructuring without functional changes
- REMOVE    – Deletions of code or features
- STYLE     – Formatting or non-functional style changes
- CHANGE    – Generic changes when no specific type applies

### Task Reference [task#0000]

- Must match the task number used in the branch name
- Always written as task#0000
- Required and enclosed in brackets

### Commit Description

- Must be short and clear
- Written in imperative form
- Summarizes the overall change, even if multiple modifications were made

---

This convention is mandatory for all contributions to the repository.
