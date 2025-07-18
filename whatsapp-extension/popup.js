// Popup script for CRM WhatsApp Extension
document.addEventListener('DOMContentLoaded', function() {
  const statusDot = document.getElementById('status-dot');
  const statusText = document.getElementById('status-text');
  const connectBtn = document.getElementById('connect-btn');
  const disconnectBtn = document.getElementById('disconnect-btn');
  const refreshBtn = document.getElementById('refresh-btn');
  const qrSection = document.getElementById('qr-section');
  const qrCodeImage = document.getElementById('qr-code-image');

  // Initialize popup
  updateStatus();

  // Event listeners
  connectBtn.addEventListener('click', connectWhatsApp);
  disconnectBtn.addEventListener('click', disconnectWhatsApp);
  refreshBtn.addEventListener('click', updateStatus);

  // Update status from background script
  async function updateStatus() {
    try {
      const response = await sendMessageToBackground('getStatus');
      updateUI(response.status, response.qrCode);
    } catch (error) {
      console.error('Failed to get status:', error);
      updateUI('disconnected');
    }
  }

  // Update UI based on status
  function updateUI(status, qrCode = null) {
    // Update status indicator
    statusDot.className = `status-dot ${status}`;
    statusText.textContent = `Status: ${status.charAt(0).toUpperCase() + status.slice(1)}`;

    // Show/hide buttons based on status
    if (status === 'connected') {
      connectBtn.style.display = 'none';
      disconnectBtn.style.display = 'block';
      qrSection.style.display = 'none';
    } else {
      connectBtn.style.display = 'block';
      disconnectBtn.style.display = 'none';
    }

    // Show QR code if available
    if (qrCode && status === 'connecting') {
      qrSection.style.display = 'block';
      qrCodeImage.innerHTML = `<img src="data:image/png;base64,${qrCode}" alt="WhatsApp QR Code">`;
    } else {
      qrSection.style.display = 'none';
    }
  }

  // Connect WhatsApp
  async function connectWhatsApp() {
    try {
      connectBtn.textContent = 'Connecting...';
      connectBtn.disabled = true;

      const response = await sendMessageToBackground('getQRCode');
      if (response.qrCode) {
        updateUI('connecting', response.qrCode);
        
        // Start polling for connection status
        pollConnectionStatus();
      } else {
        throw new Error('Failed to get QR code');
      }
    } catch (error) {
      console.error('Failed to connect:', error);
      alert('Failed to connect WhatsApp: ' + error.message);
      updateUI('disconnected');
    } finally {
      connectBtn.textContent = 'Connect WhatsApp';
      connectBtn.disabled = false;
    }
  }

  // Disconnect WhatsApp
  async function disconnectWhatsApp() {
    try {
      disconnectBtn.textContent = 'Disconnecting...';
      disconnectBtn.disabled = true;

      // Send disconnect command to local service
      await fetch('http://localhost:3001/disconnect', { method: 'POST' });
      updateUI('disconnected');
    } catch (error) {
      console.error('Failed to disconnect:', error);
      alert('Failed to disconnect WhatsApp: ' + error.message);
    } finally {
      disconnectBtn.textContent = 'Disconnect';
      disconnectBtn.disabled = false;
    }
  }

  // Poll for connection status
  function pollConnectionStatus() {
    const pollInterval = setInterval(async () => {
      try {
        const response = await sendMessageToBackground('getStatus');
        if (response.status === 'connected') {
          clearInterval(pollInterval);
          updateUI('connected');
        } else if (response.status === 'disconnected') {
          clearInterval(pollInterval);
          updateUI('disconnected');
        }
      } catch (error) {
        console.error('Polling error:', error);
        clearInterval(pollInterval);
        updateUI('disconnected');
      }
    }, 2000); // Poll every 2 seconds

    // Stop polling after 2 minutes
    setTimeout(() => {
      clearInterval(pollInterval);
    }, 120000);
  }

  // Send message to background script
  function sendMessageToBackground(action, data = {}) {
    return new Promise((resolve, reject) => {
      chrome.runtime.sendMessage({ action, ...data }, (response) => {
        if (chrome.runtime.lastError) {
          reject(new Error(chrome.runtime.lastError.message));
        } else {
          resolve(response);
        }
      });
    });
  }
}); 