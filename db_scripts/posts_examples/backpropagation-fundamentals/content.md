# Backpropagation Fundamentals

## Overview

Backpropagation is the cornerstone algorithm for training neural networks. It efficiently computes gradients of the loss function with respect to network parameters using the chain rule.

## The Chain Rule in Neural Networks

The power of backpropagation lies in its use of the chain rule to decompose the gradient computation:

```
∂L/∂w = (∂L/∂y) × (∂y/∂z) × (∂z/∂w)
```

Where:
- L is the loss function
- y is the network output
- z is the pre-activation
- w are the weights

## Forward Pass

During the forward pass, we:
1. Compute activations layer by layer
2. Store intermediate values for backward pass
3. Calculate the final loss

## Backward Pass

The backward pass propagates gradients from output to input:

```python
def backward(self, grad_output):
    # Gradient of loss w.r.t. pre-activation
    grad_z = grad_output * self.activation_derivative(self.z)

    # Gradient w.r.t. weights
    grad_w = np.dot(self.input.T, grad_z)

    # Gradient w.r.t. bias
    grad_b = np.sum(grad_z, axis=0)

    # Gradient w.r.t. input (for previous layer)
    grad_input = np.dot(grad_z, self.weights.T)

    return grad_input
```

## Computational Efficiency

Backpropagation is efficient because:
- **Single backward pass** computes all gradients
- **O(n)** time complexity for n parameters
- **Reuses** forward pass computations

## Common Activation Functions

### ReLU
```python
f(x) = max(0, x)
f'(x) = 1 if x > 0 else 0
```

### Sigmoid
```python
f(x) = 1 / (1 + e^(-x))
f'(x) = f(x) * (1 - f(x))
```

### Tanh
```python
f(x) = tanh(x)
f'(x) = 1 - tanh²(x)
```

## Challenges

### Vanishing Gradients
- Occurs with sigmoid/tanh in deep networks
- Solution: ReLU, batch normalization, residual connections

### Exploding Gradients
- Gradients grow exponentially
- Solution: Gradient clipping, careful initialization

## Best Practices

1. **Use appropriate initialization** (Xavier, He)
2. **Apply gradient clipping** for RNNs
3. **Monitor gradient magnitudes** during training
4. **Use batch normalization** to stabilize gradients
5. **Choose suitable activation functions** (ReLU family)

## Further Reading

- Rumelhart, Hinton, Williams (1986): Original backprop paper
- Understanding the difficulty of training deep feedforward neural networks
- Batch Normalization: Accelerating Deep Network Training
