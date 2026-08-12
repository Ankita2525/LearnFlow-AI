<div align="center">

<img width="100%" src="https://capsule-render.vercel.app/api?type=venom&height=250&color=0:00C9A7,42:5B5FEF,100:C850C0&text=LearnFlow%20AI&fontColor=ffffff&fontSize=72&fontAlignY=41&desc=Multi-Agent%20Learning%20Orchestration%20System&descAlignY=63&descSize=21&animation=fadeIn" alt="LearnFlow AI banner" />

AI agents that plan a curriculum together — then a stateful instructor teaches it one stage at a time.



Multi-Agent Systems · LLM Orchestration · Stateful AI · Curriculum Planning · Conversational AI · Prompt Engineering · Human-in-the-Loop

</div>

🎓 Overview

LearnFlow AI is a multi-stage AI learning system that separates curriculum planning from instruction delivery.

A learner provides a topic. A task-specification stage sharpens the learning objective, two role-constrained agents collaborate to design the course, a synthesis stage converts that discussion into a syllabus, and a dedicated TeachingGPT controller uses the syllabus plus conversation history to drive an interactive instructor.

Learning Topic
     ↓
Task Specification
     ↓
Instructor ↔ Teaching Assistant Planning Loop
     ↓
Syllabus Synthesis
     ↓
Stateful TeachingGPT Controller
     ↓
Interactive Instructor
     ↓
Learner Feedback → Conversation Context → Next Stage

The central engineering idea is simple:

Planning what to teach and executing how to teach it are separate AI responsibilities.

⚡ 30-second engineering snapshot

AI systems layer

Implementation

Task refinement

Dedicated LLM stage turns a broad topic into a concrete teaching objective of at most 50 words

Multi-agent planning

Instructor and Teaching Assistant agents exchange role-constrained messages for up to 5 planning turns

Curriculum synthesis

A separate summarization agent converts the complete planning dialogue into a course syllabus

Stateful instruction

TeachingGPT owns the generated syllabus, current teaching task, and accumulated conversation history

Instruction control

Prompt contract enforces syllabus order, one-stage-at-a-time delivery, explanations, examples, and formulas where relevant

Human-in-the-loop

<END_OF_TURN> explicitly returns control to the learner before the next teaching stage

Application layer

Gradio exposes a syllabus builder and a conversational AI Instructor interface

Model orchestration

LangChain ChatOpenAI, message templates, LLMChain, and a custom Chain controller separate model calls from UI logic

🧠 AI workflow

LearnFlow AI is implemented as a sequence of specialized model interactions rather than one monolithic chatbot prompt.

flowchart LR
    U[User Topic] --> TS[Task Specifier]
    TS --> TA[Teaching Assistant Agent]
    TA <--> IN[Instructor Agent]
    TA --> H[Planning History]
    IN --> H
    H --> SY[Syllabus Synthesizer]
    SY --> C[Generated Curriculum]
    C --> TG[TeachingGPT Controller]
    U --> TG
    TG --> IA[Interactive Instructor]
    IA --> R[Learner Response]
    R --> M[Conversation History]
    M --> IA

Why this decomposition matters

The code assigns a clear responsibility to each stage:

Task Specifier — removes ambiguity from the initial learning request.

Teaching Assistant — decomposes the curriculum and issues one instruction at a time.

Instructor — generates concrete teaching content and examples in response to each instruction.

Syllabus Synthesizer — converts the planning exchange into the final course structure.

TeachingGPT — controls runtime instruction using syllabus state and learner conversation history.

This creates explicit agent boundaries, state handoffs, and prompt contracts that are easier to inspect than a single large prompt.

1️⃣ Task specification

The first LLM stage improves the raw user request before curriculum generation begins.

Example input:

Reinforcement Learning

The application converts it into a teaching task:

Generate a course syllabus to teach the topic: Reinforcement Learning

A dedicated task-specification agent then makes the request more concrete while keeping the result to 50 words or fewer.

flowchart LR
    A[Raw Topic] --> B[Task Specifier]
    B --> C[Bounded Learning Objective]
    C --> D[Planning Agents]

This stage gives the downstream planning loop a more precise objective than the topic name alone.

2️⃣ Multi-agent curriculum planning

The curriculum is generated through collaboration between two role-specific agents.

👨‍🏫 Instructor agent

Its system contract requires it to:

remain in the Instructor role,

respond to one instructional request at a time,

produce concrete solutions,

explain its solution,

include useful implementations/examples,

end each planning response with Next request.

🧑‍💻 Teaching Assistant agent

Its system contract requires it to:

remain in the Teaching Assistant role,

issue one instruction at a time,

attach optional input when needed,

continue decomposing the task until completion,

emit <TASK_DONE> only when the planning task is solved.

The planning loop is bounded by:

chat_turn_limit = 5

sequenceDiagram
    participant TA as Teaching Assistant
    participant IN as Instructor
    participant SY as Syllabus Synthesizer

    TA->>IN: Instruction + optional input
    IN-->>TA: Detailed teaching solution
    TA->>IN: Next curriculum request
    IN-->>TA: Expanded instructional content
    Note over TA,IN: Bounded to 5 planning turns
    TA->>SY: Planning history
    IN->>SY: Planning history
    SY-->>SY: Synthesize final syllabus

The bounded loop prevents curriculum planning from becoming an uncontrolled open-ended agent conversation.

3️⃣ Syllabus synthesis

Every Instructor / Teaching Assistant exchange is appended to conversation_history.

After the planning loop completes, LearnFlow AI creates a separate synthesis agent and asks it to convert that history into a course-syllabus format.

Agent collaboration history
          ↓
Dedicated synthesis prompt
          ↓
Generated course syllabus

The generated syllabus becomes a runtime artifact that is passed to the teaching controller rather than discarded after generation.

4️⃣ Stateful teaching controller

The teaching phase is managed by a custom LangChain controller:

class TeachingGPT(Chain, BaseModel):
    syllabus: str
    conversation_topic: str
    conversation_history: List[str]

When a syllabus is generated, the application initializes the runtime state:

teaching_agent.seed_agent(syllabus, task)

TeachingGPT therefore maintains three explicit pieces of instructional state:

Generated syllabus
      +
Teaching objective
      +
Learner / instructor conversation history

That state is supplied to the instructor chain on every instructional turn.

5️⃣ Syllabus-constrained instruction

The instructor is not asked to teach freely.

Its runtime prompt explicitly instructs the model to:

follow the syllabus in its original order,

avoid reordering topics,

explain definitions,

include formulas where relevant,

provide examples,

use previous conversation history,

generate only one teaching stage at a time,

return control to the learner before continuing.

flowchart TD
    S[Syllabus] --> P[Instructor Prompt]
    T[Teaching Objective] --> P
    H[Conversation History] --> P
    P --> LLM[OpenAI Chat Model]
    LLM --> O[One Teaching Stage]
    O --> END[END_OF_TURN]
    END --> USER[Learner Response]
    USER --> H

This makes the generated curriculum an active control input for the teaching loop instead of static text displayed once in the UI.

🔄 Human-in-the-loop execution

Every learner message is added to conversation_history before the instructor generates the next step.

The teaching prompt requires generated responses to terminate with:

<END_OF_TURN>

This creates a controlled interaction cycle:

Instructor explanation
      ↓
<END_OF_TURN>
      ↓
Learner response / question
      ↓
Conversation state updated
      ↓
Next syllabus-aligned stage

The model therefore receives the evolving learner interaction as context rather than treating every message as an isolated query.

🏗️ System architecture

flowchart TD
    UI[Gradio UI]

    UI --> TOPIC[Topic Input]
    TOPIC --> SPEC[Task Specification Agent]

    SPEC --> AP[Instructor Prompt Contract]
    SPEC --> UP[Teaching Assistant Prompt Contract]

    AP --> A1[Instructor DiscussAgent]
    UP --> A2[Teaching Assistant DiscussAgent]

    A1 <--> A2
    A1 --> HIST[Collaboration History]
    A2 --> HIST

    HIST --> SUM[Syllabus Synthesis Agent]
    SUM --> SYL[Generated Syllabus]

    SYL --> CTRL[TeachingGPT Controller]
    TOPIC --> CTRL

    CTRL --> CHAIN[InstructorConversationChain]
    CHAIN --> LLM[OpenAI Chat Model]
    LLM --> RESP[Single Teaching Stage]
    RESP --> CHAT[Gradio Chatbot]

    CHAT --> HUMAN[Learner Message]
    HUMAN --> MEM[Conversation History]
    MEM --> CHAIN

The repository also includes its original architecture visualization:

<div align="center">
  <img src="diagram.png" width="88%" alt="LearnFlow AI original architecture diagram" />
</div>

🧩 Prompt contracts as system boundaries

The implementation uses several prompt layers with different responsibilities rather than sharing one generic system prompt across the application.

Prompt layer

Responsibility

Task Specification

Transform a broad topic into a more specific instructional task

Instructor Inception Prompt

Define Instructor identity and response contract during planning

Teaching Assistant Inception Prompt

Define Teaching Assistant identity and task-decomposition contract

Syllabus Synthesis Prompt

Convert planning history into a curriculum artifact

Teaching Instructor Prompt

Execute the syllabus using runtime conversation state

These prompt contracts provide behavioral separation between planning, synthesis, and teaching.

They are prompt-level controls rather than hard runtime guarantees; production schema validation and automated evaluation would be the next reliability layer.

💬 Interactive application

The Gradio interface exposes two separate product flows.

📚 Syllabus Builder

The learner enters a topic and selects:

Build the Bot!!!

The application then:

Topic input
   ↓
Generate teaching task
   ↓
Run multi-agent curriculum planning
   ↓
Generate syllabus
   ↓
Seed TeachingGPT state
   ↓
Display syllabus

🤖 AI Instructor

The second tab provides a conversational teaching interface.

Each learner message is sent to TeachingGPT, which generates the next syllabus-aligned response. The Gradio UI streams the generated text character-by-character for a conversational experience.

The application also catches OpenAI quota errors and converts them into a clearer user-facing message.

🔬 Agent implementation

Curriculum-generation agents share a lightweight reusable abstraction:

class DiscussAgent:
    def __init__(self, system_message, model):
        self.system_message = system_message
        self.model = model
        self.init_messages()

Each DiscussAgent maintains its own stored message history:

System role
   +
Incoming message
   +
Generated response
   +
Next incoming message
   ...

This abstraction is used across task specification, curriculum role-play, and syllabus synthesis.

The teaching phase uses a separate custom Chain controller because it needs different runtime state and execution behavior.

⚙️ Engineering highlights

Separation of planning and execution

Curriculum generation and curriculum delivery are implemented as separate phases with an explicit syllabus handoff.

Bounded agent collaboration

The planning loop has a fixed maximum of 5 turns rather than allowing open-ended agent-to-agent generation.

Explicit conversational state

TeachingGPT owns the syllabus, learning objective, and accumulated conversation history.

Role-constrained agents

Instructor and Teaching Assistant prompts explicitly prohibit role switching and define message formats for each role.

Learner-controlled progression

Instruction proceeds one stage at a time with an explicit end-of-turn marker.

Model / UI separation

The LLM workflow lives in dedicated Python modules while run.py focuses on Gradio interaction and application wiring.

User-facing error handling

OpenAI quota failures are intercepted and converted into a readable application response.

🛠️ Technology stack

Layer

Technology

Language

Python 3.10+

LLM orchestration

LangChain

Model provider

OpenAI Chat Models

Agent abstraction

Custom DiscussAgent

Teaching controller

Custom LangChain Chain + Pydantic state

Prompting

LangChain system/human message templates + PromptTemplate

Application UI

Gradio Blocks

Runtime context

In-memory Python conversation history

Development tooling

setuptools, Black, pre-commit configuration

The repository currently pins:

langchain==0.0.208
openai==0.27.8
pydantic==1.10.13
numpy==1.26.4
gradio==3.41.2

📁 Repository structure

LearnFlow-AI/
├── README.md
├── diagram.png                 # Original architecture diagram
├── requirements.txt
├── setup.py
├── pyproject.toml
├── Makefile
│
└── src/
    ├── run.py                  # Gradio application + workflow wiring
    ├── generating_syllabus.py # Task specification + multi-agent syllabus planning
    ├── teaching_agent.py      # Stateful TeachingGPT instructional controller
    └── EduGPT.ipynb           # Notebook prototype / experimentation

🚀 Run locally

1. Clone

git clone https://github.com/Ankita2525/LearnFlow-AI.git
cd LearnFlow-AI

2. Create an environment

python3.10 -m venv .venv
source .venv/bin/activate

On Windows:

.venv\Scripts\activate

3. Install dependencies

pip install -r requirements.txt

4. Configure the OpenAI key

The current implementation reads .env directly and expects:

OPENAI_API_KEY=your_openai_api_key

Do not commit real credentials.

5. Start the application

python src/run.py

Gradio prints the local application URL in the terminal.

✅ Implemented capabilities

topic-driven learning workflow

LLM-based task specification

role-constrained Instructor and Teaching Assistant agents

bounded 5-turn multi-agent curriculum planning

dedicated syllabus synthesis stage

generated syllabus handoff into runtime instruction

custom stateful TeachingGPT controller

syllabus-aware instructor prompting

conversation-history-aware responses

one-stage-at-a-time teaching behavior

explicit human-in-the-loop turn boundaries

Gradio syllabus-generation interface

Gradio AI Instructor chat interface

character-streamed response presentation

OpenAI quota error handling

modular Python implementation plus notebook prototype

📈 Production evolution

The current code establishes the multi-agent planning + stateful instruction core. A production deployment would naturally harden that architecture with:

structured syllabus schemas and validation,

persistent learner/session storage,

authentication and multi-user isolation,

RAG over trusted course material with citations,

automated syllabus and instruction-quality evaluations,

model/prompt regression testing,

traces for agent handoffs and model calls,

latency, token, cost, and failure telemetry,

retries/timeouts and graceful failure handling,

asynchronous long-running curriculum generation,

provider-independent model routing,

deployment and observability infrastructure.

These are architectural extensions; they are not claimed as implemented in the current repository.

🌱 Why LearnFlow AI?

A generic chatbot answers the next question.

A learning system has to coordinate a sequence:

Define the learning objective
        ↓
Plan the curriculum
        ↓
Synthesize the learning path
        ↓
Teach one stage
        ↓
Observe learner feedback
        ↓
Continue with context

LearnFlow AI turns that sequence into an explicit multi-agent workflow with role separation, state handoffs, and learner-controlled progression.

Don't just answer the learner. Build the learning flow.

<div align="center">

LearnFlow AI

Multi-Agent Systems · LLM Orchestration · Stateful Instruction · Human-in-the-Loop Learning

</div>

<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&height=110&color=0:C850C0,50:5B5FEF,100:00C9A7&section=footer" alt="LearnFlow AI footer" />
