/**
 * Global Real-Time Validation & Input Restriction Engine
 */

const FieldRules = {
    name: {
        allowed: /^[A-Za-z ]*$/,
        regex: /^[A-Za-z ]+$/,
        min: 3, max: 50,
        msg: "Only alphabets and spaces allowed (3-50 chars)."
    },
    memberId: {
        allowed: /^[STU0-9\-]*$/,
        regex: /^STU-\d{3}$/,
        msg: "Format: STU-XXX"
    },
    email: {
        allowed: /^[^\s]*$/,
        regex: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
        msg: "Valid email required."
    },
    phone: {
        allowed: /^[0-9]*$/,
        regex: /^[6-9]\d{9}$/,
        max: 10,
        msg: "Exactly 10 digits starting with 6,7,8,9."
    },
    password: {
        allowed: /.*/, // Any char
        regex: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,50}$/,
        msg: "Min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special char."
    },
    bookTitle: {
        allowed: /^[A-Za-z0-9 \-':,\.]*$/,
        regex: /^[A-Za-z0-9 \-':,\.]+$/,
        min: 3, max: 100,
        msg: "Min 3 chars. Only standard punctuation allowed."
    },
    author: {
        allowed: /^[A-Za-z \.']*$/,
        regex: /^[A-Za-z \.']+$/,
        min: 3, max: 100,
        msg: "Only alphabets, spaces, periods, apostrophes."
    },
    publisher: {
        allowed: /^[A-Za-z0-9 &*\.,\-]*$/,
        regex: /^[A-Za-z0-9 &*\.,\-]+$/,
        msg: "Alphabets, numbers, and & * . , -"
    },
    isbn: {
        allowed: /^[\d\-]*$/,
        regex: /^(\d{10}|\d{13}|\d+-\d+-\d+-\d+-\d+)$/,
        msg: "Digits and hyphens only."
    },
    shelf: {
        allowed: /^[A-Z0-9\-]*$/,
        regex: /^[A-Z0-9\-]+$/,
        msg: "A-Z, 0-9, and hyphen."
    },
    tags: {
        allowed: /^[A-Za-z0-9, ]*$/,
        regex: /^[A-Za-z0-9, ]+$/,
        msg: "Letters, numbers, comma, space."
    },
    year: {
        allowed: /^[0-9]*$/,
        regex: /^[0-9]{4}$/,
        max: 4,
        msg: "Exactly 4 digits."
    },
    copies: {
        allowed: /^[0-9]*$/,
        regex: /^[1-9][0-9]*$/,
        msg: "Positive integer only."
    },
    rating: {
        allowed: /^[0-9\.]*$/,
        regex: /^[1-5](\.[0-9])?$/,
        msg: "1.0 to 5.0"
    }
};

function getRule(input) {
    const id = (input.id || "").toLowerCase();
    const name = (input.name || "").toLowerCase();
    const type = input.type;
    
    if (name.includes("password") || id.includes("password")) return FieldRules.password;
    if (name.includes("email") || type === "email") return FieldRules.email;
    if (name.includes("phone") || id.includes("phone")) return FieldRules.phone;
    if (name.includes("member") || id.includes("member_id")) return FieldRules.memberId;
    if (name.includes("name") || id === "name" || id.includes("name")) return FieldRules.name;
    if (id.includes("title")) return FieldRules.bookTitle;
    if (id.includes("author")) return FieldRules.author;
    if (id.includes("publisher")) return FieldRules.publisher;
    if (id.includes("isbn")) return FieldRules.isbn;
    if (id.includes("shelf")) return FieldRules.shelf;
    if (id.includes("tag")) return FieldRules.tags;
    if (id.includes("year")) return FieldRules.year;
    if (id.includes("copies") || id.includes("loan_period") || id.includes("max_books")) return FieldRules.copies;
    if (id.includes("rating")) return FieldRules.rating;

    return null;
}

// Attach keystroke restrictions
function attachRestrictions(input) {
    if (input.dataset.restricted === "true") return;
    input.dataset.restricted = "true";
    
    // Store previous valid value to revert to if needed
    let prevValue = input.value;
    
    input.addEventListener("input", function(e) {
        const rule = getRule(input);
        let val = input.value;
        
        // Anti-HTML/Script globally
        if (val.toLowerCase().includes("<") || val.toLowerCase().includes(">") || val.toLowerCase().includes("script")) {
            input.value = prevValue;
            validateAndHighlight(input);
            return;
        }

        // Active character restriction
        if (rule && rule.allowed && !rule.allowed.test(val)) {
            input.value = prevValue; // Revert to valid
            validateAndHighlight(input);
            return;
        }
        
        // Active length restriction
        if (rule && rule.max && val.length > rule.max) {
            input.value = prevValue; // Revert
            validateAndHighlight(input);
            return;
        }
        
        // Restrict double spaces globally
        if (val.includes("  ")) {
            input.value = val.replace(/\s\s+/g, ' ');
        }
        
        // Passed restrictions
        prevValue = input.value;
        validateAndHighlight(input);
    });

    input.addEventListener("blur", function() {
        input.value = input.value.trim();
        prevValue = input.value;
        validateAndHighlight(input);
    });
}

function validateAndHighlight(input) {
    let isValid = true;
    let errorMsg = "";
    const val = input.value;
    
    if (input.required && val.length === 0) {
        isValid = false;
        errorMsg = "Required field.";
    } else if (val.length > 0) {
        const rule = getRule(input);
        
        if (input.id && input.id.toLowerCase().includes("confirm")) {
            const form = input.closest('form');
            if (form) {
                const passField = Array.from(form.elements).find(el => el.type === 'password' && !el.id.toLowerCase().includes("confirm"));
                if (passField && val !== passField.value) {
                    isValid = false;
                    errorMsg = "Passwords do not match.";
                }
            }
        } else if (rule) {
            if (rule.regex && !rule.regex.test(val)) {
                isValid = false;
                errorMsg = rule.msg;
            } else if (rule.min && val.length < rule.min) {
                isValid = false;
                errorMsg = rule.msg;
            }
        }
        
        if (input.type === "number") {
            const num = parseFloat(val);
            if (input.min && num < parseFloat(input.min)) { isValid = false; errorMsg = `Min ${input.min}`; }
            if (input.max && num > parseFloat(input.max)) { isValid = false; errorMsg = `Max ${input.max}`; }
        }
    }

    // Update UI
    let errorSpan = input.nextElementSibling;
    if (!errorSpan || !errorSpan.classList.contains('validation-error')) {
        errorSpan = document.createElement('span');
        errorSpan.className = 'validation-error';
        errorSpan.style.display = 'block';
        errorSpan.style.fontSize = '12px';
        errorSpan.style.marginTop = '4px';
        input.parentNode.insertBefore(errorSpan, input.nextSibling);
    }

    if (!isValid) {
        input.style.borderColor = '#dc3545';
        errorSpan.textContent = `❌ ${errorMsg}`;
        errorSpan.style.color = '#dc3545';
    } else {
        input.style.borderColor = val.length > 0 ? '#198754' : '';
        errorSpan.textContent = val.length > 0 ? '✅ Looks good' : '';
        errorSpan.style.color = '#198754';
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
        if (input.hasAttribute('readonly') || input.hasAttribute('disabled') || input.type === 'hidden') return;
        if (input.required && input.value.trim() === "") allValid = false;
        if (input.style.borderColor === 'rgb(220, 53, 69)') allValid = false;
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
            attachRestrictions(input);
            validateAndHighlight(input);
        });
        
        checkFormValidity(form);
        
        form.addEventListener('submit', (e) => {
            let formValid = true;
            let firstInvalid = null;
            
            inputs.forEach(input => {
                if (input.type === "hidden" || input.hasAttribute('readonly') || input.hasAttribute('disabled')) return;
                const isValid = validateAndHighlight(input);
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
window.reinitValidation = initValidation;
