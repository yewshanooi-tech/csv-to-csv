from flask import Flask, render_template, request, redirect, url_for
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
        return "No file part"
    file = request.files['file']
    if not file.filename or not isinstance(file.filename, str):
        return "No selected file"
    if file.filename.endswith('.csv'):
        filepath = os.path.join(app.config['IMPORTS_FOLDER'], str(file.filename))
        file.save(filepath)

        # Process the uploaded file
        uploaded_df = pd.read_csv(filepath)
        columns_df = pd.read_csv(os.path.join('templates', 'columns.csv'))

        # Example mapping logic (adjust as needed)
        mapped_df = pd.DataFrame()
        mapped_df['Supplier Name'] = uploaded_df['Name']
        mapped_df['Supplier Email'] = uploaded_df['Email']
        mapped_df['Subtotal'] = uploaded_df['Subtotal']
        mapped_df['Total'] = uploaded_df['Total']

        # Ensure output folder exists
        if not os.path.exists(app.config['EXPORTS_FOLDER']):
            os.makedirs(app.config['EXPORTS_FOLDER'])

        # Save the mapped data to a new file
        output_filename = f"{os.path.splitext(file.filename)[0]}_mapped.csv"
        mapped_df.to_csv(os.path.join(app.config['EXPORTS_FOLDER'], output_filename), index=False)

        return redirect(url_for('index'))
    return "Invalid file format"

if __name__ == '__main__':
    if not os.path.exists(app.config['IMPORTS_FOLDER']):
        os.makedirs(app.config['IMPORTS_FOLDER'])
    if not os.path.exists(app.config['EXPORTS_FOLDER']):
        os.makedirs(app.config['EXPORTS_FOLDER'])
    app.run(debug=True)
