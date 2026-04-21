# Post-install admin setup — payment-channel-metadata

This module change adds fields but does not ship rental-specific journal data. After installing/upgrading the module, an administrator must complete the following one-time configuration.

## 1. Set `Channel Type` on each rental-facing journal

Menu: **Accounting → Configuration → Journals**

For each journal used to collect rental payments, open the journal form and set **Channel Type** (new field, next to Type):

| Journal name (example)       | Channel Type |
|------------------------------|--------------|
| Cash                         | Cash         |
| EDC-KBank-Silom-T1           | EDC          |
| EDC-SCB-Silom-T1             | EDC          |
| QR-KBank-Silom               | QR           |
| Online-Omise                 | Online       |
| Manual Bank Transfer         | Other        |

Leave `Channel Type` empty on journals not used for rental income (e.g. internal transfers, expense journals); those will simply be excluded from rental channel reports.

## 2. Configure `Inbound Payment Methods` per journal (brand / gateway variants)

Menu: **Accounting → Configuration → Journals → <journal> → Incoming Payments** tab

This change does NOT introduce a custom `card_brand` field. Card brands (VISA / Mastercard / JCB / AMEX / UnionPay), QR providers (PromptPay QR, TrueMoney), and online gateway sub-methods are represented as native `account.payment.method.line` rows, one per brand/variant per journal.

On each method line:
- **Payment Method**: `Manual Payment` (the built-in one) — do NOT pick a provider method such as Stripe/PayPal; those trigger provider-specific behavior
- **Name**: the brand/variant display label that cashiers will see in the Pay wizard dropdown

### Suggested setup per channel

**Cash journal**
- Cash

**EDC journal (per terminal / merchant account)**
- VISA
- Mastercard
- JCB
- AMEX (if terminal supports)
- UnionPay (if terminal supports)

**QR journal (per destination bank)**
- PromptPay QR
- (additional providers if the bank feed supports them)

**Online journal (per gateway)**
- Credit Card
- Internet Banking
- TrueMoney
- (add gateway-specific options as needed)

**Other journal**
- Bank Transfer
- (any remaining ad-hoc channels)

## 3. Verify the Pay wizard dropdown

Open any rental invoice and click **Pay**:
- Select a configured journal
- Confirm the **Payment Method** dropdown lists only the method lines configured for that journal
- Confirm the **Approval Code** field is visible and optional
- Confirm the **Reference 1** and **Reference 2** fields remain visible (they are gated on rental-origin, not on this change)

## Notes

- Brand/variant changes are data, not code. Admins can add a new brand at any time by creating a new method line — no module upgrade required.
- Renaming a method line (e.g. "VISA" → "VISA Card") will retroactively update the `display_method` field on existing payments at the next recompute trigger.
- This change does NOT yet enforce which journal a cashier must use for which channel. Operational discipline (or a future phase) handles that.
