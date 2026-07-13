/**
 * Ads Tutorials — Main Scripts
 * B2B Foreign Trade Demo Site for GTM Course
 */

// Initialize GTM dataLayer (creates it if not present)
window.dataLayer = window.dataLayer || [];

// ── reCAPTCHA v3 helper ──
var SITE_KEY = '6LcgPFEtAAAAAMsUX3VzYJMdjDY3Mg_V_vcIfneq';

function getRecaptchaToken(action) {
  return new Promise(function(resolve, reject) {
    grecaptcha.ready(function() {
      grecaptcha.execute(SITE_KEY, { action: action }).then(function(token) {
        resolve(token);
      }).catch(reject);
    });
  });
}

// ---------- Form Handler (Contact page) ----------
document.addEventListener('DOMContentLoaded', function () {

  var inquiryForm = document.getElementById('inquiry-form');
  if (inquiryForm) {
    inquiryForm.addEventListener('submit', function (e) {
      e.preventDefault();

      // Generate reCAPTCHA token before submitting
      getRecaptchaToken('inquiry').then(function(token) {
        document.getElementById('recaptcha-token').value = token;

        var name = inquiryForm.querySelector('[name="name"]').value;
        var email = inquiryForm.querySelector('[name="email"]').value;
        var company = inquiryForm.querySelector('[name="company"]').value;
        var product = inquiryForm.querySelector('[name="product"]').value;
        var message = inquiryForm.querySelector('[name="message"]').value;

        var formData = { name: name, email: email, company: company, product: product, message: message, recaptcha_token: token };

        // Push to dataLayer
        window.dataLayer.push({
          event: 'form_submit',
          form_type: 'inquiry',
          form_data: formData
        });

        // Send to backend API
        fetch('/api/submissions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData)
        }).then(function () {
          window.location.href = '/thank-you.html';
        }).catch(function () {
          window.location.href = '/thank-you.html';
        });
      }).catch(function() {
        // reCAPTCHA failed — submit anyway with fallback
        window.location.href = '/thank-you.html';
      });
    });
  }

  // ── Data Request Form Handler ──
  var dataForm = document.querySelector('[data-form-type="data_request"]');
  if (dataForm) {
    dataForm.addEventListener('submit', function (e) {
      e.preventDefault();
      getRecaptchaToken('data_request').then(function(token) {
        var tokenInput = dataForm.querySelector('[name="recaptcha_token"]');
        if (tokenInput) tokenInput.value = token;
        dataForm.submit();
      }).catch(function() {
        dataForm.submit();
      });
    });
  }

  // Track "Send Inquiry" CTA clicks on product detail page
  var inquiryBtns = document.querySelectorAll('.btn-inquiry');
  inquiryBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var productName = btn.getAttribute('data-product') || '';
      window.dataLayer.push({
        event: 'inquiry_click',
        product_name: productName
      });
    });
  });

  // Track "Download Catalog" clicks
  var downloadBtns = document.querySelectorAll('.btn-download');
  downloadBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var catalogName = btn.getAttribute('data-catalog') || '';
      window.dataLayer.push({
        event: 'download_click',
        catalog_name: catalogName
      });
      alert('Catalog download triggered — tracked via dataLayer.\nIn production, this would download a PDF.');
    });
  });

  // Track CTA button clicks on homepage
  var ctaBtns = document.querySelectorAll('.btn-cta');
  ctaBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var ctaName = btn.getAttribute('data-cta') || '';
      window.dataLayer.push({
        event: 'cta_click',
        cta_name: ctaName
      });
    });
  });
});

// ---------- Product Filter (Products page) ----------
function filterProducts(category) {
  // Update active filter button
  document.querySelectorAll('.filter-tag').forEach(function (tag) {
    tag.classList.toggle('active', tag.getAttribute('data-filter') === category);
  });

  // Show/hide product cards
  document.querySelectorAll('.product-card').forEach(function (card) {
    if (category === 'all' || card.getAttribute('data-category') === category) {
      card.style.display = '';
    } else {
      card.style.display = 'none';
    }
  });
}

// ---------- Product Search ----------
function searchProducts() {
  var query = document.getElementById('search-input').value.toLowerCase();
  var found = false;

  document.querySelectorAll('.product-card').forEach(function (card) {
    var title = card.querySelector('h3').textContent.toLowerCase();
    if (title.indexOf(query) >= 0) {
      card.style.display = '';
      found = true;
    } else {
      card.style.display = 'none';
    }
  });

  var noResult = document.getElementById('no-results');
  if (noResult) {
    noResult.style.display = found ? 'none' : 'block';
  }
}

// ---------- B2B Purchase Flow ----------
var b2bCurrentOrder = null;

function openB2bOrder(productId, productName, price) {
  b2bCurrentOrder = { id: productId, name: productName, price: price };
  document.getElementById('b2b-checkout-product-name').textContent = productName + ' — $' + price.toFixed(2);
  document.getElementById('b2b-checkout-overlay').classList.add('open');

  window.dataLayer.push({
    event: 'begin_checkout',
    ecommerce: {
      currency: 'USD',
      value: price,
      items: [{ item_id: productId, item_name: productName, price: price, quantity: 1 }]
    }
  });
}

function closeB2bOrder() {
  document.getElementById('b2b-checkout-overlay').classList.remove('open');
}

document.addEventListener('DOMContentLoaded', function () {
  var b2bForm = document.getElementById('b2b-checkout-form');
  if (b2bForm) {
    b2bForm.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!b2bCurrentOrder) return;

      var name = b2bForm.querySelector('[name="name"]').value;
      var email = b2bForm.querySelector('[name="email"]').value;
      var company = b2bForm.querySelector('[name="company"]').value;
      var qty = parseInt(b2bForm.querySelector('[name="qty"]').value) || 1;
      var total = b2bCurrentOrder.price * qty;
      var txnId = 'PO-' + Date.now().toString(36).toUpperCase();

      window.dataLayer.push({
        event: 'purchase',
        ecommerce: {
          transaction_id: txnId,
          value: total,
          currency: 'USD',
          items: [{
            item_id: b2bCurrentOrder.id,
            item_name: b2bCurrentOrder.name,
            price: b2bCurrentOrder.price,
            quantity: qty
          }],
          user_data: { name: name, email: email, company: company }
        }
      });

      // Show confirmation
      closeB2bOrder();
      b2bForm.reset();
      document.getElementById('b2b-confirm').classList.add('show');
      document.getElementById('b2b-order-id').textContent = txnId;
      document.getElementById('b2b-confirm-product').textContent = b2bCurrentOrder.name + ' × ' + qty;
      document.getElementById('b2b-confirm-value').textContent = '$' + total.toFixed(2);
      document.getElementById('b2b-confirm').scrollIntoView({ behavior: 'smooth' });

      b2bCurrentOrder = null;
    });
  }
});
