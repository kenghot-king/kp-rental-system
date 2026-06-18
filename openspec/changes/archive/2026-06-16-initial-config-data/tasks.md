## 1. Data File

- [X] 1.1 Create `data/initial_config.xml` with `noupdate="1"`
- [X] 1.2 Add rental company settings (min_extra_hour=2)
- [X] 1.3 Add Output 7% include tax (sale, tax-included, Output VAT account)
- [X] 1.4 Add Input 7% include tax (purchase, tax-included, Input VAT account)
- [X] 1.5 Add Cash journal (type: cash)
- [X] 1.6 Add VISA journal (type: bank)
- [X] 1.7 Add MASTER journal (type: bank)
- [X] 1.8 Add QR PromptPay journal (type: bank)
- [X] 1.9 Add Transfer journal (type: bank)

## 2. Module Setup

- [X] 2.1 Add `l10n_th` to module dependencies
- [X] 2.2 Add `data/initial_config.xml` to manifest data list

## 3. Verification

- [X] 3.1 Drop database, reinstall modules, verify all config is created automatically
