"""
Fixture generator for verifying the rental-receipt-header change.

Creates one partner + five customer invoices covering every branch of
`_get_name_invoice_report` and the template's conditional title:

    A. paid + 7% VAT                → header: ใบเสร็จรับเงิน/ใบกำกับภาษี
    B. paid + 0% VAT only           → header: ใบเสร็จรับเงิน
    C. paid + no taxes              → header: ใบเสร็จรับเงิน
    D. posted, unpaid               → Print must raise UserError
    E. posted, partially paid       → Print must raise UserError
    F. out_refund (credit note)     → header: ใบลดหนี้, prints regardless

Run it after `docker compose up` + module upgrade. It prints clickable
/report/pdf URLs for A/B/C/F and record URLs for D/E (which should error).
"""

import xmlrpc.client
from datetime import date

URL = "http://localhost:8069"
DB = "test_ce"
USER = "admin"
PWD = "admin"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
assert uid, "Authentication failed"
rpc = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")


def call(model, method, *args, **kwargs):
    return rpc.execute_kw(DB, uid, PWD, model, method, list(args), kwargs)


def find_or_create_tax(name, amount):
    ids = call("account.tax", "search", [("name", "=", name), ("type_tax_use", "=", "sale")])
    if ids:
        return ids[0]
    return call("account.tax", "create", {
        "name": name,
        "amount_type": "percent",
        "amount": amount,
        "type_tax_use": "sale",
    })


def find_or_create_partner():
    ids = call("res.partner", "search", [("name", "=", "Receipt Header Test Customer")])
    if ids:
        return ids[0]
    return call("res.partner", "create", {
        "name": "Receipt Header Test Customer",
        "company_type": "person",
    })


def pick_product():
    ids = call("product.product", "search", [("sale_ok", "=", True)], limit=1)
    assert ids, "No sellable product found; create one first"
    return ids[0]


def pay_full(invoice_id):
    wiz_id = call(
        "account.payment.register",
        "create",
        {},
        context={"active_model": "account.move", "active_ids": [invoice_id]},
    )
    call("account.payment.register", "action_create_payments", [wiz_id])


def pay_partial(invoice_id, amount):
    wiz_id = call(
        "account.payment.register",
        "create",
        {"amount": amount},
        context={"active_model": "account.move", "active_ids": [invoice_id]},
    )
    call("account.payment.register", "action_create_payments", [wiz_id])


def make_invoice(partner_id, product_id, tax_ids, price, name):
    inv = call("account.move", "create", {
        "move_type": "out_invoice",
        "partner_id": partner_id,
        "invoice_date": str(date.today()),
        "ref": name,
        "invoice_line_ids": [(0, 0, {
            "product_id": product_id,
            "quantity": 1,
            "price_unit": price,
            "tax_ids": [(6, 0, tax_ids)],
        })],
    })
    call("account.move", "action_post", [inv])
    return inv


def make_refund(partner_id, product_id, tax_ids, price, name):
    rfd = call("account.move", "create", {
        "move_type": "out_refund",
        "partner_id": partner_id,
        "invoice_date": str(date.today()),
        "ref": name,
        "invoice_line_ids": [(0, 0, {
            "product_id": product_id,
            "quantity": 1,
            "price_unit": price,
            "tax_ids": [(6, 0, tax_ids)],
        })],
    })
    call("account.move", "action_post", [rfd])
    return rfd


def pdf_url(inv_id):
    return f"{URL}/report/pdf/account.report_invoice/{inv_id}"


def record_url(inv_id):
    return f"{URL}/odoo/action-account.action_move_out_invoice_type/{inv_id}"


def main():
    vat7 = find_or_create_tax("Test VAT 7%", 7.0)
    vat0 = find_or_create_tax("Test VAT 0%", 0.0)
    partner = find_or_create_partner()
    product = pick_product()

    results = []

    a = make_invoice(partner, product, [vat7], 1000.0, "A paid+VAT7")
    pay_full(a)
    results.append(("A", "paid + 7% VAT", "ใบเสร็จรับเงิน/ใบกำกับภาษี", pdf_url(a)))

    b = make_invoice(partner, product, [vat0], 1000.0, "B paid+VAT0")
    pay_full(b)
    results.append(("B", "paid + 0% VAT only", "ใบเสร็จรับเงิน", pdf_url(b)))

    c = make_invoice(partner, product, [], 1000.0, "C paid+noTax")
    pay_full(c)
    results.append(("C", "paid + no taxes", "ใบเสร็จรับเงิน", pdf_url(c)))

    d = make_invoice(partner, product, [vat7], 1000.0, "D unpaid")
    results.append(("D", "posted, unpaid", "UserError expected", record_url(d)))

    e = make_invoice(partner, product, [vat7], 1000.0, "E partial")
    pay_partial(e, 100.0)
    results.append(("E", "posted, partial pay", "UserError expected", record_url(e)))

    f = make_refund(partner, product, [vat7], 500.0, "F credit note")
    results.append(("F", "out_refund (credit note)", "ใบลดหนี้", pdf_url(f)))

    print("\nFixture invoices created. Expected print outcomes:\n")
    for label, scenario, expected, url in results:
        print(f"  [{label}] {scenario}")
        print(f"       expect: {expected}")
        print(f"       {url}")
        print()


if __name__ == "__main__":
    main()
