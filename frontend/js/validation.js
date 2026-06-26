/**
 * Global Real-Time Validation Engine for LibraryAI Pro
 */

const ValidationRules = {
    name: {
        regex: /^[A-Za-z ]+$/,
        min: 3,
        max: 50,
        msg: "Only alphabets and spaces, 3-50 chars"
    },
    memberId: {
        regex: /^STU-\d{3}$/,
        msg: "Must follow format STU-XXX (e.g. STU-001)"
    },
    email: {
        regex: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
        msg: "Enter a valid email address"
    },
    phone: {
        regex: /^[6-9]\d{9}$/,
        msg: "Must be exactly 10 digits starting with 6,7,8, or 9"
    },
    password: {
        regex: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,50}$/,
        msg: "Min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special char"
    },
    bookTitle: {
        regex: /^[^<>]*$/,
        min: 3,
        max: 100,
        msg: "Min 3 chars, no HTML tags"
    },
    author: {
        regex: /^[A-Za-z \.]+$/,
        min: 3,
        max: 100,
        msg: "Only alphabets, spaces, and periods"
    },
    publisher: {
        regex: /^[A-Za-z0-9 &\-\.,]+$/,
        msg: "No special characters (except & - . ,)"
    },
    isbn: {
        regex: /^(\d{10}|\d{13}|\d+-\d+-\d+-\d+-\d+)$/,
        msg: "Must be valid 10 or 13 digit ISBN"
    },
    shelf: {
        regex: /^[A-Z0-9\-]+$/,
        msg: "E.g. A1, B-12"
    }
};

// Cleans multiple consecutive spaces
function sanitizeString(val) {
    return val.trim().replace(/\s+/g, ' ');
}

// Determines the rule for an input based on its name, id, or type
function getRuleForInput(input) {
    const id = (input.id || "").toLowerCase();
    const name = (input.name || "").toLowerCase();
    const type = input.type;
    
    if (name.includes("password") || id.includes("password")) return ValidationRules.password;
    if (name.includes("email") || type === "email") return ValidationRules.email;
    if (name.includes("phone") || id.includes("phone")) return ValidationRules.phone;
    if (name.includes("member") || id.includes("member_id") || id === "member_id") return ValidationRules.memberId;
    if (name.includes("name") || id === "name" || id.includes("name")) return ValidationRules.name;
    if (id.includes("title")) return ValidationRules.bookTitle;
    if (id.includes("author")) return ValidationRules.author;
    if (id.includes("publisher")) return ValidationRules.publisher;
    if (id.includes("isbn")) return ValidationRules.isbn;
    if (id.includes("shelf")) return ValidationRules.shelf;

    return null; // No strict regex rule
}

function validateInput(input) {
    let isValid = true;
    let errorMsg = "";
    
    const val = sanitizeString(input.value);
    
    if (input.required && val.length === 0) {
        isValid = false;
        errorMsg = "This field is required";
    } else if (val.length > 0) {
        // Special case: Confirm Password
        if (input.id && input.id.toLowerCase().includes("confirm")) {
            // Find the original password field in the same form
            const form = input.closest('form');
            if (form) {
                const passField = Array.from(form.elements).find(el => el.type === 'password' && !el.id.toLowerCase().includes("confirm"));
                if (passField && val !== passField.value) {
                    isValid = false;
                    errorMsg = "Passwords do not match";
                }
            }
        } else if (input.type === "number") {
            const num = parseFloat(val);
            if (input.min && num < parseFloat(input.min)) {
                isValid = false;
                errorMsg = `Must be at least ${input.min}`;
            }
            if (input.max && num > parseFloat(input.max)) {
                isValid = false;
                errorMsg = `Must be at most ${input.max}`;
            }
        } else {
            const rule = getRuleForInput(input);
            if (rule) {
                if (rule.regex && !rule.regex.test(val)) {
                    isValid = false;
                    errorMsg = rule.msg;
                } else if (rule.min && val.length < rule.min) {
                    isValid = false;
                    errorMsg = rule.msg;
                } else if (rule.max && val.length > rule.max) {
                    isValid = false;
                    errorMsg = rule.msg;
                }
            }
            
            // XSS Check for all inputs
            if (val.toLowerCase().includes("<script>") || val.toLowerCase().includes("javascript:")) {
                isValid = false;
                errorMsg = "Malicious content detected";
            }
        }
    }

    // UI Updates
    let errorSpan = input.nextElementSibling;
    if (!errorSpan || !errorSpan.classList.contains('validation-error')) {
        errorSpan = document.createElement('span');
        errorSpan.className = 'validation-error';
        errorSpan.style.color = '#dc3545';
        errorSpan.style.fontSize = '12px';
        errorSpan.style.display = 'block';
        errorSpan.style.marginTop = '4px';
        input.parentNode.insertBefore(errorSpan, input.nextSibling);
    }

    if (!isValid) {
        input.style.borderColor = '#dc3545';
        errorSpan.textContent = `❌ ${errorMsg}`;
    } else {
        input.style.borderColor = val.length > 0 ? '#198754' : '';
        errorSpan.textContent = val.length > 0 ? '✅ Looks good' : '';
        if (val.length > 0) errorSpan.style.color = '#198754';
    }
    
    checkFormValidity(input.closest('form'));
    return isValid;
}

function checkFormValidity(form) {
    if (!form) return;
    const submitBtn = form.querySelector('button[type="submit"]');
    if (!submitBtn) return;
    
    let allValid = true;
    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        if (input.hasAttribute('readonly') || input.hasAttribute('disabled')) return;
        
        const val = input.value;
        if (input.required && val.trim() === "") {
            allValid = false;
        } else if (input.style.borderColor === 'rgb(220, 53, 69)') { // #dc3545 in rgb
            allValid = false;
        }
    });
    
    submitBtn.disabled = !allValid;
    submitBtn.style.opacity = allValid ? '1' : '0.5';
    submitBtn.style.cursor = allValid ? 'pointer' : 'not-allowed';
}

function initValidation() {
    document.querySelectorAll('form').forEach(form => {
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (input.type === "hidden") return;
            
            input.addEventListener('input', () => {
                validateInput(input);
            });
            input.addEventListener('blur', () => {
                input.value = sanitizeString(input.value);
                validateInput(input);
            });
        });
        
        // Initial form check
        checkFormValidity(form);
        
        // Intercept form submit to prevent defaults explicitly if invalid
        form.addEventListener('submit', (e) => {
            let formValid = true;
            let firstInvalid = null;
            
            inputs.forEach(input => {
                if (input.type === "hidden" || input.hasAttribute('readonly') || input.hasAttribute('disabled')) return;
                const isValid = validateInput(input);
                if (!isValid) {
                    formValid = false;
                    if (!firstInvalid) firstInvalid = input;
                }
            });
            
            if (!formValid) {
                e.preventDefault();
                e.stopImmediatePropagation();
                if (firstInvalid) firstInvalid.focus();
            }
        });
    });
}

document.addEventListener('DOMContentLoaded', initValidation);
// Re-bind dynamically injected forms if needed
window.reinitValidation = initValidation;
