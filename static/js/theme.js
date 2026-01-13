/**
 * Theme Management System
 * Handles theme switching, persistence, and code highlighting theme
 */

// ============================================
// SETTINGS MANAGEMENT
// ============================================

function loadSettings() {
    const style = localStorage.getItem('style') || 'modern';
    const theme = localStorage.getItem('theme') || 'light';
    const lang = localStorage.getItem('language') || 'en';

    applyStyle(style);
    applyTheme(theme);
    applyLanguage(lang);
    updateSettingsUI();
}

function setStyle(style) {
    localStorage.setItem('style', style);
    applyStyle(style);
    updateSettingsUI();
}

function setTheme(theme) {
    localStorage.setItem('theme', theme);
    applyTheme(theme);
    updateCodeTheme(theme);
    updateSettingsUI();
}

function setLanguage(lang) {
    localStorage.setItem('language', lang);
    applyLanguage(lang);
    updateSettingsUI();
}

function applyStyle(style) {
    document.documentElement.setAttribute('data-style', style);
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
}

function applyLanguage(lang) {
    document.documentElement.setAttribute('data-lang', lang);

    // Update all text with data-lang-key
    document.querySelectorAll('[data-lang-key]').forEach(el => {
        const key = el.getAttribute('data-lang-key');
        if (window.translations && window.translations[lang] && window.translations[lang][key]) {
            el.textContent = window.translations[lang][key];
        }
    });
}

function updateCodeTheme(theme) {
    const hljsTheme = document.getElementById('hljs-theme');
    if (hljsTheme) {
        if (theme === 'dark') {
            hljsTheme.href = 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css';
        } else {
            hljsTheme.href = 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css';
        }
    }
}

function updateSettingsUI() {
    const style = localStorage.getItem('style') || 'modern';
    const theme = localStorage.getItem('theme') || 'light';
    const lang = localStorage.getItem('language') || 'en';

    // Update style options
    document.querySelectorAll('.settings-option[data-style]').forEach(el => {
        el.classList.toggle('active', el.getAttribute('data-style') === style);
    });

    // Update theme options
    document.querySelectorAll('.settings-option[data-theme]').forEach(el => {
        el.classList.toggle('active', el.getAttribute('data-theme') === theme);
    });

    // Update language options
    document.querySelectorAll('.settings-option[data-lang]').forEach(el => {
        el.classList.toggle('active', el.getAttribute('data-lang') === lang);
    });
}

// ============================================
// MODAL MANAGEMENT
// ============================================

function toggleSettings() {
    const modal = document.getElementById('settingsModal');
    if (modal) {
        if (modal.style.display === 'none' || modal.style.display === '') {
            modal.style.display = 'flex';
        } else {
            modal.style.display = 'none';
        }
    }
}

function closeSettingsIfOutside(event) {
    if (event.target.id === 'settingsModal') {
        toggleSettings();
    }
}

// ============================================
// INITIALIZATION
// ============================================

// Load settings when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadSettings);
} else {
    loadSettings();
}

// Re-highlight code after HTMX swaps
if (typeof htmx !== 'undefined') {
    document.body.addEventListener('htmx:afterSwap', () => {
        if (typeof hljs !== 'undefined') {
            document.querySelectorAll('pre code').forEach(block => {
                hljs.highlightElement(block);
            });
        }
    });
}

// Highlight code on page load
document.addEventListener('DOMContentLoaded', () => {
    if (typeof hljs !== 'undefined') {
        document.querySelectorAll('pre code').forEach(block => {
            hljs.highlightElement(block);
        });
    }
});
