from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import subprocess
import os
import uuid

app = FastAPI()

@app.post("/compile-latex/")
async def compile_latex(file: UploadFile = File(...)):
    # Create a unique directory for this compilation to avoid conflicts
    compile_dir = f"/tmp/{uuid.uuid4()}"
    os.makedirs(compile_dir, exist_ok=True)
    
    # Save the uploaded file
    latex_file_path = os.path.join(compile_dir, file.filename)
    with open(latex_file_path, "wb") as latex_file:
        content = await file.read()
        latex_file.write(content)
    
    # Compile the LaTeX file
    result = subprocess.run(
        ["pdflatex", "-output-directory", compile_dir, latex_file_path],
        capture_output=True
    )
    
    if result.returncode != 0:
        # If compilation failed, return the error log
        return {"error": result.stderr.decode()}
    
    # Find the generated PDF file
    pdf_file_path = os.path.join(compile_dir, file.filename.replace(".tex", ".pdf"))
    
    if not os.path.exists(pdf_file_path):
        return {"error": "PDF generation failed"}
    
    # Return the generated PDF
    return FileResponse(pdf_file_path, media_type="application/pdf", filename="output.pdf")
