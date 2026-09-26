import React, { useState, useEffect } from 'react';
import { Box, Typography, Button, Card, CardContent, CardActions, Grid, LinearProgress, Dialog, DialogTitle, DialogContent, DialogActions, TextField, MenuItem, Chip, IconButton, Tooltip, Divider } from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon, Edit as EditIcon, CloudUpload as CloudUploadIcon, Download as DownloadIcon, Visibility as VisibilityIcon, FlashOn as FlashOnIcon } from '@mui/icons-material';
import axios from 'axios';
import { Link } from 'react-router-dom';

function AnkiPage() {
  const [decks, setDecks] = useState([]);
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    subject_id: '',
    description: '',
  });
  const [subjects, setSubjects] = useState([]);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deckToDelete, setDeckToDelete] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [decksResponse, notesResponse, subjectsResponse] = await Promise.all([
        axios.get('/api/anki/decks'),
        axios.get('/api/notes?limit=100'),
        axios.get('/api/subjects'),
      ]);
      
      setDecks(decksResponse.data || []);
      setNotes(notesResponse.data || []);
      setSubjects(subjectsResponse.data || []);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDeck = async () => {
    try {
      await axios.post('/api/anki/decks', formData);
      fetchData();
      handleCloseDialog();
    } catch (error) {
      console.error('Error creating deck:', error);
    }
  };

  const handleDeleteDeck = async () => {
    if (!deckToDelete) return;
    
    try {
      await axios.delete(`/api/anki/decks/${deckToDelete.id}`);
      fetchData();
      setDeleteDialogOpen(false);
      setDeckToDelete(null);
    } catch (error) {
      console.error('Error deleting deck:', error);
    }
  };

  const handleExportAll = async () => {
    setExporting(true);
    setExportProgress(0);
    
    try {
      // Export all cards
      await axios.post('/api/anki/export');
      setExportProgress(100);
    } catch (error) {
      console.error('Error exporting to Anki:', error);
    } finally {
      setExporting(false);
    }
  };

  const handleExportDeck = async (deckId) => {
    setExporting(true);
    setExportProgress(0);
    
    try {
      await axios.post('/api/anki/export', { deck_id: deckId });
      setExportProgress(100);
    } catch (error) {
      console.error('Error exporting deck to Anki:', error);
    } finally {
      setExporting(false);
    }
  };

  const handleOpenDialog = () => {
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setFormData({
      name: '',
      subject_id: '',
      description: '',
    });
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const checkAnkiConnection = async () => {
    try {
      const response = await axios.get('/api/health');
      return response.data.services.anki === 'ok';
    } catch (error) {
      return false;
    }
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
        <Typography>Chargement...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="div">
          Cartes Anki
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button 
            variant="outlined" 
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleOpenDialog}
          >
            Nouveau deck
          </Button>
          
          <Button 
            variant="contained" 
            color="success"
            startIcon={<CloudUploadIcon />}
            onClick={handleExportAll}
            disabled={exporting || decks.length === 0}
          >
            {exporting ? 'Export en cours...' : 'Exporter tout vers Anki'}
          </Button>
        </Box>
      </Box>

      {exporting && (
        <Box sx={{ mb: 3 }}>
          <LinearProgress variant="determinate" value={exportProgress} />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Export: {exportProgress}%
          </Typography>
        </Box>
      )}

      {/* Info Card */}
      <Card elevation={2} sx={{ mb: 3, p: 2, bgcolor: 'background.paper' }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <FlashOnIcon color="warning" sx={{ mr: 2, fontSize: 40 }} />
          <Box>
            <Typography variant="h6">
              Connexion Anki
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Assurez-vous que l'add-on Anki-Connect est installé et que Anki est ouvert.
            </Typography>
          </Box>
        </Box>
      </Card>

      {/* Decks Grid */}
      <Grid container spacing={3}>
        {decks.length === 0 ? (
          <Grid item xs={12}>
            <Card elevation={2}>
              <CardContent sx={{ textAlign: 'center', p: 4 }}>
                <Typography variant="body1" color="text.secondary">
                  Aucun deck trouvé
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Créez un deck ou générez des cartes à partir de vos notes
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ) : (
          decks.map((deck) => (
            <Grid item xs={12} sm={6} md={4} key={deck.id}>
              <Card elevation={2}>
                <CardContent sx={{ p: 3 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6" component="div">
                      {deck.name}
                    </Typography>
                    <Chip 
                      label={deck.is_synced ? 'Synchronisé' : 'Non synchronisé'}
                      color={deck.is_synced ? 'success' : 'warning'}
                      size="small"
                    />
                  </Box>
                  
                  {deck.description && (
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {deck.description}
                    </Typography>
                  )}
                  
                  <Divider sx={{ my: 1 }} />
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                      {deck.cards?.length || 0} cartes
                    </Typography>
                    
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Tooltip title="Exporter vers Anki">
                        <IconButton 
                          size="small" 
                          color="success"
                          onClick={() => handleExportDeck(deck.id)}
                        >
                          <CloudUploadIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      
                      <Tooltip title="Modifier">
                        <IconButton 
                          size="small" 
                          color="primary"
                          onClick={() => handleOpenDialog(deck)}
                        >
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      
                      <Tooltip title="Supprimer">
                        <IconButton 
                          size="small" 
                          color="error"
                          onClick={() => {
                            setDeckToDelete(deck);
                            setDeleteDialogOpen(true);
                          }}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))
        )}
      </Grid>

      {/* Notes with Anki Cards */}
      {notes.filter(note => note.anki_cards && note.anki_cards.length > 0).length > 0 && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="h5" gutterBottom>
            Notes avec cartes Anki
          </Typography>
          
          <Grid container spacing={2}>
            {notes.filter(note => note.anki_cards && note.anki_cards.length > 0).map((note) => (
              <Grid item xs={12} sm={6} md={4} key={note.id}>
                <Card elevation={2}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {note.title}
                    </Typography>
                    <Chip 
                      label={`${note.anki_cards.length} cartes`}
                      color="primary"
                      size="small"
                      sx={{ mr: 1 }}
                    />
                    <Chip 
                      label={note.subject_name || 'Non classé'}
                      size="small"
                    />
                  </CardContent>
                  <CardActions>
                    <Button 
                      size="small" 
                      color="primary"
                      component={Link} 
                      to={`/notes/${note.id}`}
                    >
                      Voir
                    </Button>
                    <Button 
                      size="small" 
                      color="success"
                      onClick={() => handleExportDeck(null, note.id)}
                    >
                      Exporter
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {/* Create Deck Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          Nouveau deck Anki
        </DialogTitle>
        
        <DialogContent sx={{ p: 3 }}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Nom du deck"
                name="name"
                value={formData.name}
                onChange={handleChange}
                variant="outlined"
                autoFocus
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                select
                fullWidth
                label="Matière associée"
                name="subject_id"
                value={formData.subject_id}
                onChange={handleChange}
                variant="outlined"
              >
                <MenuItem value="">Aucune matière</MenuItem>
                {subjects.map((subject) => (
                  <MenuItem key={subject.id} value={subject.id}>
                    {subject.name}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                variant="outlined"
                multiline
                rows={3}
              />
            </Grid>
          </Grid>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={handleCloseDialog} color="secondary">
            Annuler
          </Button>
          <Button 
            onClick={handleCreateDeck} 
            color="primary" 
            variant="contained"
          >
            Créer
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Deck Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        aria-labelledby="delete-dialog-title"
      >
        <DialogTitle id="delete-dialog-title">
          Supprimer le deck
        </DialogTitle>
        <DialogContent>
          {deckToDelete && (
            <Typography>
              Êtes-vous sûr de vouloir supprimer le deck "{deckToDelete.name}" ?
              Les cartes associées seront également supprimées.
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)} color="primary">
            Annuler
          </Button>
          <Button onClick={handleDeleteDeck} color="error" autoFocus>
            Supprimer
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default AnkiPage;
