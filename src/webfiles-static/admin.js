// Divs
const DIV_LOADING = document.getElementById('loading');
const DIV_CONFIG = document.getElementById('config');

// Inputs
const inputWifiSSID = document.getElementById('inputWifiSSID');
const inputWifiPassword = document.getElementById('inputWifiPassword');
const inputMqttServer = document.getElementById('inputMqttServer');
const inputMqttPort = document.getElementById('inputMqttPort');
const inputMqttUsername = document.getElementById('inputMqttUsername');
const inputMqttPassword = document.getElementById('inputMqttPassword');
const inputDeviceName = document.getElementById('inputDeviceName');
const inputAdminPassword = document.getElementById('inputAdminPassword');

const inputThresholdWarning = document.getElementById('inputThresholdWarning');
const inputThresholdAlert = document.getElementById('inputThresholdAlert');
const cbSoundEnabled = document.getElementById('cbSoundEnabled');

// Buttons
const btnSave = document.getElementById('btnSave');
const btnReset = document.getElementById('btnReset');
btnSave.onclick = saveConfig;
btnReset.onclick = resetDevice;

// Start requesting status updates
getConfig();

function getConfig() {
  fetch('/get-config')
      .then((response) => response.json())
      .then((data) => {
        console.log('Config received:', data);
        inputWifiSSID.value = data.wifiSsid;
        inputWifiPassword.value = data.wifiPassword;
        inputMqttServer.value = data.mqttServer;
        inputMqttPort.value = data.mqttPort;
        inputMqttUsername.value = data.mqttUsername;
        inputMqttPassword.value = data.mqttPassword;
        inputDeviceName.value = data.deviceName;
        inputAdminPassword.value = data.adminPassword;
        inputThresholdWarning.value = data.thresholdWarningPpm;
        inputThresholdAlert.value = data.thresholdAlertPpm;
        cbSoundEnabled.checked = data.isSoundOn;

        DIV_LOADING.style.display = 'none';
        DIV_CONFIG.style.display = 'block';
      });
}

async function saveConfig() {
  btnSave.disabled = true;
  btnSave.innerHTML = 'Saving...';

  const config = {
    'wifiSsid': inputWifiSSID.value || '',
    'wifiPassword': inputWifiPassword.value || '',
    'mqttServer': inputMqttServer.value || '',
    'mqttPort': parseInt(inputMqttPort.value, 10) || null,
    'mqttUsername': inputMqttUsername.value || '',
    'mqttPassword': inputMqttPassword.value || '',
    'deviceName': inputDeviceName.value || '',
    'adminPassword': inputAdminPassword.value || '',
    'thresholdWarningPpm': parseInt(inputThresholdWarning.value, 10) || null,
    'thresholdAlertPpm': parseInt(inputThresholdAlert.value, 10) || null,
    'isSoundOn': cbSoundEnabled.checked,
  };
  const dataStr = JSON.stringify(config);
  console.log('save config:', config);

  const response = await fetch('/save-config', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: dataStr,
  });
  console.log('save response:', response);
  btnSave.disabled = false;
  btnSave.innerHTML = 'Saved ✅';
  document.getElementById('savedSubtext').innerHTML = 'Restart the device to apply new network/mqtt configuration.';
}

function resetDevice() {
  btnReset.disabled = true;
  btnReset.innerHTML = 'Restarting...';
  document.getElementById('savedSubtext').innerHTML = 'The device is restarting and will try to connect to the network. Please refresh this page manually.';
  fetch('/reset');
}
