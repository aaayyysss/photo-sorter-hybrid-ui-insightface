const socket = io("http://130.162.243.107:5000");  // Replace with real server IP

function appendLog(message) {
  const statusLog = document.getElementById('statusLog');
  statusLog.textContent += message + "\n";
  statusLog.scrollTop = statusLog.scrollHeight;
}

const slider = document.getElementById("thresholdSlider");
const valueLabel = document.getElementById("thresholdValue");
slider.oninput = function() {
  valueLabel.innerText = this.value;
};

document.getElementById('buildButton').addEventListener('click', () => {
  const refPath = document.getElementById('refInput').value;
  const unsortedPath = document.getElementById('unsortedInput').value;
  const outputPath = document.getElementById('outputInput').value;

  appendLog('🟡 Sending build reference request...');
  socket.emit('build_reference', { refPath, unsortedPath, outputPath });
});

document.getElementById('startButton').addEventListener('click', () => {
  const refPath = document.getElementById('refInput').value;
  const unsortedPath = document.getElementById('unsortedInput').value;
  const outputPath = document.getElementById('outputInput').value;
  const threshold = parseFloat(document.getElementById('thresholdSlider').value);

  appendLog('🟡 Starting photo sorting...');
  socket.emit('start_sorting', { refPath, unsortedPath, outputPath, threshold });
});

socket.on('log', (msg) => appendLog(msg));
socket.on('build_reference_done', (msg) => {
  appendLog(`✅ ${msg}`);
  document.getElementById('startButton').disabled = false;
});
socket.on('build_reference_error', (err) => appendLog(`❌ ERROR: ${err}`));
socket.on('sorting_done', (msg) => appendLog(`✅ ${msg}`));
socket.on('sorting_error', (err) => appendLog(`❌ ERROR: ${err}`));
