// ── Cart State ──
let cart = {};

// ── Get CSRF cookie ──
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

// ── Save cart to Django session silently ──
function saveCartToSession() {
  fetch('/save-cart/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
    body: JSON.stringify({ cart: cart }),
  })
  .then(res => res.json())
  .then(data => {
    if (!data.success) {
      console.error('Failed to save cart to session');
    }
  })
  .catch(err => {
    console.error('Save cart error:', err);
  });
}

// ── Image fallback ──
function initImages() {
  document.querySelectorAll('.prod-img').forEach(function (img) {
    const fallback = img.dataset.fallback;
    img.addEventListener('error', function () {
      if (fallback && this.src !== fallback) {
        this.src = fallback;
      }
    });
  });
}

// ── Add to cart ──
function addToCart(card) {
  const id     = card.dataset.id;
  const name   = card.dataset.name;
  const nameJa = card.dataset.nameJa;
  const price  = parseInt(card.dataset.price);
  const image  = card.querySelector('.prod-img')
                   ? card.querySelector('.prod-img').src
                   : '';

  if (cart[id]) {
    cart[id].qty += 1;
  } else {
    cart[id] = { name, nameJa, price, image, qty: 1 };
  }

  updateStockDisplay(id, card);
  renderCart();
  saveCartToSession();
}

// ── Update stock display on card ──
function updateStockDisplay(id, card) {
  const originalStock = parseInt(card.dataset.stock) || 0;
  const inCart        = cart[id] ? cart[id].qty : 0;
  const remaining     = originalStock - inCart;
  const stockEl       = document.getElementById('stock-' + id);

  if (!stockEl) return;

  if (remaining <= 0) {
    stockEl.textContent = 'Out of stock';
    card.classList.add('out-of-stock');
    card.style.pointerEvents = 'none';
    card.style.opacity = '0.45';
  } else {
    stockEl.textContent = 'Stock: ' + remaining;
    card.classList.remove('out-of-stock');
    card.style.pointerEvents = '';
    card.style.opacity = '';
  }
}

// ── Change quantity ──
function changeQty(id, delta) {
  if (!cart[id]) return;
  cart[id].qty += delta;
  if (cart[id].qty <= 0) delete cart[id];

  // Update stock display on product card
  const card = document.querySelector(`.prod-card[data-id="${id}"]`);
  if (card) updateStockDisplay(id, card);

  renderCart();
  saveCartToSession();
}

// ── Clear cart ──
function clearCart() {
  cart = {};

  // Reset all stock displays
  document.querySelectorAll('.prod-card').forEach(card => {
    const id            = card.dataset.id;
    const originalStock = parseInt(card.dataset.stock) || 0;
    const stockEl       = document.getElementById('stock-' + id);
    if (stockEl) {
      if (originalStock <= 0) {
        stockEl.textContent = 'Out of stock';
      } else {
        stockEl.textContent = 'Stock: ' + originalStock;
        card.classList.remove('out-of-stock');
        card.style.pointerEvents = '';
        card.style.opacity = '';
      }
    }
  });

  renderCart();
  saveCartToSession();
}

// ── Render cart ──
function renderCart() {
  const items     = Object.entries(cart);
  const countEl   = document.getElementById('cartCount');
  const itemsEl   = document.getElementById('cartItems');
  const summaryEl = document.getElementById('cartSummaryBlock');

  const totalQty = items.reduce((s, [, v]) => s + v.qty, 0);
  countEl.textContent = totalQty + (totalQty === 1 ? ' item' : ' items');

  if (items.length === 0) {
    itemsEl.innerHTML = `
      <div class="cart-empty">
        <i class="bi bi-bag"></i>
        <span>カートは空です</span>
        <span style="font-size:11px">Tap a product to add</span>
      </div>`;
    summaryEl.style.display = 'none';
    return;
  }

  let subtotal = 0;
  let taxTotal = 0;

  itemsEl.innerHTML = items.map(([id, item]) => {
    const lineTotal = item.price * item.qty;
    const tax       = Math.round(lineTotal - (lineTotal / 1.1));
    subtotal += lineTotal - tax;
    taxTotal += tax;

    const imgHtml = item.image
      ? `<img src="${item.image}" class="cart-item-img">`
      : '';

    return `
      <div class="cart-row">
        ${imgHtml}
        <div class="cart-info">
          <div class="cart-item-name">${item.name}</div>
          <div class="cart-item-unit">¥${item.price.toLocaleString()} each</div>
        </div>
        <div class="qty-controls">
          <button class="qty-btn" onclick="changeQty('${id}', -1)">−</button>
          <span class="qty-num">${item.qty}</span>
          <button class="qty-btn" onclick="changeQty('${id}', 1)">+</button>
        </div>
        <div class="cart-line-price">¥${lineTotal.toLocaleString()}</div>
      </div>`;
  }).join('');

  const total = subtotal + taxTotal;
  document.getElementById('sumSubtotal').textContent = '¥' + subtotal.toLocaleString();
  document.getElementById('sumTax').textContent      = '¥' + taxTotal.toLocaleString();
  document.getElementById('sumTotal').textContent    = '¥' + total.toLocaleString();
  summaryEl.style.display = 'block';
}

// ── Category filter ──
function filterCategory(catId, btn) {
  document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('.prod-card').forEach(card => {
    const show = catId === 'all' || card.dataset.category === catId;
    card.style.display = show ? '' : 'none';
  });
}

// ── Search filter ──
function filterProducts() {
  const q = document.getElementById('searchInput').value.toLowerCase();
  document.querySelectorAll('.prod-card').forEach(card => {
    const match = card.dataset.name.toLowerCase().includes(q) ||
                  card.dataset.nameJa.includes(q);
    card.style.display = match ? '' : 'none';
  });
}

// ── Checkout ──
function proceedCheckout() {
  if (Object.keys(cart).length === 0) {
    alert('Cart is empty!');
    return;
  }
  window.location.href = '/checkout/';
}

// ── Init ──
document.addEventListener('DOMContentLoaded', initImages);