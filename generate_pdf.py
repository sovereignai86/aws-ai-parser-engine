from fpdf import FPDF
from datetime import datetime

class InvoicePDF(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 20)
        self.cell(0, 10, "WAYNE ENTERPRISES", ln=True, align="C")
        self.set_font("helvetica", "I", 10)
        self.cell(0, 10, "1007 Mountain Drive, Gotham City", ln=True, align="C")
        self.ln(10)

def create_invoice(filename):
    pdf = InvoicePDF()
    pdf.add_page()
    
    # Invoice Metadata
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, f"INVOICE #WE-2026-999", ln=True)
    pdf.cell(0, 10, f"DATE: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    pdf.ln(5)

    # Table Header
    pdf.set_fill_color(200, 200, 200)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(80, 10, "Description", 1, 0, "C", True)
    pdf.cell(30, 10, "Qty", 1, 0, "C", True)
    pdf.cell(40, 10, "Unit Price", 1, 0, "C", True)
    pdf.cell(40, 10, "Total", 1, 1, "C", True)

    # Line Items
    items = [
        ("Bat-Armor (Kevlar Reinforced)", 2, 15000.00),
        ("Grappling Hook (Titanium)", 5, 1200.00),
        ("Smoke Pellets (Box of 50)", 10, 450.00)
    ]

    pdf.set_font("helvetica", "", 10)
    grand_total = 0
    for desc, qty, price in items:
        total = qty * price
        grand_total += total
        pdf.cell(80, 10, desc, 1)
        pdf.cell(30, 10, str(qty), 1, 0, "C")
        pdf.cell(40, 10, f"${price:,.2f}", 1, 0, "R")
        pdf.cell(40, 10, f"${total:,.2f}", 1, 1, "R")

    # Grand Total
    pdf.ln(5)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(150, 10, "GRAND TOTAL:", 0, 0, "R")
    pdf.cell(40, 10, f"${grand_total:,.2f}", 1, 1, "C")

    # Notes section to test AI reasoning
    pdf.ln(10)
    pdf.set_font("helvetica", "I", 8)
    pdf.multi_cell(0, 5, "NOTE: Please deliver to the secret cave entrance. Do not use the front gate. Bill to 'The Batman' directly.")
    
    pdf.output(filename)
    print(f"✅ Successfully generated {filename}")

if __name__ == "__main__":
    create_invoice("complex_invoice.pdf")
