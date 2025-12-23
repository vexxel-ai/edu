/**
 * Base Visualization Class
 * All visualizations inherit from this base class
 */
class BaseVisualization {
    constructor(containerId, config = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            throw new Error(`Container with id "${containerId}" not found`);
        }
        this.config = config;
        this.state = 'paused'; // paused | playing | stepping
        this.animationSpeed = config.speed || 1000; // ms
    }

    // Must be implemented by subclasses
    init() {
        throw new Error('init() must be implemented by subclass');
    }

    play() {
        throw new Error('play() must be implemented by subclass');
    }

    pause() {
        this.state = 'paused';
    }

    reset() {
        throw new Error('reset() must be implemented by subclass');
    }

    step() {
        throw new Error('step() must be implemented by subclass');
    }

    // Utility methods
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    destroy() {
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

// Make available globally
if (typeof window !== 'undefined') {
    window.BaseVisualization = BaseVisualization;
}
