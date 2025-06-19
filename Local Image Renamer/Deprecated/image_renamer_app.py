<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Local Image Renamer</title>
  <style>
    body { font-family: sans-serif; text-align: center; padding: 2rem; background: #111; color: #f5f5f5; }
    #drop-area {
      border: 2px dashed #888;
      padding: 2rem;
      margin: auto;
      max-width: 500px;
      background: #222;
      border-radius: 1rem;
      transition: 0.3s;
    }
    #drop-area.hover { border-color: #4caf50; background: #333; }
    input[type="file"] { display: none; }
    button { margin-top: 1rem; padding: 0.5rem 1rem; cursor: pointer; }
    #status { margin-top: 1rem; }
  </style>
</head>
<body>
  <h1>Bulk Image Renamer</h1>
  <div id="drop-area">
    <p>Drag and drop a folder of images here</p>
    <input type="file" id="folderInput" webkitdirectory directory multiple />
    <button onclick="document.getElementById('folderInput').click()">Select Folder</button>
    <div id="status"></div>
  </div>

  <script>
    const dropArea = document.getElementById('drop-area');
    const folderInput = document.getElementById('folderInput');
    const status = document.getElementById('status');

    ['dragenter', 'dragover'].forEach(evt => {
      dropArea.addEventListener(evt, e => {
        e.preventDefault();
        dropArea.classList.add('hover');
      });
    });

    ['dragleave', 'drop'].forEach(evt => {
      dropArea.addEventListener(evt, e => {
        e.preventDefault();
        dropArea.classList.remove('hover');
      });
    });

    dropArea.addEventListener('drop', e => {
      handleFiles(e.dataTransfer.files);
    });

    folderInput.addEventListener('change', e => {
      handleFiles(e.target.files);
    });

    function handleFiles(fileList) {
      const files = Array.from(fileList).filter(f => /\.(jpe?g|png|webp)$/i.test(f.name));
      if (files.length === 0) return alert("No supported images found.");

      const formData = new FormData();
      files.forEach(f => formData.append("files", f));
      status.textContent = `Uploading ${files.length} images...`;

      fetch("http://localhost:5000/upload", {
        method: "POST",
        body: formData
      })
      .then(r => r.json())
      .then(data => {
        status.textContent = "Renaming complete. Groups created:" + Object.keys(data.groups).join(", ");
      })
      .catch(err => {
        console.error(err);
        status.textContent = "Error during upload.";
      });
    }
  </script>
</body>
</html>
