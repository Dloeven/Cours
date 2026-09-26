"""
Anki card generation module.
"""

import json
import requests
from typing import List, Dict, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


class AnkiConnect:
    """Handles communication with Anki via Anki-Connect plugin."""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
    
    def request(self, action: str, **params) -> dict:
        """Make a request to Anki-Connect."""
        payload = {
            "action": action,
            "version": 6,
            "params": params
        }
        
        try:
            response = requests.post(self.base_url, json=payload)
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "result": None}
    
    def check_connection(self) -> bool:
        """Check if Anki-Connect is available."""
        response = self.request("version")
        return response.get("error") is None
    
    def create_deck(self, deck_name: str) -> dict:
        """Create a new deck in Anki."""
        return self.request("createDeck", deck=deck_name)
    
    def delete_deck(self, deck_name: str) -> dict:
        """Delete a deck from Anki."""
        return self.request("deleteDecks", decks=[deck_name], cardsToo=True)
    
    def get_deck_list(self) -> dict:
        """Get list of all decks."""
        return self.request("deckNames")
    
    def add_note(self, note: dict) -> dict:
        """Add a note to Anki."""
        return self.request("addNote", note=note)
    
    def add_notes(self, notes: List[dict]) -> dict:
        """Add multiple notes to Anki."""
        return self.request("addNotes", notes=notes)
    
    def update_note(self, note_id: str, fields: dict) -> dict:
        """Update a note in Anki."""
        return self.request("updateNoteFields", note=note_id, fields=fields)
    
    def delete_note(self, note_id: str) -> dict:
        """Delete a note from Anki."""
        return self.request("deleteNotes", notes=[note_id])
    
    def get_notes(self, deck_name: str) -> dict:
        """Get all notes from a deck."""
        return self.request("findNotes", query=f"deck:{deck_name}")


class AnkiCardGenerator:
    """Generates Anki cards from notes and formulas."""
    
    def __init__(self, anki_connect: Optional[AnkiConnect] = None):
        self.anki = anki_connect or AnkiConnect()
        self.default_model = "Basic"
        self.default_deck = os.getenv("ANKI_DECK_NAME", "Cours Organizer")
    
    def create_basic_card(self, front: str, back: str, deck_name: Optional[str] = None, 
                         tags: Optional[List[str]] = None) -> dict:
        """Create a basic Anki card."""
        deck_name = deck_name or self.default_deck
        
        note = {
            "deckName": deck_name,
            "modelName": self.default_model,
            "fields": {
                "Front": front,
                "Back": back
            },
            "tags": tags or []
        }
        
        return self.anki.add_note(note)
    
    def create_cloze_card(self, text: str, cloze_number: int = 1, 
                         deck_name: Optional[str] = None, 
                         tags: Optional[List[str]] = None) -> dict:
        """Create a cloze deletion card."""
        deck_name = deck_name or self.default_deck
        
        note = {
            "deckName": deck_name,
            "modelName": "Cloze",
            "fields": {
                "Text": text
            },
            "tags": tags or []
        }
        
        return self.anki.add_note(note)
    
    def generate_cards_from_definitions(self, definitions: List[Dict], 
                                        deck_name: Optional[str] = None,
                                        tags: Optional[List[str]] = None) -> List[dict]:
        """Generate Anki cards from definitions."""
        cards = []
        deck_name = deck_name or self.default_deck
        
        for definition in definitions:
            term = definition.get("term", "")
            definition_text = definition.get("definition", "")
            
            if term and definition_text:
                card = self.create_basic_card(
                    front=term,
                    back=definition_text,
                    deck_name=deck_name,
                    tags=(tags or []) + ["definition"]
                )
                cards.append(card)
        
        return cards
    
    def generate_cards_from_formulas(self, formulas: List[Dict],
                                     deck_name: Optional[str] = None,
                                     tags: Optional[List[str]] = None) -> List[dict]:
        """Generate Anki cards from formulas."""
        cards = []
        deck_name = deck_name or self.default_deck
        
        for formula in formulas:
            content = formula.get("content", "")
            context = formula.get("context", "")
            formula_type = formula.get("type", "math")
            
            if content:
                # Card 1: Formula on front, context on back
                card1 = self.create_basic_card(
                    front=content,
                    back=context,
                    deck_name=deck_name,
                    tags=(tags or []) + ["formula", formula_type]
                )
                cards.append(card1)
                
                # Card 2: Context on front, formula on back (for recall)
                if len(context) > 10:
                    card2 = self.create_basic_card(
                        front=context,
                        back=content,
                        deck_name=deck_name,
                        tags=(tags or []) + ["formula-recall", formula_type]
                    )
                    cards.append(card2)
        
        return cards
    
    def generate_cards_from_questions(self, questions: List[str],
                                     answers: Optional[List[str]] = None,
                                     deck_name: Optional[str] = None,
                                     tags: Optional[List[str]] = None) -> List[dict]:
        """Generate Anki cards from questions."""
        cards = []
        deck_name = deck_name or self.default_deck
        
        for i, question in enumerate(questions):
            if answers and i < len(answers):
                answer = answers[i]
            else:
                answer = ""
            
            if question:
                card = self.create_basic_card(
                    front=question,
                    back=answer,
                    deck_name=deck_name,
                    tags=(tags or []) + ["question"]
                )
                cards.append(card)
        
        return cards
    
    def generate_cards_from_text(self, text: str, 
                                 deck_name: Optional[str] = None,
                                 max_cards: int = 20,
                                 include_definitions: bool = True,
                                 include_formulas: bool = True,
                                 include_questions: bool = True,
                                 tags: Optional[List[str]] = None) -> List[dict]:
        """Generate Anki cards from text using NLP and formula extraction."""
        from .nlp import nlp_processor
        from .formulas import formula_extractor
        
        cards = []
        deck_name = deck_name or self.default_deck
        
        # Extract definitions
        if include_definitions:
            definitions = nlp_processor.extract_definitions(text)
            if definitions:
                cards.extend(self.generate_cards_from_definitions(
                    definitions, deck_name, tags
                ))
        
        # Extract formulas
        if include_formulas:
            formulas = formula_extractor.extract_formulas(text)
            if formulas:
                cards.extend(self.generate_cards_from_formulas(
                    formulas, deck_name, tags
                ))
        
        # Extract questions
        if include_questions:
            questions = nlp_processor.extract_questions(text)
            if questions:
                cards.extend(self.generate_cards_from_questions(
                    questions, None, deck_name, tags
                ))
        
        # Limit number of cards
        return cards[:max_cards]
    
    def generate_summary_card(self, text: str, summary: str,
                             deck_name: Optional[str] = None,
                             tags: Optional[List[str]] = None) -> dict:
        """Generate a card with text on front and summary on back."""
        deck_name = deck_name or self.default_deck
        
        return self.create_basic_card(
            front=text[:500],  # Limit length
            back=summary,
            deck_name=deck_name,
            tags=(tags or []) + ["summary"]
        )
    
    def create_deck_for_subject(self, subject_name: str) -> dict:
        """Create a dedicated deck for a subject."""
        deck_name = f"{self.default_deck} - {subject_name}"
        return self.anki.create_deck(deck_name)
    
    def sync_with_anki(self, note_id: int, deck_name: str, 
                      cards_data: List[Dict]) -> List[dict]:
        """Sync generated cards with Anki."""
        results = []
        
        for card_data in cards_data:
            result = self.create_basic_card(
                front=card_data.get("front", ""),
                back=card_data.get("back", ""),
                deck_name=deck_name,
                tags=card_data.get("tags", []) + [f"note-{note_id}"]
            )
            results.append(result)
        
        return results
    
    def export_to_anki_package(self, cards: List[Dict], file_path: str) -> bool:
        """Export cards to Anki package (.apkg) file."""
        # This would require using the anki package directly
        # For now, we'll just return False as this is complex
        return False


# Singleton instances
anki_connect = AnkiConnect()
anki_card_generator = AnkiCardGenerator(anki_connect)


# Convenience functions
def generate_cards_from_text(text: str, **kwargs) -> List[dict]:
    """Generate cards from text."""
    return anki_card_generator.generate_cards_from_text(text, **kwargs)


def create_basic_card(front: str, back: str, **kwargs) -> dict:
    """Create a basic card."""
    return anki_card_generator.create_basic_card(front, back, **kwargs)


def check_anki_connection() -> bool:
    """Check if Anki is connected."""
    return anki_connect.check_connection()
