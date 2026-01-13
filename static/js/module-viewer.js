/**
 * Module Viewer
 * Slide viewer, magnifier, fullscreen, layout switching
 */

// ============================================
// LAYOUT INITIALIZATION
// ============================================

function initLayout() {
    const wrapper = document.getElementById('contentWrapper');
    const studioLeftPanel = document.getElementById('studioLeftPanel');
    const studioRightPanel = document.getElementById('studioRightPanel');
    const contentGrid = document.getElementById('contentGrid');

    if (!wrapper || !contentGrid) return;

    // Get all main content sections
    const sections = contentGrid.querySelectorAll('.section:not([id*="-studio"])');

    // Check if wrapper has layout-horizontal class (set by template based on notes/slides presence)
    const hasNotesOrSlides = wrapper.classList.contains('layout-horizontal');

    if (hasNotesOrSlides && studioLeftPanel && studioRightPanel) {
        // Split view: Notes/Slides | HTML Content
        studioLeftPanel.style.display = 'block';
        studioRightPanel.style.display = 'block';
        // Hide main sections
        sections.forEach(section => {
            section.style.display = 'none';
        });
    } else {
        // No notes/slides - centered layout
        if (studioLeftPanel) studioLeftPanel.style.display = 'none';
        if (studioRightPanel) studioRightPanel.style.display = 'none';
        // Show main sections
        sections.forEach(section => {
            section.style.display = 'block';
        });
    }
}

function switchStudioTab(tabName) {
    // Only switch tabs in the studio left panel
    const leftPanel = document.getElementById('studioLeftPanel');
    if (!leftPanel) return;

    // Remove active class from all vertical tab buttons and contents
    const tabs = leftPanel.querySelectorAll('.vertical-tab-btn');
    const contents = leftPanel.querySelectorAll('.studio-tab-content');

    tabs.forEach(tab => {
        tab.classList.remove('active');
    });

    contents.forEach(content => {
        content.classList.remove('active');
    });

    // Add active class to the selected tab and content
    const selectedTab = leftPanel.querySelector(`.vertical-tab-btn[data-tab="${tabName}"]`);
    const selectedContent = document.getElementById(`studio-tab-${tabName}`);

    if (selectedTab) {
        selectedTab.classList.add('active');
    }

    if (selectedContent) {
        selectedContent.classList.add('active');

        // Re-initialize magnifier if we're on the notes tab
        if (tabName === 'notes') {
            setTimeout(() => {
                initMagnifier('slideContainer', 'magnifier');
            }, 100);
        }
    }
}

// ============================================
// FULLSCREEN MANAGEMENT
// ============================================

function toggleFullscreen() {
    // Fullscreen the entire content wrapper
    const contentWrapper = document.getElementById('contentWrapper');

    if (!contentWrapper) {
        console.log('Content wrapper not found');
        return;
    }

    if (!document.fullscreenElement) {
        // Enter fullscreen
        contentWrapper.requestFullscreen().catch(err => {
            console.error('Error entering fullscreen:', err);
        });
    } else {
        // Exit fullscreen
        document.exitFullscreen();
    }
}

// Listen for fullscreen changes
document.addEventListener('fullscreenchange', () => {
    const fullscreenBtn = document.getElementById('fullscreenBtn');
    if (!fullscreenBtn) return;

    const enterIcon = fullscreenBtn.querySelector('.fullscreen-enter-icon');
    const exitIcon = fullscreenBtn.querySelector('.fullscreen-exit-icon');
    const label = fullscreenBtn.querySelector('.focus-mode-label');

    if (document.fullscreenElement) {
        // In fullscreen
        fullscreenBtn.classList.add('active');
        fullscreenBtn.title = 'Exit Focus Mode (ESC or F)';
        if (enterIcon) enterIcon.classList.add('hidden');
        if (exitIcon) exitIcon.classList.remove('hidden');
        if (label) label.textContent = 'Exit Focus';
    } else {
        // Not in fullscreen
        fullscreenBtn.classList.remove('active');
        fullscreenBtn.title = 'Focus Mode (F)';
        if (enterIcon) enterIcon.classList.remove('hidden');
        if (exitIcon) exitIcon.classList.add('hidden');
        if (label) label.textContent = 'Focus Mode';
    }
});

// Keyboard shortcut: F for fullscreen
document.addEventListener('keydown', (e) => {
    if (e.key === 'f' || e.key === 'F') {
        // Don't trigger if user is typing in an input
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            return;
        }
        e.preventDefault();
        toggleFullscreen();
    }
});

// ============================================
// SLIDE VIEWER
// ============================================

let currentSlide = 1;
let totalSlides = 0;

function initSlideViewer(total) {
    totalSlides = total;
    currentSlide = 1;
    showSlide(currentSlide);
}

function showSlide(n) {
    const slides = document.querySelectorAll('.slide-image');

    if (slides.length === 0) return;

    if (n > totalSlides) currentSlide = totalSlides;
    if (n < 1) currentSlide = 1;

    slides.forEach(slide => slide.classList.remove('active'));
    slides[currentSlide - 1].classList.add('active');

    // Update counter displays (both legacy and corner counter)
    const currentSlideEl = document.getElementById('currentSlide');
    const currentSlideEl2 = document.getElementById('currentSlide2');

    if (currentSlideEl) currentSlideEl.textContent = currentSlide;
    if (currentSlideEl2) currentSlideEl2.textContent = currentSlide;

    // Update button states (both legacy and floating)
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const prevBtn2 = document.getElementById('prevBtn2');
    const nextBtn2 = document.getElementById('nextBtn2');
    const prevBtnFloating = document.getElementById('prevBtnFloating');
    const nextBtnFloating = document.getElementById('nextBtnFloating');

    const isFirst = currentSlide === 1;
    const isLast = currentSlide === totalSlides;

    if (prevBtn) prevBtn.disabled = isFirst;
    if (nextBtn) nextBtn.disabled = isLast;
    if (prevBtn2) prevBtn2.disabled = isFirst;
    if (nextBtn2) nextBtn2.disabled = isLast;
    if (prevBtnFloating) prevBtnFloating.disabled = isFirst;
    if (nextBtnFloating) nextBtnFloating.disabled = isLast;
}

function nextSlide() {
    currentSlide++;
    showSlide(currentSlide);
}

function prevSlide() {
    currentSlide--;
    showSlide(currentSlide);
}

// Keyboard navigation
document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') prevSlide();
    if (e.key === 'ArrowRight') nextSlide();
});

// ============================================
// MAGNIFYING GLASS ZOOM
// ============================================

function initMagnifier(containerId, magnifierId) {
    const container = document.getElementById(containerId);
    const magnifier = document.getElementById(magnifierId);

    if (!container || !magnifier) return;

    const zoomLevel = 1.1; // 1.1x zoom (10% increase)

    container.addEventListener('mousemove', function(e) {
        const activeImage = container.querySelector('.slide-image.active');
        if (!activeImage) return;

        // Calculate background position based on mouse location
        const imgRect = activeImage.getBoundingClientRect();
        const imgX = e.clientX - imgRect.left;
        const imgY = e.clientY - imgRect.top;

        // Magnifier is fixed at bottom, so center the zoomed area around mouse position
        const magnifierRect = magnifier.getBoundingClientRect();
        const bgPosX = -imgX * zoomLevel + magnifierRect.width / 2;
        const bgPosY = -imgY * zoomLevel + magnifierRect.height / 2;

        // Set magnifier background
        magnifier.style.backgroundImage = `url('${activeImage.src}')`;
        magnifier.style.backgroundSize = `${imgRect.width * zoomLevel}px ${imgRect.height * zoomLevel}px`;
        magnifier.style.backgroundPosition = `${bgPosX}px ${bgPosY}px`;

        magnifier.classList.add('active');
    });

    container.addEventListener('mouseleave', function() {
        magnifier.classList.remove('active');
    });
}

// ============================================
// FILTERS (for modules page)
// ============================================

function toggleFilters() {
    const panel = document.getElementById('filterPanel');
    if (panel) {
        panel.classList.toggle('open');
    }
}

// Close filters when clicking a tag on mobile
if (typeof htmx !== 'undefined') {
    document.addEventListener('htmx:afterSwap', () => {
        if (window.innerWidth < 768) {
            const panel = document.getElementById('filterPanel');
            if (panel) {
                panel.classList.remove('open');
            }
        }
    });
}

// ============================================
// CODE TABS
// ============================================

function switchCodeTab(tabIndex) {
    // Remove active class from all tabs and content
    const tabs = document.querySelectorAll('.code-tab');
    const contents = document.querySelectorAll('.code-content');

    tabs.forEach(tab => tab.classList.remove('active'));
    contents.forEach(content => content.classList.remove('active'));

    // Add active class to selected tab and content
    const selectedTab = document.querySelector(`.code-tab[data-tab-index="${tabIndex}"]`);
    const selectedContent = document.querySelector(`.code-content[data-code-index="${tabIndex}"]`);

    if (selectedTab) selectedTab.classList.add('active');
    if (selectedContent) {
        selectedContent.classList.add('active');
        // Re-run highlight.js on the new content
        const codeBlock = selectedContent.querySelector('code');
        if (codeBlock && typeof hljs !== 'undefined') {
            hljs.highlightElement(codeBlock);
        }
    }
}

function copyCode(codeIndex) {
    const codeContent = document.querySelector(`.code-content[data-code-index="${codeIndex}"]`);
    if (!codeContent) return;

    const codeBlock = codeContent.querySelector('code');
    if (!codeBlock) return;

    // Copy to clipboard
    const text = codeBlock.textContent;
    navigator.clipboard.writeText(text).then(() => {
        // Update button text
        const btn = codeContent.querySelector('.copy-code-btn');
        const btnText = btn.querySelector('.copy-text');
        const originalText = btnText.textContent;

        btnText.textContent = 'Copied!';
        btn.style.background = 'var(--accent)';
        btn.style.color = 'white';

        // Reset after 2 seconds
        setTimeout(() => {
            btnText.textContent = originalText;
            btn.style.background = '';
            btn.style.color = '';
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy code:', err);
    });
}

// ============================================
// EXERCISE TOGGLES
// ============================================

function toggleSolution(exerciseIndex) {
    const exerciseCard = document.querySelector(`.exercise-card[data-exercise-index="${exerciseIndex}"]`);
    if (!exerciseCard) return;

    const solution = exerciseCard.querySelector('.exercise-solution');
    const btn = exerciseCard.querySelector('.show-solution-btn');
    const btnText = btn.querySelector('.solution-btn-text');

    if (solution.style.display === 'none' || !solution.style.display) {
        // Show solution
        solution.style.display = 'block';
        btnText.textContent = 'Hide Solution';
        btn.classList.add('expanded');
    } else {
        // Hide solution
        solution.style.display = 'none';
        btnText.textContent = 'Show Solution';
        btn.classList.remove('expanded');
    }
}

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize layout if on module detail page
    initLayout();

    // Initialize magnifiers for both containers (if they exist)
    initMagnifier('slideContainer', 'magnifier');
    initMagnifier('slideContainer2', 'magnifier2');

    // Initialize syntax highlighting for code snippets
    if (typeof hljs !== 'undefined') {
        document.querySelectorAll('.code-content code').forEach((block) => {
            hljs.highlightElement(block);
        });
    }
});
