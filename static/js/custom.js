// IELTS Simulator - Custom JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('IELTS Simulator loaded!');

    // Theme toggle
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('theme', newTheme);

            const icon = this.querySelector('i');
            if (newTheme === 'dark') {
                icon.classList.remove('fa-moon');
                icon.classList.add('fa-sun');
            } else {
                icon.classList.remove('fa-sun');
                icon.classList.add('fa-moon');
            }
        });

        // Load saved theme
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-bs-theme', savedTheme);
        const icon = themeToggle.querySelector('i');
        if (savedTheme === 'dark') {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
        }
    }

    // Word counter for writing textareas
    const textareas = document.querySelectorAll('textarea[data-word-count]');
    textareas.forEach(textarea => {
        const counterId = textarea.id + '_counter';
        let counter = document.getElementById(counterId);

        if (!counter) {
            counter = document.createElement('div');
            counter.className = 'form-text text-end mt-1';
            counter.id = counterId;
            counter.innerHTML = 'Words: <span class="fw-bold">0</span>';
            textarea.parentNode.appendChild(counter);
        }

        textarea.addEventListener('input', function() {
            const words = this.value.trim().split(/\s+/).filter(word => word.length > 0);
            const wordCount = words.length;
            counter.querySelector('span').textContent = wordCount;

            const minWords = parseInt(this.dataset.minWords) || 0;
            if (minWords > 0 && wordCount < minWords) {
                counter.classList.add('text-danger');
            } else {
                counter.classList.remove('text-danger');
            }
        });
    });

    // Timer for tests
    function startTimer(minutes, elementId) {
        const timerElement = document.getElementById(elementId);
        if (!timerElement) return;

        let timeLeft = minutes * 60;

        const timer = setInterval(function() {
            const mins = Math.floor(timeLeft / 60);
            const secs = timeLeft % 60;

            timerElement.innerHTML = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

            if (timeLeft <= 300) { // 5 minutes
                timerElement.classList.add('text-danger');
                timerElement.classList.add('pulse');
            }

            timeLeft--;

            if (timeLeft < 0) {
                clearInterval(timer);
                // Auto-submit form if exists
                const form = document.querySelector('form');
                if (form) {
                    if (confirm('Time is up! Submit your test?')) {
                        form.submit();
                    }
                }
            }
        }, 1000);
    }

    // Initialize any timers on page
    const timerElements = document.querySelectorAll('[data-timer-minutes]');
    timerElements.forEach(element => {
        const minutes = parseInt(element.dataset.timerMinutes);
        const elementId = element.id;
        if (minutes && elementId) {
            startTimer(minutes, elementId);
        }
    });
});

// Utility functions
function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    document.body.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();

    // Remove after hide
    toast.addEventListener('hidden.bs.toast', function () {
        toast.remove();
    });
}

// Export for use in templates
window.showToast = showToast;