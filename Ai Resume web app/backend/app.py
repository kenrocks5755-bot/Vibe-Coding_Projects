import os
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from ollama_client import OllamaClient
from pdf_utils import extract_text_from_pdf, generate_pdf_resume
import io

app = Flask(__name__, 
            static_folder='../frontend',
            template_folder='../frontend',
            static_url_path='')
CORS(app)

ollama = OllamaClient()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if not file.filename.endswith('.pdf'):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    text = extract_text_from_pdf(file)
    if not text:
        return jsonify({"error": "Failed to extract text from PDF"}), 500

    analysis = ollama.analyze_resume(text)
    if not analysis:
        return jsonify({"error": "AI analysis failed. Is Ollama running?"}), 500

    return jsonify({"analysis": analysis})

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Required fields
    required = ['name', 'education', 'skills', 'experience', 'projects']
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"Field '{field}' is required"}), 400

    # Use Ollama to format the resume content professionally
    resume_content = ollama.generate_resume_content(data)
    if not resume_content:
        return jsonify({"error": "AI resume generation failed. Is Ollama running?"}), 500

    # Generate PDF in memory
    pdf_buffer = io.BytesIO()
    success = generate_pdf_resume(resume_content, pdf_buffer)
    if not success:
        return jsonify({"error": "Failed to generate PDF"}), 500

    pdf_buffer.seek(0)
    
    # We return the resume content text AND the PDF is available via a separate download logic 
    # OR we just send the PDF. The requirement says: "Return AI generated resume text + downloadable PDF"
    # To handle both, we might want to return the text and a link, but for simplicity in a single POST:
    # We can return the text, and the frontend can request the PDF or we can send the PDF directly.
    # Let's send the PDF and include the text in headers or just return JSON with text and BASE64? 
    # Better: return JSON with text, and have a separate GET /download-pdf or similar.
    # OR: just return the PDF and the frontend displays the text from the JSON if we did it differently.
    
    # Let's adjust: Return JSON with the content. The frontend can then call /download-pdf with the content.
    return jsonify({
        "content": resume_content,
        "message": "Resume content generated successfully"
    })

@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    data = request.json
    content = data.get('content')
    if not content:
        return jsonify({"error": "No content provided"}), 400
    
    pdf_buffer = io.BytesIO()
    success = generate_pdf_resume(content, pdf_buffer)
    if not success:
        return jsonify({"error": "Failed to generate PDF"}), 500
    
    pdf_buffer.seek(0)
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name="resume.pdf",
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
