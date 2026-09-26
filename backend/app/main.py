"""
Main FastAPI application for Cours Organizer.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
from datetime import datetime
import os
import tempfile
import shutil
from pathlib import Path

from . import models, schemas, database
from .ocr import extract_text_from_bytes, ocr_processor
from .nlp import nlp_processor, extract_keywords, generate_summary, extract_definitions, extract_questions
from .formulas import formula_extractor, extract_formulas, categorize_formula
from .anki import anki_card_generator, check_anki_connection, create_basic_card, generate_cards_from_text

# Initialize FastAPI app
app = FastAPI(
    title="Cours Organizer API",
    description="API for organizing course notes, extracting formulas, and generating Anki cards",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Database dependency
get_db = database.get_db

# Initialize database
@app.on_event("startup")
def startup_event():
    database.init_db()
    # Create uploads directory
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("processed", exist_ok=True)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/api/health", response_model=schemas.HealthResponse)
async def health_check():
    """Check API health status."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "database": "ok",
            "ocr": "ok" if os.path.exists("/usr/bin/tesseract") else "not available",
            "anki": "ok" if check_anki_connection() else "not connected",
        }
    }


# ==================== Subject Endpoints ====================

@app.post("/api/subjects", response_model=schemas.SubjectResponse)
async def create_subject(
    subject: schemas.SubjectCreate,
    db=Depends(get_db)
):
    """Create a new subject."""
    db_subject = models.Subject(**subject.model_dump())
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject


@app.get("/api/subjects", response_model=List[schemas.SubjectResponse])
async def get_subjects(
    skip: int = 0,
    limit: int = 100,
    db=Depends(get_db)
):
    """Get list of all subjects."""
    subjects = db.query(models.Subject).offset(skip).limit(limit).all()
    return subjects


@app.get("/api/subjects/{subject_id}", response_model=schemas.SubjectResponse)
async def get_subject(
    subject_id: int,
    db=Depends(get_db)
):
    """Get a specific subject."""
    subject = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


@app.put("/api/subjects/{subject_id}", response_model=schemas.SubjectResponse)
async def update_subject(
    subject_id: int,
    subject_update: schemas.SubjectUpdate,
    db=Depends(get_db)
):
    """Update a subject."""
    db_subject = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    if not db_subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    for key, value in subject_update.model_dump().items():
        if value is not None:
            setattr(db_subject, key, value)
    
    db_subject.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_subject)
    return db_subject


@app.delete("/api/subjects/{subject_id}", response_model=schemas.MessageResponse)
async def delete_subject(
    subject_id: int,
    db=Depends(get_db)
):
    """Delete a subject."""
    db_subject = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    if not db_subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    db.delete(db_subject)
    db.commit()
    return {"message": "Subject deleted successfully", "success": True}


# ==================== Note Endpoints ====================

@app.post("/api/notes/upload", response_model=schemas.UploadResponse)
async def upload_note(
    file: UploadFile = File(...),
    title: str = Query(None),
    subject_id: Optional[int] = Query(None),
    tags: Optional[str] = Query(None),
    db=Depends(get_db)
):
    """Upload a note file and process it."""
    try:
        # Read file content
        file_content = await file.read()
        file_type = file.content_type.split('/')[-1].lower()
        
        # Determine file type
        if file.filename:
            ext = Path(file.filename).suffix.lower().replace('.', '')
            if ext in ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff']:
                file_type = ext
            elif ext in ['pdf', 'docx', 'txt']:
                file_type = ext
        
        # Save file temporarily
        uploads_dir = "uploads"
        os.makedirs(uploads_dir, exist_ok=True)
        
        file_path = os.path.join(uploads_dir, f"{datetime.now().timestamp()}_{file.filename}")
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Create note in database
        db_note = models.Note(
            title=title or file.filename,
            subject_id=subject_id,
            file_path=file_path,
            file_type=file_type,
            tags=tags,
            is_processed=False,
            is_ocr_done=False,
        )
        db.add(db_note)
        db.commit()
        db.refresh(db_note)
        
        # Extract text using OCR
        try:
            text = extract_text_from_bytes(file_content, file_type)
            db_note.original_content = text
            db_note.content = text
            db_note.is_ocr_done = True
            db_note.word_count = len(text.split())
            db.commit()
        except Exception as e:
            print(f"OCR failed: {e}")
        
        return {
            "note_id": db_note.id,
            "file_path": file_path,
            "message": "File uploaded and OCR completed",
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/notes", response_model=List[schemas.NoteListResponse])
async def get_notes(
    subject_id: Optional[int] = None,
    is_processed: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db=Depends(get_db)
):
    """Get list of all notes with optional filtering."""
    query = db.query(models.Note)
    
    if subject_id is not None:
        query = query.filter(models.Note.subject_id == subject_id)
    
    if is_processed is not None:
        query = query.filter(models.Note.is_processed == is_processed)
    
    notes = query.offset(skip).limit(limit).all()
    
    # Format response
    result = []
    for note in notes:
        subject_name = None
        if note.subject:
            subject_name = note.subject.name
        
        result.append({
            **note.__dict__,
            "subject_name": subject_name,
        })
    
    return result


@app.get("/api/notes/{note_id}", response_model=schemas.NoteResponse)
async def get_note(
    note_id: int,
    db=Depends(get_db)
):
    """Get a specific note."""
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@app.put("/api/notes/{note_id}", response_model=schemas.NoteResponse)
async def update_note(
    note_id: int,
    note_update: schemas.NoteUpdate,
    db=Depends(get_db)
):
    """Update a note."""
    db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    for key, value in note_update.model_dump().items():
        if value is not None:
            setattr(db_note, key, value)
    
    db_note.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_note)
    return db_note


@app.delete("/api/notes/{note_id}", response_model=schemas.MessageResponse)
async def delete_note(
    note_id: int,
    db=Depends(get_db)
):
    """Delete a note."""
    db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Delete associated files
    if db_note.file_path and os.path.exists(db_note.file_path):
        os.remove(db_note.file_path)
    
    db.delete(db_note)
    db.commit()
    return {"message": "Note deleted successfully", "success": True}


# ==================== Processing Endpoints ====================

@app.post("/api/notes/{note_id}/process", response_model=schemas.NoteResponse)
async def process_note(
    note_id: int,
    request: schemas.ProcessNoteRequest,
    db=Depends(get_db)
):
    """Process a note (OCR, summary, formulas, Anki cards)."""
    db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Get note content
    content = db_note.content or db_note.original_content or ""
    
    # Do OCR if requested and not already done
    if request.do_ocr and not db_note.is_ocr_done and db_note.file_path:
        try:
            text = extract_text_from_bytes(
                open(db_note.file_path, 'rb').read(),
                db_note.file_type or 'pdf'
            )
            db_note.original_content = text
            db_note.content = text
            db_note.is_ocr_done = True
            db_note.word_count = len(text.split())
        except Exception as e:
            print(f"OCR processing failed: {e}")
    
    # Do summary if requested
    if request.do_summary and not db_note.is_summary_done:
        try:
            summary = generate_summary(content, max_length=500)
            db_summary = models.Summary(
                note_id=note_id,
                content=summary,
                type="general",
                length=len(summary.split())
            )
            db.add(db_summary)
            db_note.is_summary_done = True
        except Exception as e:
            print(f"Summary generation failed: {e}")
    
    # Do formula extraction if requested
    if request.do_formulas and not db_note.is_formulas_done:
        try:
            formulas = extract_formulas(content, confidence_threshold=0.7)
            for formula_data in formulas:
                db_formula = models.Formula(
                    note_id=note_id,
                    content=formula_data.get('content', ''),
                    latex=formula_data.get('latex', ''),
                    type=formula_data.get('type', 'math'),
                    context=formula_data.get('context', ''),
                    confidence=formula_data.get('confidence', 0.0)
                )
                db.add(db_formula)
            db_note.is_formulas_done = True
        except Exception as e:
            print(f"Formula extraction failed: {e}")
    
    # Do Anki card generation if requested
    if request.do_anki:
        try:
            cards_data = anki_card_generator.generate_cards_from_text(
                content,
                deck_name=f"Cours Organizer - {db_note.title}",
                max_cards=20,
                include_definitions=True,
                include_formulas=True,
                include_questions=True
            )
            
            # Save cards to database
            for card_data in cards_data:
                db_card = models.AnkiCard(
                    note_id=note_id,
                    front=card_data.get('front', ''),
                    back=card_data.get('back', ''),
                    card_type='basic',
                    tags=','.join(card_data.get('tags', []))
                )
                db.add(db_card)
        except Exception as e:
            print(f"Anki card generation failed: {e}")
    
    db_note.is_processed = True
    db_note.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_note)
    
    return db_note


@app.post("/api/notes/{note_id}/summary", response_model=schemas.SummaryResponse)
async def generate_note_summary(
    note_id: int,
    request: schemas.SummaryRequest,
    db=Depends(get_db)
):
    """Generate a summary for a note."""
    db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    content = db_note.content or db_note.original_content or ""
    
    summary = generate_summary(
        content,
        max_length=request.max_length,
        summary_type=request.type
    )
    
    # Save summary
    db_summary = models.Summary(
        note_id=note_id,
        content=summary,
        type=request.type,
        length=len(summary.split())
    )
    db.add(db_summary)
    db.commit()
    db.refresh(db_summary)
    
    return db_summary


@app.get("/api/notes/{note_id}/summaries", response_model=List[schemas.SummaryResponse])
async def get_note_summaries(
    note_id: int,
    db=Depends(get_db)
):
    """Get all summaries for a note."""
    summaries = db.query(models.Summary).filter(models.Summary.note_id == note_id).all()
    return summaries


@app.post("/api/notes/{note_id}/formulas", response_model=List[schemas.FormulaResponse])
async def extract_note_formulas(
    note_id: int,
    request: schemas.FormulaExtractionRequest,
    db=Depends(get_db)
):
    """Extract formulas from a note."""
    db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    content = db_note.content or db_note.original_content or ""
    
    formulas = extract_formulas(
        content,
        confidence_threshold=request.confidence_threshold
    )
    
    # Save formulas to database
    db_formulas = []
    for formula_data in formulas:
        db_formula = models.Formula(
            note_id=note_id,
            content=formula_data.get('content', ''),
            latex=formula_data.get('latex', ''),
            type=formula_data.get('type', 'math'),
            context=formula_data.get('context', ''),
            confidence=formula_data.get('confidence', 0.0)
        )
        db.add(db_formula)
        db_formulas.append(db_formula)
    
    db.commit()
    
    return db_formulas


@app.get("/api/notes/{note_id}/formulas", response_model=List[schemas.FormulaResponse])
async def get_note_formulas(
    note_id: int,
    db=Depends(get_db)
):
    """Get all formulas for a note."""
    formulas = db.query(models.Formula).filter(models.Formula.note_id == note_id).all()
    return formulas


# ==================== Anki Endpoints ====================

@app.post("/api/notes/{note_id}/anki", response_model=List[schemas.AnkiCardResponse])
async def generate_anki_cards(
    note_id: int,
    request: schemas.AnkiCardGenerateRequest,
    db=Depends(get_db)
):
    """Generate Anki cards from a note."""
    db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    content = db_note.content or db_note.original_content or ""
    
    # Generate cards
    cards = anki_card_generator.generate_cards_from_text(
        content,
        deck_name=request.deck_name,
        max_cards=request.max_cards,
        include_definitions=request.include_definitions,
        include_formulas=request.include_formulas,
        include_questions=request.include_questions,
        tags=[f"note-{note_id}"]
    )
    
    # Save cards to database
    db_cards = []
    for card_data in cards:
        db_card = models.AnkiCard(
            note_id=note_id,
            deck_id=request.deck_id,
            front=card_data.get('front', ''),
            back=card_data.get('back', ''),
            card_type='basic',
            tags=','.join(card_data.get('tags', []))
        )
        db.add(db_card)
        db_cards.append(db_card)
    
    db.commit()
    
    return db_cards


@app.get("/api/notes/{note_id}/anki", response_model=List[schemas.AnkiCardResponse])
async def get_anki_cards(
    note_id: int,
    db=Depends(get_db)
):
    """Get all Anki cards for a note."""
    cards = db.query(models.AnkiCard).filter(models.AnkiCard.note_id == note_id).all()
    return cards


@app.post("/api/anki/export", response_model=schemas.MessageResponse)
async def export_to_anki(
    deck_id: Optional[int] = None,
    note_id: Optional[int] = None,
    db=Depends(get_db)
):
    """Export cards to Anki via Anki-Connect."""
    if not check_anki_connection():
        raise HTTPException(status_code=503, detail="Anki is not connected")
    
    # Get cards to export
    query = db.query(models.AnkiCard)
    if deck_id:
        query = query.filter(models.AnkiCard.deck_id == deck_id)
    elif note_id:
        query = query.filter(models.AnkiCard.note_id == note_id)
    
    cards = query.all()
    
    # Export each card
    for card in cards:
        try:
            anki_card_generator.create_basic_card(
                front=card.front,
                back=card.back,
                deck_name=card.deck.name if card.deck else "Cours Organizer",
                tags=card.tags.split(',') if card.tags else []
            )
            card.is_synced = True
            db.commit()
        except Exception as e:
            print(f"Failed to export card {card.id}: {e}")
    
    return {
        "message": f"Exported {len(cards)} cards to Anki",
        "success": True,
        "data": {"exported_count": len(cards)}
    }


# ==================== Anki Deck Endpoints ====================

@app.post("/api/anki/decks", response_model=schemas.AnkiDeckResponse)
async def create_anki_deck(
    deck: schemas.AnkiDeckCreate,
    db=Depends(get_db)
):
    """Create a new Anki deck."""
    db_deck = models.AnkiDeck(**deck.model_dump())
    db.add(db_deck)
    db.commit()
    db.refresh(db_deck)
    
    # Create in Anki if connected
    if check_anki_connection():
        anki_card_generator.create_deck_for_subject(deck.name)
        db_deck.is_synced = True
        db.commit()
    
    return db_deck


@app.get("/api/anki/decks", response_model=List[schemas.AnkiDeckResponse])
async def get_anki_decks(
    skip: int = 0,
    limit: int = 100,
    db=Depends(get_db)
):
    """Get list of all Anki decks."""
    decks = db.query(models.AnkiDeck).offset(skip).limit(limit).all()
    return decks


# ==================== Utility Endpoints ====================

@app.post("/api/ocr", response_model=schemas.MessageResponse)
async def extract_text(
    file: UploadFile = File(...),
    language: str = "fra+eng"
):
    """Extract text from a file using OCR."""
    try:
        file_content = await file.read()
        file_type = file.content_type.split('/')[-1].lower()
        
        text = extract_text_from_bytes(file_content, file_type)
        
        return {
            "message": "Text extracted successfully",
            "success": True,
            "data": {"text": text}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/nlp/keywords", response_model=schemas.MessageResponse)
async def extract_keywords_endpoint(
    text: str,
    top_n: int = 10
):
    """Extract keywords from text."""
    keywords = extract_keywords(text, top_n)
    return {
        "message": "Keywords extracted successfully",
        "success": True,
        "data": {"keywords": keywords}
    }


@app.post("/api/nlp/summary", response_model=schemas.MessageResponse)
async def generate_summary_endpoint(
    text: str,
    max_length: int = 500
):
    """Generate a summary of text."""
    summary = generate_summary(text, max_length)
    return {
        "message": "Summary generated successfully",
        "success": True,
        "data": {"summary": summary}
    }


@app.post("/api/formulas/extract", response_model=schemas.MessageResponse)
async def extract_formulas_endpoint(
    text: str,
    confidence_threshold: float = 0.7
):
    """Extract formulas from text."""
    formulas = extract_formulas(text, confidence_threshold)
    return {
        "message": "Formulas extracted successfully",
        "success": True,
        "data": {"formulas": formulas}
    }


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
