import React, { useState, useEffect } from 'react';
import { Box, Typography, Button, Grid, Card, CardContent, CardActions, Chip, TextField, MenuItem, IconButton, Tooltip, LinearProgress, Dialog, DialogTitle, DialogContent, DialogActions } from '@mui/material';
import { Add as AddIcon, Search as SearchIcon, Delete as DeleteIcon, Edit as EditIcon, Visibility as VisibilityIcon, FileCopy as FileCopyIcon, CheckCircle as CheckCircleIcon, Pending as PendingIcon } from '@mui/icons-material';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { DataGrid } from '@mui/x-data-grid';

function NotesPage() {
  const [notes, setNotes] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSubject, setSelectedSubject] = useState('');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [noteToDelete, setNoteToDelete] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [notesResponse, subjectsResponse] = await Promise.all([
        axios.get('/api/notes?limit=100'),
        axios.get('/api/subjects'),
      ]);
      
      setNotes(notesResponse.data || []);
      setSubjects(subjectsResponse.data || []);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!noteToDelete) return;
    
    try {
      await axios.delete(`/api/notes/${noteToDelete.id}`);
      setNotes(notes.filter(note => note.id !== noteToDelete.id));
      setDeleteDialogOpen(false);
      setNoteToDelete(null);
    } catch (error) {
      console.error('Error deleting note:', error);
    }
  };

  const handleProcess = async (noteId) => {
    try {
      await axios.post(`/api/notes/${noteId}/process`, {
        do_ocr: true,
        do_summary: true,
        do_formulas: true,
        do_anki: false,
      });
      // Refresh data
      fetchData();
    } catch (error) {
      console.error('Error processing note:', error);
    }
  };

  const handleDuplicate = async (noteId) => {
    // This would implement note duplication
    console.log('Duplicate note:', noteId);
  };

  const filteredNotes = notes.filter(note => {
    const matchesSearch = !searchQuery || 
      note.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (note.subject_name && note.subject_name.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (note.tags && note.tags.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesSubject = !selectedSubject || note.subject_id === parseInt(selectedSubject);
    
    return matchesSearch && matchesSubject;
  });

  const columns = [
    {
      field: 'title',
      headerName: 'Titre',
      flex: 1,
      renderCell: (params) => (
        <Box>
          <Typography variant="body1">{params.value}</Typography>
          {params.row.tags && (
            <Chip label={params.row.tags} size="small" color="secondary" sx={{ mt: 0.5 }} />
          )}
        </Box>
      ),
    },
    {
      field: 'subject_name',
      headerName: 'Matière',
      width: 150,
      renderCell: (params) => (
        <Chip label={params.value || 'Non classé'} color="primary" size="small" />
      ),
    },
    {
      field: 'file_type',
      headerName: 'Type',
      width: 120,
      renderCell: (params) => (
        <Chip label={params.value || 'Texte'} size="small" />
      ),
    },
    {
      field: 'word_count',
      headerName: 'Mots',
      width: 100,
    },
    {
      field: 'is_processed',
      headerName: 'Statut',
      width: 120,
      renderCell: (params) => (
        params.value ? (
          <Chip icon={<CheckCircleIcon />} label="Traité" color="success" size="small" />
        ) : (
          <Chip icon={<PendingIcon />} label="En attente" color="warning" size="small" />
        )
      ),
    },
    {
      field: 'created_at',
      headerName: 'Date',
      width: 180,
      valueFormatter: (params) => new Date(params).toLocaleDateString('fr-FR'),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 150,
      sortable: false,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Voir">
            <IconButton 
              size="small" 
              color="primary"
              component={Link} 
              to={`/notes/${params.row.id}`}
            >
              <VisibilityIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Traiter">
            <IconButton 
              size="small" 
              color="secondary"
              onClick={() => handleProcess(params.row.id)}
              disabled={params.row.is_processed}
            >
              <FileCopyIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Dupliquer">
            <IconButton 
              size="small" 
              color="info"
              onClick={() => handleDuplicate(params.row.id)}
            >
              <FileCopyIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Supprimer">
            <IconButton 
              size="small" 
              color="error"
              onClick={() => {
                setNoteToDelete(params.row);
                setDeleteDialogOpen(true);
              }}
            >
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      ),
    },
  ];

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
        <Typography>Chargement des notes...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="div">
          Mes Notes
        </Typography>
        
        <Button 
          variant="contained" 
          color="primary"
          startIcon={<AddIcon />}
          component={Link} 
          to="/notes/upload"
        >
          Ajouter une note
        </Button>
      </Box>

      {/* Filters */}
      <Card elevation={2} sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={6} md={4}>
            <TextField
              fullWidth
              label="Rechercher"
              variant="outlined"
              size="small"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon color="action" sx={{ mr: 1 }} />,
              }}
            />
          </Grid>
          
          <Grid item xs={12} sm={6} md={4}>
            <TextField
              select
              fullWidth
              label="Matière"
              variant="outlined"
              size="small"
              value={selectedSubject}
              onChange={(e) => setSelectedSubject(e.target.value)}
            >
              <MenuItem value="">Toutes les matières</MenuItem>
              {subjects.map((subject) => (
                <MenuItem key={subject.id} value={subject.id}>
                  {subject.name}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          
          <Grid item xs={12} sm={6} md={4}>
            <Button 
              variant="outlined" 
              color="secondary"
              onClick={() => {
                setSearchQuery('');
                setSelectedSubject('');
              }}
              fullWidth
            >
              Réinitialiser
            </Button>
          </Grid>
        </Grid>
      </Card>

      {/* Notes Table */}
      <Card elevation={2} sx={{ p: 2 }}>
        <Box sx={{ height: 500, width: '100%' }}>
          <DataGrid
            rows={filteredNotes}
            columns={columns}
            pageSize={10}
            rowsPerPageOptions={[10, 25, 50]}
            getRowId={(row) => row.id}
            localeText={{
              noRowsLabel: 'Aucune note trouvée',
              toolbarDensity: 'Taille',
              toolbarDensityLabel: 'Taille',
              toolbarDensityCompact: 'Compact',
              toolbarDensityStandard: 'Standard',
              toolbarDensityComfortable: 'Confortable',
            }}
          />
        </Box>
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
          {noteToDelete && (
            <Typography>
              Êtes-vous sûr de vouloir supprimer la note "{noteToDelete.title}" ?
              Cette action est irréversible.
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

export default NotesPage;
