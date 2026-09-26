"""
Pydantic schemas for the Cours Organizer API.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SubjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    color: str = "#4285F4"
    icon: str = "📚"


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None


class SubjectResponse(SubjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NoteType(str, Enum):
    PDF = "pdf"
    IMAGE = "image"
    DOCX = "docx"
    TEXT = "text"
    MARKDOWN = "markdown"


class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    subject_id: Optional[int] = None
    author: Optional[str] = None
    date_taken: Optional[datetime] = None
    tags: Optional[str] = None


class NoteCreate(NoteBase):
    file: Optional[bytes] = None
    file_type: Optional[NoteType] = None


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    subject_id: Optional[int] = None
    content: Optional[str] = None
    author: Optional[str] = None
    date_taken: Optional[datetime] = None
    tags: Optional[str] = None


class NoteResponse(NoteBase):
    id: int
    content: Optional[str] = None
    original_content: Optional[str] = None
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    page_count: int = 1
    word_count: int = 0
    is_processed: bool = False
    is_ocr_done: bool = False
    is_summary_done: bool = False
    is_formulas_done: bool = False
    created_at: datetime
    updated_at: datetime
    subject: Optional[SubjectResponse] = None
    
    class Config:
        from_attributes = True


class NoteListResponse(BaseModel):
    id: int
    title: str
    subject_id: Optional[int] = None
    subject_name: Optional[str] = None
    file_type: Optional[str] = None
    page_count: int = 1
    word_count: int = 0
    is_processed: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True


class FormulaBase(BaseModel):
    content: str
    latex: Optional[str] = None
    type: Optional[str] = None
    context: Optional[str] = None
    confidence: float = 0.0


class FormulaResponse(FormulaBase):
    id: int
    note_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class SummaryBase(BaseModel):
    content: str
    type: str = "general"
    length: Optional[int] = None


class SummaryResponse(SummaryBase):
    id: int
    note_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class SummaryRequest(BaseModel):
    type: str = "general"
    max_length: Optional[int] = 500
    include_key_points: bool = True


class AnkiDeckBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    subject_id: Optional[int] = None
    description: Optional[str] = None


class AnkiDeckCreate(AnkiDeckBase):
    pass


class AnkiDeckResponse(AnkiDeckBase):
    id: int
    anki_deck_id: Optional[str] = None
    is_synced: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AnkiCardBase(BaseModel):
    deck_id: int
    front: str
    back: str
    card_type: str = "basic"
    tags: Optional[str] = None
    note_id: Optional[int] = None


class AnkiCardCreate(AnkiCardBase):
    pass


class AnkiCardResponse(AnkiCardBase):
    id: int
    anki_card_id: Optional[str] = None
    is_synced: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AnkiCardGenerateRequest(BaseModel):
    deck_id: Optional[int] = None
    deck_name: Optional[str] = None
    card_type: str = "basic"
    max_cards: int = 20
    include_formulas: bool = True
    include_definitions: bool = True
    include_questions: bool = True


class OCRRequest(BaseModel):
    language: str = "fra+eng"
    preprocess: bool = True
    enhance_quality: bool = True


class FormulaExtractionRequest(BaseModel):
    confidence_threshold: float = 0.7
    include_context: bool = True
    context_length: int = 50


class ProcessNoteRequest(BaseModel):
    do_ocr: bool = True
    do_summary: bool = True
    do_formulas: bool = True
    do_anki: bool = False


class MessageResponse(BaseModel):
    message: str
    success: bool = True
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    services: dict = {}


class UploadResponse(BaseModel):
    note_id: int
    file_path: Optional[str] = None
    message: str
    success: bool = True
