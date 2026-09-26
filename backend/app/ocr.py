"""
OCR processing module for extracting text from images and PDFs.
"""

import os
import tempfile
import re
from pathlib import Path
from typing import Optional, Tuple, List
from PIL import Image
import pytesseract
import cv2
import numpy as np
import pdf2image
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
import io


class OCRProcessor:
    """Handles OCR processing for various file types."""
    
    def __init__(self, language: str = "fra+eng", use_easyocr: bool = False):
        self.language = language
        self.use_easyocr = use_easyocr
        
        # Try to import easyocr if requested
        if use_easyocr:
            try:
                import easyocr
                self.easyocr_reader = easyocr.Reader([language])
            except ImportError:
                self.use_easyocr = False
                print("EasyOCR not available, falling back to Tesseract")
        
        # Check if Tesseract is available
        try:
            pytesseract.get_tesseract_version()
        except EnvironmentError:
            raise EnvironmentError(
                "Tesseract OCR is not installed or not in your PATH. "
                "Please install it from https://github.com/tesseract-ocr/tesseract"
            )
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results."""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Apply dilation to make text more prominent
        kernel = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], np.uint8)
        dilated = cv2.dilate(thresh, kernel, iterations=1)
        
        return dilated
    
    def enhance_image_quality(self, image: np.ndarray) -> np.ndarray:
        """Enhance image quality for better OCR."""
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply histogram equalization
        equalized = cv2.equalizeHist(gray)
        
        # Apply slight blur to reduce noise
        blurred = cv2.GaussianBlur(equalized, (3, 3), 0)
        
        return blurred
    
    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from an image file."""
        try:
            # Open image with PIL
            img = Image.open(image_path)
            
            # Convert to numpy array
            image_np = np.array(img)
            
            # Preprocess image
            processed_img = self.preprocess_image(image_np)
            
            # Use Tesseract
            text = pytesseract.image_to_string(
                processed_img, 
                lang=self.language,
                config='--psm 6'
            )
            
            return self.clean_text(text)
            
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return ""
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from a PDF file."""
        all_text = ""
        
        try:
            # Method 1: Try to extract text directly from PDF
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        all_text += page_text + "\n"
            
            # If we got text, return it
            if len(all_text.strip()) > 0:
                return self.clean_text(all_text)
            
            # Method 2: Convert PDF to images and use OCR
            print("PDF text extraction failed, trying OCR on images...")
            images = convert_from_path(pdf_path)
            
            for i, image in enumerate(images):
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    image.save(temp_file.name, 'PNG')
                    page_text = self.extract_text_from_image(temp_file.name)
                    all_text += f"--- Page {i+1} ---\n" + page_text + "\n"
                    os.unlink(temp_file.name)
            
            return self.clean_text(all_text)
            
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    def extract_text_from_docx(self, docx_path: str) -> str:
        """Extract text from a DOCX file."""
        try:
            from docx import Document
            doc = Document(docx_path)
            all_text = "\n".join([para.text for para in doc.paragraphs])
            return self.clean_text(all_text)
        except ImportError:
            print("python-docx not available")
            return ""
        except Exception as e:
            print(f"Error extracting text from DOCX: {e}")
            return ""
    
    def extract_text(self, file_path: str, file_type: Optional[str] = None) -> str:
        """Extract text from a file based on its type."""
        if file_type is None:
            file_type = self.detect_file_type(file_path)
        
        print(f"Processing {file_path} as {file_type}")
        
        if file_type == "pdf":
            return self.extract_text_from_pdf(file_path)
        elif file_type in ["png", "jpg", "jpeg", "gif", "bmp", "tiff"]:
            return self.extract_text_from_image(file_path)
        elif file_type == "docx":
            return self.extract_text_from_docx(file_path)
        elif file_type == "txt":
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # Try to detect and process as image
            try:
                return self.extract_text_from_image(file_path)
            except:
                return ""
    
    def extract_text_from_bytes(self, file_bytes: bytes, file_type: str) -> str:
        """Extract text from file bytes."""
        with tempfile.NamedTemporaryFile(suffix=self.get_extension(file_type), delete=False) as temp_file:
            temp_file.write(file_bytes)
            temp_file_path = temp_file.name
        
        try:
            text = self.extract_text(temp_file_path, file_type)
            return text
        finally:
            os.unlink(temp_file_path)
    
    def detect_file_type(self, file_path: str) -> str:
        """Detect file type from extension."""
        ext = Path(file_path).suffix.lower().replace('.', '')
        
        image_extensions = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'tif']
        if ext in image_extensions:
            return ext
        
        return ext
    
    def get_extension(self, file_type: str) -> str:
        """Get file extension from type."""
        if file_type in ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff']:
            return f".{file_type}"
        elif file_type == "pdf":
            return ".pdf"
        elif file_type == "docx":
            return ".docx"
        elif file_type == "txt":
            return ".txt"
        else:
            return ".tmp"
    
    def clean_text(self, text: str) -> str:
        """Clean extracted text by removing excessive whitespace and special characters."""
        if not text:
            return ""
        
        # Replace multiple newlines with single newline
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Replace multiple spaces with single space
        text = re.sub(r'[ \t]{2,}', ' ', text)
        
        # Remove special characters at the start/end of lines
        text = re.sub(r'^[^\w\s]+', '', text, flags=re.MULTILINE)
        text = re.sub(r'[^\w\s]+$', '', text, flags=re.MULTILINE)
        
        # Clean up common OCR errors
        text = text.replace('ﬁ', 'fi').replace('ﬂ', 'fl').replace('ﬀ', 'ff')
        
        # Trim whitespace
        text = text.strip()
        
        return text
    
    def split_into_chunks(self, text: str, max_length: int = 500) -> List[str]:
        """Split text into chunks of maximum length."""
        chunks = []
        current_chunk = ""
        
        for paragraph in text.split('\n\n'):
            if len(current_chunk) + len(paragraph) < max_length:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks


# Singleton instance
ocr_processor = OCRProcessor()


# Convenience functions
def extract_text(file_path: str, file_type: Optional[str] = None) -> str:
    """Extract text from a file."""
    return ocr_processor.extract_text(file_path, file_type)


def extract_text_from_bytes(file_bytes: bytes, file_type: str) -> str:
    """Extract text from file bytes."""
    return ocr_processor.extract_text_from_bytes(file_bytes, file_type)
