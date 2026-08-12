<div align="center">

<img width="100%" src="https://capsule-render.vercel.app/api?type=venom&height=260&color=0:00C9A7,45:5B5FEF,100:C850C0&text=LearnFlow%20AI&fontColor=ffffff&fontSize=72&fontAlignY=42&desc=Multi-Agent%20AI%20Tutor%20for%20Personalized%20Learning%20Flows&descAlignY=64&descSize=20&animation=fadeIn" alt="LearnFlow AI banner" />

A multi-stage AI learning system that plans curriculum, coordinates specialist agents, and delivers stateful instruction.



Multi-Agent Systems · LLM Orchestration · Stateful Agents · Curriculum Planning · Conversational AI · Prompt Engineering · Human-in-the-Loop · AI System Design

</div>

🎓 What is LearnFlow AI?

LearnFlow AI is a multi-agent AI learning platform that separates curriculum planning from instruction delivery instead of relying on a single general-purpose chatbot prompt.

A learner provides a topic, multiple role-specialized LLM agents collaborate to refine the learning objective and construct a syllabus, and a dedicated stateful instructor then teaches from that generated curriculum one stage at a time.

The system is organized as a multi-stage AI workflow:

Learner chooses a topic
        ↓
AI agents collaboratively design a syllabus
        ↓
A dedicated teaching agent is seeded with that syllabus
        ↓
The learner enters an interactive tutoring conversation
        ↓
The instructor teaches one stage at a time
        ↓
Learner feedback becomes conversation context
        ↓
The lesson continues in syllabus order

Instead of asking a general chatbot to "teach me machine learning," LearnFlow AI first creates a course structure and then constrains the instructor to follow that structure throughout the conversation.

⚡ 30-second engineering overview

AI systems layer

Implementation

Task planning

A dedicated task-specification agent converts a broad topic into a bounded, concrete teaching objective

Multi-agent orchestration

Instructor and Teaching Assistant agents collaborate through role-constrained message loops for up to 5 planning turns

Curriculum synthesis

A separate synthesis agent transforms multi-agent discussion history into a structured syllabus

Stateful execution

TeachingGPT maintains syllabus state, topic state, and accumulated learner/instructor conversation context

Behavioral constraints

Instructor prompts enforce curriculum order, depth requirements, one-stage-at-a-time delivery, and explicit turn boundaries

Human-in-the-loop control

<END_OF_TURN> hands control back to the learner before the system proceeds

Application layer

Gradio exposes independent curriculum-generation and conversational-instructor workflows

Model abstraction

LangChain chains/messages isolate model interaction from controller and UI logic

🏭 Production-minded AI system design

LearnFlow AI is structured around separation of responsibilities rather than one monolithic prompt. Each model call has a narrow role and a defined handoff to the next stage.

User Intent
   ↓
Task Specification
   ↓
Multi-Agent Planning Loop
   ↓
Curriculum Synthesis
   ↓
Stateful Instructor Controller
   ↓
Human Feedback / Conversation Context
   └──────────────→ next instructional turn

System boundaries

Boundary

Responsibility

Planner

Refines an underspecified learning request

Role-play agents

Explore and decompose curriculum content from complementary roles

Synthesizer

Converts free-form agent collaboration into the course artifact

Controller

Owns runtime syllabus/topic/history state

Instructor chain

Generates the next teaching step from controlled context

UI

Collects learner input and streams the instructional response

Prompt-level reliability controls already present

The repository uses explicit prompt contracts to reduce uncontrolled model behavior:

role invariants prevent the Instructor and Teaching Assistant from intentionally swapping responsibilities,

planning is bounded by a 5-turn collaboration limit,

the teaching agent is instructed not to reorder the generated syllabus,

each teaching response covers one stage at a time,

<END_OF_TURN> creates an explicit learner-intervention point,

prior conversation history is supplied on subsequent instructional turns.

These are prompt-level controls, not hard runtime guarantees; production validation and automated evaluation are listed later as the next reliability layer.

🧠 Core idea

A useful tutoring system needs more than a strong model response.

LearnFlow AI decomposes the learning workflow into distinct responsibilities:

flowchart LR
    U[Learning Topic] --> TS[Task Specifier]
    TS --> R[Instructor ↔ Teaching Assistant Role Play]
    R --> S[Syllabus Synthesizer]
    S --> C[Generated Curriculum]
    C --> T[TeachingGPT Controller]
    T --> I[Interactive AI Instructor]
    I --> H[Learner Response]
    H --> M[Conversation Memory]
    M --> I

This architecture creates a clean separation between:

planning what should be taught

structuring the learning path

delivering the lesson

maintaining dialogue context

✨ Learning flow

1. Choose a topic

The user begins with a topic such as:

Reinforcement Learning
Natural Language Processing
Neural Networks
Decision Trees
Computer Vision

The Gradio interface converts that into an initial task:

Generate a course syllabus to teach the topic: <USER_TOPIC>

2. Expand the learning objective

Before curriculum generation begins, LearnFlow AI uses a dedicated task-specification prompt.

The goal is to convert a broad request into a more concrete teaching objective in 50 words or fewer.

flowchart LR
    A["Reinforcement Learning"] --> B[Task Specifier Agent]
    B --> C[More Specific Learning Objective]

This additional planning step gives the downstream agents richer context than the raw topic alone.

3. Generate the syllabus through agent collaboration

The syllabus is not produced by a single prompt.

LearnFlow AI initializes two role-based agents:

👨‍🏫 Instructor

Responsible for:

proposing concrete explanations,

giving examples,

contributing domain expertise,

solving the instructional task.

🧑‍💻 Teaching Assistant

Responsible for:

decomposing the task,

issuing one instructional request at a time,

guiding the discussion toward a complete curriculum.

The two agents exchange messages for up to 5 collaboration turns.

sequenceDiagram
    participant TA as Teaching Assistant Agent
    participant IN as Instructor Agent
    participant SY as Syllabus Synthesizer

    TA->>IN: Instruction + optional input
    IN-->>TA: Specific teaching solution
    TA->>IN: Next instruction
    IN-->>TA: Expanded content
    TA->>IN: Continue curriculum design
    IN-->>TA: Additional instructional material
    Note over TA,IN: Up to 5 collaborative turns
    TA->>SY: Full discussion history
    IN->>SY: Full discussion history
    SY-->>SY: Synthesize course syllabus

The complete conversation is then passed to a third LLM role whose only responsibility is converting the discussion into a course-syllabus format.

🧑‍🏫 The TeachingGPT controller

Once a syllabus is generated, the application seeds a dedicated teaching controller.

teaching_agent.seed_agent(syllabus, task)

TeachingGPT maintains three pieces of state:

syllabus
conversation_topic
conversation_history

The instructor receives all three on every turn.

That creates a stateful teaching loop:

flowchart TD
    S[Generated Syllabus] --> TG[TeachingGPT]
    T[Topic / Teaching Task] --> TG
    H[Conversation History] --> TG

    TG --> P[Instructor Prompt]
    P --> LLM[LLM Response]
    LLM --> E["&lt;END_OF_TURN&gt;"]
    E --> U[User Responds]
    U --> H

🧭 Syllabus-constrained teaching

The instructor prompt contains several explicit behavioral rules.

The model is instructed to:

follow the syllabus in its original order,

avoid skipping or reordering topics,

explain concepts beyond syllabus headings,

include definitions,

include formulas when relevant,

provide examples,

respond using previous conversation history,

teach only one stage at a time,

allow the learner to respond before continuing.

This turns the syllabus into a lightweight instructional control layer rather than treating it as passive text.

🔄 Human-in-the-loop lesson progression

LearnFlow AI deliberately stops after every teaching stage.

The instructor appends:

<END_OF_TURN>

to signal that control should return to the learner.

The learner's next message is added to the shared conversation history:

Instructor explanation
        ↓
<END_OF_TURN>
        ↓
Learner question / response
        ↓
Conversation history updated
        ↓
Next instructor step

This creates a conversational teaching loop instead of generating an entire lesson in one uninterrupted response.

🏗️ Architecture

flowchart TD
    UI[Gradio Application]

    UI --> TOPIC[Topic Input]
    TOPIC --> SPEC[Task Specification Agent]

    SPEC --> ASYS[Instructor System Prompt]
    SPEC --> USYS[Teaching Assistant System Prompt]

    ASYS --> A1[Instructor DiscussAgent]
    USYS --> A2[Teaching Assistant DiscussAgent]

    A1 <--> A2

    A1 --> HIST[Agent Collaboration History]
    A2 --> HIST

    HIST --> SUM[Syllabus Summarizer Agent]
    SUM --> SYL[Generated Syllabus]

    SYL --> CTRL[TeachingGPT Controller]
    TOPIC --> CTRL

    CTRL --> CHAIN[InstructorConversationChain]
    CHAIN --> LLM[OpenAI Chat Model]
    LLM --> RESP[One Teaching Stage]
    RESP --> CHAT[Gradio Chatbot]

    CHAT --> HUMAN[Learner Message]
    HUMAN --> MEM[Conversation History]
    MEM --> CHAIN

🖼️ Original project flow

The repository already includes the original system diagram:

<div align="center">
  <img src="diagram.png" width="90%" alt="LearnFlow AI architecture diagram" />
</div>

It captures the same three-stage idea implemented in the source:

1. Define the learning goal → 2. Generate the syllabus → 3. Teach interactively

💬 Product experience

The Gradio application exposes two tabs.

📚 Input Your Information

The learner enters a topic and clicks:

Build the Bot!!!

The application:

creates a teaching task,

generates a syllabus,

seeds the teaching agent,

returns the syllabus to the user.

🤖 AI Instructor

The second tab provides a chatbot interface backed by the stateful teaching controller.

Responses are streamed character-by-character into the UI, creating a conversational typing effect.

The application also detects OpenAI quota errors and surfaces a clearer user-facing message instead of exposing the raw exception.

🔬 Multi-agent orchestration in the code

LearnFlow AI defines a reusable DiscussAgent abstraction.

Each agent contains:

System role
      +
LLM
      +
Stored message history

Its interaction model is simple:

messages = self.update_messages(input_message)
output_message = self.model(messages)
self.update_messages(output_message)

This abstraction is reused for:

task specification,

Instructor role-play,

Teaching Assistant role-play,

syllabus synthesis.

That keeps the curriculum-generation logic modular instead of hard-coding every LLM call into one function.

🧩 Prompt-engineering strategy

The project uses several prompt layers, each with a different responsibility.

Prompt layer

Responsibility

Task Specifier

Turn a broad learning topic into a concrete teaching objective

Instructor Role Prompt

Produce detailed instructional solutions

Teaching Assistant Role Prompt

Drive curriculum planning one instruction at a time

Syllabus Synthesizer

Convert collaboration history into a structured course syllabus

Teaching Agent Prompt

Follow the syllabus and conversation history during tutoring

This is closer to a small LLM workflow than a single prompt-response chatbot.

🔬 AI engineering depth

LearnFlow AI demonstrates several patterns that matter in larger AI applications:

Decomposition        → specialized agents instead of one overloaded prompt
Orchestration        → deterministic Python controls the sequence of LLM roles
State                → controller-owned syllabus/topic/history across turns
Context construction → generated curriculum + learner history shape inference
Guardrails           → explicit role, ordering, and turn-completion policies
Human oversight      → user receives control between instructional stages
Modularity           → planning, synthesis, teaching, and presentation remain separate

The important engineering idea is that model capability is wrapped in an application-level control flow. The LLM supplies reasoning and language generation; Python code owns agent sequencing, bounded collaboration, persistent in-process state, and UI handoffs.

📁 Repository structure

LearnFlow-AI/
├── README.md
├── diagram.png
├── requirements.txt
├── setup.py
├── pyproject.toml
├── Makefile
│
└── src/
    ├── run.py                  # Gradio application entry point
    ├── generating_syllabus.py # Multi-agent curriculum generation
    ├── teaching_agent.py      # Stateful TeachingGPT controller
    └── EduGPT.ipynb           # Original notebook prototype

🛠 Technology stack

Layer

Technology

Language

Python

LLM framework

LangChain

LLM provider

OpenAI Chat Models

Agent architecture

Role-based DiscussAgent + LLMChain

State/controller

Pydantic + LangChain Chain

Prompting

PromptTemplate, system/human message templates

Interface

Gradio Blocks

Conversation state

In-memory Python history

Development tooling

Black, pre-commit, setuptools

Current pinned dependencies include:

langchain==0.0.208
openai==0.27.8
pydantic==1.10.13
numpy==1.26.4
gradio==3.41.2

🚀 Run locally

1. Clone the repository

git clone https://github.com/Ankita2525/LearnFlow-AI.git
cd LearnFlow-AI

2. Create a virtual environment

The repository targets Python 3.10+.

python3.10 -m venv venv
source venv/bin/activate

3. Install dependencies

pip install -r requirements.txt

4. Configure OpenAI

Create a .env file in the repository root:

OPENAI_API_KEY=your_openai_api_key

Do not commit this file.

5. Start the application

python src/run.py

Gradio will print the local application URL in the terminal.

✅ Implemented system capabilities

topic-driven learning flow

LLM-based task specification

role-based multi-agent curriculum planning

Instructor ↔ Teaching Assistant collaboration

bounded multi-turn syllabus generation

dedicated syllabus summarization step

stateful TeachingGPT controller

syllabus-constrained instructional prompting

conversation-history-aware tutoring

one-stage-at-a-time teaching behavior

human-in-the-loop turn boundaries

Gradio syllabus builder

Gradio conversational instructor

streamed typing-style responses

OpenAI quota error handling

notebook prototype + modular Python implementation

🧭 Engineering roadmap

The repository already establishes the multi-agent curriculum-planning and stateful tutoring core. The next engineering phase is to harden that core with the evaluation, persistence, observability, and deployment layers expected from production AI systems.

Personalized learning

learner profiles and skill levels

knowledge-state tracking

diagnostic assessments

adaptive difficulty

prerequisite detection

mastery-based progression

spaced repetition

Retrieval and grounding

RAG over textbooks, lecture notes, papers, or course materials

citations and source attribution

vector database-backed course memory

syllabus-to-document alignment

retrieval evaluation and answer-grounding checks

Agent reliability & evaluation

structured outputs and schema validation for curriculum artifacts

golden evaluation datasets for syllabus quality and instructional behavior

prompt/model regression suites

LLM-as-judge plus deterministic rubric checks where appropriate

learning-objective coverage and ordering metrics

hallucination / unsupported-content checks for grounded course modes

failure-mode taxonomy across planning, synthesis, and teaching stages

trace-level inspection of agent handoffs and context propagation

model/version A/B evaluation before rollout

Platform architecture & operations

persistent PostgreSQL-backed learner/session state

multi-user authentication and authorization

asynchronous curriculum-generation jobs

provider-independent model gateway / routing layer

centralized secrets and environment configuration

versioned API layer for web/mobile clients

request tracing across agent stages

token, latency, error-rate, and cost telemetry

retries, timeouts, graceful degradation, and failure recovery

deployment health checks and production observability

Product experience

course progress dashboard

quizzes and automatic feedback

flashcard generation

project-based assignments

downloadable learning plans

lesson completion tracking

instructor personas

code execution for programming courses

🌱 Why LearnFlow AI?

A generic chatbot can answer a question.

A learning system has to manage a journey.

LearnFlow AI explores that distinction by separating:

What should I learn?
        ↓
How should it be organized?
        ↓
How should it be explained?
        ↓
Did the learner understand?
        ↓
What should come next?

LearnFlow AI implements the planning, organization, and guided-instruction layers through a coordinated multi-agent workflow with explicit state and human turn-taking.

Don't just answer the learner. Build the learning flow.

<div align="center">

LearnFlow AI

Multi-Agent Learning · LLM Orchestration · Conversational AI · Curriculum Generation

</div>

<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&height=110&color=0:C850C0,50:5B5FEF,100:00C9A7&section=footer" alt="footer" />
