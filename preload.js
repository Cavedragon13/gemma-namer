const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('gemmaAPI', {
  pickFolder: () => ipcRenderer.invoke('pick-folder'),
  getFiles: (folderPath) => ipcRenderer.invoke('get-files', folderPath),
});
