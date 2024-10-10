const { app, BrowserWindow, ipcMain, Menu } = require('electron')
const path = require('node:path')

const createWindow = () => {
    const mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false
        }
    })

    mainWindow.loadFile('index.html')
}

app.whenReady().then(() => {
    Menu.setApplicationMenu(null);
    createWindow()

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow()
    })
})

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit()
})

ipcMain.on('submit-form', async (event, formData) => {
    try {
        const response = await fetch('API_ENDPOINT', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
        });

        const data = await response.json();
        event.reply('form-response', { success: true, data });
    } catch (error) {
        console.error('Error:', error);
        event.reply('form-response', { success: false, error: error.message });
    }
});