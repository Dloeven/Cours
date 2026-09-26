import React, { useState, useEffect } from 'react';
import { Box, Typography, Card, CardContent, CardHeader, Grid, TextField, Button, Divider, Switch, FormControlLabel, Alert, Snackbar } from '@mui/material';
import { Save as SaveIcon, Settings as SettingsIcon } from '@mui/icons-material';
import axios from 'axios';

function SettingsPage() {
  const [settings, setSettings] = useState({
    apiUrl: '',
    ankiHost: 'localhost',
    ankiPort: '8765',
    ocrLanguage: 'fra+eng',
    defaultDeck: 'Cours Organizer',
    theme: 'light',
    notifications: true,
    autoProcess: false,
  });
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSettings();
    checkHealth();
  }, []);

  const fetchSettings = async () => {
    try {
      // In a real app, we would fetch settings from the backend
      // For now, we'll use default values
      setSettings({
        apiUrl: window.location.origin + '/api',
        ankiHost: localStorage.getItem('ankiHost') || 'localhost',
        ankiPort: localStorage.getItem('ankiPort') || '8765',
        ocrLanguage: localStorage.getItem('ocrLanguage') || 'fra+eng',
        defaultDeck: localStorage.getItem('defaultDeck') || 'Cours Organizer',
        theme: localStorage.getItem('theme') || 'light',
        notifications: localStorage.getItem('notifications') !== 'false',
        autoProcess: localStorage.getItem('autoProcess') === 'true',
      });
    } catch (error) {
      console.error('Error fetching settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const checkHealth = async () => {
    try {
      const response = await axios.get('/api/health');
      setHealth(response.data);
    } catch (error) {
      console.error('Error checking health:', error);
    }
  };

  const handleSave = () => {
    try {
      // Save settings to localStorage
      localStorage.setItem('ankiHost', settings.ankiHost);
      localStorage.setItem('ankiPort', settings.ankiPort);
      localStorage.setItem('ocrLanguage', settings.ocrLanguage);
      localStorage.setItem('defaultDeck', settings.defaultDeck);
      localStorage.setItem('theme', settings.theme);
      localStorage.setItem('notifications', settings.notifications);
      localStorage.setItem('autoProcess', settings.autoProcess);
      
      setSuccess('Paramètres enregistrés avec succès!');
      
      // Reload the page to apply theme changes
      if (settings.theme !== localStorage.getItem('theme')) {
        setTimeout(() => window.location.reload(), 1000);
      }
    } catch (error) {
      setError('Erreur lors de l\'enregistrement des paramètres');
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSettings(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleCloseSuccess = () => setSuccess(null);
  const handleCloseError = () => setError(null);

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        <SettingsIcon color="primary" sx={{ verticalAlign: 'middle', mr: 1 }} />
        Paramètres
      </Typography>

      {/* Health Status */}
      <Card elevation={2} sx={{ mb: 3 }}>
        <CardHeader title="Statut du système" />
        <CardContent>
          {health ? (
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">
                  API
                </Typography>
                <Typography variant="body1">
                  {health.status === 'healthy' ? '✅ Fonctionnel' : '❌ Déconnecté'}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">
                  Version
                </Typography>
                <Typography variant="body1">
                  {health.version}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">
                  Base de données
                </Typography>
                <Typography variant="body1">
                  {health.services?.database === 'ok' ? '✅ Connectée' : '❌ Déconnectée'}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">
                  Anki
                </Typography>
                <Typography variant="body1">
                  {health.services?.anki === 'ok' ? '✅ Connecté' : '❌ Non connecté'}
                </Typography>
              </Grid>
            </Grid>
          ) : (
            <Typography variant="body1" color="text.secondary">
              Chargement du statut...
            </Typography>
          )}
        </CardContent>
      </Card>

      {/* General Settings */}
      <Card elevation={2} sx={{ mb: 3 }}>
        <CardHeader title="Paramètres généraux" />
        <CardContent>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="URL de l'API"
                name="apiUrl"
                value={settings.apiUrl}
                onChange={handleChange}
                variant="outlined"
                disabled
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Langue par défaut de l'OCR"
                name="ocrLanguage"
                value={settings.ocrLanguage}
                onChange={handleChange}
                variant="outlined"
                select
              >
                <MenuItem value="fra+eng">Français + Anglais</MenuItem>
                <MenuItem value="fra">Français</MenuItem>
                <MenuItem value="eng">Anglais</MenuItem>
                <MenuItem value="spa">Espagnol</MenuItem>
                <MenuItem value="deu">Allemand</MenuItem>
              </TextField>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Deck Anki par défaut"
                name="defaultDeck"
                value={settings.defaultDeck}
                onChange={handleChange}
                variant="outlined"
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Switch
                    name="autoProcess"
                    checked={settings.autoProcess}
                    onChange={handleChange}
                    color="primary"
                  />
                }
                label="Traiter automatiquement les nouvelles notes"
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Anki Settings */}
      <Card elevation={2} sx={{ mb: 3 }}>
        <CardHeader title="Paramètres Anki" />
        <CardContent>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Hôte Anki"
                name="ankiHost"
                value={settings.ankiHost}
                onChange={handleChange}
                variant="outlined"
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Port Anki"
                name="ankiPort"
                value={settings.ankiPort}
                onChange={handleChange}
                variant="outlined"
                type="number"
              />
            </Grid>
            
            <Grid item xs={12}>
              <Alert severity="info">
                Assurez-vous que l'add-on Anki-Connect est installé dans Anki et que Anki est ouvert.
              </Alert>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Interface Settings */}
      <Card elevation={2} sx={{ mb: 3 }}>
        <CardHeader title="Interface" />
        <CardContent>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                label="Thème"
                name="theme"
                value={settings.theme}
                onChange={handleChange}
                variant="outlined"
              >
                <MenuItem value="light">Clair</MenuItem>
                <MenuItem value="dark">Sombre</MenuItem>
                <MenuItem value="system">Système</MenuItem>
              </TextField>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Switch
                    name="notifications"
                    checked={settings.notifications}
                    onChange={handleChange}
                    color="primary"
                  />
                }
                label="Activer les notifications"
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Save Button */}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 3 }}>
        <Button 
          variant="contained" 
          color="primary" 
          startIcon={<SaveIcon />}
          onClick={handleSave}
          disabled={loading}
          size="large"
        >
          Enregistrer les paramètres
        </Button>
      </Box>

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
    </Box>
  );
}

export default SettingsPage;

// Add MenuItem import
import { MenuItem } from '@mui/material';
