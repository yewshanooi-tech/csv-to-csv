from flask import Flask, render_template, request, redirect, url_for, make_response, send_file
import os
import pandas as pd

app = Flask(__name__)
app.config['IMPORTS_FOLDER'] = os.path.join(os.getcwd(), 'data', 'imports')
app.config['EXPORTS_FOLDER'] = os.path.join(os.getcwd(), 'data', 'exports')


def clean_csv(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace Line Separator and Paragraph Separator with newlines
    content = content.replace("\u2028", "\n").replace("\u2029", "\n")

    cleaned_filepath = f"{os.path.splitext(filepath)[0]}_cleaned.csv"
    with open(cleaned_filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return cleaned_filepath


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return make_response("<script>alert('No file attachment in request.'); window.location.href='/';</script>")

    file = request.files['file']

    if not file.filename or not isinstance(file.filename, str):
        return make_response("<script>alert('No file uploaded. Please upload a .csv file.'); window.location.href='/';</script>")

    if file.filename.endswith('.csv'):
        filepath = os.path.join(app.config['IMPORTS_FOLDER'], str(file.filename))
        file.save(filepath)

        # Clean the uploaded CSV file before mapping
        cleaned_filepath = clean_csv(filepath)

        uploaded_df = pd.read_csv(cleaned_filepath)
        columns_df = pd.read_csv(os.path.join('templates', 'columns.csv'))


        # Column Mappings (source:target)
        column_mapping = [
            {'source': 'Financial Status', 'target': 'Document Type'},
            {'source': 'Name', 'target': 'Document Number'},
            {'source': 'Currency', 'target': 'Document Currency Code'},

            {'source': 'Lineitem name', 'target': 'Description of Product or Service'},
            {'source': 'Lineitem price', 'target': 'Unit Price'},
            {'source': 'Lineitem quantity', 'target': 'Quantity'},
            {'source': 'Subtotal', 'target': 'Subtotal excluding taxes discounts & charges'},
            {'source': 'Total', 'target': 'Total Excluding Tax on Line Level'},

            {'source': 'Total', 'target': 'Invoice Total Amount Excluding Tax'},
            {'source': 'Total', 'target': 'Invoice Total Amount Including Tax'},
            {'source': 'Total', 'target': 'Invoice Total Payable Amount'}
        ]


        # Default Column Values (target)
        default_values = {
            "Supplier's Name": "BloomThis Flora Sdn. Bhd.",
            "Supplier's TIN": "C24046757040",
            "Supplier's Registration Type": "BRN",
            "Supplier's Registration Number": "201501029070",
            "Supplier's E-mail": "accounts@bloomthis.co",
            "Supplier's MSIC code": "47734",
            "Supplier's Address Line 1": "9, Lorong 51A/227C, Seksyen 51A",
            "Supplier's City Name": "Petaling Jaya",
            "Supplier's State": "Selangor",
            "Supplier's Country": "Malaysia",
            "Supplier's Contact Number": "+60162992263",

            "Classification": "008",
            "Tax Type": "E",
            "Tax Amount": "0",

            "Invoice Total Tax Amount": "0"
        }


        # Dynamic mapping logic
        mapped_df = pd.DataFrame()
        for column in columns_df.columns:
            matching_sources = [mapping['source'] for mapping in column_mapping if mapping['target'] == column]
            if matching_sources:
                for source_column in matching_sources:
                    if source_column in uploaded_df.columns:
                        # Mapping for Financial Status:Document Type
                        if column == 'Document Type' and source_column == 'Financial Status':
                            mapped_df[column] = uploaded_df[source_column].map(
                                {'paid': 'Invoice', 'refunded': 'Refund Note'}).fillna('')
                        else:
                            mapped_df[column] = uploaded_df[source_column]
                        break
            else:
                # Ensure default values are applied correctly
                mapped_df[column] = default_values.get(column, None)


        # Fill missing columns with default values
        for default_column, default_value in default_values.items():
            if default_column not in mapped_df.columns:
                mapped_df[default_column] = default_value
            else:
                mapped_df[default_column] = mapped_df[default_column].fillna(default_value)


        # Ensure output folder exists
        if not os.path.exists(app.config['EXPORTS_FOLDER']):
            os.makedirs(app.config['EXPORTS_FOLDER'])


        # Save the mapped data to a new file
        output_filename = f"{os.path.splitext(os.path.basename(cleaned_filepath))[0]}_mapped.xlsx"
        mapped_df.to_excel(os.path.join(app.config['EXPORTS_FOLDER'], output_filename), index=False, engine='openpyxl')
        # output_filename = f"{os.path.splitext(os.path.basename(cleaned_filepath))[0]}_mapped.csv"
        # mapped_df.to_csv(os.path.join(app.config['EXPORTS_FOLDER'], output_filename), index=False)


        return render_template('index.html', download_url=url_for('download_file', filename=output_filename))
    return make_response("<script>alert('Invalid file format. Please upload a .csv file.'); window.location.href='/';</script>")

@app.route('/download/<filename>')
def download_file(filename):
    filepath = os.path.join(app.config['EXPORTS_FOLDER'], filename)

    if not os.path.exists(filepath):
        return make_response("<script>alert('File not found.'); window.location.href='/';</script>")

    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists(app.config['IMPORTS_FOLDER']):
        os.makedirs(app.config['IMPORTS_FOLDER'])
    if not os.path.exists(app.config['EXPORTS_FOLDER']):
        os.makedirs(app.config['EXPORTS_FOLDER'])
    app.run(debug=True)
