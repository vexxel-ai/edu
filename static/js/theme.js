/**
 * Theme Management System
 * Handles theme switching, persistence, and code highlighting theme
 */

// ============================================
// SETTINGS MANAGEMENT
// ============================================

function loadSettings() {
    const palette = localStorage.getItem('palette') || 'modern-light';
    const lang = localStorage.getItem('language') || 'en';

    applyPalette(palette);
    applyLanguage(lang);
    updateSettingsUI();
}

function setPalette(style, theme) {
    const palette = theme ? `${style}-${theme}` : style;
    localStorage.setItem('palette', palette);
    applyPalette(palette);
    updateSettingsUI();
}

function setLanguage(lang) {
    localStorage.setItem('language', lang);
    applyLanguage(lang);
    updateSettingsUI();
}

function applyPalette(palette) {
    // Map of palette names to their style and theme attributes
    const paletteMap = {
        'modern-light': { style: 'modern', theme: 'light' },
        'modern-dark': { style: 'modern', theme: 'dark' },
        'terminal-light': { style: 'terminal', theme: 'light' },
        'terminal-dark': { style: 'terminal', theme: 'dark' },
        'notebook': { style: 'notebook', theme: '' },
        'oceanic': { style: 'oceanic', theme: '' },
        'oceanic-dark': { style: 'oceanic-dark', theme: '' },
        'sunset': { style: 'sunset', theme: '' },
        'sunset-dark': { style: 'sunset-dark', theme: '' },
    };

    const config = paletteMap[palette] || { style: 'modern', theme: 'light' };

    document.documentElement.setAttribute('data-style', config.style);
    if (config.theme) {
        document.documentElement.setAttribute('data-theme', config.theme);
    } else {
        document.documentElement.removeAttribute('data-theme');
    }

    // Update code highlighting theme
    // Use 'dark' for highlight.js if palette name contains 'dark'
    const isDark = palette.includes('dark');
    updateCodeTheme(isDark ? 'dark' : 'light');
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
    const palette = localStorage.getItem('palette') || 'modern-light';
    const lang = localStorage.getItem('language') || 'en';

    // Update palette options
    document.querySelectorAll('.settings-option[data-palette]').forEach(el => {
        const elPalette = el.getAttribute('data-palette');
        el.classList.toggle('active', elPalette === palette);
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
