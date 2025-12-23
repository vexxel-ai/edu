/**
 * MLP Forward Propagation Visualization
 * Shows animated forward pass through a multi-layer perceptron
 */
class MLPForwardVisualization extends BaseVisualization {
    constructor(containerId, config = {}) {
        super(containerId, config);

        this.layers = config.layers || [3, 4, 2]; // [input, hidden, output]
        this.activation = config.activation || 'relu';
        this.inputData = config.inputData || [0.5, 0.8, 0.3];
        this.speed = config.speed || 1000;

        this.svg = null;
        this.currentLayer = 0;
        this.activations = [];
        this.weights = [];

        this.nodeRadius = 25;
        this.layerSpacing = 180;
        this.width = 800;
        this.height = 500;
    }

    init() {
        // Clear container
        this.container.innerHTML = '';

        // Create container structure
        const wrapper = document.createElement('div');
        wrapper.className = 'relative w-full h-full flex flex-col';
        wrapper.innerHTML = `
            <div class="flex-1 relative" id="${this.container.id}-svg"></div>
            <div class="bg-gray-800 border-t border-gray-700 px-6 py-4">
                <div class="flex items-center justify-center space-x-4">
                    <button id="btn-play" class="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition">
                        ▶ Play
                    </button>
                    <button id="btn-pause" class="px-6 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg font-medium transition">
                        ⏸ Pause
                    </button>
                    <button id="btn-step" class="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition">
                        ⏭ Step
                    </button>
                    <button id="btn-reset" class="px-6 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition">
                        ↻ Reset
                    </button>
                    <div class="ml-4 px-4 py-2 bg-gray-700 rounded-lg">
                        <span class="text-sm text-gray-300">Activation: <strong class="text-blue-400">${this.activation.toUpperCase()}</strong></span>
                    </div>
                </div>
            </div>
        `;
        this.container.appendChild(wrapper);

        // Create SVG
        const svgContainer = document.getElementById(`${this.container.id}-svg`);
        this.svg = d3.select(svgContainer)
            .append('svg')
            .attr('width', '100%')
            .attr('height', '100%')
            .attr('viewBox', `0 0 ${this.width} ${this.height}`)
            .attr('preserveAspectRatio', 'xMidYMid meet');

        // Initialize data structures
        this.initializeWeights();
        this.initializeActivations();

        // Draw network
        this.drawNetwork();

        // Attach event listeners
        this.attachEventListeners();

        // Draw legend
        this.drawLegend();
    }

    initializeWeights() {
        this.weights = [];
        for (let l = 0; l < this.layers.length - 1; l++) {
            const layerWeights = [];
            for (let i = 0; i < this.layers[l]; i++) {
                const nodeWeights = [];
                for (let j = 0; j < this.layers[l + 1]; j++) {
                    nodeWeights.push((Math.random() - 0.5) * 2); // Random weights between -1 and 1
                }
                layerWeights.push(nodeWeights);
            }
            this.weights.push(layerWeights);
        }
    }

    initializeActivations() {
        this.activations = this.layers.map(size => Array(size).fill(0));
        this.activations[0] = [...this.inputData];
    }

    drawNetwork() {
        // Calculate total width needed
        const totalWidth = this.layers.length * this.layerSpacing;
        const startX = (this.width - totalWidth) / 2 + this.layerSpacing / 2;

        // Draw connections first (so they're behind neurons)
        for (let l = 0; l < this.layers.length - 1; l++) {
            this.drawConnections(l, startX);
        }

        // Draw neurons
        this.layers.forEach((numNodes, layerIdx) => {
            this.drawLayer(layerIdx, numNodes, startX);
        });

        // Draw layer labels
        this.drawLayerLabels(startX);
    }

    drawConnections(layerIdx, startX) {
        const fromLayer = this.layers[layerIdx];
        const toLayer = this.layers[layerIdx + 1];

        const fromX = startX + layerIdx * this.layerSpacing;
        const toX = startX + (layerIdx + 1) * this.layerSpacing;

        const fromSpacing = this.height / (fromLayer + 1);
        const toSpacing = this.height / (toLayer + 1);

        for (let i = 0; i < fromLayer; i++) {
            for (let j = 0; j < toLayer; j++) {
                const fromY = (i + 1) * fromSpacing;
                const toY = (j + 1) * toSpacing;

                this.svg.append('line')
                    .attr('class', `connection conn-${layerIdx}-${i}-${j}`)
                    .attr('x1', fromX + this.nodeRadius)
                    .attr('y1', fromY)
                    .attr('x2', toX - this.nodeRadius)
                    .attr('y2', toY)
                    .attr('stroke', '#4b5563')
                    .attr('stroke-width', 1.5)
                    .attr('opacity', 0.2);
            }
        }
    }

    drawLayer(layerIdx, numNodes, startX) {
        const x = startX + layerIdx * this.layerSpacing;
        const spacing = this.height / (numNodes + 1);

        for (let i = 0; i < numNodes; i++) {
            const y = (i + 1) * spacing;

            // Neuron circle
            this.svg.append('circle')
                .attr('class', `neuron neuron-${layerIdx}-${i}`)
                .attr('cx', x)
                .attr('cy', y)
                .attr('r', this.nodeRadius)
                .attr('fill', '#374151')
                .attr('stroke', '#6b7280')
                .attr('stroke-width', 2);

            // Value text
            this.svg.append('text')
                .attr('class', `neuron-value value-${layerIdx}-${i}`)
                .attr('x', x)
                .attr('y', y + 5)
                .attr('text-anchor', 'middle')
                .attr('fill', 'white')
                .attr('font-size', '14px')
                .attr('font-weight', 'bold')
                .attr('opacity', 0)
                .text('0.00');
        }
    }

    drawLayerLabels(startX) {
        const labels = ['Input Layer', 'Hidden Layer', 'Output Layer'];
        const labelCount = Math.min(this.layers.length, labels.length);

        for (let i = 0; i < labelCount; i++) {
            const x = startX + i * this.layerSpacing;

            this.svg.append('text')
                .attr('x', x)
                .attr('y', 30)
                .attr('text-anchor', 'middle')
                .attr('fill', '#9ca3af')
                .attr('font-size', '14px')
                .attr('font-weight', '600')
                .text(labels[i]);
        }
    }

    drawLegend() {
        const legend = this.svg.append('g')
            .attr('class', 'legend')
            .attr('transform', `translate(20, ${this.height - 80})`);

        // Active neuron
        legend.append('circle')
            .attr('cx', 10)
            .attr('cy', 10)
            .attr('r', 8)
            .attr('fill', '#3b82f6');

        legend.append('text')
            .attr('x', 25)
            .attr('y', 15)
            .attr('fill', '#d1d5db')
            .attr('font-size', '12px')
            .text('Active Neuron');

        // Inactive neuron
        legend.append('circle')
            .attr('cx', 10)
            .attr('cy', 35)
            .attr('r', 8)
            .attr('fill', '#374151')
            .attr('stroke', '#6b7280')
            .attr('stroke-width', 2);

        legend.append('text')
            .attr('x', 25)
            .attr('y', 40)
            .attr('fill', '#d1d5db')
            .attr('font-size', '12px')
            .text('Inactive Neuron');

        // Active connection
        legend.append('line')
            .attr('x1', 10)
            .attr('y1', 60)
            .attr('x2', 40)
            .attr('y2', 60)
            .attr('stroke', '#3b82f6')
            .attr('stroke-width', 2);

        legend.append('text')
            .attr('x', 50)
            .attr('y', 65)
            .attr('fill', '#d1d5db')
            .attr('font-size', '12px')
            .text('Active Connection');
    }

    attachEventListeners() {
        document.getElementById('btn-play').addEventListener('click', () => this.play());
        document.getElementById('btn-pause').addEventListener('click', () => this.pause());
        document.getElementById('btn-step').addEventListener('click', () => this.step());
        document.getElementById('btn-reset').addEventListener('click', () => this.reset());
    }

    async play() {
        if (this.state === 'playing') return;

        this.state = 'playing';
        this.currentLayer = 0;

        // Reset and show input
        await this.reset();
        await this.showInputValues();
        await this.sleep(this.speed);

        // Animate through each layer
        for (let l = 0; l < this.layers.length - 1; l++) {
            if (this.state !== 'playing') break;

            await this.animateLayer(l);
            await this.sleep(this.speed);
        }

        this.state = 'paused';
    }

    async showInputValues() {
        // Activate input neurons
        for (let i = 0; i < this.layers[0]; i++) {
            await this.activateNeuron(0, i, this.activations[0][i]);
        }
    }

    async animateLayer(layerIdx) {
        // Highlight connections
        await this.highlightConnections(layerIdx);
        await this.sleep(300);

        // Calculate activations for next layer
        await this.computeNextLayer(layerIdx);
        await this.sleep(300);

        // Show activation function
        if (layerIdx < this.layers.length - 2) {
            await this.showActivationBadge(layerIdx + 1);
        }

        this.currentLayer = layerIdx + 1;
    }

    async highlightConnections(layerIdx) {
        // Reset all connections
        this.svg.selectAll('.connection')
            .transition()
            .duration(200)
            .attr('stroke', '#4b5563')
            .attr('opacity', 0.2);

        // Highlight connections for this layer
        for (let i = 0; i < this.layers[layerIdx]; i++) {
            for (let j = 0; j < this.layers[layerIdx + 1]; j++) {
                this.svg.select(`.conn-${layerIdx}-${i}-${j}`)
                    .transition()
                    .duration(300)
                    .attr('stroke', '#3b82f6')
                    .attr('stroke-width', 2)
                    .attr('opacity', 0.8);
            }
        }
    }

    async computeNextLayer(layerIdx) {
        const nextLayer = layerIdx + 1;

        // Compute activations
        for (let j = 0; j < this.layers[nextLayer]; j++) {
            let sum = 0;
            for (let i = 0; i < this.layers[layerIdx]; i++) {
                sum += this.activations[layerIdx][i] * this.weights[layerIdx][i][j];
            }

            // Apply activation function
            const activated = this.applyActivation(sum);
            this.activations[nextLayer][j] = activated;

            // Animate neuron
            await this.activateNeuron(nextLayer, j, activated);
            await this.sleep(100);
        }
    }

    async activateNeuron(layer, index, value) {
        const neuron = this.svg.select(`.neuron-${layer}-${index}`);
        const text = this.svg.select(`.value-${layer}-${index}`);

        // Pulse animation
        await neuron
            .transition()
            .duration(200)
            .attr('fill', '#3b82f6')
            .attr('r', this.nodeRadius + 5)
            .transition()
            .duration(200)
            .attr('r', this.nodeRadius)
            .end();

        // Show value
        text.text(value.toFixed(2))
            .transition()
            .duration(200)
            .attr('opacity', 1);
    }

    async showActivationBadge(layerIdx) {
        const totalWidth = this.layers.length * this.layerSpacing;
        const startX = (this.width - totalWidth) / 2 + this.layerSpacing / 2;
        const x = startX + layerIdx * this.layerSpacing;

        const badge = this.svg.append('g')
            .attr('class', 'activation-badge')
            .attr('opacity', 0);

        badge.append('rect')
            .attr('x', x - 40)
            .attr('y', this.height - 30)
            .attr('width', 80)
            .attr('height', 30)
            .attr('rx', 5)
            .attr('fill', '#8b5cf6');

        badge.append('text')
            .attr('x', x)
            .attr('y', this.height - 10)
            .attr('text-anchor', 'middle')
            .attr('fill', 'white')
            .attr('font-size', '14px')
            .attr('font-weight', 'bold')
            .text(this.activation.toUpperCase());

        await badge
            .transition()
            .duration(300)
            .attr('opacity', 1)
            .end();

        await this.sleep(600);

        await badge
            .transition()
            .duration(300)
            .attr('opacity', 0)
            .remove()
            .end();
    }

    applyActivation(x) {
        switch (this.activation.toLowerCase()) {
            case 'relu':
                return Math.max(0, x);
            case 'sigmoid':
                return 1 / (1 + Math.exp(-x));
            case 'tanh':
                return Math.tanh(x);
            case 'leaky_relu':
                return x > 0 ? x : 0.01 * x;
            default:
                return x; // Linear
        }
    }

    pause() {
        this.state = 'paused';
    }

    async step() {
        if (this.currentLayer >= this.layers.length - 1) {
            return;
        }

        if (this.currentLayer === 0) {
            await this.showInputValues();
        } else {
            await this.animateLayer(this.currentLayer);
        }

        this.currentLayer++;
    }

    async reset() {
        this.state = 'paused';
        this.currentLayer = 0;

        // Reset activations
        this.initializeActivations();

        // Reset visuals
        this.svg.selectAll('.neuron')
            .transition()
            .duration(200)
            .attr('fill', '#374151')
            .attr('r', this.nodeRadius);

        this.svg.selectAll('.neuron-value')
            .transition()
            .duration(200)
            .attr('opacity', 0);

        this.svg.selectAll('.connection')
            .transition()
            .duration(200)
            .attr('stroke', '#4b5563')
            .attr('stroke-width', 1.5)
            .attr('opacity', 0.2);

        this.svg.selectAll('.activation-badge').remove();
    }
}

// Make available globally
if (typeof window !== 'undefined') {
    window.MLPForwardVisualization = MLPForwardVisualization;
}
