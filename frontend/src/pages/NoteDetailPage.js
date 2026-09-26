import React, { useState, useEffect } from 'react';
import { Box, Typography, Card, CardContent, CardActions, Button, Chip, Grid, LinearProgress, Tabs, Tab, Divider, IconButton, Tooltip, Dialog, DialogTitle, DialogContent, DialogActions, TextField, MenuItem } from '@mui/material';
import { Edit as EditIcon, Delete as DeleteIcon, ContentCopy as ContentCopyIcon, Summarize as SummarizeIcon, Functions as FunctionsIcon, FlashOn as FlashOnIcon, Save as SaveIcon, Download as DownloadIcon } from '@mui/icons-material';
import { Link, useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

function NoteDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [note, setNote] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);
  const [summaries, setSummaries] = useState([]);
  const [formulas, setFormulas] = useState([]);
  const [ankiCards, setAnkiCards] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [editMode, setEditMode] = useState(false);
  const [editedNote, setEditedNote] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  useEffect(() => {
    fetchData();
  }, [id]);

  const fetchData = async () => {
    try {
      const [noteResponse, subjectsResponse] = await Promise.all([
        axios.get(`/api/notes/${id}`),
        axios.get('/api/subjects'),
      ]);
      
      setNote(noteResponse.data);
      setEditedNote(noteResponse.data);
      setSubjects(subjectsResponse.data || []);
      
      // Fetch related data
      if (noteResponse.data) {
        const [summariesResponse, formulasResponse, ankiResponse] = await Promise.all([
          axios.get(`/api/notes/${id}/summaries`),
          axios.get(`/api/notes/${id}/formulas`),
          axios.get(`/api/notes/${id}/anki`),
        ]);
        
        setSummaries(summariesResponse.data || []);
        setFormulas(formulasResponse.data || []);
        setAnkiCards(ankiResponse.data || []);
      }
    } catch (error) {
      console.error('Error fetching note:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleProcess = async () => {
    setGenerating(true);
    try {
      await axios.post(`/api/notes/${id}/process`, {
        do_ocr: !note.is_ocr_done,
        do_summary: !note.is_summary_done,
        do_formulas: !note.is_formulas_done,
        do_anki: false,
      });
      fetchData();
    } catch (error) {
      console.error('Error processing note:', error);
    } finally {
      setGenerating(false);
    }
  };

  const handleGenerateSummary = async () => {
    setGenerating(true);
    try {
      await axios.post(`/api/notes/${id}/summary`, {
        type: 'general',
        max_length: 500,
        include_key_points: true,
      });
      fetchData();
    } catch (error) {
      console.error('Error generating summary:', error);
    } finally {
      setGenerating(false);
    }
  };

  const handleExtractFormulas = async () => {
    setGenerating(true);
    try {
      await axios.post(`/api/notes/${id}/formulas`, {
        confidence_threshold: 0.7,
        include_context: true,
        context_length: 50,
      });
      fetchData();
    } catch (error) {
      console.error('Error extracting formulas:', error);
    } finally {
      setGenerating(false);
    }
  };

  const handleGenerateAnkiCards = async () => {
    setGenerating(true);
    try {
      await axios.post(`/api/notes/${id}/anki`, {
        max_cards: 20,
        include_definitions: true,
        include_formulas: true,
        include_questions: true,
      });
      fetchData();
    } catch (error) {
      console.error('Error generating Anki cards:', error);
    } finally {
      setGenerating(false);
    }
  };

  const handleSave = async () => {
    try {
      await axios.put(`/api/notes/${id}`, editedNote);
      setNote(editedNote);
      setEditMode(false);
    } catch (error) {
      console.error('Error saving note:', error);
    }
  };

  const handleDelete = async () => {
    try {
      await axios.delete(`/api/notes/${id}`);
      navigate('/notes');
    } catch (error) {
      console.error('Error deleting note:', error);
    }
  };

  const handleExportToAnki = async () => {
    try {
      await axios.post('/api/anki/export', { note_id: id });
      // Show success message
    } catch (error) {
      console.error('Error exporting to Anki:', error);
    }
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
        <Typography>Chargement de la note...</Typography>
      </Box>
    );
  }

  if (!note) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h6" color="error">
          Note non trouvée
        </Typography>
        <Button variant="contained" component={Link} to="/notes">
          Retour à la liste
        </Button>
      </Box>
    );
  }

  const tabContent = [
    {
      label: 'Contenu',
      component: (
        <Box>
          {editMode ? (
            <TextField
              fullWidth
              multiline
              rows={20}
              value={editedNote.content || ''}
              onChange={(e) => setEditedNote({ ...editedNote, content: e.target.value })}
              variant="outlined"
            />
          ) : (
            <Box sx={{ p: 2, bgcolor: 'background.paper', borderRadius: 1, border: '1px solid #eee' }}>
              <ReactMarkdown>{note.content || note.original_content || 'Aucun contenu'}</ReactMarkdown>
            </Box>
          )}
        </Box>
      ),
    },
    {
      label: 'Résumé',
      component: (
        <Box>
          {summaries.length === 0 ? (
            <Box sx={{ textAlign: 'center', p: 4 }}>
              <Typography variant="body1" color="text.secondary">
                Aucun résumé généré
              </Typography>
              <Button 
                variant="contained" 
                startIcon={<SummarizeIcon />}
                onClick={handleGenerateSummary}
                disabled={generating}
              >
                Générer un résumé
              </Button>
            </Box>
          ) : (
            summaries.map((summary, index) => (
              <Card key={index} elevation={2} sx={{ mb: 2 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Résumé {index + 1} ({summary.type})
                  </Typography>
                  <Divider sx={{ my: 1 }} />
                  <Typography variant="body1">
                    {summary.content}
                  </Typography>
                </CardContent>
              </Card>
            ))
          )}
        </Box>
      ),
    },
    {
      label: 'Formules',
      component: (
        <Box>
          {formulas.length === 0 ? (
            <Box sx={{ textAlign: 'center', p: 4 }}>
              <Typography variant="body1" color="text.secondary">
                Aucune formule extraite
              </Typography>
              <Button 
                variant="contained" 
                startIcon={<FunctionsIcon />}
                onClick={handleExtractFormulas}
                disabled={generating}
              >
                Extraire les formules
              </Button>
            </Box>
          ) : (
            <Grid container spacing={2}>
              {formulas.map((formula, index) => (
                <Grid item xs={12} sm={6} md={4} key={index}>
                  <Card elevation={2}>
                    <CardContent>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        {formula.type}
                      </Typography>
                      <Typography variant="h6" component="div" sx={{ fontFamily: 'monospace' }}>
                        {formula.latex || formula.content}
                      </Typography>
                      {formula.context && (
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 1, fontStyle: 'italic' }}>
                          "{formula.context}"
                        </Typography>
                      )}
                      <Chip 
                        label={`Confiance: ${(formula.confidence * 100).toFixed(0)}%`}
                        size="small"
                        color="primary"
                        sx={{ mt: 1 }}
                      />
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </Box>
      ),
    },
    {
      label: 'Cartes Anki',
      component: (
        <Box>
          {ankiCards.length === 0 ? (
            <Box sx={{ textAlign: 'center', p: 4 }}>
              <Typography variant="body1" color="text.secondary">
                Aucune carte Anki générée
              </Typography>
              <Button 
                variant="contained" 
                startIcon={<FlashOnIcon />}
                onClick={handleGenerateAnkiCards}
                disabled={generating}
              >
                Générer des cartes Anki
              </Button>
            </Box>
          ) : (
            <Grid container spacing={2}>
              {ankiCards.map((card, index) => (
                <Grid item xs={12} sm={6} key={index}>
                  <Card elevation={2}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Carte {index + 1}
                      </Typography>
                      <Box sx={{ p: 2, bgcolor: 'action.hover', borderRadius: 1, mb: 2 }}>
                        <Typography variant="body1" fontWeight="bold">
                          {card.front}
                        </Typography>
                      </Box>
                      <Divider sx={{ my: 1 }} />
                      <Box sx={{ p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
                        <Typography variant="body1">
                          {card.back}
                        </Typography>
                      </Box>
                      {card.tags && (
                        <Box sx={{ mt: 2 }}>
                          {card.tags.split(',').map((tag, tagIndex) => (
                            <Chip key={tagIndex} label={tag} size="small" sx={{ mr: 1, mb: 1 }} />
                          ))}
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
          
          {ankiCards.length > 0 && (
            <Box sx={{ textAlign: 'center', mt: 4 }}>
              <Button 
                variant="contained" 
                color="success"
                startIcon={<FlashOnIcon />}
                onClick={handleExportToAnki}
              >
                Exporter vers Anki
              </Button>
            </Box>
          )}
        </Box>
      ),
    },
  ];

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" component="div">
            {note.title}
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
            {note.subject && (
              <Chip label={note.subject.name} color="primary" sx={{ mr: 1 }} />
            )}
            <Chip label={note.file_type || 'Texte'} sx={{ mr: 1 }} />
            <Chip label={`${note.word_count || 0} mots`} sx={{ mr: 1 }} />
            <Chip 
              label={note.is_processed ? 'Traité' : 'En attente'}
              color={note.is_processed ? 'success' : 'warning'}
            />
          </Box>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          {editMode ? (
            <>
              <Button 
                variant="contained" 
                color="success"
                startIcon={<SaveIcon />}
                onClick={handleSave}
              >
                Enregistrer
              </Button>
              <Button 
                variant="outlined" 
                onClick={() => {
                  setEditMode(false);
                  setEditedNote(note);
                }}
              >
                Annuler
              </Button>
            </>
          ) : (
            <>
              <Tooltip title="Modifier">
                <Button 
                  variant="outlined" 
                  startIcon={<EditIcon />}
                  onClick={() => setEditMode(true)}
                >
                  Modifier
                </Button>
              </Tooltip>
              
              <Tooltip title="Supprimer">
                <Button 
                  variant="outlined" 
                  color="error"
                  startIcon={<DeleteIcon />}
                  onClick={() => setDeleteDialogOpen(true)}
                >
                  Supprimer
                </Button>
              </Tooltip>
            </>
          )}
        </Box>
      </Box>

      {/* Process Button */}
      {!note.is_processed && (
        <Box sx={{ mb: 3 }}>
          <Button 
            variant="contained" 
            color="primary"
            startIcon={<ContentCopyIcon />}
            onClick={handleProcess}
            disabled={generating}
            fullWidth
            sx={{ py: 2 }}
          >
            {generating ? 'Traitement en cours...' : 'Traiter la note (OCR, Résumé, Formules)'}
          </Button>
          {generating && (
            <LinearProgress sx={{ mt: 2 }} />
          )}
        </Box>
      )}

      {/* Tabs */}
      <Card elevation={2}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          {tabContent.map((tab, index) => (
            <Tab key={index} label={tab.label} />
          ))}
        </Tabs>
        <Divider />
        <CardContent>
          {tabContent[activeTab].component}
        </CardContent>
      </Card>

      {/* Delete Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        aria-labelledby="delete-dialog-title"
      >
        <DialogTitle id="delete-dialog-title">
          Supprimer la note
        </DialogTitle>
        <DialogContent>
          <Typography>
            Êtes-vous sûr de vouloir supprimer la note "{note.title}" ?
            Cette action est irréversible.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)} color="primary">
            Annuler
          </Button>
          <Button onClick={handleDelete} color="error" autoFocus>
            Supprimer
          </Button>
        </DialogActions>
      </Dialog>

      {/* Navigation */}
      <Box sx={{ mt: 3 }}>
        <Button variant="outlined" component={Link} to="/notes">
          Retour à la liste des notes
        </Button>
      </Box>
    </Box>
  );
}

export default NoteDetailPage;
