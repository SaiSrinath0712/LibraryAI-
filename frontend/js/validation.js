/**
 * Global Real-Time Strict Input Restriction Engine
 */

const FieldRules = {
    name: {
        allowedCharRegex: /^[A-Za-z ]$/, // For keydown checking
        stripRegex: /[^A-Za-z ]/g,       // For paste stripping
        regex: /^[A-Za-z ]+$/,           // Full string validation
        min: 3, max: 50,
        msg: "Only alphabets and spaces allowed (3-50 chars)."
    },
    memberId: {
        allowedCharRegex: /^[STU0-9\-]$/i,
        stripRegex: /[^STU0-9\-]/gi,
        regex: /^STU-\d{3}$/,
        msg: "Format: STU-XXX"
    },
    email: {
        allowedCharRegex: /^[^\s]$/,
        stripRegex: /\s/g,
        regex: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
        msg: "Valid email required."
    },
    phone: {
        allowedCharRegex: /^[0-9]$/,
        stripRegex: /[^0-9]/g,
        regex: /^[6-9]\d{9}$/,
        max: 10,
        msg: "Exactly 10 digits starting with 6,7,8,9."
    },
    password: {
        allowedCharRegex: /./, // Any char
        stripRegex: null,
        regex: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,50}$/,
        msg: "Min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special char."
    },
    bookTitle: {
        allowedCharRegex: /^[A-Za-z0-9 \-':,\.]$/,
        stripRegex: /[^A-Za-z0-9 \-':,\.]/g,
        regex: /^[A-Za-z0-9 \-':,\.]+$/,
        min: 3, max: 100,
        msg: "Min 3 chars. Only standard punctuation allowed."
    },
    author: {
        allowedCharRegex: /^[A-Za-z \.']$/,
        stripRegex: /[^A-Za-z \.']/g,
        regex: /^[A-Za-z \.']+$/,
        min: 3, max: 100,
        msg: "Only alphabets, spaces, periods, apostrophes."
    },
    publisher: {
        allowedCharRegex: /^[A-Za-z0-9 &*\.,]$/,
        stripRegex: /[^A-Za-z0-9 &*\.,]/g,
        regex: /^[A-Za-z0-9 &*\.,]+$/,
        msg: "Alphabets, numbers, and & * . ,"
    },
    isbn: {
        allowedCharRegex: /^[\d\-]$/,
        stripRegex: /[^\d\-]/g,
        regex: /^(\d{10}|\d{13}|\d+-\d+-\d+-\d+-\d+)$/,
        msg: "Digits and hyphens only."
    },
    shelf: {
        allowedCharRegex: /^[A-Z0-9\-]$/i,
        stripRegex: /[^A-Z0-9\-]/gi,
        regex: /^[A-Z0-9\-]+$/,
        msg: "A-Z, 0-9, and hyphen."
    },
    tags: {
        allowedCharRegex: /^[A-Za-z0-9, ]$/,
        stripRegex: /[^A-Za-z0-9, ]/g,
        regex: /^[A-Za-z0-9, ]+$/,
        msg: "Letters, numbers, comma, space."
    },
    year: {
        allowedCharRegex: /^[0-9]$/,
        stripRegex: /[^0-9]/g,
        regex: /^[0-9]{4}$/,
        max: 4,
        msg: "Exactly 4 digits."
    },
    copies: {
        allowedCharRegex: /^[0-9]$/,
        stripRegex: /[^0-9]/g,
        regex: /^[1-9][0-9]*$/,
        msg: "Positive integer only."
    },
    rating: {
        allowedCharRegex: /^[0-9\.]$/,
        stripRegex: /[^0-9\.]/g,
        regex: /^[1-5](\.[0-9])?$/,
        msg: "1.0 to 5.0"
    },
    description: {
        allowedCharRegex: /./, 
        stripRegex: /[<>]/g, 
        regex: /^[^<>]*$/,
        msg: "HTML/Script tags not allowed."
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
    if (id.includes("copies") || id.includes("loan_period") || id.includes("max_books") || id.includes("fine")) return FieldRules.copies;
    if (id.includes("rating")) return FieldRules.rating;
    if (id.includes("note") || id.includes("description") || name.includes("note") || name.includes("description")) return FieldRules.description;

    return null;
}

// Intercept Keystrokes natively
function handleKeydown(e, rule, max) {
    // Allow special control keys (Backspace, Delete, Arrow keys, Tab, Ctrl+A/C/V)
    if (
        e.key.length !== 1 || 
        e.ctrlKey || e.metaKey || e.altKey
    ) {
        return;
    }

    let char = e.key;

    // 1. Strict Character Filter
    if (rule && rule.allowedCharRegex) {
        if (!rule.allowedCharRegex.test(char)) {
            e.preventDefault(); // Completely block the keystroke
            return;
        }
    }

    // 2. Length restriction block (Don't let them type the 11th digit, etc)
    const currentLen = e.target.value.length;
    // Account for selected text that would be overwritten
    const selectionLen = e.target.selectionEnd - e.target.selectionStart;
    
    if (max && (currentLen - selectionLen) >= max) {
        e.preventDefault();
        return;
    }
}

// Intercept Pastes natively
function handlePaste(e, rule, max) {
    e.preventDefault();
    
    let pastedText = (e.clipboardData || window.clipboardData).getData('text');
    
    // Globally kill scripts
    pastedText = pastedText.replace(/[<>]/g, '').replace(/script/gi, '');
    
    // Apply field specific stripping
    if (rule && rule.stripRegex) {
        pastedText = pastedText.replace(rule.stripRegex, '');
    }
    
    // Insert cleaned text at cursor position
    const target = e.target;
    const start = target.selectionStart;
    const end = target.selectionEnd;
    
    const currentVal = target.value;
    let newVal = currentVal.substring(0, start) + pastedText + currentVal.substring(end);
    
    // Prevent double spaces universally on paste
    newVal = newVal.replace(/\s\s+/g, ' ');
    
    // Apply length caps
    if (max && newVal.length > max) {
        newVal = newVal.substring(0, max);
    }
    
    target.value = newVal;
    validateAndHighlight(target);
    
    // Move cursor to end of pasted text
    const newPos = start + pastedText.length;
    target.setSelectionRange(newPos, newPos);
}

// Fallback for drag-and-drop or mobile predictive keyboards
function handleInput(e, rule, max) {
    let val = e.target.value;
    const target = e.target;
    
    // Globally kill scripts
    if (val.toLowerCase().includes("<") || val.toLowerCase().includes(">") || val.toLowerCase().includes("script")) {
        val = val.replace(/[<>]/g, '').replace(/script/gi, '');
    }

    if (rule && rule.stripRegex) {
        val = val.replace(rule.stripRegex, '');
    }
    
    if (val.includes("  ")) {
        val = val.replace(/\s\s+/g, ' ');
    }
    
    if (max && val.length > max) {
        val = val.substring(0, max);
    }

    if (target.value !== val) {
        target.value = val;
    }
    
    validateAndHighlight(target);
}


function attachRestrictions(input) {
    if (input.dataset.restricted === "true") return;
    input.dataset.restricted = "true";
    
    const rule = getRule(input);
    const max = rule && rule.max ? rule.max : (input.getAttribute('maxlength') ? parseInt(input.getAttribute('maxlength')) : null);
    
    input.addEventListener("keydown", (e) => handleKeydown(e, rule, max));
    input.addEventListener("paste", (e) => handlePaste(e, rule, max));
    input.addEventListener("input", (e) => handleInput(e, rule, max));
    input.addEventListener("drop", (e) => {
        e.preventDefault(); // Prevent dragging and dropping text completely for extreme strictness
    });

    input.addEventListener("blur", function() {
        if(input.value) {
            input.value = input.value.trim();
            validateAndHighlight(input);
        }
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
        if (val.length > 0) {
            errorSpan.textContent = '✅ Looks good';
            errorSpan.style.color = '#198754';
        } else {
            const rule = getRule(input);
            if (rule && rule.msg) {
                errorSpan.textContent = `ℹ️ ${rule.msg}`;
                errorSpan.style.color = '#8ea1b5'; // subtle gray/blue
            } else {
                errorSpan.textContent = '';
            }
        }
    }
    
    checkContainerValidity(input.closest('form, .gate-form, .modal, #s-reg, #s-login'));
    return isValid;
}

function checkContainerValidity(container) {
    if (!container) return;
    
    // Find all buttons in the container that trigger submissions (Login, Register, Save, etc.)
    // We target primary buttons by looking for 'submit', or specific classes like 'g-sub', 'btn-p', etc.
    const submitBtns = container.querySelectorAll('button[type="submit"], button.g-sub, button.btn-p, button[onclick*="Login"], button[onclick*="Register"], button[onclick*="save"], button[onclick*="Save"]');
    
    if (!submitBtns || submitBtns.length === 0) return;
    
    let allValid = true;
    const inputs = container.querySelectorAll('input:not([type="hidden"]), select, textarea');
    inputs.forEach(input => {
        if (input.hasAttribute('readonly') || input.hasAttribute('disabled')) return;
        if (input.required && input.value.trim() === "") allValid = false;
        if (input.style.borderColor === 'rgb(220, 53, 69)') allValid = false; // #dc3545
    });
    
    submitBtns.forEach(btn => {
        // Prevent click if invalid
        btn.disabled = !allValid;
        btn.style.opacity = allValid ? '1' : '0.5';
        btn.style.cursor = allValid ? 'pointer' : 'not-allowed';
    });
}

function initValidation() {
    // 1. Attach restrictions and listeners to ALL inputs globally
    const inputs = document.querySelectorAll('input:not([type="hidden"]), select, textarea');
    inputs.forEach(input => {
        attachRestrictions(input);
        validateAndHighlight(input);
    });
    
    // 2. Initial container validity check
    const containers = document.querySelectorAll('form, .gate-form, .modal, #s-reg, #s-login, #al-login');
    containers.forEach(container => checkContainerValidity(container));
    
    // 3. Optional: Intercept form submits natively if they exist
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', (e) => {
            let formValid = true;
            let firstInvalid = null;
            
            const formInputs = form.querySelectorAll('input:not([type="hidden"]), select, textarea');
            formInputs.forEach(input => {
                if (input.hasAttribute('readonly') || input.hasAttribute('disabled')) return;
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
