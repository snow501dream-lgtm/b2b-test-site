/**
 * HengXin Industrial — Main Scripts
 * B2B Foreign Trade Demo Site for GTM Course
 */

// Initialize GTM dataLayer (creates it if not present)
window.dataLayer = window.dataLayer || [];

// ---------- Form Handler (Contact page) ----------
document.addEventListener('DOMContentLoaded', function () {

  const inquiryForm = document.getElementById('inquiry-form');
  if (inquiryForm) {
    inquiryForm.addEventListener('submit', function (e) {
      e.preventDefault();

      // Collect form data
      var name = inquiryForm.querySelector('[name="name"]').value;
      var email = inquiryForm.querySelector('[name="email"]').value;
      var company = inquiryForm.querySelector('[name="company"]').value;
      var message = inquiryForm.querySelector('[name="message"]').value;

      // Push to dataLayer — used for GTM triggers and GA4 events
      window.dataLayer.push({
        event: 'form_submit',
        form_type: 'inquiry',
        form_data: {
          name: name,
          email: email,
          company: company,
          message: message
        }
      });

      // Redirect to thank-you page (conversion destination)
      window.location.href = '/thank-you.html';
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
