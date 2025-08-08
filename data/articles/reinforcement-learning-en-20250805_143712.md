# A Practitioner's Guide to Reinforcement Learning: From Q-Tables to Policy Gradients and Real-World Impact

## Introduction: The Third Paradigm of Machine Learning

In the landscape of artificial intelligence, machine learning is often discussed in terms of two major approaches: supervised and unsupervised learning. However, a third, powerful paradigm has emerged as a critical driver of modern AI breakthroughs: Reinforcement Learning (RL). Unlike its counterparts, RL is not about learning from a static dataset of labeled examples or finding hidden structures in unlabeled data. Instead, it is about learning to make optimal decisions through direct interaction with a dynamic environment. This section introduces the fundamental principles of RL, explaining how it differs from other machine learning methods and why it has become indispensable for solving some of the most complex challenges in AI today.

### Why RL is Different from Supervised and Unsupervised Learning

Supervised learning excels at tasks with clear, labeled data—for instance, identifying cats in images by training on a dataset where each image is marked as "cat" or "not cat." Unsupervised learning, on the other hand, finds inherent patterns in data without any labels, such as grouping customers into different market segments.

Reinforcement Learning operates on a different principle entirely. It doesn't rely on a dataset of correct answers. Instead, an RL agent learns by receiving evaluative feedback in the form of rewards or penalties. The goal is not to predict a single correct label for a given input but to develop a long-term strategy, or *policy*, that maximizes the total cumulative reward over a sequence of actions (Sutton & Barto, 2018). This makes it uniquely suited for sequential decision-making problems where the impact of an action may not be immediately clear.

### Learning from Interaction: The Trial-and-Error Approach

At its core, RL is learning from experience. The process involves an agent (the learner or decision-maker) interacting with an environment (everything outside the agent). This interaction unfolds in a sequence of steps:
1.  The agent observes the current state of the environment.
2.  Based on its policy, it takes an action.
3.  The environment transitions to a new state and provides the agent with a reward (or penalty).

The agent repeats this process, continuously updating its policy based on the feedback it receives. This trial-and-error approach is analogous to how humans learn complex skills. A child learns to walk not by being told the precise muscle movements for each step, but by trying, falling (receiving negative feedback), and gradually discovering the sequence of actions that leads to successful walking (positive feedback). This paradigm shifts the focus from explicitly programming rules to designing an effective environment and reward system, allowing the agent to discover its own optimal behavior.

### The Growing Importance in Modern AI

The ability to learn optimal strategies without explicit supervision has made RL a critical tool for solving complex, dynamic problems where the best solution is not known in advance. Its successes are well-documented, from mastering strategic games like Go (AlphaGo) to controlling sophisticated robotic arms in manufacturing.

More recently, RL has become a cornerstone of training state-of-the-art Large Language Models (LLMs). Techniques like Reinforcement Learning from Human Feedback (RLHF) are used to fine-tune models like ChatGPT, aligning their responses with human preferences for helpfulness and safety. As AI systems are tasked with increasingly autonomous and complex responsibilities in fields like finance, healthcare, and logistics, the principles of RL will only grow in importance. This guide will walk you through the journey of RL, from its foundational concepts to the advanced methods driving real-world impact.

## The Core Framework of Reinforcement Learning

At its heart, Reinforcement Learning (RL) models a goal-oriented learning process through a formal framework. This framework is built on a continuous interaction between a learner and its surroundings, governed by a clear set of rules and objectives. Understanding these core components is the first step toward mastering RL.

### The Agent and the Environment: A Constant Dialogue

The two central figures in any RL problem are the **agent** and the **environment**.

*   The **agent** is the learner or decision-maker. It could be a software program learning to play a game, a robot learning to navigate a room, or an algorithm learning to optimize a trading strategy.
*   The **environment** is the world—real or virtual—with which the agent interacts. It encompasses everything outside the agent.

The relationship between the agent and the environment is a continuous feedback loop. The agent observes the environment, takes an action, and the environment responds by transitioning to a new state and providing a reward. This cycle repeats, allowing the agent to learn from the consequences of its actions over time (Sutton & Barto, 2018).

### States, Actions, and Rewards: The Building Blocks

The dialogue between the agent and the environment is composed of three fundamental elements: states, actions, and rewards.

*   **State (s):** A state is a snapshot of the environment at a particular moment. It provides the agent with all the necessary information to make a decision. For a chess-playing agent, the state would be the current positions of all pieces on the board.
*   **Action (a):** An action is a move the agent can make from a given state. The set of all possible actions in a state is called the action space. For the chess agent, an action would be moving a specific piece to a valid new square.
*   **Reward (R):** After the agent takes an action, the environment provides a numerical reward. This reward is a feedback signal that tells the agent how good or bad its last action was. A positive reward (e.g., +1 for winning a game) encourages the behavior, while a negative reward or penalty (e.g., -1 for losing) discourages it. The agent's ultimate goal is not to maximize the immediate reward, but the cumulative reward over the long run.

### Policies: The Agent's Strategy or Brain

The agent's behavior is governed by its **policy**, often denoted by the Greek letter pi (π). A policy is the agent's strategy or "brain"—it maps a given state to the action the agent should take. The central goal of any RL algorithm is to find an optimal policy that maximizes the total expected reward over time.

There are two main approaches to finding this optimal policy:

1.  **Value-Based Methods:** These methods, like the famous **Q-Learning**, focus on learning a *value function*. This function estimates the expected long-term return (the "value") of being in a particular state or taking a specific action in a state. The policy is then implicitly derived by simply choosing the action with the highest value in any given state (Sutton & Barto, 2018).
2.  **Policy-Based Methods:** These methods, such as **Policy Gradients**, learn the policy directly without needing a value function as an intermediary. The algorithm directly adjusts the policy's parameters to find the one that produces the greatest cumulative reward. This approach is especially powerful in environments with a vast or continuous range of possible actions.

### The Fundamental Trade-off: Exploration vs. Exploitation

As an agent learns, it faces a classic dilemma: should it **exploit** its current knowledge to get a guaranteed reward, or should it **explore** new, untried actions in the hope of discovering an even better reward? This is known as the exploration-exploitation trade-off.

*   **Exploitation** involves using the best strategy found so far. It's like ordering your favorite dish at a restaurant every time because you know it's good.
*   **Exploration** involves trying random or novel actions to gather more information about the environment. It's like trying a new dish on the menu—it might be terrible, or it might become your new favorite.

An agent that only exploits may get stuck in a suboptimal strategy, never realizing a better one exists. An agent that only explores will perform poorly because it constantly takes random actions. A key challenge in RL is to find a sophisticated balance between the two, ensuring the agent explores enough to find an optimal policy but exploits it effectively once found (Sutton & Barto, 2018).

## Foundational Algorithms: Learning Value with Q-Learning

Q-learning is a cornerstone of reinforcement learning. It's a model-free, value-based algorithm that enables an agent to learn the best course of action in an environment by trial and error. The "Q" in Q-learning stands for "Quality," representing the quality of taking a specific action from a specific state. At its core, Q-learning is about learning a function, `Q(s, a)`, that can tell the agent the expected future rewards for performing action `a` in state `s`.

### Introducing the Q-Table: A 'Cheat Sheet' for Optimal Actions

The primary goal of the Q-learning algorithm is to construct a simple lookup table, known as a **Q-table**. Think of this table as the agent's ultimate "cheat sheet." The rows of the table represent all possible states (`s`) in the environment, and the columns represent all possible actions (`a`) the agent can take. The value stored at the intersection `Q(s, a)` is the agent's best estimate of the total future reward it can expect if it takes action `a` from state `s` and continues playing optimally thereafter.

To build this table, the agent interacts with its environment, which is defined by a few key components:
*   **States (s)**: The distinct situations or locations the agent can be in.
*   **Actions (a)**: The set of possible moves the agent can make.
*   **Rewards (R)**: The feedback from the environment after an action. Positive rewards encourage behavior, while negative rewards (or costs) discourage it.

Initially, the Q-table is filled with zeros, signifying the agent's complete ignorance. Through exploration, the agent gradually updates these values, filling the cheat sheet with the wisdom gained from experience.

### The Bellman Equation: Propagating Value Through States

The magic of Q-learning lies in how it updates the Q-table. It uses a rule derived from the **Bellman equation**, which connects the value of the current state to the value of the next state. Each time the agent takes an action, it observes the outcome and updates the corresponding Q-value using the following formula (Sutton & Barto, 2018):

`Q(s, a) ← Q(s, a) + α * [R + γ * max(Q(s', a')) - Q(s, a)]`

Let's break this down:
*   `Q(s, a)`: The current Q-value for the state-action pair.
*   **`α` (alpha)**: The **learning rate** (a value between 0 and 1). This determines how much the new information overrides the old. A low `α` means the agent learns slowly, while a high `α` means it learns quickly.
*   **`R`**: The immediate **reward** received after taking action `a` in state `s`.
*   **`γ` (gamma)**: The **discount factor** (a value between 0 and 1). This determines the importance of future rewards. A `γ` of 0 makes the agent "short-sighted" by only considering immediate rewards, while a `γ` close to 1 makes it strive for long-term gains.
*   **`max(Q(s', a'))`**: The maximum Q-value for the next state `s'`. This is the crucial part: the update rule incorporates the best possible value achievable from the *next* state. This allows the value of good outcomes (like reaching a goal) to be propagated backward to earlier states and actions over time.

### The Q-Learning Algorithm: A Step-by-Step Walkthrough

The learning process is an iterative loop that continues until the Q-table values stabilize or "converge."

1.  **Initialize**: Create the Q-table and initialize all `Q(s, a)` values to 0.
2.  **Choose an Action**: From the current state `s`, select an action `a`. To balance finding new paths with using known good ones, we use an **epsilon-greedy** strategy. With probability *epsilon* (`ε`), we choose a random action (exploration). Otherwise, with probability 1-*epsilon*, we choose the action with the highest Q-value for that state (exploitation).
3.  **Perform Action & Observe**: Perform action `a` and observe the outcome: the new state `s'` and the reward `R`.
4.  **Update Q-Table**: Update the value `Q(s, a)` using the Bellman equation described above.
5.  **Repeat**: Set the new state `s'` as the current state and repeat the process until a terminal state is reached, completing one "episode." This entire cycle is repeated for many episodes to allow the agent to explore the environment thoroughly.

### Practical Implementation: A Grid-World Example

Let's imagine a simple 2x3 grid world.
*   **Agent**: Starts at S1.
*   **States**: 6 squares (S1-S6).
*   **Goal**: S6 (treasure) with a reward of **+100**.
*   **Hazard**: S3 (fire pit) with a reward of **-100**.
*   **Actions**: Up, Down, Left, Right.
*   **Step Cost**: Every move has a small negative reward of **-1** to encourage efficiency.

**Initial Q-Table (all values are 0):**
| State | Up | Down | Left | Right |
| :--- | :-: | :--: | :--: | :---: |
| S1 | 0 | 0 | 0 | 0 |
| S2 | 0 | 0 | 0 | 0 |
| ... | ... | ... | ... | ... |

**Learning in Action:**

1.  **First Steps**: The agent starts at S1. Since all Q-values are 0, it explores by randomly moving **Right** to S2. It receives a reward of -1. The `Q(S1, Right)` value is updated using the formula, becoming a small negative number.
2.  **Finding the Goal**: After several random moves, the agent is at S5 and happens to move **Right**. It lands on S6, the goal, and receives a massive reward of **+100**. The update for `Q(S5, Right)` is now significant: the `R` term is +100, making `Q(S5, Right)` a large positive value.
3.  **Propagating the Value**: In a new episode, the agent finds itself at S4. It might explore and move **Right** to S5. When it updates `Q(S4, Right)`, the `max(Q(S5, a'))` term is now the large positive value from `Q(S5, Right)`. As a result, the high value of the goal state gets "passed back" to S4.

Over thousands of episodes, this value propagation continues. The Q-values along the optimal path (S1 -> S2 -> S5 -> S6) will become much higher than other paths, effectively creating a map that guides the agent from any square to the treasure while avoiding the fire pit.

## Advanced Algorithms: Optimizing Behavior with Policy Gradients

While Q-learning provides a powerful framework for understanding value, its approach of learning the value of every state-action pair can be inefficient or even intractable in complex scenarios. Policy gradient methods offer a more direct route to optimal behavior by learning the policy itself, shifting the focus from "what is this action worth?" to "what is the best action to take?"

### Shifting Focus: From Learning Values to Learning Policies Directly

Policy gradient methods are a class of algorithms that directly learn and optimize a policy, which is essentially a mapping from a given state to a probability distribution over possible actions [1, 5]. Instead of first trying to determine the value of being in a state or taking an action, these methods adjust the policy's parameters to directly maximize the expected reward.

This stands in contrast to value-based methods like Q-learning. The primary goal of Q-learning is to learn an action-value function (the Q-function) that estimates the expected return for taking an action in a given state [4]. The policy is then derived *indirectly* from this value function, typically by always selecting the action with the highest estimated Q-value in any given state [1]. In essence, policy gradients search for the best policy, while value-based methods search for the best value function and then use it to define a policy.

### Policy Gradients vs. Q-Learning: A Head-to-Head Comparison

The fundamental difference in approach leads to several key distinctions between policy gradient and value-based methods:

*   **Primary Learning Target:**
    *   **Policy Gradients:** Directly learn and optimize the parameters of the policy function. The output *is* the policy [1, 3].
    *   **Q-Learning:** Learns a value function (e.g., Q-values) that estimates the value of state-action pairs. The policy is an implicit byproduct of these learned values [1, 4].

*   **Handling Action Spaces:**
    *   **Policy Gradients:** Excel in high-dimensional or continuous action spaces [3].
    *   **Q-Learning:** Struggle with continuous spaces, as finding the action that maximizes the Q-value becomes a difficult optimization problem in itself.

*   **Policy Type:**
    *   **Policy Gradients:** Naturally learn *stochastic* (probabilistic) policies.
    *   **Q-Learning:** Typically result in *deterministic* policies, where for any given state, the agent will always choose the single action with the highest learned value.

### Mastering Continuous Action Spaces

One of the most significant advantages of policy gradient methods is their natural ability to handle continuous action spaces. Imagine an agent controlling a robotic arm or setting the throttle of a vehicle. The number of possible actions (e.g., the precise angle of a joint or the exact percentage of throttle) is infinite.

Traditional Q-learning would require finding the action that maximizes the Q-value across this infinite range, which is computationally challenging. Policy gradient methods elegantly sidestep this problem. They can output a probability distribution (for example, a Gaussian distribution defined by a mean and standard deviation) over the entire continuous range of actions [3]. The agent then samples an action from this distribution, making the process both direct and computationally feasible.

### Stochastic Policies: Embracing Randomness for Optimal Results

Policy gradient methods learn stochastic policies, where the output for a given state is a probability for each possible action. This means that even in the same state, the agent might choose to take different actions based on these probabilities. This inherent randomness can be a powerful advantage.

In some environments, an element of unpredictability is optimal (think of a game of rock-paper-scissors). Furthermore, stochasticity encourages exploration, preventing the agent from getting stuck on a suboptimal strategy that it initially believed to be the best. In contrast, the deterministic policies derived from Q-learning can be brittle; if the single "best" action is found to be flawed, the policy has no alternative. By learning a distribution over actions, policy gradient methods build more robust and exploratory agents capable of discovering more nuanced strategies.

## Reinforcement Learning in Action: Real-World Applications

Reinforcement Learning is rapidly moving from theoretical research to tangible, real-world applications, where it is solving complex decision-making and optimization problems across a multitude of industries. By training systems to make sequential decisions through trial and error, RL has evolved into a critical tool for tackling dynamic challenges that were previously intractable. From robotics and healthcare to finance and large-scale language models, RL is helping organizations improve efficiency, reduce costs, and unlock new capabilities (Sutton & Barto, 2018).

### Robotics and Industrial Automation
In robotics, RL enables machines to learn complex manipulation and navigation tasks with a high degree of adaptability. Instead of being explicitly programmed for every possible contingency, a robot can learn to grasp irregularly shaped objects, assemble components, or navigate cluttered warehouses through experience. The RL agent receives rewards for successfully completing sub-tasks (e.g., a successful grasp) and penalties for failures (e.g., dropping an item), allowing it to develop a robust policy that can generalize to new situations far more effectively than traditional control algorithms.

### Strategic Decision-Making in Finance and Trading
The financial sector uses RL for strategic optimization in high-stakes, dynamic environments. Key applications include:
*   **Algorithmic Trading:** RL agents can be trained to execute trades by learning strategies that maximize returns while managing risk. They can analyze vast amounts of market data to identify patterns and adapt their actions to market volatility in real-time.
*   **Portfolio Management:** RL can optimize the allocation of assets in a portfolio over the long term, rebalancing dynamically based on market trends and risk tolerance to achieve specific financial goals.

### Dynamic Treatment Regimes in Healthcare
Healthcare is a field where RL is making significant strides in personalizing patient care. In what are known as Dynamic Treatment Regimes (DTRs), RL models can help determine the optimal sequence of treatments for patients with chronic diseases like cancer or HIV. The model treats the patient's current health status as the "state" and the available medical interventions as "actions." By optimizing for long-term health outcomes (the "reward"), RL can suggest a personalized treatment plan that adapts over time to the patient's response, leading to more effective and individualized care.

### Optimizing Large Language Models: RLHF and DPO
Perhaps the most visible recent application of RL is in the fine-tuning of Large Language Models (LLMs). After initial training, models like ChatGPT and Claude are further refined using techniques based on RL.
*   **Reinforcement Learning from Human Feedback (RLHF):** In this process, humans rank different model-generated responses to a prompt. This preference data is used to train a "reward model" that learns to score outputs based on helpfulness and safety. The LLM is then fine-tuned using an RL algorithm (like PPO) to maximize the scores from this reward model, effectively aligning its behavior with human preferences.
*   **Direct Preference Optimization (DPO):** A more recent and computationally efficient alternative to RLHF, DPO achieves similar alignment goals by using the preference data to directly optimize the language model's policy, bypassing the need to train a separate reward model.

### Autonomous Vehicles and Resource Management
RL is a core component in the development of autonomous vehicles. It is used to train the decision-making modules—often called the "driving policy"—that control steering, acceleration, and braking. The RL agent's state is comprised of rich sensor data (from cameras, LiDAR, etc.), and its actions are rewarded based on factors like reaching the destination safely, maintaining a smooth ride, and obeying traffic laws. Beyond a single vehicle, RL is also applied to broader resource management problems, such as optimizing traffic flow in smart cities, managing fleets of delivery drones, or controlling energy consumption in a network of electric vehicles.

## Key Challenges and the Future Horizon of RL

Despite its immense potential, Reinforcement Learning (RL) faces significant practical challenges that can hinder its widespread adoption. A fundamental tension in RL is the "Exploration vs. Exploitation" dilemma, where an agent must constantly balance acting on known good strategies with exploring new ones to discover potentially better outcomes (University of Alberta, n.d.). Overcoming this and other technical barriers is the primary focus of current research, paving the way for a future where RL is even more powerful and accessible.

### The Data Hunger: Overcoming Sample Inefficiency
One of the most significant barriers in RL is its sample inefficiency. Many algorithms require vast amounts of training data—millions or even billions of interactions with an environment—to learn an effective policy. This "data hunger" makes training expensive, time-consuming, and impractical for many real-world scenarios where data collection is costly or slow. This challenge is directly tied to the exploration problem; an agent must interact extensively with its environment to gather enough diverse data to generalize effectively.

### The Art and Science of Reward Function Design
The success of an RL agent is critically dependent on its reward function. Designing a function that accurately captures the desired outcome without creating unintended loopholes or perverse incentives is a complex task that is often more art than science. A poorly specified reward can lead an agent to learn behaviors that are technically optimal for the given reward but fail to achieve the actual, real-world goal. For example, an agent rewarded for speed might learn to cut corners in a way that is unsafe or undesirable. This difficulty in crafting perfect reward signals remains a major hurdle in applying RL to complex, nuanced problems (IABAC, 2023).

### Emerging Solutions: Offline RL and Policy Gradient Methods
To combat data inefficiency, researchers are developing innovative techniques. **Offline RL** is a promising approach where an agent learns from a fixed, pre-existing dataset of interactions without needing to explore the environment further. This is particularly valuable in fields like healthcare or autonomous driving, where live exploration can be risky or expensive. Another key development has been the rise of **policy gradient methods**. Unlike traditional value-based methods like Q-learning which struggle with continuous action spaces (e.g., steering a car), policy gradient methods can directly learn a policy that outputs a continuous range of actions, significantly expanding the applicability of RL (Neptune.ai, 2023).

### The Next Frontier: Multi-Agent Systems and Safety
The future of RL is moving towards solving even more complex and collaborative problems. This includes **Multi-Agent Reinforcement Learning (MARL)**, which studies how multiple agents can learn to cooperate or compete in a shared environment, with applications ranging from robotic warehouse optimization to traffic flow control. As RL systems become more autonomous, ensuring their **safety and ethical alignment** is paramount. A major breakthrough in this area is the application of RL to improve Large Language Models (LLMs) through techniques like **Reinforcement Learning from Human Feedback (RLHF)** and **Direct Preference Optimization (DPO)**, which help align model outputs with human values and preferences. These advancements are pushing RL into a new era of real-world impact across autonomous vehicles, robotics, personalized healthcare, and finance.

## Conclusion: Integrating RL into Your Toolkit

Reinforcement Learning represents a fundamental shift from programming explicit instructions to designing systems that learn optimal behavior through interaction. Moving from the foundational logic of Q-tables to the sophisticated calculus of Policy Gradients, we've seen how RL provides a powerful framework for solving complex, sequential decision-making problems. As a practitioner, understanding how to integrate this tool into your own work is the final, crucial step.

### Recap: Key Differences and When to Use Which Approach

Throughout this guide, we've explored different families of RL algorithms. The choice of which to use depends heavily on your problem's nature:

*   **Value-Based Methods (e.g., Q-Learning):** These methods are ideal for problems with discrete, manageable action spaces. Their goal is to learn the value of being in a particular state or taking a specific action. If you can reasonably represent your problem in a table-like structure (even a very large one), a value-based approach is a great starting point.
*   **Policy-Based Methods (e.g., Policy Gradients):** When faced with continuous or high-dimensional action spaces—like controlling a robotic arm's torque or setting a financial trading price—policy-based methods are superior. They directly learn the optimal policy without needing to compute the value of every state-action pair, making them more scalable and effective in complex environments.
*   **Hybrid Methods (e.g., Actor-Critic):** These approaches combine the strengths of both, using a "critic" to learn value functions and an "actor" to update the policy. They often provide the state-of-the-art performance and stability needed for challenging real-world tasks.

### Identifying Problems Suitable for Reinforcement Learning

How do you spot a problem where RL might be the answer? Look for scenarios with these characteristics:

1.  **Sequential Decisions:** The problem involves a series of actions over time where each action influences future outcomes.
2.  **A Clear Goal, but No Obvious Path:** You can define what success looks like (a reward signal), but you cannot easily write down the explicit rules or heuristics to achieve it. The system must learn the strategy through trial and error.
3.  **An Interactive Environment:** There is an environment (real or simulated) with which an agent can interact, take actions, and receive feedback (observations and rewards).

This paradigm is incredibly versatile, making it applicable to optimizing robotic control systems, developing autonomous trading strategies in finance, personalizing patient treatment plans in healthcare, and managing dynamic energy grids.

### Final Thoughts for the AI/ML Practitioner

Integrating Reinforcement Learning into your toolkit requires embracing a new mindset. The central challenge is no longer just feature engineering or model selection, but also managing the fundamental "Exploration vs. Exploitation" dilemma and designing effective reward functions—a task that is often more art than science.

Be aware of the practical hurdles. RL can be notoriously sample-inefficient, often requiring millions of interactions to train. However, the field is rapidly evolving to address these limitations. The future of RL lies in its integration with other AI disciplines, with techniques like Offline RL improving data efficiency and multi-agent systems tackling even more complex problems.

We are already seeing this integration bear fruit in spectacular ways. The development of modern Large Language Models relies heavily on techniques like Reinforcement Learning from Human Feedback (RLHF) and Direct Preference Optimization (DPO) to align model outputs with human values. This proves that RL is not a niche academic pursuit but a critical component of state-of-the-art AI. As you move forward, view RL as a powerful, if challenging, tool capable of solving a class of problems that were previously intractable.

## Sources

- Sutton, R. S., & Barto, A. G. (2018). Reinforcement Learning: An Introduction. MIT Press.
- Coursera Course: Fundamentals of Reinforcement Learning (University of Alberta)
- Research papers and articles explaining the mechanics of Q-Learning and the Bellman Equation.
- Technical blogs and articles comparing value-based (Q-Learning) and policy-based (Policy Gradient) methods.
- Industry reports and articles on the application of RL in finance, healthcare, and robotics (e.g., from sources like Neptune.ai, IABAC).
- Documentation and articles on modern RL applications like Reinforcement Learning from Human Feedback (RLHF) and Direct Preference Optimization (DPO) for LLMs.
