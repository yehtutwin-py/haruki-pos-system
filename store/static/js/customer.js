// ── Customer state ──
let currentCustomer = null;

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    document.cookie.split(';').forEach(cookie => {
      const c = cookie.trim();
      if (c.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(c.substring(name.length + 1));
      }
    });
  }
  return cookieValue;
}

// ── Search customer by phone ──
function searchCustomer() {
  const phone = document.getElementById('phoneInput').value.trim();
  if (!phone) return;

  fetch('/customer/search/?phone=' + encodeURIComponent(phone))
    .then(res => res.json())
    .then(data => {
      if (data.found) {
        attachCustomer(data.customer);
      } else {
        showModalError(data.error);
        openRegisterModal(phone);
      }
    })
    .catch(err => console.error('Search error:', err));
}

// ── Attach customer to UI ──
function attachCustomer(customer) {
  currentCustomer = customer;
  document.getElementById('customerSearchArea').style.display  = 'none';
  document.getElementById('customerFoundArea').style.display   = 'flex';
  document.getElementById('customerName').textContent   = customer.name;
  document.getElementById('customerPoints').textContent =
    customer.points.toLocaleString() + ' pts';
  closeModal();
}

// ── Remove customer ──
function removeCustomer() {
  currentCustomer = null;
  document.getElementById('customerSearchArea').style.display = 'flex';
  document.getElementById('customerFoundArea').style.display  = 'none';
  document.getElementById('phoneInput').value = '';

  fetch('/customer/search/?phone=clear', { method: 'GET' });
}

// ── Open register modal ──
function openRegisterModal(phone) {
  document.getElementById('regPhone').value = phone || '';
  document.getElementById('memberModal').classList.add('open');
}

// ── Close modal ──
function closeModal() {
  document.getElementById('memberModal').classList.remove('open');
  document.getElementById('modalError').style.display = 'none';
}

// ── Show modal error ──
function showModalError(msg) {
  const el = document.getElementById('modalError');
  el.textContent    = msg;
  el.style.display  = 'block';
}

// ── Register new customer ──
function registerCustomer() {
  const name  = document.getElementById('regName').value.trim();
  const phone = document.getElementById('regPhone').value.trim();
  const email = document.getElementById('regEmail').value.trim();

  if (!name || !phone) {
    showModalError('Name and phone number are required.');
    return;
  }

  fetch('/customer/register/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
    body: JSON.stringify({ name, phone, email }),
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      attachCustomer(data.customer);
    } else {
      showModalError(data.error);
    }
  })
  .catch(err => console.error('Register error:', err));
}

// ── Search on Enter key ──
document.addEventListener('DOMContentLoaded', () => {
  const phoneInput = document.getElementById('phoneInput');
  if (phoneInput) {
    phoneInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') searchCustomer();
    });
  }
});