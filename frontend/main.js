const { app, BrowserWindow, ipcMain, Menu } = require('electron');
const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const keytar = require('keytar');
const axios = require('axios');


let db;

const initDatabase = () => {
  return new Promise((resolve, reject) => {
    const dbPath = path.join(app.getPath('userData'), 'apikeys.sqlite');
    db = new sqlite3.Database(dbPath, (err) => {
      if (err) {
        console.error('Database opening error: ', err);
        reject(err);
      } else {
        console.log('Database created or opened successfully at:', dbPath);
        db.run(`CREATE TABLE IF NOT EXISTS api_keys (
          id TEXT PRIMARY KEY,
          service TEXT NOT NULL
        )`, (err) => {
          if (err) {
            console.error('Table creation error: ', err);
            reject(err);
          } else {
            console.log('API keys table created or already exists');
            resolve();
          }
        });
      }
    });
  });
};

const createWindow = () => {
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });
  mainWindow.webContents.openDevTools()
  mainWindow.loadFile('index.html');
};

app.whenReady().then(async () => {
  try {
    await initDatabase();
    console.log('Database initialized successfully');
  } catch (error) {
    console.error('Failed to initialize database:', error);
  }
  
  Menu.setApplicationMenu(null);
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

ipcMain.handle('save-api-keys', async (event, keys) => {
  try {
    for (const [id, value] of Object.entries(keys)) {
      await keytar.setPassword('summarizer-app', id, value);
      await new Promise((resolve, reject) => {
        db.run('INSERT OR REPLACE INTO api_keys (id, service) VALUES (?, ?)', [id, 'summarizer-app'], (err) => {
          if (err) reject(err);
          else resolve();
        });
      });
    }
    console.log('API keys saved successfully');
    return { success: true };
  } catch (error) {
    console.error('Error saving API keys:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('get-api-keys', async () => {
  try {
    const keys = {};
    await new Promise((resolve, reject) => {
      db.all('SELECT id FROM api_keys WHERE service = ?', ['summarizer-app'], async (err, rows) => {
        if (err) {
          reject(err);
        } else {
          for (const row of rows) {
            const decryptedValue = await keytar.getPassword('summarizer-app', row.id);
            if (decryptedValue) {
              keys[row.id] = decryptedValue;
            }
          }
          resolve();
        }
      });
    });
    console.log('API keys retrieved successfully');
    return { success: true, keys };
  } catch (error) {
    console.error('Error retrieving API keys:', error);
    return { success: false, error: error.message };
  }
});


// Helper to retrieve an API key from Keytar based on service and key name
const getApiKeyFromKeytar = async (service, keyName) => {
  try {
    const key = await keytar.getPassword(service, keyName);
    if (!key) {
      throw new Error(`API key for ${keyName} not found in Keytar.`);
    }
    return key;
  } catch (error) {
    console.error(`Error retrieving key from Keytar for ${keyName}:`, error);
    throw error;
  }
};

// Helper function to get key names from the database
const getApiKeyName = (service, keyType) => {
  return new Promise((resolve, reject) => {
    db.get(
      'SELECT id FROM api_keys WHERE service = ? AND id = ?',
      [service, keyType],
      (err, row) => {
        if (err) {
          reject(err);
        } else {
          resolve(row ? row.id : null);
        }
      }
    );
  });
};



// IPC handler for processing playlist submission
ipcMain.handle('submit-playlist', async (event, data) => {
  try {
    console.log('Playlist submitted:', data);

    // Retrieve API key names from the database
    const youtubeApiKeyName = await getApiKeyName('summarizer-app', 'youtubeApiKey');
    const mistralApiKeyName = await getApiKeyName('summarizer-app', 'mistralApiKey');
    const obsidianVaultPathName = await getApiKeyName('summarizer-app', 'obsidianVaultPath');


    if (!youtubeApiKeyName || !mistralApiKeyName) {
      throw new Error('Missing API key names in database. Please check your settings.');
    }

    // Retrieve actual API keys from Keytar using the names
    const youtubeApiKey = await getApiKeyFromKeytar('summarizer-app', youtubeApiKeyName);
    const mistralApiKey = await getApiKeyFromKeytar('summarizer-app', mistralApiKeyName);
    const obsidianVaultPath = await getApiKeyFromKeytar('summarizer-app', obsidianVaultPathName);

    // Prepare the request payload
    const payload = {
      playlist_id: data.playlistId,
      action_flag: data.action,
      youtube_api_key: youtubeApiKey,
      mistral_api_key: mistralApiKey,
      obsidian_vault_path: obsidianVaultPath,
    };
    console.log(payload)
    // Send the request to the backend
    const response = await axios.post('http://localhost:5000/api/summarize', payload, {
      headers: { 'Content-Type': 'application/json' },
    });

    if (response.data.status === 'success') {
      return { success: true, message: response.data.message };
    } else {
      throw new Error(response.data.message || 'An error occurred while processing the playlist.');
    }
  } catch (error) {
    console.error('Error processing playlist submission:', error);
    return { success: false, error: error.message };
  }
});

// IPC handler for processing transcript submission
ipcMain.handle('submit-transcript', async (event, data) => {
  try {
    console.log('Transcript submitted:', data);

    // Retrieve API key names from the database
    const mistralApiKeyName = await getApiKeyName('summarizer-app', 'mistralApiKey');
    const obsidianVaultPathName = await getApiKeyName('summarizer-app', 'obsidianVaultPath');

    if (!mistralApiKeyName || !obsidianVaultPathName) {
      throw new Error('Missing API key names in database. Please check your settings.');
    }

    // Retrieve actual API keys from Keytar using the names
    const mistralApiKey = await getApiKeyFromKeytar('summarizer-app', mistralApiKeyName);
    const obsidianVaultPath = await getApiKeyFromKeytar('summarizer-app', obsidianVaultPathName);

    // Prepare the request payload
    const payload = {
      transcript: data.transcript,
      title: data.title,
      course: data.course,
      action_flag: data.action,
      mistral_api_key: mistralApiKey,
      obsidian_vault_path: obsidianVaultPath,
    };

    console.log(payload);

    // Send the request to the backend
    const response = await axios.post('http://localhost:5000/api/process_transcript', payload, {
      headers: { 'Content-Type': 'application/json' },
    });

    if (response.data.status === 'success') {
      return { success: true, message: response.data.message };
    } else {
      throw new Error(response.data.message || 'An error occurred while processing the transcript.');
    }
  } catch (error) {
    console.error('Error processing transcript submission:', error);
    return { success: false, error: error.message };
  }
});