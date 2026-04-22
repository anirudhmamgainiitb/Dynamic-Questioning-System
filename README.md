**Dynamic Questioning System**

A system that asks the right follow-up questions for insurance claims based on user input.

 **Overview**

This project simulates how an insurance agent gathers information step by step.

Instead of fixed questions or full LLM dependence, it uses a state-driven pipeline to decide what to ask next.

**Key Features**
Dynamic follow-up questions
State-based reasoning
No repetition (anti-loop logic)
Domain-aware question generation
Deterministic and interpretable system


**Core Modules**
Generator – creates question bank
Validator – cleans and deduplicates
Retriever – selects best question
State Updater – extracts structured info
Termination Policy – decides when to stop
