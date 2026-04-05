/**
 * rating.js
 * Interactive star picker for the rating form.
 */

const LABELS = ['', 'Very Poor', 'Poor', 'Acceptable', 'Good', 'Excellent'];

function setRating(fieldName, value) {
  document.getElementById('input-' + fieldName).value = value;
  document.getElementById('label-' + fieldName).textContent = LABELS[value];

  const buttons = document.querySelectorAll(`.star-picker[data-field="${fieldName}"] .star-btn`);
  buttons.forEach(btn => {
    const v = parseInt(btn.dataset.value, 10);
    btn.classList.toggle('active', v <= value);
  });
}

// Keyboard accessibility: allow Enter/Space to select a star button
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.star-btn').forEach(btn => {
    btn.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        btn.click();
      }
    });
  });
});
