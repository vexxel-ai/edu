# Introduction to Reinforcement Learning

Reinforcement Learning (RL) represents one of the three fundamental paradigms in machine learning, alongside supervised and unsupervised learning. Unlike supervised learning where we learn from labeled examples, or unsupervised learning where we find patterns in unlabeled data, reinforcement learning is about learning through interaction with an environment. An agent takes actions, observes the consequences, and learns to maximize cumulative rewards over time.

## The Core Framework

At its heart, reinforcement learning is formalized through the **Markov Decision Process (MDP)** framework. This mathematical model provides the theoretical foundation for understanding sequential decision-making problems. An MDP consists of five key components that work together to define the learning problem.

### Key Components

**The Agent** is the learner or decision maker. Think of it as an intelligent entity that observes the world, makes decisions, and learns from the outcomes. The agent could be a robot learning to walk, a program learning to play chess, or an algorithm optimizing energy consumption in a data center.

**The Environment** represents everything outside the agent. It's the world the agent interacts with, responds to the agent's actions, and provides feedback. The environment could be physical (like a maze) or virtual (like a video game), simple or incredibly complex.

**States** describe the current situation or configuration of the environment. A state captures all relevant information needed to make decisions. In chess, the state is the current board position. In autonomous driving, it includes sensor readings, car velocity, road conditions, and nearby objects.

**Actions** are the choices available to the agent in each state. These could be discrete (move left, right, up, down) or continuous (steering angle, acceleration). The set of available actions may depend on the current state.

**Rewards** provide the learning signal. After each action, the environment returns a numerical reward indicating how good or bad that action was. Rewards are the only way the agent learns what behavior is desirable. The reward signal is crucial—poorly designed rewards lead to unexpected and often undesirable behavior.

## The Reinforcement Learning Problem

The fundamental objective in RL is to learn a **policy** π that tells the agent which action to take in each state. Formally, a policy maps states to actions. The goal is to find the optimal policy π* that maximizes the **expected cumulative reward**, also called the return.

The return at time t is defined as:

G_t = R_{t+1} + γR_{t+2} + γ²R_{t+3} + ... = Σ γᵏR_{t+k+1}

Here, γ (gamma) is the discount factor between 0 and 1. It determines how much we value future rewards compared to immediate rewards. A γ close to 0 makes the agent myopic (only caring about immediate rewards), while γ close to 1 makes it far-sighted.

### Value Functions

Two crucial concepts in RL are the **state-value function** V(s) and the **action-value function** Q(s,a).

The state-value function V^π(s) represents the expected return starting from state s and following policy π:

V^π(s) = E_π[G_t | S_t = s]

The action-value function Q^π(s,a) represents the expected return starting from state s, taking action a, and then following policy π:

Q^π(s,a) = E_π[G_t | S_t = s, A_t = a]

These value functions are fundamental because optimal behavior can be derived from them. If we know Q*(s,a) for all states and actions, the optimal policy simply selects the action with the highest Q-value in each state.

## Classic Algorithms

### Q-Learning

Q-learning is a foundational model-free RL algorithm that learns the optimal action-value function Q* directly, without requiring a model of the environment. It's an **off-policy** algorithm, meaning it learns about the optimal policy while following a different exploratory policy.

The Q-learning update rule is beautifully simple:

Q(s,a) ← Q(s,a) + α[r + γ max_a' Q(s',a') - Q(s,a)]

Here's a complete implementation:

```python
import numpy as np

def q_learning(env, episodes=1000, alpha=0.1, gamma=0.99, epsilon=0.1):
    '''
    Q-learning algorithm implementation.

    Parameters:
    - env: The environment with n_states and n_actions
    - episodes: Number of training episodes
    - alpha: Learning rate (step size)
    - gamma: Discount factor
    - epsilon: Exploration rate for ε-greedy policy
    '''
    # Initialize Q-table with zeros
    Q = np.zeros((env.n_states, env.n_actions))

    for episode in range(episodes):
        state = env.reset()
        done = False

        while not done:
            # Epsilon-greedy action selection
            if np.random.random() < epsilon:
                # Explore: random action
                action = env.action_space.sample()
            else:
                # Exploit: best known action
                action = np.argmax(Q[state])

            # Take action and observe result
            next_state, reward, done = env.step(action)

            # Q-learning update (off-policy)
            best_next_action = np.argmax(Q[next_state])
            td_target = reward + gamma * Q[next_state, best_next_action]
            td_error = td_target - Q[state, action]
            Q[state, action] += alpha * td_error

            state = next_state

    return Q
```

### SARSA

SARSA (State-Action-Reward-State-Action) is similar to Q-learning but is an **on-policy** algorithm. It updates Q-values based on the action actually taken by the current policy, not the best possible action:

Q(s,a) ← Q(s,a) + α[r + γQ(s',a') - Q(s,a)]

The difference is subtle but important. SARSA is more conservative because it learns the value of the policy it's actually following, including the exploration. Q-learning is more aggressive, always assuming optimal future behavior.

## Exploration vs Exploitation

One of the central dilemmas in RL is the exploration-exploitation tradeoff. Should the agent **exploit** what it already knows to maximize reward, or should it **explore** to potentially discover better strategies?

Common exploration strategies include:

1. **ε-greedy**: With probability ε, choose a random action; otherwise choose the best known action
2. **Softmax**: Choose actions probabilistically based on their Q-values
3. **Upper Confidence Bound (UCB)**: Balance exploration and exploitation using uncertainty estimates
4. **Optimistic initialization**: Start with optimistic Q-values to encourage exploration

## Deep Reinforcement Learning

Traditional RL methods store Q-values in tables, which becomes infeasible for large or continuous state spaces. **Deep Reinforcement Learning** uses neural networks as function approximators to handle high-dimensional inputs.

### DQN (Deep Q-Network)

DQN revolutionized RL by successfully combining Q-learning with deep neural networks. Key innovations include:

- **Experience Replay**: Store transitions in a replay buffer and sample randomly for training, breaking temporal correlations
- **Target Network**: Use a separate, slowly-updated network for computing target values, improving stability
- **Frame Stacking**: Use multiple consecutive frames as input to capture temporal information

```python
import torch
import torch.nn as nn

class DQN(nn.Module):
    def __init__(self, state_dim, action_dim, hidden_dim=128):
        super(DQN, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, action_dim)
        )

    def forward(self, state):
        return self.network(state)
```

## Policy Gradient Methods

While value-based methods like Q-learning learn which actions are best, **policy gradient methods** directly learn the policy itself. They parameterize the policy (often with a neural network) and use gradient ascent to maximize expected return.

The core idea is the **policy gradient theorem**, which provides a way to compute gradients of the expected return with respect to policy parameters. This enables us to adjust the policy to increase the probability of actions that lead to higher returns.

Popular policy gradient algorithms include REINFORCE, Actor-Critic methods, Proximal Policy Optimization (PPO), and Trust Region Policy Optimization (TRPO).

## Applications

Reinforcement learning has achieved remarkable success across diverse domains:

- **Game Playing**: AlphaGo defeated world champions; OpenAI Five mastered Dota 2
- **Robotics**: Learning locomotion, manipulation, and complex motor skills
- **Autonomous Driving**: Learning driving policies from experience
- **Resource Management**: Optimizing data center cooling, chip design
- **Finance**: Portfolio management and algorithmic trading
- **Healthcare**: Treatment optimization and drug discovery

## Challenges and Future Directions

Despite impressive successes, RL faces several challenges:

- **Sample Efficiency**: RL often requires enormous amounts of experience
- **Reward Engineering**: Designing good reward functions is difficult
- **Sim-to-Real Transfer**: Policies learned in simulation may not transfer to reality
- **Safety**: Exploration can lead to dangerous behavior during training
- **Partial Observability**: Real environments often don't provide complete state information

Active research areas include hierarchical RL, meta-learning, multi-agent RL, and combining RL with other learning paradigms.

## Getting Started

To begin your RL journey, start with simple environments like OpenAI Gym. Implement basic algorithms like Q-learning and SARSA on gridworlds. Progress to more complex environments and deep RL methods. The handwritten notes and video resources below provide visual explanations and practical examples to deepen your understanding.
