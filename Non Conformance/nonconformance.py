import re
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import pytesseract
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Define the upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = './files'

# Function to check if a file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to perform OCR on a PDF
def perform_ocr(pdf_path):
    extracted_text = ""

    # Open the PDF file using PyMuPDF
    pdf_document = fitz.open(pdf_path)

    # Iterate through pages and extract text
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        page_text = page.get_text()
        extracted_text += page_text

    return extracted_text

# Function to extract information from the OCR text
def extract_information(extracted_text):
    # Define regular expressions to extract information
    name_work_road_pattern = r"Name of Work/ Road:\s*(.*?)\n"
    location_pattern = r"Location:\s*(.*?)\n"
    summary_pattern = r"Description of Non-conformance\n(.*?)\nReceived by:"
    site_engineer_pattern = r"Received by:\s*(.*?)\nIssued by:"
    piu_pattern = r"Issued by:\s*(.*?)\n\(For Site Engineer\)"
    date_pattern = r"Date:: (.*?)\nDate: : (.*?)$"

    # Extract information using regular expressions
    name_work_road_match = re.search(name_work_road_pattern, extracted_text)
    location_match = re.search(location_pattern, extracted_text)
    summary_match = re.search(summary_pattern, extracted_text, re.DOTALL)
    site_engineer_match = re.search(site_engineer_pattern, extracted_text)
    piu_match = re.search(piu_pattern, extracted_text)
    date_match = re.search(date_pattern, extracted_text)

    # Extracted values
    name_work_road = name_work_road_match.group(1) if name_work_road_match else None
    location = location_match.group(1) if location_match else None
    summary = summary_match.group(1).strip() if summary_match else None
    site_engineer = site_engineer_match.group(1) if site_engineer_match else None
    piu = piu_match.group(1) if piu_match else None

    # Extract both dates
    date1 = date_match.group(1) if date_match else None
    date2 = date_match.group(2) if date_match else None

    # Compare the two dates and assign them
    report_issued_date, report_received_date = None, None
    if date1 and date2:
        date_format = "%d-%m-%Y"
        date1_parsed = datetime.strptime(date1, date_format)
        date2_parsed = datetime.strptime(date2, date_format)
        if date1_parsed <= date2_parsed:
            report_issued_date = date1
            report_received_date = date2
        else:
            report_issued_date = date2
            report_received_date = date1

    # Find the position of "Summary:"
    summary_start = extracted_text.find("Summary:") + len("Summary:")
    summary_text = extracted_text[summary_start:].strip()

    return {
        "name_work_road": name_work_road,
        "location": location,
        "summary": summary,
        "site_engineer": site_engineer,
        "piu": piu,
        "report_issued_date": report_issued_date,
        "report_received_date": report_received_date,
        "summary_text": summary_text,
    }

# Function to extract parameter discrepancies
def extract_parameter_discrepancies(summary_text):
    # Convert the summary text to lowercase
    summary_text = summary_text.lower()

    # Initialize a dictionary to store parameter discrepancies
    parameter_discrepancies = {}

    # Split the summary text into sentences
    sentences = summary_text.split(". ")

    # Define regular expressions to identify discrepancies
    discrepancy_patterns = {
        "too_high_pattern": r'(?:high|too high|exceeds the permissible range|above acceptable levels|out of range|over the limit|beyond the norm)',
        "too_low_pattern": r'(?:low|too low|below the acceptable range|falls short of expectations|under the limit|less than expected|lower than normal)'
    }

    # Iterate through each sentence in the summary
    for sentence in sentences:
        # Extract parameter names mentioned in the sentence (case-insensitive)
        mentioned_parameters = re.findall(r'\b(?:soil gradation|atterberg limits|natural moisture content|proctor density|cbr|swelling index|moisture content at the time of compaction|thickness|field density|horizontal alignment)\b', sentence, flags=re.IGNORECASE)

        # Check for discrepancies in the sentence
        discrepancy = "not mentioned"
        for param in mentioned_parameters:
            for key, pattern in discrepancy_patterns.items():
                if re.search(pattern, sentence, flags=re.IGNORECASE):
                    discrepancy = key.replace("_pattern", "")
                    break
            parameter_discrepancies[param] = discrepancy

    return parameter_discrepancies

# Define suggestions for resolving discrepancies (lowercase)
suggestions = {
    "soil gradation": {
        "not mentioned": "Perform additional soil testing and consider adjusting the mix proportions to meet the required gradation.",
        "too_high": "Reduce the gradation to fall within the acceptable limits.",
        "too_low": "Increase the gradation to meet the minimum required limits."
    },
    "atterberg limits": {
        "not mentioned": "Conduct more comprehensive Atterberg limits tests to accurately assess soil properties. Modify construction techniques as needed.",
        "too_high": "Reduce the Atterberg limits to acceptable levels.",
        "too_low": "Increase the Atterberg limits to meet the specified range."
    },
    "natural moisture content": {
        "not mentioned": "Adjust the moisture content during compaction or consider soil stabilization methods.",
        "too_high": "Reduce the moisture content at the time of compaction.",
        "too_low": "Increase the moisture content at the time of compaction."
    },
    "proctor density": {
        "not mentioned": "Ensure proper compaction methods and equipment are used. Re-compact the soil as necessary.",
        "too_high": "Reduce the density to meet the specified range.",
        "too_low": "Increase the density to the required level."
    },
    "cbr": {
        "not mentioned": "Perform additional CBR testing and assess the suitability of the subgrade. Consider soil improvement techniques.",
        "too_high": "Reduce the CBR value to the acceptable range.",
        "too_low": "Increase the CBR value to meet the specified minimum."
    },
    "swelling index": {
        "not mentioned": "Evaluate soil moisture levels and implement appropriate moisture control measures.",
        "too_high": "Reduce the swelling index by controlling moisture levels.",
        "too_low": "Increase the swelling index to meet design requirements."
    },
    "moisture content at the time of compaction": {
        "not mentioned": "Monitor and control moisture content during compaction to achieve the specified range.",
        "too_high": "Reduce the moisture content at the time of compaction.",
        "too_low": "Increase the moisture content at the time of compaction."
    },
    "thickness": {
        "not mentioned": "Verify the thickness of road layers and ensure they meet design specifications. Adjust layer thickness if necessary.",
        "too_high": "Reduce the thickness to the specified level.",
        "too_low": "Increase the thickness to meet design requirements."
    },
    "field density": {
        "not mentioned": "Perform additional field density tests and take corrective actions based on the results.",
        "too_high": "Reduce the field density to meet the specified range.",
        "too_low": "Increase the field density to the required level."
    },
    "horizontal alignment": {
        "not mentioned": "Review and adjust the road alignment as needed to meet design requirements.",
        "too_high": "Adjust the horizontal alignment to fall within acceptable limits.",
        "too_low": "Modify the horizontal alignment to meet design specifications."
    }
}

# Function to generate compliance report suggestions
def generate_compliance_report_suggestions(parameter_discrepancies):
    compliance_report = []
    for param, discrepancy in parameter_discrepancies.items():
        param = param.lower()
        if param in suggestions:
            discrepancy_suggestion = suggestions[param].get(discrepancy, "No specific suggestion available.")
            compliance_report.append(f"{param.capitalize()}: {discrepancy_suggestion}")
    return compliance_report

# Function to generate the compliance report PDF
def generate_compliance_report_pdf(report_data, compliance_report, output_pdf_path):
    # Create a PDF document
    doc = SimpleDocTemplate(output_pdf_path, pagesize=letter)

    # Define the PDF content
    story = []
    styles = getSampleStyleSheet()
    title = "Compliance Report"
    report_date = datetime.now().strftime("%Y-%m-%d")

    # Title
    title_text = "<h1>{}</h1>".format(title)
    story.append(Paragraph(title_text, styles["Title"]))

    # Site Engineer
    site_engineer_text = "<b>Site Engineer:</b> {}".format(report_data["site_engineer"])
    story.append(Paragraph(site_engineer_text, styles["Normal"]))

    # Date of Receiving
    date_received_text = "<b>Date of Issuing:</b> {}".format(report_data["report_received_date"])
    story.append(Paragraph(date_received_text, styles["Normal"]))

    # Suggestions
    story.append(Paragraph("<b>Suggestions:</b>", styles["Heading2"]))
    for suggestion in compliance_report:
        story.append(Paragraph(suggestion, styles["Normal"]))

    # Build the PDF document
    doc.build(story)

# Define the route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Define the route to handle file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    print(request.data)

    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']


    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Perform OCR on the uploaded PDF
        extracted_text = perform_ocr(file_path)

        # Extract information from the OCR text
        report_data = extract_information(extracted_text)

        # Extract parameter discrepancies
        parameter_discrepancies = extract_parameter_discrepancies(report_data["summary_text"])

        # Generate compliance report suggestions
        compliance_report = generate_compliance_report_suggestions(parameter_discrepancies)

        # Generate the compliance report PDF
        output_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Compliance_Report.pdf')
        generate_compliance_report_pdf(report_data, compliance_report, output_pdf_path)

        # return render_template('result.html', report_data=report_data, compliance_report=compliance_report, pdf_path=output_pdf_path)
        return send_from_directory(app.config['UPLOAD_FOLDER'],'Compliance_Report.pdf', as_attachment=True)
    else:
        return redirect(request.url)

# Define a route to serve the generated PDF
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
