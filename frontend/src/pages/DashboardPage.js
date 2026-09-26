import React, { useState, useEffect } from 'react';
import { Box, Typography, Grid, Card, CardContent, CardActions, Button, Chip, LinearProgress } from '@mui/material';
import { Upload as UploadIcon, Book as BookIcon, Assessment as AssessmentIcon, FlashOn as FlashOnIcon } from '@mui/icons-material';
import { Link } from 'react-router-dom';
import axios from 'axios';

function DashboardPage() {
  const [stats, setStats] = useState({
    totalNotes: 0,
    totalSubjects: 0,
    processedNotes: 0,
    ankiCards: 0,
  });
  const [loading, setLoading] = useState(true);
  const [recentNotes, setRecentNotes] = useState([]);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        // Fetch notes
        const notesResponse = await axios.get('/api/notes?limit=100');
        const notes = notesResponse.data || [];
        
        // Fetch subjects
        const subjectsResponse = await axios.get('/api/subjects');
        const subjects = subjectsResponse.data || [];
        
        // Fetch Anki cards
        const ankiResponse = await axios.get('/api/anki/decks');
        const ankiDecks = ankiResponse.data || [];
        
        setStats({
          totalNotes: notes.length,
          totalSubjects: subjects.length,
          processedNotes: notes.filter(n => n.is_processed).length,
          ankiCards: ankiDecks.reduce((sum, deck) => sum + (deck.cards?.length || 0), 0),
        });
        
        // Get recent notes
        setRecentNotes(notes.slice(0, 5));
      } catch (error) {
        console.error('Error fetching stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
        <Typography>Chargement...</Typography>
      </Box>
    );
  }

  const progress = stats.totalNotes > 0 ? (stats.processedNotes / stats.totalNotes) * 100 : 0;

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Tableau de bord
      </Typography>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={3}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <BookIcon color="primary" sx={{ mr: 1, fontSize: 40 }} />
                <Typography variant="h5" component="div">
                  Matières
                </Typography>
              </Box>
              <Typography variant="h3" color="primary">
                {stats.totalSubjects}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={3}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <UploadIcon color="secondary" sx={{ mr: 1, fontSize: 40 }} />
                <Typography variant="h5" component="div">
                  Notes
                </Typography>
              </Box>
              <Typography variant="h3" color="secondary">
                {stats.totalNotes}
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={progress} 
                sx={{ mt: 1, height: 8, borderRadius: 4 }}
              />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {stats.processedNotes} traitées
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={3}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <AssessmentIcon color="success" sx={{ mr: 1, fontSize: 40 }} />
                <Typography variant="h5" component="div">
                  Résumés
                </Typography>
              </Box>
              <Typography variant="h3" color="success.main">
                {stats.processedNotes}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={3}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <FlashOnIcon color="warning" sx={{ mr: 1, fontSize: 40 }} />
                <Typography variant="h5" component="div">
                  Cartes Anki
                </Typography>
              </Box>
              <Typography variant="h3" color="warning.main">
                {stats.ankiCards}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" gutterBottom>
          Actions rapides
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Button 
              variant="contained" 
              color="primary"
              component={Link} 
              to="/notes/upload"
              fullWidth
              startIcon={<UploadIcon />}
              sx={{ py: 2 }}
            >
              Ajouter une note
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button 
              variant="outlined" 
              color="primary"
              component={Link} 
              to="/subjects"
              fullWidth
              startIcon={<BookIcon />}
              sx={{ py: 2 }}
            >
              Gérer les matières
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button 
              variant="outlined" 
              color="secondary"
              component={Link} 
              to="/anki"
              fullWidth
              startIcon={<FlashOnIcon />}
              sx={{ py: 2 }}
            >
              Exporter vers Anki
            </Button>
          </Grid>
        </Grid>
      </Box>

      {/* Recent Notes */}
      <Box>
        <Typography variant="h5" gutterBottom>
          Notes récentes
        </Typography>
        
        {recentNotes.length === 0 ? (
          <Typography variant="body1" color="text.secondary">
            Aucune note trouvée. <Link to="/notes/upload">Ajoutez-en une</Link> pour commencer.
          </Typography>
        ) : (
          recentNotes.map((note) => (
            <Card key={note.id} elevation={2} sx={{ mb: 2 }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Typography variant="h6" component="div">
                    {note.title}
                  </Typography>
                  <Chip 
                    label={note.subject_name || 'Non classé'}
                    color="primary"
                    size="small"
                  />
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Chip 
                    label={note.file_type || 'texte'}
                    size="small"
                    sx={{ mr: 1 }}
                  />
                  <Chip 
                    label={`${note.word_count || 0} mots`}
                    size="small"
                    sx={{ mr: 1 }}
                  />
                  <Chip 
                    label={note.is_processed ? 'Traité' : 'En attente'}
                    color={note.is_processed ? 'success' : 'warning'}
                    size="small"
                  />
                </Box>
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
                  color="secondary"
                  onClick={async () => {
                    try {
                      await axios.post(`/api/notes/${note.id}/process`, {
                        do_ocr: !note.is_ocr_done,
                        do_summary: !note.is_summary_done,
                        do_formulas: !note.is_formulas_done,
                        do_anki: false,
                      });
                      window.location.reload();
                    } catch (error) {
                      console.error('Error processing note:', error);
                    }
                  }}
                >
                  {note.is_processed ? 'Retraiter' : 'Traiter'}
                </Button>
              </CardActions>
            </Card>
          ))
        )}
      </Box>
    </Box>
  );
}

export default DashboardPage;
