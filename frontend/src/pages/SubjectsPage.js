import React, { useState, useEffect } from 'react';
import { Box, Typography, Button, Grid, Card, CardContent, CardActions, TextField, Dialog, DialogTitle, DialogContent, DialogActions, IconButton, Tooltip, Chip, LinearProgress } from '@mui/material';
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon, Save as SaveIcon, Cancel as CancelIcon, ColorLens as ColorLensIcon } from '@mui/icons-material';
import axios from 'axios';

function SubjectsPage() {
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [currentSubject, setCurrentSubject] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [subjectToDelete, setSubjectToDelete] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    color: '#4285F4',
    icon: '📚',
  });

  useEffect(() => {
    fetchSubjects();
  }, []);

  const fetchSubjects = async () => {
    try {
      const response = await axios.get('/api/subjects');
      setSubjects(response.data || []);
    } catch (error) {
      console.error('Error fetching subjects:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      await axios.post('/api/subjects', formData);
      fetchSubjects();
      handleCloseDialog();
    } catch (error) {
      console.error('Error creating subject:', error);
    }
  };

  const handleUpdate = async () => {
    if (!currentSubject) return;
    
    try {
      await axios.put(`/api/subjects/${currentSubject.id}`, formData);
      fetchSubjects();
      handleCloseDialog();
    } catch (error) {
      console.error('Error updating subject:', error);
    }
  };

  const handleDelete = async () => {
    if (!subjectToDelete) return;
    
    try {
      await axios.delete(`/api/subjects/${subjectToDelete.id}`);
      fetchSubjects();
      setDeleteDialogOpen(false);
      setSubjectToDelete(null);
    } catch (error) {
      console.error('Error deleting subject:', error);
    }
  };

  const handleOpenDialog = (subject = null) => {
    if (subject) {
      setCurrentSubject(subject);
      setFormData({
        name: subject.name,
        description: subject.description || '',
        color: subject.color || '#4285F4',
        icon: subject.icon || '📚',
      });
    } else {
      setCurrentSubject(null);
      setFormData({
        name: '',
        description: '',
        color: '#4285F4',
        icon: '📚',
      });
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setCurrentSubject(null);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const colors = [
    '#4285F4', '#34A853', '#FBBC05', '#EA4335', '#9C27B0', 
    '#FF5722', '#009688', '#795548', '#607D8B', '#E91E63'
  ];

  const icons = ['📚', '📖', '🧪', '🔢', '🎨', '💻', '🌍', '📜', '📊', '⚗️'];

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
        <Typography>Chargement des matières...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="div">
          Matières
        </Typography>
        
        <Button 
          variant="contained" 
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Ajouter une matière
        </Button>
      </Box>

      {/* Subjects Grid */}
      <Grid container spacing={3}>
        {subjects.length === 0 ? (
          <Grid item xs={12}>
            <Card elevation={2}>
              <CardContent sx={{ textAlign: 'center', p: 4 }}>
                <Typography variant="body1" color="text.secondary">
                  Aucune matière trouvée
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Ajoutez une matière pour commencer à organiser vos notes
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ) : (
          subjects.map((subject) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={subject.id}>
              <Card elevation={2}>
                <CardContent sx={{ p: 3, textAlign: 'center' }}>
                  <Box 
                    sx={{
                      width: 60,
                      height: 60,
                      mx: 'auto',
                      mb: 2,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      borderRadius: '50%',
                      bgcolor: subject.color || '#4285F4',
                      color: 'white',
                      fontSize: '2rem',
                    }}
                  >
                    <span>{subject.icon || '📚'}</span>
                  </Box>
                  
                  <Typography variant="h6" gutterBottom>
                    {subject.name}
                  </Typography>
                  
                  {subject.description && (
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {subject.description}
                    </Typography>
                  )}
                  
                  <Chip 
                    label={`0 notes`}
                    size="small"
                    variant="outlined"
                  />
                </CardContent>
                
                <CardActions sx={{ justifyContent: 'center' }}>
                  <Tooltip title="Modifier">
                    <IconButton 
                      size="small" 
                      color="primary"
                      onClick={() => handleOpenDialog(subject)}
                    >
                      <EditIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  
                  <Tooltip title="Supprimer">
                    <IconButton 
                      size="small" 
                      color="error"
                      onClick={() => {
                        setSubjectToDelete(subject);
                        setDeleteDialogOpen(true);
                      }}
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </CardActions>
              </Card>
            </Grid>
          ))
        )}
      </Grid>

      {/* Subject Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {currentSubject ? 'Modifier la matière' : 'Nouvelle matière'}
        </DialogTitle>
        
        <DialogContent sx={{ p: 3 }}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Nom"
                name="name"
                value={formData.name}
                onChange={handleChange}
                variant="outlined"
                autoFocus
              />
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
            
            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                label="Couleur"
                name="color"
                value={formData.color}
                onChange={handleChange}
                variant="outlined"
              >
                {colors.map((color) => (
                  <MenuItem key={color} value={color}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Box sx={{ width: 20, height: 20, bgcolor: color, mr: 1, borderRadius: 1 }} />
                      {color}
                    </Box>
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                label="Icône"
                name="icon"
                value={formData.icon}
                onChange={handleChange}
                variant="outlined"
              >
                {icons.map((icon) => (
                  <MenuItem key={icon} value={icon}>
                    {icon}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
          </Grid>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={handleCloseDialog} color="secondary" startIcon={<CancelIcon />}>
            Annuler
          </Button>
          <Button 
            onClick={currentSubject ? handleUpdate : handleCreate} 
            color="primary" 
            startIcon={<SaveIcon />}
            variant="contained"
          >
            {currentSubject ? 'Enregistrer' : 'Créer'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        aria-labelledby="delete-dialog-title"
      >
        <DialogTitle id="delete-dialog-title">
          Supprimer la matière
        </DialogTitle>
        <DialogContent>
          {subjectToDelete && (
            <Typography>
              Êtes-vous sûr de vouloir supprimer la matière "{subjectToDelete.name}" ?
              Les notes associées ne seront pas supprimées.
            </Typography>
          )}
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
    </Box>
  );
}

export default SubjectsPage;
