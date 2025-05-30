const pickFolderBtn = document.getElementById('pickFolderBtn');
const folderPathDiv = document.getElementById('folderPath');
const fileListDiv = document.getElementById('fileList');

pickFolderBtn.onclick = async () => {
  const folder = await window.gemmaAPI.pickFolder();
  if (!folder) return;
  folderPathDiv.textContent = `Selected: ${folder}`;
  fileListDiv.innerHTML = 'Loading...';
  const files = await window.gemmaAPI.getFiles(folder);
  fileListDiv.innerHTML = files.map(f => `<div class="file-item">${f.replace(folder, '.')}</div>`).join('');
};
