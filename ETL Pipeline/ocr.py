import pdfplumber
import pandas as pd

def extract_metadata(page_text):
    metadata = {
        "Date": "",
        "Surveyor's Name": "",
        "Road Name": ""
    }

    for line in page_text:
        key, value = map(str.strip, line.split(':'))
        if key in metadata:
            metadata[key] = value

    return metadata

def PDFToDataframes(filesPath):
    with pdfplumber.open(filesPath) as pdf:
        # Initialize dataframes for metadata and test results
        metadata_df = pd.DataFrame()  # Remove columns=["Key", "Value"]
        test_results_df = pd.DataFrame(columns=["Test Name", "Subtest Name", "Value"])

        table_settings = {
            "vertical_strategy": "lines",
            "horizontal_strategy": "lines",
            "intersection_x_tolerance": 15
        }

        for page in pdf.pages:
            page_text = page.extract_text().split('\n')[:3]  # Assuming 3 lines at the top

            # Extract and update metadata from each page
            page_metadata = extract_metadata(page_text)
            metadata_df = metadata_df.append(pd.DataFrame.from_dict([page_metadata]), ignore_index=True)

            tables = page.find_tables(table_settings)
            if tables:
                for table_number, table in enumerate(tables, start=1):
                    tb = table.extract()
                    df = pd.DataFrame(tb[1:], columns=tb[0])
                    test_results_df = pd.concat([test_results_df, df], ignore_index=True)

        # Add metadata columns to test_results
        test_results_df["Date"] = metadata_df["Date"][0]
        test_results_df["Surveyor Name"] = metadata_df["Surveyor's Name"][0]
        test_results_df["Road Name"] = metadata_df["Road Name"][0]
        # Add "Report Type" column and fill with "qcr1"
        test_results_df["Report Type"] = "qcr1"

        return test_results_df

# Provide the PDF file path here
input_pdf = '/content/drive/MyDrive/SIH/QCR Reports/test_report_3.pdf'
test_results = PDFToDataframes(input_pdf)
