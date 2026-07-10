import os
from flask import Blueprint, render_template, request
from werkzeug.utils import secure_filename

upload_bp = Blueprint("upload", __name__)

UPLOAD_FOLDER = "uploads"

ALLOWED_EXTENSIONS = {
    "pdf",
    "png",
    "jpg",
    "jpeg"
}


def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == "POST":

        if "document" not in request.files:
            return "No file selected."

        file = request.files["document"]

        if file.filename == "":
            return "No file selected."

        if file and allowed_file(file.filename):

            filename = secure_filename(file.filename)

            filepath = os.path.join(UPLOAD_FOLDER, filename)

            file.save(filepath)

            extension = filename.rsplit(".", 1)[1].lower()

            if extension in ["png", "jpg", "jpeg"]:

                return render_template(
                    "upload.html",
                    success=True,
                    filename=filename,
                    image=True
                )

            else:

                return render_template(
                    "upload.html",
                    success=True,
                    filename=filename,
                    image=False
                )

        else:

            return render_template(
                "upload.html",
                error="Only PDF, PNG, JPG and JPEG files are allowed."
            )

    return render_template("upload.html")