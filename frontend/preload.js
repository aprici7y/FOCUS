const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  send: (channel, data) => {
    ipcRenderer.send(channel, data);
  },
  receive: (channel, func) => {
    ipcRenderer.on(channel, (event, ...args) => func(...args));
  },
  saveApiKeys: (keys) => ipcRenderer.invoke('save-api-keys', keys),
  getApiKeys: () => ipcRenderer.invoke('get-api-keys'),
  submitPlaylist: (data) => ipcRenderer.invoke('submit-playlist', data),
  submitTranscript: (data) => ipcRenderer.invoke('submit-transcript', data) 
});