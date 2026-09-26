import React, { useState, useEffect } from 'react';
import { Box, Typography, Card, CardContent, CardActions, Button, TextField, MenuItem, Grid, LinearProgress, Alert, Snackbar } from '@mui/material';
import { Upload as UploadIcon, CloudUpload as CloudUploadIcon } from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function UploadNotePage() {
  const [subjects, setSubjects] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState('');
  const [title, setTitle] = useState('');
  const [tags, setTags] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchSubjects = async () => {
      try {
        const response = await axios.get('/api/subjects');
        setSubjects(response.data || []);
      } catch (error) {
        console.error('Error fetching subjects:', error);
      }
    };

    fetchSubjects();
  }, []);

  const { getRootProps, getInputProps, isDragActive, acceptedFiles } = useDropzone({
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.tiff'],
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        setFile(acceptedFiles[0]);
      }
    },
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Veuillez sélectionner un fichier');
      return;
    }

    setLoading(true);
    setProgress(0);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      
      if (title) formData.append('title', title);
      if (selectedSubject) formData.append('subject_id', selectedSubject);
      if (tags) formData.append('tags', tags);

      const response = await axios.post('/api/notes/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setProgress(percentCompleted);
        },
      });

      setSuccess(`Note téléchargée avec succès! ID: ${response.data.note_id}`);
      
      // Navigate to the note detail page after a short delay
      setTimeout(() => {
        navigate(`/notes/${response.data.note_id}`);
      }, 2000);
      
    } catch (error) {
      console.error('Error uploading note:', error);
      setError('Erreur lors du téléchargement: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleCloseError = () => setError(null);
  const handleCloseSuccess = () => setSuccess(null);

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Ajouter une nouvelle note
      </Typography>

      <Card elevation={3} sx={{ maxWidth: 800, mx: 'auto' }}>
        <CardContent>
          <form onSubmit={handleSubmit}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Titre"
                  variant="outlined"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Titre de la note (optionnel)"
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  select
                  fullWidth
                  label="Matière"
                  variant="outlined"
                  value={selectedSubject}
                  onChange={(e) => setSelectedSubject(e.target.value)}
                >
                  <MenuItem value="">Aucune matière</MenuItem>
                  {subjects.map((subject) => (
                    <MenuItem key={subject.id} value={subject.id}>
                      {subject.name}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Tags"
                  variant="outlined"
                  value={tags}
                  onChange={(e) => setTags(e.target.value)}
                  placeholder="Séparés par des virgules"
                />
              </Grid>

              <Grid item xs={12}>
                <Card 
                  variant="outlined" 
                  sx={{
                    p: 4,
                    textAlign: 'center',
                    cursor: 'pointer',
                    borderColor: isDragActive ? 'primary.main' : 'divider',
                    bgcolor: isDragActive ? 'action.hover' : 'background.paper',
                  }}
                  {...getRootProps()}
                >
                  <input {...getInputProps()} />
                  <CloudUploadIcon color="primary" sx={{ fontSize: 60, mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    {isDragActive 
                      ? 'Déposez le fichier ici' 
                      : 'Glissez-déposez un fichier ici ou cliquez pour sélectionner'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Formats acceptés: PDF, images (JPEG, PNG, etc.), DOCX, TXT
                  </Typography>
                  
                  {file && (
                    <Typography variant="body2" color="primary" sx={{ mt: 2 }}>
                      Fichier sélectionné: {file.name} ({Math.round(file.size / 1024)} Ko)
                    </Typography>
                  )}
                </Card>
              </Grid>

              {loading && (
                <Grid item xs={12}>
                  <LinearProgress variant="determinate" value={progress} />
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    Téléchargement: {progress}%
                  </Typography>
                </Grid>
              )}

              <Grid item xs={12}>
                <CardActions sx={{ justifyContent: 'flex-end' }}>
                  <Button 
                    variant="outlined" 
                    color="secondary"
                    component="a" 
                    href="/notes"
                    sx={{ mr: 2 }}
                  >
                    Annuler
                  </Button>
                  <Button 
                    type="submit" 
                    variant="contained" 
                    color="primary"
                    disabled={loading || !file}
                    startIcon={<UploadIcon />}
                  >
                    {loading ? 'Téléchargement...' : 'Télécharger'}
                  </Button>
                </CardActions>
              </Grid>
            </Grid>
          </form>
        </CardContent>
      </Card>

      {/* Error Snackbar */}
      <Snackbar 
        open={!!error} 
        autoHideDuration={6000} 
        onClose={handleCloseError}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseError} severity="error" sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>

      {/* Success Snackbar */}
      <Snackbar 
        open={!!success} 
        autoHideDuration={6000} 
        onClose={handleCloseSuccess}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSuccess} severity="success" sx={{ width: '100%' }}>
          {success}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default UploadNotePage;
