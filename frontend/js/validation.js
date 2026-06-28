/**
 * Global Real-Time Strict Input Restriction Engine
 */

const FieldRules = {
    name: {
        allowedCharRegex: /^[A-Za-z ]$/, 
        stripRegex: /[^A-Za-z ]/g,       
        regex: /^[A-Za-z ]+$/,           
        min: 3, max: 50,
        hint: "Enter your full name using only alphabets and spaces (3-50 characters).",
        err: "Name can contain only alphabets and spaces.",
        success: "Name looks good."
    },
    memberId: {
        allowedCharRegex: /^[STU0-9\-]$/i,
        stripRegex: /[^STU0-9\-]/gi,
        regex: /^STU-\d{3}$/,
        hint: "Format: STU-001",
        err: "Member ID must follow the format STU-001.",
        success: "Valid Member ID."
    },
    email: {
        allowedCharRegex: /^[^\s]$/,
        stripRegex: /\s/g,
        regex: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
        hint: "Enter a valid email address (example: user@example.com).",
        err: "Please enter a valid email address.",
        success: "Email looks good."
    },
    phone: {
        allowedCharRegex: /^[0-9]$/,
        stripRegex: /[^0-9]/g,
        regex: /^[6-9]\d{9}$/,
        max: 10,
        hint: "Enter a 10-digit mobile number starting with 6, 7, 8, or 9.",
        err: "Mobile number must contain exactly 10 digits.",
        success: "Valid mobile number."
    },
    password: {
        allowedCharRegex: /./,
        stripRegex: null,
        regex: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,50}$/,
        hint: "Password must be at least 8 characters and include one uppercase letter, one lowercase letter, one number, and one special character.",
        err: "Password does not meet the required criteria.",
        success: "Strong password."
    },
    bookTitle: {
        allowedCharRegex: /^[A-Za-z ]$/,
        stripRegex: /[^A-Za-z ]/g,
        regex: /^[A-Za-z ]+$/,
        min: 3, max: 100,
        hint: "Enter a book title (3-100 characters). Only alphabets and spaces are allowed.",
        err: "Book title can contain only alphabets and spaces.",
        success: "Book title looks good."
    },
    author: {
        allowedCharRegex: /^[A-Za-z \.']$/,
        stripRegex: /[^A-Za-z \.']/g,
        regex: /^[A-Za-z \.']+$/,
        min: 3, max: 100,
        hint: "Enter the author's name using only alphabets, spaces, periods (.), and apostrophes (').",
        err: "Author name can contain only alphabets, spaces, periods, and apostrophes.",
        success: "Author name looks good."
    },
    publisher: {
        allowedCharRegex: /^[A-Za-z0-9 &*\.,]$/,
        stripRegex: /[^A-Za-z0-9 &*\.,]/g,
        regex: /^[A-Za-z0-9 &*\.,]+$/,
        hint: "Letters, numbers, spaces, &, -, ., and commas are allowed.",
        err: "Publisher name contains invalid characters.",
        success: "Publisher looks good."
    },
    isbn: {
        allowedCharRegex: /^[\d\-]$/,
        stripRegex: /[^\d\-]/g,
        regex: /^(\d{10}|\d{13}|\d+-\d+-\d+-\d+-\d+)$/,
        hint: "Enter a valid ISBN-10 or ISBN-13 (digits and hyphens only).",
        err: "Invalid ISBN format.",
        success: "Valid ISBN."
    },
    shelf: {
        allowedCharRegex: /^[A-Z0-9\-]$/i,
        stripRegex: /[^A-Z0-9\-]/gi,
        regex: /^[A-Z0-9\-]+$/,
        hint: "Example: A1, B12, C-10.",
        err: "Invalid shelf location.",
        success: "Valid shelf location."
    },
    tags: {
        allowedCharRegex: /^[A-Za-z0-9, ]$/,
        stripRegex: /[^A-Za-z0-9, ]/g,
        regex: /^[A-Za-z0-9, ]+$/,
        hint: "Comma separated tags (e.g. ai, python, ml)",
        err: "Letters, numbers, commas, and spaces only.",
        success: "Tags look good."
    },
    year: {
        allowedCharRegex: /^[0-9]$/,
        stripRegex: /[^0-9]/g,
        regex: /^[0-9]{4}$/,
        max: 4,
        hint: "Enter a year between 1900 and the current year.",
        err: "Please enter a valid publication year.",
        success: "Valid year."
    },
    copies: {
        allowedCharRegex: /^[0-9]$/,
        stripRegex: /[^0-9]/g,
        regex: /^[1-9][0-9]*$/,
        hint: "Enter the number of copies available (1-1000).",
        err: "Copies must be a positive whole number.",
        success: "Valid number of copies."
    },
    rating: {
        allowedCharRegex: /^[0-9\.]$/,
        stripRegex: /[^0-9\.]/g,
        regex: /^[1-5](\.[0-9])?$/,
        hint: "Enter a rating between 1 and 5.",
        err: "Rating must be between 1.0 and 5.0.",
        success: "Valid rating."
    },
    description: {
        allowedCharRegex: /./, 
        stripRegex: /[<>]/g, 
        regex: /^[^<>]*$/,
        hint: "Maximum 500 characters. HTML, JavaScript, and SQL code are not allowed.",
        err: "Description contains invalid content.",
        success: "Description looks good."
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
    const val = input.value;
    
    const rule = getRule(input);
    let errorMsg = rule ? rule.err : "Invalid input";

    if (input.required && val.length === 0) {
        isValid = false;
        errorMsg = "Required field.";
    } else if (val.length > 0) {
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
            } else if (rule.min && val.length < rule.min) {
                isValid = false;
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
            if (input.id && input.id.toLowerCase().includes("confirm")) {
                errorSpan.textContent = '✅ Passwords match.';
            } else {
                errorSpan.textContent = rule ? `✅ ${rule.success}` : '✅ Looks good';
            }
            errorSpan.style.color = '#198754';
        } else {
            if (input.id && input.id.toLowerCase().includes("confirm")) {
                errorSpan.textContent = `ℹ️ Re-enter your password exactly as above.`;
            } else if (rule && rule.hint) {
                errorSpan.textContent = `ℹ️ ${rule.hint}`;
            } else {
                errorSpan.textContent = '';
            }
            errorSpan.style.color = '#8ea1b5'; // subtle gray/blue
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
        
        // Check if there is an error span showing an error
        const errorSpan = input.nextElementSibling;
        if (errorSpan && errorSpan.classList.contains('validation-error') && errorSpan.textContent.includes('❌')) {
            allValid = false;
        }
    });
    
    submitBtns.forEach(btn => {
        // Store validity state in dataset instead of disabling, to allow click interception for popup
        btn.dataset.allValid = allValid;
        btn.disabled = false; // ensure it's not disabled
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

// Intercept clicks on invalid buttons globally (capture phase)
document.addEventListener('click', (e) => {
    const btn = e.target.closest('button[type="submit"], button.g-sub, button.btn-p, button[onclick*="Login"], button[onclick*="Register"], button[onclick*="save"], button[onclick*="Save"]');
    if (btn && btn.dataset.allValid === 'false') {
        e.preventDefault();
        e.stopImmediatePropagation();
        
        let errorMsg = 'Please provide valid details. Check the highlighted fields.';
        const container = btn.closest('form, .gate-form, .modal, #s-reg, #s-login, #al-login');
        if (container) {
            const errorSpans = container.querySelectorAll('.validation-error');
            for (const span of errorSpans) {
                if (span.textContent.includes('❌')) {
                    errorMsg = span.textContent.replace('❌', '').trim();
                    break;
                }
            }
        }

        if (typeof notify === 'function') {
            notify(errorMsg, 'e');
        } else {
            alert(errorMsg);
        }
    }
}, true);

document.addEventListener('DOMContentLoaded', initValidation);
window.reinitValidation = initValidation;
