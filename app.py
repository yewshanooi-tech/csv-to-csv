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
                mapped_df[column] = None  # Handle missing columns gracefully

        # Ensure output folder exists
        if not os.path.exists(app.config['EXPORTS_FOLDER']):
            os.makedirs(app.config['EXPORTS_FOLDER'])

        # Save the mapped data to a new file
        output_filename = f"{os.path.splitext(file.filename)[0]}_mapped.csv"
        mapped_df.to_csv(os.path.join(app.config['EXPORTS_FOLDER'], output_filename), index=False)

        return redirect(url_for('index'))
    return make_response("<script>alert('Invalid file format'); window.location.href='/';</script>")

if __name__ == '__main__':
    if not os.path.exists(app.config['IMPORTS_FOLDER']):
        os.makedirs(app.config['IMPORTS_FOLDER'])
    if not os.path.exists(app.config['EXPORTS_FOLDER']):
        os.makedirs(app.config['EXPORTS_FOLDER'])
    app.run(debug=True)
