import os
import json
import pandas as pd
import csv
from io import StringIO

from flask import (
    Flask,
    render_template,
    request,
    send_file,
    jsonify,
    Response
)

from config import Config
from database import db

from services.document_processor import DocumentProcessor
from models.invoice import Invoice

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.units import inch

app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
PROCESSED_FOLDER = os.path.join(BASE_DIR, "processed")

EXPORT_FOLDER = os.path.join(BASE_DIR, "exports")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(EXPORT_FOLDER, exist_ok=True)

# Initialize database
db.init_app(app)

processor = DocumentProcessor()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    if "file" not in request.files:
        return "No file uploaded."

    file = request.files["file"]

    if file.filename == "":
        return "Please select a file."

    filename = secure_filename(file.filename)

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    file.save(filepath)

    result = processor.process_document(filepath)

    def to_float(value):
        if value is None:
            return None

        if isinstance(value, (int, float)):
            return float(value)

        value = str(value).replace(",", "").strip()

        try:
            return float(value)
        except ValueError:
            return None

    invoice = Invoice(
        vendor_name=result["invoice_data"].get("vendor_name"),
        invoice_number=result["invoice_data"].get("invoice_number"),
        invoice_date=result["invoice_data"].get("invoice_date"),
        gst_number=result["invoice_data"].get("gst_number"),
        subtotal=to_float(result["invoice_data"].get("subtotal")),
        tax_amount=to_float(result["invoice_data"].get("tax_amount")),
        total_amount=to_float(result["invoice_data"].get("total_amount")),
        ocr_text=result["ocr_text"]
    )

    db.session.add(invoice)
    db.session.commit()

    return render_template(
        "invoice_result.html",
        invoice=invoice,
        ocr=invoice.ocr_text
    )


@app.route("/history")
def history():

    invoices = Invoice.query.order_by(
        Invoice.created_at.desc()
    ).all()

    return render_template(
        "history.html",
        invoices=invoices
    )


@app.route("/invoice/<int:id>")
def view_invoice(id):

    invoice = Invoice.query.get_or_404(id)

    return render_template(
        "invoice_result.html",
        invoice=invoice,    
        ocr=invoice.ocr_text
    )

@app.route("/export/json/<int:id>")
def export_json(id):

    invoice = Invoice.query.get_or_404(id)

    invoice_data = {
        "vendor_name": invoice.vendor_name,
        "invoice_number": invoice.invoice_number,
        "invoice_date": str(invoice.invoice_date),
        "gst_number": invoice.gst_number,
        "subtotal": invoice.subtotal,
        "tax_amount": invoice.tax_amount,
        "total_amount": invoice.total_amount,
        "ocr_text": invoice.ocr_text
    }

    filename = os.path.join(
        EXPORT_FOLDER,
        f"invoice_{id}.json"
    )

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(invoice_data, f, indent=4)

    return send_file(
        filename,
        as_attachment=True
    )


@app.route("/export/csv/<int:id>")
def export_csv(id):

    invoice = Invoice.query.get_or_404(id)

    data = {
        "Vendor Name": [invoice.vendor_name],
        "Invoice Number": [invoice.invoice_number],
        "Invoice Date": [invoice.invoice_date],
        "GST Number": [invoice.gst_number],
        "Subtotal": [invoice.subtotal],
        "Tax Amount": [invoice.tax_amount],
        "Total Amount": [invoice.total_amount]
    }

    df = pd.DataFrame(data)

    filename = os.path.join(
        EXPORT_FOLDER,
        f"invoice_{id}.csv"
    )

    df.to_csv(filename, index=False)

    return send_file(
        filename,
        as_attachment=True
    )

@app.route("/export/pdf/<int:id>")
def export_pdf(id):

    invoice = Invoice.query.get_or_404(id)

    filename = os.path.join(
        EXPORT_FOLDER,
        f"invoice_{id}.pdf"
    )

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph("<b>SmartDoc AI - Invoice Report</b>", styles["Title"])
    )

    elements.append(Paragraph("<br/>", styles["Normal"]))

    data = [
        ["Field", "Value"],
        ["Vendor", invoice.vendor_name],
        ["Invoice Number", invoice.invoice_number],
        ["Invoice Date", str(invoice.invoice_date)],
        ["GST Number", invoice.gst_number],
        ["Subtotal", str(invoice.subtotal)],
        ["Tax Amount", str(invoice.tax_amount)],
        ["Total Amount", str(invoice.total_amount)]
    ]

    table = Table(data, colWidths=[2.5*inch, 3.5*inch])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.darkblue),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),

        ("GRID", (0,0), (-1,-1), 1, colors.black),

        ("BACKGROUND", (0,1), (-1,-1), colors.beige),

        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0,0), (-1,0), 10),

        ("ALIGN", (0,0), (-1,-1), "LEFT")
    ]))

    elements.append(table)

    doc.build(elements)

    return send_file(
        filename,
        as_attachment=True
    )

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    print(app.url_map)

    app.run(debug=True)