(() => {
  const token = document.querySelector('meta[name="mscontable-session-token"]')?.content;
  if (!token) return;

  const endpoint = '/_local/session-heartbeat/';
  const tabId = typeof crypto.randomUUID === 'function'
    ? crypto.randomUUID().replaceAll('-', '')
    : Array.from(crypto.getRandomValues(new Uint8Array(16)), (byte) => byte.toString(16).padStart(2, '0')).join('');

  function sendHeartbeat() {
    return fetch(endpoint, {
      method: 'POST',
      headers: {
        'X-MSContable-Session': token,
        'X-MSContable-Tab': tabId,
      },
      credentials: 'same-origin',
      cache: 'no-store',
    }).catch(() => {});
  }

  sendHeartbeat();
  window.setInterval(() => sendHeartbeat(), 15000);
  window.addEventListener('pagehide', () => {
    const payload = JSON.stringify({ token, tab_id: tabId, closed: true });
    const body = new Blob([payload], { type: 'application/json' });
    if (!navigator.sendBeacon(endpoint, body)) {
      fetch(endpoint, {
        method: 'POST',
        headers: {
          'X-MSContable-Session': token,
          'X-MSContable-Tab': tabId,
          'X-MSContable-Closed': '1',
        },
        keepalive: true,
      }).catch(() => {});
    }
  });
})();
