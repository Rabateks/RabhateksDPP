// Main JavaScript for Rabateks DPP System

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    updateCurrentTime();
    setInterval(updateCurrentTime, 1000);
    checkDatabaseStatus();
    initializeTooltips();
    initializeDataTables();
}

// Update current time in navbar
function updateCurrentTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', {
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    
    const timeElement = document.getElementById('current-time');
    if (timeElement) {
        timeElement.textContent = timeString;
    }
}

// Check database connection status
function checkDatabaseStatus() {
    fetch('/api/stats')
        .then(response => {
            const statusElement = document.getElementById('db-status');
            if (statusElement) {
                if (response.ok) {
                    statusElement.textContent = 'Connected';
                    statusElement.className = 'badge bg-success';
                } else {
                    statusElement.textContent = 'Error';
                    statusElement.className = 'badge bg-danger';
                }
            }
        })
        .catch(error => {
            const statusElement = document.getElementById('db-status');
            if (statusElement) {
                statusElement.textContent = 'Disconnected';
                statusElement.className = 'badge bg-warning';
            }
        });
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize DataTables if available
function initializeDataTables() {
    // Check if DataTables is available and tables exist
    if (typeof $ !== 'undefined' && $.fn.DataTable) {
        // Initialize garments table
        const garmentsTable = document.getElementById('garmentsTable');
        if (garmentsTable) {
            $(garmentsTable).DataTable({
                responsive: true,
                pageLength: 25,
                order: [[0, 'desc']],
                language: {
                    search: 'Search garments:',
                    lengthMenu: 'Show _MENU_ garments per page',
                    info: 'Showing _START_ to _END_ of _TOTAL_ garments'
                }
            });
        }
        
        // Initialize orders table
        const ordersTable = document.getElementById('ordersTable');
        if (ordersTable) {
            $(ordersTable).DataTable({
                responsive: true,
                pageLength: 25,
                order: [[7, 'desc']], // Sort by created date
                language: {
                    search: 'Search orders:',
                    lengthMenu: 'Show _MENU_ orders per page',
                    info: 'Showing _START_ to _END_ of _TOTAL_ orders'
                }
            });
        }
    }
}

// Utility functions
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container-fluid');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// API helper functions
function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    return fetch(url, { ...defaultOptions, ...options })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        });
}

function showLoading(element) {
    if (element) {
        element.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        element.disabled = true;
    }
}

function hideLoading(element, originalText) {
    if (element) {
        element.innerHTML = originalText;
        element.disabled = false;
    }
}

// Form validation helpers
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Export functions for global use
window.DPPApp = {
    showAlert,
    formatNumber,
    formatDate,
    formatDateTime,
    apiRequest,
    showLoading,
    hideLoading,
    validateForm
};