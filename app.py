import os

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from services.document_processor import DocumentProcessor

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

PROCESSED_FOLDER = os.path.join(BASE_DIR, "processed")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

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
        return "Please choose a file."

    filename = secure_filename(file.filename)

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    file.save(filepath)
    print("=" * 50)
    print("Saved File :", filepath)
    print("Exists     :", os.path.exists(filepath))
    print("=" * 50)

    result = processor.process_document(filepath)

    return render_template(
        "result.html",
        extracted_text=result["text"]
    )


if __name__ == "__main__":
    app.run(debug=True)