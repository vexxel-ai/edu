# Markov Decision Processes

## Introduction

Markov Decision Processes (MDPs) provide a mathematical framework for modeling decision making in situations where outcomes are partly random and partly under the control of a decision maker.

## Formal Definition

An MDP is defined by a tuple (S, A, P, R, γ):

- **S**: Set of states
- **A**: Set of actions
- **P**: Transition probability function P(s'|s,a)
- **R**: Reward function R(s,a,s')
- **γ**: Discount factor (0 ≤ γ < 1)

## Markov Property

The Markov property states that the future is independent of the past given the present:

```
P(s_{t+1} | s_t, a_t, s_{t-1}, a_{t-1}, ..., s_0, a_0) = P(s_{t+1} | s_t, a_t)
```

## Key Components

### States
The complete description of the environment at a given time.

### Actions
Choices available to the agent that can influence state transitions.

### Transition Function
Probability of transitioning from state s to s' when taking action a:
```
P(s'|s,a) = Pr{S_{t+1} = s' | S_t = s, A_t = a}
```

### Reward Function
Immediate reward received after transition:
```
R(s,a,s') = E[R_{t+1} | S_t = s, A_t = a, S_{t+1} = s']
```

## Policy

A policy π defines the agent's behavior:
- **Deterministic**: π(s) → a
- **Stochastic**: π(a|s) → [0,1]

## Value Functions

### State Value Function
Expected return starting from state s following policy π:
```
V^π(s) = E_π[Σ_{k=0}^∞ γ^k R_{t+k+1} | S_t = s]
```

### Action Value Function (Q-function)
Expected return starting from s, taking action a, then following π:
```
Q^π(s,a) = E_π[Σ_{k=0}^∞ γ^k R_{t+k+1} | S_t = s, A_t = a]
```

## Bellman Equations

### Bellman Expectation Equation
```
V^π(s) = Σ_a π(a|s) Σ_{s'} P(s'|s,a)[R(s,a,s') + γV^π(s')]
```

### Bellman Optimality Equation
```
V*(s) = max_a Σ_{s'} P(s'|s,a)[R(s,a,s') + γV*(s')]
```

## Solution Methods

### Dynamic Programming
- **Value Iteration**: Iteratively update value function
- **Policy Iteration**: Alternate between policy evaluation and improvement

### Monte Carlo Methods
- Learn from complete episodes
- No model required

### Temporal Difference Learning
- Learn from incomplete episodes
- Combine MC and DP ideas
- Q-learning, SARSA

## Example: Grid World

Simple navigation problem:
```
+---+---+---+---+
| S |   |   | G |
+---+---+---+---+
|   | # |   |   |
+---+---+---+---+
```

- S: Start state
- G: Goal state (+1 reward)
- #: Wall (blocked)
- Actions: {up, down, left, right}
- Step cost: -0.01

## Applications

1. **Robotics**: Navigation and control
2. **Game Playing**: Chess, Go, Atari
3. **Resource Management**: Inventory, scheduling
4. **Finance**: Portfolio optimization
5. **Healthcare**: Treatment planning

## Extensions

- **Partially Observable MDPs (POMDPs)**: Incomplete state information
- **Continuous MDPs**: Continuous state/action spaces
- **Multi-Agent MDPs**: Multiple decision makers
- **Constrained MDPs**: Additional constraints on policies

## Key Insights

1. Optimal policy is deterministic
2. Value iteration converges to optimal value function
3. Policy iteration converges in polynomial time
4. Discount factor γ affects long-term vs short-term behavior
