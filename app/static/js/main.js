// Main.js - JavaScript for Personal Expense Tracker

// Initialize all tooltips/popovers/validation/flatpickr
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Form validation
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Date picker default format
    if (typeof flatpickr !== 'undefined') {
        flatpickr('.datepicker', {
            dateFormat: 'Y-m-d',
            allowInput: true
        });
    }

    // ---- Universal Date Filter wiring (Income + Expenses) ----
    setupUniversalDateFilterHandlers();
});

/* =========================
   Helpers / Utilities
   ========================= */

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

// Confirm deletion
function confirmDelete(formId) {
    if (confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
        document.getElementById(formId).submit();
    }
    return false;
}

// Custom validation for expense form
function validateExpenseForm() {
    var amount = document.getElementById('amount').value;
    if (isNaN(amount) || parseFloat(amount) <= 0) {
        alert('Please enter a valid positive amount.');
        return false;
    }
    return true;
}

/* =========================
   Date Filter (Universal)
   =========================
   Works for any page that has:
   - a <select name="date_filter"> inside a <form method="GET">
   - optional date range container with id "dateRangeInputs" or "expenseDateRangeInputs"
     (you can also add class "date-range-inputs")
   - inputs named "start_date" and "end_date"
*/
function setupUniversalDateFilterHandlers() {
    // Handle changing preset/custom options
    document.querySelectorAll('select[name="date_filter"]').forEach(function(selectEl) {
        // Initial toggle on load (keeps state consistent on back/forward nav)
        toggleDateRangeVisibility(selectEl);

        selectEl.addEventListener('change', function() {
            // Always keep the UI in sync
            toggleDateRangeVisibility(selectEl);

            // For presets (not 'custom'), auto-submit the enclosing form
            if (selectEl.value !== 'custom') {
                const form = selectEl.closest('form');
                // Clear custom date values to avoid server parsing them accidentally
                clearCustomDates(form);
                safeSubmit(form);
            }
        });
    });

    // Auto-submit for custom date range once both dates are chosen & valid
    document.addEventListener('change', function(e) {
        if (e.target.matches('input[name="start_date"], input[name="end_date"]')) {
            const form = e.target.closest('form');
            if (!form) return;

            const dateFilter = form.querySelector('select[name="date_filter"]');
            if (!dateFilter || dateFilter.value !== 'custom') return;

            const sd = form.querySelector('input[name="start_date"]')?.value || '';
            const ed = form.querySelector('input[name="end_date"]')?.value || '';

            if (!sd || !ed) return;

            // Validate order
            if (new Date(sd) > new Date(ed)) {
                alert('End date must be after start date.');
                return;
            }

            safeSubmit(form);
        }
    });
}

// Show/hide date range inputs depending on select value
function toggleDateRangeVisibility(selectEl) {
    const form = selectEl.closest('form');
    if (!form) return;

    // Support both ids and a shared class
    const range =
        form.querySelector('#dateRangeInputs') ||
        form.querySelector('#expenseDateRangeInputs') ||
        form.querySelector('.date-range-inputs');

    if (!range) return;

    if (selectEl.value === 'custom') {
        range.classList.remove('d-none');
    } else {
        range.classList.add('d-none');
    }
}

// Clear custom date fields
function clearCustomDates(form) {
    if (!form) return;
    const sd = form.querySelector('input[name="start_date"]');
    const ed = form.querySelector('input[name="end_date"]');
    if (sd) sd.value = '';
    if (ed) ed.value = '';
}

// Safely submit a form (avoid collisions with inputs named "submit")
function safeSubmit(form) {
    if (!form) return;
    // If there is an input/button named "submit", it can shadow form.submit
    const nativeSubmit = HTMLFormElement.prototype.submit;
    nativeSubmit.call(form);
}