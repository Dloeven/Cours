# Cours Organizer

Une application complète pour organiser vos cours, scanner vos prises de notes, les classer, générer des résumés, extraire des formules et créer des cartes de révision Anki.

## Fonctionnalités

- 📄 **Scan de notes** : Numérisation et OCR de vos notes manuscrites ou imprimées
- 📁 **Classement intelligent** : Organisation automatique par matière, date et type
- 📝 **Génération de résumés** : Création automatique de résumés à partir de vos notes
- 🔢 **Extraction de formules** : Détection et extraction des formules mathématiques et scientifiques
- 🎴 **Cartes Anki** : Génération automatique de cartes de révision pour Anki

## Architecture

```
Cours-Organizer/
├── backend/           # API FastAPI
│   ├── app/
│   │   ├── main.py         # Points d'entrée API
│   │   ├── models.py       # Modèles de données
│   │   ├── schemas.py      # Schémas Pydantic
│   │   ├── ocr.py          # Traitement OCR
│   │   ├── nlp.py          # Traitement NLP
│   │   ├── formulas.py     # Extraction de formules
│   │   ├── anki.py         # Génération cartes Anki
│   │   └── utils.py        # Fonctions utilitaires
│   └── requirements.txt
├── frontend/          # Interface React
│   ├── public/
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── App.js
│       └── index.js
├── docker-compose.yml
└── README.md
```

## Prérequis

- Python 3.9+
- Node.js 16+
- Docker (optionnel)

## Installation

### Méthode 1: Avec Docker (recommandé)

```bash
docker-compose up -d
```

L'application sera disponible sur:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000

### Méthode 2: Installation manuelle

#### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm start
```

## Utilisation

1. **Scanner des notes** : Téléchargez des images ou PDF de vos notes
2. **Classement** : Les notes sont automatiquement classées par matière
3. **Traitement** : L'application extrait le texte, détecte les formules et génère des résumés
4. **Export Anki** : Générez des decks Anki pour révision

## Configuration

Créez un fichier `.env` à la racine :

```env
# Backend
API_HOST=0.0.0.0
API_PORT=8000

# Anki
ANKI_API_KEY=your_anki_key
ANKI_DECK_NAME=MyCourses

# OCR
OCR_LANGUAGE=fra+eng
```

## Technologies utilisées

- **Backend**: FastAPI, Python 3.11
- **OCR**: Tesseract, EasyOCR
- **NLP**: spaCy, Transformers (HuggingFace)
- **Formules**: Latex, SymPy
- **Anki**: Anki-Connect
- **Frontend**: React, Material-UI
- **Base de données**: SQLite (par défaut)

## API Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | /api/notes/upload | Télécharger des notes |
| GET | /api/notes | Lister toutes les notes |
| GET | /api/notes/{id} | Récupérer une note |
| POST | /api/notes/{id}/summary | Générer un résumé |
| POST | /api/notes/{id}/formulas | Extraire les formules |
| POST | /api/notes/{id}/anki | Générer des cartes Anki |
| GET | /api/subjects | Lister les matières |
| POST | /api/subjects | Créer une matière |

## Contribution

1. Fork le projet
2. Créez une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit vos changements (`git commit -m 'Ajout nouvelle fonctionnalité'`)
4. Push (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request

## Licence

MIT
