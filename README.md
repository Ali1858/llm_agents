# LLM Agents Examples

This repository showcases various examples of Language Model (LLM) agents, demonstrating their capabilities in different domains. 

## What are LLM Agents?

LLM Agents are AI systems that use large language models to understand and generate human-like text, combined with the ability to reason about problems and take actions. These agents can break down complex tasks, make decisions, and execute actions based on their understanding of the input and the context.

## ReAct Framework

One of the key frameworks used in this repository is ReAct (Reason + Act). ReAct is an approach that enhances the problem-solving capabilities of language models by interleaving reasoning and acting. Here's a brief overview:

1. **Reason**: The agent analyzes the problem, considers possible approaches, and plans a course of action.
2. **Act**: Based on its reasoning, the agent takes an action, such as using a tool or generating a response.
3. **Observe**: The agent observes the results of its action.
4. **Repeat**: The process repeats, with the agent reasoning about the new state and deciding on the next action.

This cycle allows the agent to tackle complex, multi-step problems by breaking them down into manageable pieces and adapting its approach based on intermediate results.

## Examples in this Repository

1. [**SQL Agent**](nl2sql_agent.ipynb): Converts natural language queries to SQL and interacts with databases.
2. 

Each example demonstrates how LLM agents can be applied to specific domains, showcasing their flexibility and power in solving real-world problems.

## Getting Started
`pip install -r requirement`
Then follow the instruction given within the notebooks to run the agent.