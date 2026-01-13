/**
 * Content Tabs JavaScript
 * Handles tab switching for Text/Code/Exercises and solution toggling
 */

// ============================================
// CONTENT TABS (Text/Code/Exercises)
// ============================================

function switchContentTab(tabName) {
    // Update tab buttons
    const tabs = document.querySelectorAll('.content-tab');
    tabs.forEach(tab => {
        if (tab.dataset.tab === tabName) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });

    // Update tab panels
    const panels = document.querySelectorAll('.tab-panel');
    panels.forEach(panel => {
        if (panel.dataset.panel === tabName) {
            panel.classList.add('active');
        } else {
            panel.classList.remove('active');
        }
    });

    // Re-initialize syntax highlighting for code blocks
    if (tabName === 'code' && typeof hljs !== 'undefined') {
        setTimeout(() => {
            document.querySelectorAll('.tab-panel[data-panel="code"] pre code').forEach((block) => {
                hljs.highlightElement(block);
            });
        }, 50);
    }
}

// ============================================
// CODE TABS (Multiple Solutions)
// ============================================

function switchCodeTab(index) {
    // Update code tab buttons
    const codeTabs = document.querySelectorAll('.code-tab');
    codeTabs.forEach((tab, i) => {
        if (i === index) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });

    // Update code content
    const codeContents = document.querySelectorAll('.code-content');
    codeContents.forEach((content, i) => {
        if (i === index) {
            content.classList.add('active');
        } else {
            content.classList.remove('active');
        }
    });

    // Re-initialize syntax highlighting
    if (typeof hljs !== 'undefined') {
        setTimeout(() => {
            const activeContent = document.querySelector(`.code-content[data-code-index="${index}"]`);
            if (activeContent) {
                activeContent.querySelectorAll('pre code').forEach((block) => {
                    hljs.highlightElement(block);
                });
            }
        }, 50);
    }
}

// ============================================
// COPY CODE FUNCTIONALITY
// ============================================

function copyCode(index) {
    const codeContent = document.querySelector(`.code-content[data-code-index="${index}"] pre code`);
    if (!codeContent) return;

    const code = codeContent.textContent;

    // Copy to clipboard
    navigator.clipboard.writeText(code).then(() => {
        // Find the copy button
        const copyBtn = document.querySelector(`.code-content[data-code-index="${index}"] .copy-code-btn`);
        if (copyBtn) {
            const originalText = copyBtn.querySelector('.copy-text').textContent;
            copyBtn.querySelector('.copy-text').textContent = 'Copied!';
            copyBtn.style.background = 'var(--accent)';
            copyBtn.style.color = 'white';

            // Reset after 2 seconds
            setTimeout(() => {
                copyBtn.querySelector('.copy-text').textContent = originalText;
                copyBtn.style.background = '';
                copyBtn.style.color = '';
            }, 2000);
        }
    }).catch(err => {
        console.error('Failed to copy code:', err);
    });
}

// ============================================
// EXERCISE SOLUTION TOGGLE
// ============================================

function toggleSolution(exerciseIndex) {
    const exerciseCard = document.querySelector(`.exercise-card[data-exercise-index="${exerciseIndex}"]`);
    if (!exerciseCard) return;

    const solutionDiv = exerciseCard.querySelector('.exercise-solution');
    const toggleBtn = exerciseCard.querySelector('.show-solution-btn');
    const btnText = toggleBtn.querySelector('.solution-btn-text');

    if (solutionDiv.style.display === 'none' || !solutionDiv.style.display) {
        // Show solution
        solutionDiv.style.display = 'block';
        btnText.textContent = 'Hide Solution';
        toggleBtn.classList.add('revealed');
    } else {
        // Hide solution
        solutionDiv.style.display = 'none';
        btnText.textContent = 'Show Solution';
        toggleBtn.classList.remove('revealed');
    }
}

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize syntax highlighting for code blocks
    if (typeof hljs !== 'undefined') {
        document.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
    }

    // Set up keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Alt+1/2/3 to switch between Text/Code/Exercises tabs
        if (e.altKey) {
            if (e.key === '1') {
                e.preventDefault();
                switchContentTab('text');
            } else if (e.key === '2') {
                e.preventDefault();
                const codeTab = document.querySelector('.content-tab[data-tab="code"]');
                if (codeTab && !codeTab.disabled) {
                    switchContentTab('code');
                }
            } else if (e.key === '3') {
                e.preventDefault();
                const exercisesTab = document.querySelector('.content-tab[data-tab="exercises"]');
                if (exercisesTab && !exercisesTab.disabled) {
                    switchContentTab('exercises');
                }
            }
        }
    });

    // Auto-detect if only one content type exists and hide tabs
    const contentTabsWrapper = document.querySelector('.content-tabs-wrapper');
    if (contentTabsWrapper) {
        const visibleTabs = document.querySelectorAll('.content-tab:not([style*="display: none"])');
        if (visibleTabs.length === 1) {
            contentTabsWrapper.classList.add('single-tab');
        }
    }
});
