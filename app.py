from flask import Flask, render_template, request, redirect, url_for, make_response
import os
import pandas as pd

app = Flask(__name__)
app.config['IMPORTS_FOLDER'] = os.path.join(os.getcwd(), 'data', 'imports')
app.config['EXPORTS_FOLDER'] = os.path.join(os.getcwd(), 'data', 'exports')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return make_response("<script>alert('No file part'); window.location.href='/';</script>")

    file = request.files['file']

    if not file.filename or not isinstance(file.filename, str):
        return make_response("<script>alert('No file uploaded'); window.location.href='/';</script>")

    if file.filename.endswith('.csv'):
        filepath = os.path.join(app.config['IMPORTS_FOLDER'], str(file.filename))
        file.save(filepath)

        # Process the uploaded file
        uploaded_df = pd.read_csv(filepath)
        columns_df = pd.read_csv(os.path.join('templates', 'columns.csv'))

        # Define a mapping between uploaded file columns and columns.csv using a list structure
        column_mapping = [
            {'source': 'Name', 'target': 'Document Number'},
            {'source': 'Currency', 'target': 'Document Currency Code'},

            {'source': 'Lineitem name', 'target': 'Description of Product or Service'},
            {'source': 'Lineitem price', 'target': 'Unit Price'},
            {'source': 'Subtotal', 'target': 'Subtotal excluding taxes discounts & charges'},
            {'source': 'Total', 'target': 'Total Excluding Tax on Line Level'},

            {'source': 'Total', 'target': 'Invoice Total Amount Excluding Tax'},
            {'source': 'Total', 'target': 'Invoice Total Amount Including Tax'},
            {'source': 'Total', 'target': 'Invoice Total Payable Amount'}
        ]

        # Define default values for target columns
        default_values = {
            "Supplier's Name": "BloomThis Flora Sdn. Bhd.",
            "Supplier's TIN": "C24046757040",
            "Supplier's Registration Type": "BRN",
            "Supplier's Registration Number": "201501029070",
            # "Supplier's e-mail": "accounts@bloomthis.co",
            "Supplier's MSIC code": "47734",
            # "Supplier's Business Activity Description": "Retail sale of flowers, plants, seeds, fertilizers",
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
                        mapped_df[column] = uploaded_df[source_column]
                        break  # Map the first matching source column
            else:
                # Ensure default values are applied correctly
                mapped_df[column] = default_values.get(column, None)

        # Fill missing columns with default values explicitly
        for default_column, default_value in default_values.items():
            if default_column not in mapped_df.columns:
                mapped_df[default_column] = default_value
            else:
                # Replace inplace=True with explicit assignment
                mapped_df[default_column] = mapped_df[default_column].fillna(default_value)

        # Ensure output folder exists
        if not os.path.exists(app.config['EXPORTS_FOLDER']):
            os.makedirs(app.config['EXPORTS_FOLDER'])

        # Save the mapped data to a new file
        output_filename = f"{os.path.splitext(file.filename)[0]}_mapped.xlsx"
        mapped_df.to_excel(os.path.join(app.config['EXPORTS_FOLDER'], output_filename), index=False, engine='openpyxl')
        # output_filename = f"{os.path.splitext(file.filename)[0]}_mapped.csv"
        # mapped_df.to_csv(os.path.join(app.config['EXPORTS_FOLDER'], output_filename), index=False)

        return redirect(url_for('index'))
    return make_response("<script>alert('Invalid file format'); window.location.href='/';</script>")

if __name__ == '__main__':
    if not os.path.exists(app.config['IMPORTS_FOLDER']):
        os.makedirs(app.config['IMPORTS_FOLDER'])
    if not os.path.exists(app.config['EXPORTS_FOLDER']):
        os.makedirs(app.config['EXPORTS_FOLDER'])
    app.run(debug=True)
