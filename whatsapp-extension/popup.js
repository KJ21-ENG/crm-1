// Popup script for CRM WhatsApp Extension
document.addEventListener('DOMContentLoaded', function() {
  const statusDot = document.getElementById('status-dot');
  const statusText = document.getElementById('status-text');
  const connectBtn = document.getElementById('connect-btn');
  const logoutBtn = document.getElementById('logout-btn');
  const refreshBtn = document.getElementById('refresh-btn');
  const qrSection = document.getElementById('qr-section');
  const qrCodeImage = document.getElementById('qr-code-image');
  const phoneInfo = document.getElementById('phone-info');
  const phoneNumber = document.getElementById('phone-number');
  const refreshQrBtn = document.getElementById('refresh-qr-btn');

  // Initialize popup
  updateStatus();

  // Event listeners
  connectBtn.addEventListener('click', connectWhatsApp);
  logoutBtn.addEventListener('click', logoutWhatsApp);
  refreshBtn.addEventListener('click', updateStatus);
  refreshQrBtn.addEventListener('click', refreshQRCode);

  // Update status from background script
  async function updateStatus() {
    try {
      const response = await sendMessageToBackground('getStatus');
      updateUI(response.status, response.qrCode, response.phoneNumber);
    } catch (error) {
      console.error('Failed to get status:', error);
      updateUI('disconnected');
    }
  }

  // Update UI based on status
  function updateUI(status, qrCode = null, phone = null) {
    // Update status indicator
    statusDot.className = `status-dot ${status}`;
    statusText.textContent = `Status: ${status.charAt(0).toUpperCase() + status.slice(1)}`;

    // Show/hide buttons based on status
    if (status === 'connected') {
      connectBtn.style.display = 'none';
      logoutBtn.style.display = 'block';
      qrSection.style.display = 'none';
      
      // Show phone info if available
      if (phone) {
        phoneInfo.style.display = 'block';
        phoneNumber.textContent = phone;
      } else {
        phoneInfo.style.display = 'none';
      }
    } else {
      connectBtn.style.display = 'block';
      logoutBtn.style.display = 'none';
      phoneInfo.style.display = 'none';
    }

    // Show QR code if available and not connected
    if (qrCode && status !== 'connected') {
      qrSection.style.display = 'block';
      qrCodeImage.innerHTML = `<img src="data:image/png;base64,${qrCode}" alt="WhatsApp QR Code">`;
    } else if (status === 'connected') {
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

  // Logout WhatsApp
  async function logoutWhatsApp() {
    try {
      logoutBtn.textContent = 'Logging out...';
      logoutBtn.disabled = true;

      const response = await fetch('http://localhost:3001/logout', { 
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();

      if (result.success) {
        // Update UI to disconnected state
        updateUI('disconnected');
        
        // Request new QR code after a short delay
        setTimeout(async () => {
          try {
            const qrRequestResponse = await fetch('http://localhost:3001/request-qr', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              }
            });
            
            if (qrRequestResponse.ok) {
              // Wait a bit more for QR code to be generated
              setTimeout(async () => {
                try {
                  const qrResponse = await sendMessageToBackground('getQRCode');
                  if (qrResponse.qrCode) {
                    updateUI('connecting', qrResponse.qrCode);
                    pollConnectionStatus();
                  } else {
                    updateUI('disconnected');
                  }
                } catch (error) {
                  console.error('Failed to get new QR code after logout:', error);
                  updateUI('disconnected');
                }
              }, 3000); // Wait 3 seconds for QR generation
            } else {
              console.error('Failed to request new QR code');
              updateUI('disconnected');
            }
          } catch (error) {
            console.error('Failed to request new QR code after logout:', error);
            updateUI('disconnected');
          }
        }, 1000);
      } else {
        throw new Error(result.message || 'Logout failed');
      }
    } catch (error) {
      console.error('Failed to logout:', error);
      alert('Failed to logout WhatsApp: ' + error.message);
      updateUI('disconnected');
    } finally {
      logoutBtn.textContent = 'Logout WhatsApp';
      logoutBtn.disabled = false;
    }
  }

  // Refresh QR Code
  async function refreshQRCode() {
    try {
      refreshQrBtn.textContent = 'Refreshing...';
      refreshQrBtn.disabled = true;

      const response = await sendMessageToBackground('getQRCode');
      if (response.qrCode) {
        updateUI('connecting', response.qrCode);
        pollConnectionStatus();
      } else {
        throw new Error('Failed to get new QR code');
      }
    } catch (error) {
      console.error('Failed to refresh QR code:', error);
      alert('Failed to refresh QR code: ' + error.message);
    } finally {
      refreshQrBtn.textContent = 'Refresh QR Code';
      refreshQrBtn.disabled = false;
    }
  }

  // Poll for connection status
  function pollConnectionStatus() {
    const pollInterval = setInterval(async () => {
      try {
        const response = await sendMessageToBackground('getStatus');
        if (response.status === 'connected') {
          clearInterval(pollInterval);
          updateUI('connected', null, response.phoneNumber);
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