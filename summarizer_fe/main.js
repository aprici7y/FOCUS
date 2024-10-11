const { app, BrowserWindow, ipcMain, Menu } = require('electron');
const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const keytar = require('keytar');

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