import uuid
import subprocess
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

app = FastAPI()

# Allow CORS for all origins for testing (configure as needed for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/compile-latex/")
async def compile_latex(file: UploadFile = File(...)):
    # Generate a unique ID for the file
    file_id = str(uuid.uuid4())
    input_file_path = f"/tmp/{file_id}.tex"
    output_file_path = f"/tmp/{file_id}.pdf"

    try:
        # Save the uploaded file
        with open(input_file_path, "wb") as input_file:
            input_file.write(file.file.read())

        # Run pdflatex
        result = subprocess.run(
            ["pdflatex", "-output-directory", "/tmp", input_file_path],
            capture_output=True
        )

        # Log the output of the pdflatex command
        logger.info(f"pdflatex stdout: {result.stdout.decode()}")
        logger.error(f"pdflatex stderr: {result.stderr.decode()}")

        if result.returncode != 0:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to compile LaTeX: {result.stderr.decode()}"
            )

        # Return the compiled PDF
        response = FileResponse(output_file_path, media_type='application/pdf')

        # Clean up the temporary files after the response has been prepared
        @response.background
        async def cleanup():
            try:
                os.remove(input_file_path)
                os.remove(output_file_path)
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")

        return response

    except Exception as e:
        logger.error(f"Error in compile_latex: {e}")
        raise HTTPException(status_code=500, detail=str(e))
