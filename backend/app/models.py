"""
Database models for the Cours Organizer application.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class Subject(Base):
    """Represents a school subject or course."""
    __tablename__ = "subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(20), default="#4285F4")
    icon = Column(String(50), default="📚")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    notes = relationship("Note", back_populates="subject")
    anki_decks = relationship("AnkiDeck", back_populates="subject")


class Note(Base):
    """Represents a note or document."""
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    content = Column(Text, nullable=True)
    original_content = Column(Text, nullable=True)  # Raw OCR text
    file_path = Column(String(1000), nullable=True)
    file_type = Column(String(50), nullable=True)  # pdf, image, docx, etc.
    page_count = Column(Integer, default=1)
    word_count = Column(Integer, default=0)
    
    # Metadata
    author = Column(String(200), nullable=True)
    date_taken = Column(DateTime, nullable=True)
    tags = Column(String(500), nullable=True)  # Comma-separated
    
    # Processing status
    is_processed = Column(Boolean, default=False)
    is_ocr_done = Column(Boolean, default=False)
    is_summary_done = Column(Boolean, default=False)
    is_formulas_done = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subject = relationship("Subject", back_populates="notes")
    formulas = relationship("Formula", back_populates="note")
    summaries = relationship("Summary", back_populates="note")
    anki_cards = relationship("AnkiCard", back_populates="note")
    chunks = relationship("NoteChunk", back_populates="note")


class NoteChunk(Base):
    """Represents a chunk of a note for better processing."""
    __tablename__ = "note_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=False)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    start_page = Column(Integer, nullable=True)
    end_page = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    note = relationship("Note", back_populates="chunks")


class Formula(Base):
    """Represents an extracted formula."""
    __tablename__ = "formulas"
    
    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=False)
    content = Column(Text, nullable=False)
    latex = Column(Text, nullable=True)
    type = Column(String(100), nullable=True)  # math, physics, chemistry, etc.
    context = Column(Text, nullable=True)
    confidence = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    note = relationship("Note", back_populates="formulas")


class Summary(Base):
    """Represents a generated summary."""
    __tablename__ = "summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=False)
    content = Column(Text, nullable=False)
    type = Column(String(50), default="general")  # general, short, detailed
    length = Column(Integer, nullable=True)  # Number of words/characters
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    note = relationship("Note", back_populates="summaries")


class AnkiDeck(Base):
    """Represents an Anki deck."""
    __tablename__ = "anki_decks"
    
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    name = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    anki_deck_id = Column(String(100), nullable=True)  # ID from Anki
    is_synced = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subject = relationship("Subject", back_populates="anki_decks")
    cards = relationship("AnkiCard", back_populates="deck")


class AnkiCard(Base):
    """Represents an Anki flashcard."""
    __tablename__ = "anki_cards"
    
    id = Column(Integer, primary_key=True, index=True)
    deck_id = Column(Integer, ForeignKey("anki_decks.id"), nullable=False)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=True)
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    card_type = Column(String(50), default="basic")  # basic, cloze, etc.
    tags = Column(String(500), nullable=True)
    anki_card_id = Column(String(100), nullable=True)  # ID from Anki
    is_synced = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    deck = relationship("AnkiDeck", back_populates="cards")
    note = relationship("Note", back_populates="anki_cards")
