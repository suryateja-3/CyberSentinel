/* ==========================================================================
   CYBER SENTINEL - FORM VALIDATION UTILITIES
   Accessible, real-time validation with ARIA feedback
   ========================================================================== */

/**
 * Apply or clear validation state on a form control element.
 * @param {HTMLElement} control
 * @param {string|null} errorMessage - null = clear, string = show error
 */
export function setFieldValidity(control, errorMessage) {
  const group = control.closest('.form-group');
  const msgEl = group?.querySelector('.validation-msg');

  if (errorMessage) {
    control.classList.add('invalid');
    control.setAttribute('aria-invalid', 'true');
    if (msgEl) {
      msgEl.textContent = errorMessage;
      msgEl.style.display = 'flex';
    }
  } else {
    control.classList.remove('invalid');
    control.setAttribute('aria-invalid', 'false');
    if (msgEl) {
      msgEl.textContent = '';
      msgEl.style.display = 'none';
    }
  }
}

/**
 * Validate a URL string.
 * @param {string} value
 * @returns {{ valid: boolean, message?: string }}
 */
export function validateURL(value) {
  const trimmed = value.trim();
  if (!trimmed) return { valid: false, message: 'URL is required.' };
  if (trimmed.length > 2048) return { valid: false, message: 'URL is too long (max 2048 characters).' };
  try {
    const url = new URL(trimmed);
    if (!['http:', 'https:'].includes(url.protocol)) {
      return { valid: false, message: 'Only http:// and https:// URLs are supported.' };
    }
    return { valid: true };
  } catch {
    // Try with prepended https://
    try {
      new URL('https://' + trimmed);
      return { valid: false, message: 'Please include the full URL with http:// or https://.' };
    } catch {
      return { valid: false, message: 'Please enter a valid URL (e.g. https://example.com).' };
    }
  }
}

/**
 * Validate article text for fake news detection.
 * @param {string} value
 * @returns {{ valid: boolean, message?: string }}
 */
export function validateArticleText(value) {
  const trimmed = value.trim();
  if (!trimmed) return { valid: false, message: 'Article text is required.' };
  const wordCount = trimmed.split(/\s+/).filter(Boolean).length;
  if (wordCount < 20) return { valid: false, message: `Too short — minimum 20 words required (currently ${wordCount}).` };
  if (trimmed.length > 10000) return { valid: false, message: 'Text too long — maximum 10,000 characters.' };
  return { valid: true };
}

/**
 * Validate transaction amount.
 * @param {string} value
 * @returns {{ valid: boolean, message?: string }}
 */
export function validateAmount(value) {
  const num = parseFloat(value);
  if (!value || isNaN(num)) return { valid: false, message: 'Please enter a valid amount.' };
  if (num <= 0) return { valid: false, message: 'Amount must be greater than zero.' };
  if (num > 1_000_000) return { valid: false, message: 'Amount exceeds maximum limit ($1,000,000).' };
  return { valid: true };
}

/**
 * Validate a non-empty text field.
 * @param {string} value
 * @param {string} fieldName
 * @param {number} [maxLen=200]
 */
export function validateRequired(value, fieldName = 'This field', maxLen = 200) {
  const trimmed = value.trim();
  if (!trimmed) return { valid: false, message: `${fieldName} is required.` };
  if (trimmed.length > maxLen) return { valid: false, message: `${fieldName} must be under ${maxLen} characters.` };
  return { valid: true };
}

/**
 * Add live character counter to a textarea or input.
 * @param {HTMLElement} control
 * @param {number} maxChars
 */
export function attachCharCounter(control, maxChars) {
  const counterId = `${control.id || 'field'}-counter`;
  let counter = document.getElementById(counterId);
  if (!counter) {
    counter = document.createElement('span');
    counter.id = counterId;
    counter.className = 'char-counter';
    counter.setAttribute('aria-live', 'polite');
    control.parentElement?.appendChild(counter);
  }
  const update = () => {
    const len = control.value.length;
    counter.textContent = `${len} / ${maxChars}`;
    counter.className = `char-counter${len >= maxChars ? ' at-limit' : len >= maxChars * 0.85 ? ' near-limit' : ''}`;
  };
  control.addEventListener('input', update);
  update();
}
