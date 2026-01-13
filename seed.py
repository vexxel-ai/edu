"""
Seed script to populate the database with sample data.

Run this script to create:
- 3 sample modules (posts)
- Hierarchical tags
- Various media assets (slides, images, YouTube links, blog links, HTML)
"""

from sqlmodel import Session, select

from app.database import create_db_and_tables, engine
from app.models import MediaAsset, MediaType, Post, PostTag, Tag


def create_tags(session: Session) -> dict[str, Tag]:
    """Create hierarchical tag structure."""
    tags = {}

    # Root tags
    tags["rl"] = Tag(name="Reinforcement Learning", slug="reinforcement-learning")
    tags["dl"] = Tag(name="Deep Learning", slug="deep-learning")
    tags["algo"] = Tag(name="Algorithms", slug="algorithms")
    tags["cs"] = Tag(name="Computer Science", slug="computer-science")

    session.add_all([tags["rl"], tags["dl"], tags["algo"], tags["cs"]])
    session.commit()
    session.refresh(tags["rl"])
    session.refresh(tags["dl"])
    session.refresh(tags["algo"])
    session.refresh(tags["cs"])

    # Child tags for RL
    tags["rl_problem"] = Tag(
        name="The RL Problem",
        slug="the-rl-problem",
        parent_id=tags["rl"].id
    )
    tags["mdp"] = Tag(
        name="Markov Decision Processes",
        slug="markov-decision-processes",
        parent_id=tags["rl"].id
    )

    # Child tags for Deep Learning
    tags["gnn"] = Tag(
        name="Graph Neural Networks",
        slug="graph-neural-networks",
        parent_id=tags["dl"].id
    )
    tags["message_passing"] = Tag(
        name="Message Passing",
        slug="message-passing",
        parent_id=tags["gnn"].id
    )

    # Child tags for Algorithms
    tags["dp"] = Tag(
        name="Dynamic Programming",
        slug="dynamic-programming",
        parent_id=tags["algo"].id
    )

    # Child tags for CS
    tags["theory"] = Tag(
        name="Theory",
        slug="theory",
        parent_id=tags["cs"].id
    )

    session.add_all([
        tags["rl_problem"],
        tags["mdp"],
        tags["gnn"],
        tags["message_passing"],
        tags["dp"],
        tags["theory"]
    ])
    session.commit()

    for tag in tags.values():
        session.refresh(tag)

    return tags


def create_posts(session: Session, tags: dict[str, Tag]) -> None:
    """Create sample posts with different media types."""

    # Post 1: Reinforcement Learning Basics (Images + YouTube + Blog)
    post1 = Post(
        title="Reinforcement Learning Basics",
        slug="reinforcement-learning-basics",
        description="""
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
        """
    )
    session.add(post1)
    session.commit()
    session.refresh(post1)

    # Add tags to post1
    session.add(PostTag(post_id=post1.id, tag_id=tags["rl"].id))
    session.add(PostTag(post_id=post1.id, tag_id=tags["rl_problem"].id))

    # Add media assets to post1 (using kadane example notes)
    assets1 = [
        MediaAsset(
            post_id=post1.id,
            type=MediaType.IMAGE,
            url="/static/content/kadane/example_0.jpg",
            title="Kadane's Algorithm - Page 1",
            order=1
        ),
        MediaAsset(
            post_id=post1.id,
            type=MediaType.IMAGE,
            url="/static/content/kadane/example_1.jpg",
            title="Kadane's Algorithm - Page 2",
            order=2
        ),
        MediaAsset(
            post_id=post1.id,
            type=MediaType.IMAGE,
            url="/static/content/kadane/example_2.jpg",
            title="Kadane's Algorithm - Page 3",
            order=3
        ),
        MediaAsset(
            post_id=post1.id,
            type=MediaType.IMAGE,
            url="/static/uploads/example_x.jpg",
            title="Books on Shelves Problem",
            order=4
        ),
        MediaAsset(
            post_id=post1.id,
            type=MediaType.YOUTUBE,
            url="https://www.youtube.com/embed/2pWv7GOvuf0",
            title="Introduction to Reinforcement Learning",
            order=5
        ),
        MediaAsset(
            post_id=post1.id,
            type=MediaType.BLOG_LINK,
            url="https://spinningup.openai.com/en/latest/spinningup/rl_intro.html",
            title="OpenAI Spinning Up - Introduction to RL",
            order=6
        ),
    ]
    session.add_all(assets1)

    # Post 2: Graph Neural Networks (Slides + Images)
    post2 = Post(
        title="Graph Neural Networks: An Introduction",
        slug="graph-neural-networks-intro",
        description="""
# Graph Neural Networks: Extending Deep Learning to Graph-Structured Data

Graph Neural Networks (GNNs) represent a revolutionary paradigm in deep learning, enabling neural networks to process and learn from graph-structured data. While traditional deep learning has achieved remarkable success on grid-like data (images with CNNs) and sequential data (text with RNNs and Transformers), many real-world problems involve complex relational structures that are best represented as graphs.

## The Motivation for GNNs

The world is fundamentally interconnected. Social networks connect people through friendships and interactions. Molecules are graphs where atoms are nodes and chemical bonds are edges. The internet itself is a massive graph of web pages connected by hyperlinks. Knowledge bases organize information as entities and their relationships. Citation networks connect research papers through references.

Traditional neural network architectures struggle with graph data because:

1. **Variable Size**: Graphs can have arbitrary numbers of nodes and edges
2. **No Fixed Order**: Unlike sequences or grids, graph nodes have no canonical ordering
3. **Complex Topology**: The connectivity pattern itself contains crucial information
4. **Permutation Invariance**: The same graph should produce the same output regardless of how nodes are indexed

Graph Neural Networks solve these challenges by operating directly on graph structures, learning representations that capture both node features and the graph's topology.

## Core Concepts and Foundations

### Graph Representation

A graph G = (V, E) consists of:
- **Nodes (vertices) V**: Entities in the network
- **Edges E**: Relationships or connections between nodes
- **Node Features X**: Attribute vectors describing each node
- **Edge Features**: Optional attributes describing edges
- **Adjacency Matrix A**: Encodes the graph structure

Graphs can be directed or undirected, weighted or unweighted, and may include self-loops and multiple edges.

### The Message Passing Framework

The fundamental operation in GNNs is **message passing**—a paradigm where nodes iteratively aggregate information from their neighbors to update their representations. This process has three key steps:

**1. Message Creation**: Each node creates messages for its neighbors based on its current representation

**2. Aggregation**: Each node collects and combines messages from its neighbors using a permutation-invariant function (sum, mean, max, or attention)

**3. Update**: Each node updates its representation by combining its current state with the aggregated neighbor information

This can be expressed mathematically as:

h_v^(k+1) = UPDATE^(k)(h_v^(k), AGGREGATE^(k)({h_u^(k) : u ∈ N(v)}))

Where:
- h_v^(k) is the representation of node v at layer k
- N(v) is the neighborhood of node v
- UPDATE and AGGREGATE are learnable functions (typically neural networks)

### A Complete GNN Layer Implementation

Here's a full implementation of a basic Graph Convolutional Network (GCN) layer:

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class GCNLayer(nn.Module):
    '''
    Graph Convolutional Network layer implementing message passing.

    Based on the paper "Semi-Supervised Classification with Graph Convolutional Networks"
    by Kipf & Welling (2017).
    '''
    def __init__(self, in_features, out_features, use_bias=True):
        super(GCNLayer, self).__init__()
        self.in_features = in_features
        self.out_features = out_features

        # Learnable weight matrix
        self.weight = nn.Parameter(torch.FloatTensor(in_features, out_features))

        if use_bias:
            self.bias = nn.Parameter(torch.FloatTensor(out_features))
        else:
            self.register_parameter('bias', None)

        self.reset_parameters()

    def reset_parameters(self):
        # Xavier/Glorot initialization
        nn.init.xavier_uniform_(self.weight)
        if self.bias is not None:
            nn.init.zeros_(self.bias)

    def forward(self, node_features, adjacency_matrix):
        '''
        Forward pass of GCN layer.

        Args:
            node_features: (N, in_features) - node feature matrix
            adjacency_matrix: (N, N) - graph structure (normalized)

        Returns:
            (N, out_features) - updated node representations
        '''
        # Step 1: Linear transformation of node features
        # (N, in_features) @ (in_features, out_features) = (N, out_features)
        support = torch.mm(node_features, self.weight)

        # Step 2: Aggregate neighbor information via matrix multiplication
        # (N, N) @ (N, out_features) = (N, out_features)
        output = torch.sparse.mm(adjacency_matrix, support)

        # Step 3: Add bias if specified
        if self.bias is not None:
            output = output + self.bias

        return output

class GCN(nn.Module):
    '''Complete Graph Convolutional Network model.'''
    def __init__(self, input_dim, hidden_dim, output_dim, dropout=0.5):
        super(GCN, self).__init__()
        self.gc1 = GCNLayer(input_dim, hidden_dim)
        self.gc2 = GCNLayer(hidden_dim, output_dim)
        self.dropout = dropout

    def forward(self, x, adj):
        # First GCN layer with ReLU and dropout
        x = F.relu(self.gc1(x, adj))
        x = F.dropout(x, self.dropout, training=self.training)

        # Second GCN layer
        x = self.gc2(x, adj)

        return F.log_softmax(x, dim=1)
```

## Popular GNN Architectures

### Graph Convolutional Networks (GCN)

GCNs apply convolutional operations to graphs by defining convolution as aggregating features from neighbors. The key insight is normalizing the adjacency matrix using the graph Laplacian to ensure stable learning:

Ã = D^(-1/2) A D^(-1/2)

Where D is the degree matrix and A is the adjacency matrix with self-loops.

### Graph Attention Networks (GAT)

GATs introduce attention mechanisms to weigh neighbor contributions differently. Instead of treating all neighbors equally, the model learns which neighbors are most relevant:

```python
class GATLayer(nn.Module):
    '''Graph Attention Network layer.'''
    def __init__(self, in_features, out_features, n_heads=8, dropout=0.6):
        super(GATLayer, self).__init__()
        self.n_heads = n_heads
        self.out_features = out_features

        # Multi-head attention weights
        self.W = nn.Parameter(torch.zeros(in_features, out_features * n_heads))
        self.a = nn.Parameter(torch.zeros(2 * out_features, 1))

        self.leakyrelu = nn.LeakyReLU(0.2)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, adj):
        # Linear transformation
        h = torch.mm(x, self.W).view(-1, self.n_heads, self.out_features)

        # Compute attention scores for each edge
        N = h.size(0)
        a_input = torch.cat([h.repeat(1, 1, N).view(N * N, -1),
                            h.repeat(N, 1, 1).view(N * N, -1)], dim=1)
        e = self.leakyrelu(torch.matmul(a_input, self.a).squeeze(1))

        # Mask attention scores for non-existing edges
        attention = torch.where(adj > 0, e, torch.tensor(-1e9).to(x.device))
        attention = F.softmax(attention, dim=1)
        attention = self.dropout(attention)

        # Aggregate with attention weights
        h_prime = torch.matmul(attention, h)

        return F.elu(h_prime)
```

### GraphSAGE (Sample and Aggregate)

GraphSAGE enables inductive learning by sampling and aggregating features from a node's local neighborhood. It supports various aggregation functions (mean, LSTM, pooling) and can generalize to previously unseen nodes.

### Message Passing Neural Networks (MPNN)

MPNNs provide a general framework that unifies many GNN variants. They explicitly separate message creation, aggregation, and update steps, allowing flexible design of each component.

## Training Graph Neural Networks

### Node Classification

Predicting labels for nodes in a graph (e.g., classifying research papers by topic in a citation network):

```python
def train_node_classification(model, features, labels, adj, idx_train):
    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)

    for epoch in range(200):
        optimizer.zero_grad()

        # Forward pass
        output = model(features, adj)

        # Compute loss only on training nodes
        loss = F.nll_loss(output[idx_train], labels[idx_train])

        # Backward pass
        loss.backward()
        optimizer.step()

        if epoch % 10 == 0:
            print(f'Epoch {epoch}, Loss: {loss.item():.4f}')
```

### Graph Classification

Predicting properties of entire graphs (e.g., molecular property prediction):

After node-level message passing, we need graph-level pooling:

```python
def graph_classification_forward(node_features, edge_index, batch):
    # Apply GNN layers
    x = self.conv1(node_features, edge_index)
    x = F.relu(x)
    x = self.conv2(x, edge_index)

    # Global pooling to get graph-level representation
    x = global_mean_pool(x, batch)  # or global_max_pool, global_add_pool

    # Classification head
    x = self.fc(x)
    return x
```

### Link Prediction

Predicting missing edges in a graph (e.g., friend recommendations in social networks):

Encode nodes with GNN, then score potential edges using node pair representations.

## Real-World Applications

**Drug Discovery**: GNNs model molecular structures to predict properties, drug-target interactions, and synthesizability. Companies like Atomwise and Insilico Medicine use GNNs to accelerate drug development.

**Recommendation Systems**: Pinterest and Alibaba use GNNs to model user-item interactions, capturing complex relationships for personalized recommendations.

**Traffic Forecasting**: GNNs model road networks to predict traffic speeds and congestion, helping optimize routes and manage cities.

**Social Network Analysis**: Identifying communities, detecting fake accounts, and predicting information spread.

**Knowledge Graphs**: Reasoning about entities and relations for question answering and semantic search (used by Google, Amazon, Microsoft).

**Computer Vision**: Scene understanding by modeling objects as graph nodes and their relationships as edges.

**Code Understanding**: Representing programs as abstract syntax trees or control flow graphs for bug detection and code completion.

## Advanced Topics and Challenges

### Over-Smoothing

A key challenge: as GNNs get deeper, node representations become increasingly similar (over-smoothing). Solutions include:
- Residual connections
- Jumping knowledge networks
- Adaptive depth mechanisms

### Scalability

Training on massive graphs (billions of nodes) requires:
- Mini-batch sampling strategies
- Cluster-GCN approaches
- Efficient sparse operations
- Distributed training

### Heterogeneous and Dynamic Graphs

Real graphs often have multiple node/edge types (heterogeneous) and evolve over time (dynamic). Recent work extends GNNs to handle these complexities.

### Explainability

Understanding why a GNN makes certain predictions is crucial for high-stakes applications. Methods like GNNExplainer identify important subgraphs for predictions.

## Getting Started with GNNs

**Libraries and Tools**:
- **PyTorch Geometric (PyG)**: Most popular GNN library with extensive model implementations
- **Deep Graph Library (DGL)**: Efficient and flexible, supports PyTorch and TensorFlow
- **Spektral**: GNN library for Keras/TensorFlow
- **GraphGym**: Experimentation platform for GNN research

**Datasets**:
- Cora, CiteSeer, PubMed (citation networks)
- PROTEINS, MUTAG (molecular graphs)
- Reddit, OGB datasets (large-scale benchmarks)

Start with node classification on small citation networks, then progress to graph classification and more complex tasks. The combination of handwritten notes, slides, and code examples below will help you master these powerful models for graph-structured data!
        """
    )
    session.add(post2)
    session.commit()
    session.refresh(post2)

    # Add tags to post2
    session.add(PostTag(post_id=post2.id, tag_id=tags["dl"].id))
    session.add(PostTag(post_id=post2.id, tag_id=tags["gnn"].id))
    session.add(PostTag(post_id=post2.id, tag_id=tags["message_passing"].id))

    # Add media assets to post2 (using kadane example notes)
    assets2 = [
        MediaAsset(
            post_id=post2.id,
            type=MediaType.IMAGE,
            url="/static/content/kadane/example_0.jpg",
            title="Kadane's Algorithm - Page 1",
            order=1
        ),
        MediaAsset(
            post_id=post2.id,
            type=MediaType.IMAGE,
            url="/static/content/kadane/example_1.jpg",
            title="Kadane's Algorithm - Page 2",
            order=2
        ),
        MediaAsset(
            post_id=post2.id,
            type=MediaType.IMAGE,
            url="/static/content/kadane/example_2.jpg",
            title="Kadane's Algorithm - Page 3",
            order=3
        ),
        MediaAsset(
            post_id=post2.id,
            type=MediaType.SLIDE,
            url="https://docs.google.com/presentation/d/e/2PACX-1vSvQDVBesLdaM8BoM-hzFyfWgzphBYNd2RETlC5Di71PNZJ64LzywW5bb7djM91tc8l1D3jW1fOI95P/embed?start=false&loop=false&delayms=3000",
            title="Graph Deep Learning Slides",
            order=4
        ),
    ]
    session.add_all(assets2)

    # Post 3: Kadane's Algorithm (Text only + HTML visualization)
    post3 = Post(
        title="Kadane's Algorithm: Maximum Subarray Problem",
        slug="kadanes-algorithm",
        description="""
# Kadane's Algorithm: A Dynamic Programming Masterpiece

Kadane's Algorithm stands as one of the most elegant examples of dynamic programming in computer science. Despite its apparent simplicity, this algorithm demonstrates profound insights into optimization and showcases how clever thinking can reduce seemingly complex problems to remarkably efficient solutions. The maximum subarray problem it solves appears frequently in real-world applications, from analyzing stock market data to signal processing and bioinformatics.

## The Maximum Subarray Problem

Given an array of integers (which may include negative numbers, positive numbers, or both), find the contiguous subarray that has the largest sum. The subarray must be non-empty and maintain the original order of elements.

**Classic Example:**
```
Input: [-2, 1, -3, 4, -1, 2, 1, -5, 4]
Output: 6
Explanation: The subarray [4, -1, 2, 1] has the largest sum of 6
```

At first glance, you might consider checking every possible subarray—there are O(n²) such subarrays in an array of length n. For each subarray, computing its sum takes O(n) time in the worst case, leading to a brute-force O(n³) solution. We can optimize this to O(n²) using prefix sums, but Kadane's Algorithm achieves the optimal O(n) time complexity with O(1) space.

## The Elegant Solution

Kadane's Algorithm is based on a beautiful insight: at each position in the array, we face a simple decision—should we extend the current subarray by including this element, or should we start a completely new subarray from this element?

Here's the complete implementation:

```python
def kadane(arr):
    '''
    Find the maximum sum of any contiguous subarray.

    Args:
        arr: List of integers (can include negative numbers)

    Returns:
        Integer representing the maximum subarray sum
    '''
    if not arr:
        raise ValueError("Array must be non-empty")

    # max_ending_here: maximum sum of subarray ending at current position
    max_ending_here = arr[0]

    # max_so_far: maximum sum found so far (global maximum)
    max_so_far = arr[0]

    for i in range(1, len(arr)):
        # Key decision: extend current subarray or start new one?
        # If max_ending_here is negative, starting fresh is better
        max_ending_here = max(arr[i], max_ending_here + arr[i])

        # Update global maximum if we found a better sum
        max_so_far = max(max_so_far, max_ending_here)

    return max_so_far

# Example usage
arr = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
result = kadane(arr)
print(f"Maximum subarray sum: {result}")  # Output: 6
```

## Understanding the Algorithm Through Dynamic Programming

Kadane's Algorithm is fundamentally a dynamic programming solution, though its elegance makes this less obvious than traditional DP implementations.

**Define the Subproblem:**
Let `dp[i]` represent the maximum sum of any subarray that **ends at index i**.

**Recurrence Relation:**
```
dp[i] = max(arr[i], dp[i-1] + arr[i])
```

This says: the best subarray ending at position i is either:
1. Just the element arr[i] itself (starting a new subarray)
2. The best subarray ending at i-1, extended to include arr[i]

**Base Case:**
```
dp[0] = arr[0]
```

The answer to our problem is:
```
max(dp[0], dp[1], dp[2], ..., dp[n-1])
```

Kadane's Algorithm implements this DP solution with O(1) space by observing that we only need the previous `dp` value, not the entire array of `dp` values.

## Step-by-Step Execution

Let's trace through the algorithm with our example array:

```
Array: [-2, 1, -3, 4, -1, 2, 1, -5, 4]
Index:  0   1   2  3   4  5  6   7  8

i=0: max_ending_here = -2, max_so_far = -2
     Starting with first element

i=1: max_ending_here = max(1, -2+1) = max(1, -1) = 1
     max_so_far = max(-2, 1) = 1
     Better to start fresh at 1

i=2: max_ending_here = max(-3, 1+(-3)) = max(-3, -2) = -2
     max_so_far = max(1, -2) = 1
     Extend, but sum becomes negative

i=3: max_ending_here = max(4, -2+4) = max(4, 2) = 4
     max_so_far = max(1, 4) = 4
     Better to start fresh at 4

i=4: max_ending_here = max(-1, 4+(-1)) = max(-1, 3) = 3
     max_so_far = max(4, 3) = 4
     Extend: [4, -1]

i=5: max_ending_here = max(2, 3+2) = max(2, 5) = 5
     max_so_far = max(4, 5) = 5
     Extend: [4, -1, 2]

i=6: max_ending_here = max(1, 5+1) = max(1, 6) = 6
     max_so_far = max(5, 6) = 6
     Extend: [4, -1, 2, 1]

i=7: max_ending_here = max(-5, 6+(-5)) = max(-5, 1) = 1
     max_so_far = max(6, 1) = 6
     Extend but sum drops: [4, -1, 2, 1, -5]

i=8: max_ending_here = max(4, 1+4) = max(4, 5) = 5
     max_so_far = max(6, 5) = 6
     Extend: [4, -1, 2, 1, -5, 4]

Final answer: 6 (from subarray [4, -1, 2, 1])
```

## Finding the Actual Subarray

The basic algorithm returns only the maximum sum. If we also need the subarray indices:

```python
def kadane_with_indices(arr):
    '''
    Find maximum subarray sum and return sum, start index, and end index.

    Returns:
        Tuple of (max_sum, start_index, end_index)
    '''
    max_ending_here = arr[0]
    max_so_far = arr[0]

    start = 0  # Start of maximum subarray
    end = 0    # End of maximum subarray
    temp_start = 0  # Temporary start position

    for i in range(1, len(arr)):
        # If starting fresh, update temporary start
        if arr[i] > max_ending_here + arr[i]:
            max_ending_here = arr[i]
            temp_start = i
        else:
            max_ending_here = max_ending_here + arr[i]

        # Update global maximum
        if max_ending_here > max_so_far:
            max_so_far = max_ending_here
            start = temp_start
            end = i

    return max_so_far, start, end

# Example
arr = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
max_sum, start, end = kadane_with_indices(arr)
print(f"Maximum sum: {max_sum}")
print(f"Subarray: arr[{start}:{end+1}] = {arr[start:end+1]}")
# Output: Maximum sum: 6
#         Subarray: arr[3:7] = [4, -1, 2, 1]
```

## Complexity Analysis

**Time Complexity: O(n)**
- Single pass through the array
- Constant time operations per element
- Optimal for this problem (must examine every element)

**Space Complexity: O(1)**
- Only a constant number of variables
- No additional data structures
- Space-optimized dynamic programming

This makes Kadane's Algorithm extremely efficient, even for arrays with millions of elements.

## Important Edge Cases

**All Negative Numbers:**
```python
arr = [-5, -2, -8, -1, -4]
result = kadane(arr)  # Returns -1 (the largest single element)
```

**Single Element:**
```python
arr = [5]
result = kadane(arr)  # Returns 5
```

**All Positive Numbers:**
```python
arr = [1, 2, 3, 4, 5]
result = kadane(arr)  # Returns 15 (entire array)
```

**Mix with Zero:**
```python
arr = [-1, 0, -2, 3, 4, -1]
result = kadane(arr)  # Returns 7 ([3, 4])
```

## Variations and Related Problems

### Maximum Product Subarray

Instead of sum, find the maximum product. This requires tracking both maximum and minimum (since negative × negative = positive):

```python
def max_product_subarray(arr):
    if not arr:
        return 0

    max_so_far = arr[0]
    max_ending_here = arr[0]
    min_ending_here = arr[0]

    for i in range(1, len(arr)):
        temp_max = max(arr[i], max_ending_here * arr[i], min_ending_here * arr[i])
        min_ending_here = min(arr[i], max_ending_here * arr[i], min_ending_here * arr[i])
        max_ending_here = temp_max
        max_so_far = max(max_so_far, max_ending_here)

    return max_so_far
```

### Maximum Circular Subarray

Handle arrays that wrap around (circular):

```python
def max_circular_subarray(arr):
    # Case 1: Maximum subarray is in the middle (use Kadane's)
    max_kadane = kadane(arr)

    # Case 2: Maximum subarray wraps around
    # This equals: total_sum - minimum_subarray
    max_wrap = sum(arr) - kadane([-x for x in arr])

    # Handle all negative case
    if max_wrap == 0:
        return max_kadane

    return max(max_kadane, max_wrap)
```

### Maximum Sum with At Least K Elements

Find maximum sum subarray with at least k elements:

```python
def max_sum_at_least_k(arr, k):
    max_sum = sum(arr[:k])
    current_sum = max_sum
    min_prefix = 0
    prefix_sum = 0

    for i in range(k, len(arr)):
        current_sum += arr[i]
        prefix_sum += arr[i - k]
        min_prefix = min(min_prefix, prefix_sum)
        max_sum = max(max_sum, current_sum - min_prefix)

    return max_sum
```

## Real-World Applications

**Stock Trading**: Given daily price changes, find the best period to hold a stock for maximum profit.

**Signal Processing**: Identify segments in a signal with maximum energy or amplitude.

**Bioinformatics**: Find regions of DNA sequences with specific properties (GC content, hydrophobicity).

**Image Processing**: Detect regions of images with maximum cumulative brightness or contrast.

**Resource Allocation**: Determine optimal time windows for resource usage to maximize benefit.

## Practice Problems

1. **LeetCode 53 - Maximum Subarray** (Easy): Direct application
2. **LeetCode 152 - Maximum Product Subarray** (Medium): Product variation
3. **LeetCode 918 - Maximum Sum Circular Subarray** (Medium): Circular variation
4. **LeetCode 1186 - Maximum Subarray Sum with One Deletion** (Medium): With modification
5. **LeetCode 1191 - K-Concatenation Maximum Sum** (Medium): Array repetition

## Why This Algorithm Matters

Kadane's Algorithm beautifully demonstrates several key computer science principles:

1. **Dynamic Programming**: Optimal substructure and overlapping subproblems
2. **Greedy Choice**: Making locally optimal decisions (extend or start new)
3. **Space Optimization**: Reducing O(n) space to O(1)
4. **Problem Transformation**: Viewing the problem through the lens of "ending at position i"

It's a testament to the power of algorithmic thinking—transforming what seems like a quadratic problem into a linear solution through careful observation and clever design.

The handwritten notes and visualizations below provide step-by-step walkthroughs that will deepen your understanding of this fundamental algorithm!
        """
    )
    session.add(post3)
    session.commit()
    session.refresh(post3)

    # Add tags to post3
    session.add(PostTag(post_id=post3.id, tag_id=tags["algo"].id))
    session.add(PostTag(post_id=post3.id, tag_id=tags["dp"].id))

    # Add HTML visualization
    html_content = """
    <div style="font-family: monospace; padding: 20px; background: #f5f5f5; border-radius: 8px;">
        <h3 style="color: #333;">Interactive Kadane's Algorithm Visualization</h3>
        <div id="visualization" style="margin: 20px 0;">
            <p><strong>Array:</strong> [-2, 1, -3, 4, -1, 2, 1, -5, 4]</p>
            <div style="display: flex; gap: 10px; margin: 20px 0;">
                <div style="padding: 10px; background: #e3f2fd; border: 2px solid #2196f3; border-radius: 4px;">-2</div>
                <div style="padding: 10px; background: #fff; border: 1px solid #ccc; border-radius: 4px;">1</div>
                <div style="padding: 10px; background: #fff; border: 1px solid #ccc; border-radius: 4px;">-3</div>
                <div style="padding: 10px; background: #c8e6c9; border: 2px solid #4caf50; border-radius: 4px;">4</div>
                <div style="padding: 10px; background: #c8e6c9; border: 2px solid #4caf50; border-radius: 4px;">-1</div>
                <div style="padding: 10px; background: #c8e6c9; border: 2px solid #4caf50; border-radius: 4px;">2</div>
                <div style="padding: 10px; background: #c8e6c9; border: 2px solid #4caf50; border-radius: 4px;">1</div>
                <div style="padding: 10px; background: #fff; border: 1px solid #ccc; border-radius: 4px;">-5</div>
                <div style="padding: 10px; background: #fff; border: 1px solid #ccc; border-radius: 4px;">4</div>
            </div>
            <p style="color: #4caf50; font-weight: bold;">Maximum Subarray (green): [4, -1, 2, 1] = 6</p>
        </div>
    </div>
    """

    assets3 = [
        MediaAsset(
            post_id=post3.id,
            type=MediaType.IMAGE,
            url="/static/content/kadane/example_0.jpg",
            title="Kadane's Algorithm - Page 1",
            order=1
        ),
        MediaAsset(
            post_id=post3.id,
            type=MediaType.IMAGE,
            url="/static/content/kadane/example_1.jpg",
            title="Kadane's Algorithm - Page 2",
            order=2
        ),
        MediaAsset(
            post_id=post3.id,
            type=MediaType.IMAGE,
            url="/static/content/kadane/example_2.jpg",
            title="Kadane's Algorithm - Page 3",
            order=3
        ),
        MediaAsset(
            post_id=post3.id,
            type=MediaType.HTML,
            content=html_content,
            title="Kadane's Algorithm Visualization",
            order=4
        ),
    ]
    session.add_all(assets3)

    session.commit()
    print("✅ Successfully created 3 posts with various media types!")


def main():
    """Main seeding function."""
    print("🌱 Starting database seed...")

    # Create tables
    print("📋 Creating database tables...")
    create_db_and_tables()

    with Session(engine) as session:
        # Check if data already exists
        existing_posts = session.exec(select(Post)).first()
        if existing_posts:
            print("⚠️  Database already contains data. Skipping seed.")
            return

        # Create tags
        print("🏷️  Creating tags...")
        tags = create_tags(session)
        print(f"   Created {len(tags)} tags")

        # Create posts
        print("📝 Creating posts...")
        create_posts(session, tags)
        print("   Created 3 posts with media assets")

    print("✨ Database seeding completed!")


if __name__ == "__main__":
    main()
