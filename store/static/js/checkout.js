// ── Checkout JS ──

// orderTotal is injected from the template via data attribute
const orderTotal = parseInt(document.getElementById('checkoutData').dataset.total);

function calcChange() {
  const tendered = parseInt(document.getElementById('cashInput').value) || 0;
  const change   = Math.max(0, tendered - orderTotal);
  document.getElementById('changeAmt').textContent = '¥' + change.toLocaleString();
}

function setAmount(amt) {
  document.getElementById('cashInput').value = amt;
  calcChange();
}

// Show/hide cash section based on payment method
document.querySelectorAll('.payment-option').forEach(radio => {
  radio.addEventListener('change', () => {
    const cashSection = document.getElementById('cashSection');
    cashSection.style.display = radio.value === 'cash' ? 'block' : 'none';
  });
});

// Run on load
calcChange();