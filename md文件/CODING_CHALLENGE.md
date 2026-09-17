# Intern Coding Challenge: Intelligent Task Management System

## Overview
Build a **Task Management System** with intelligent features that demonstrates your coding abilities across different specializations. This challenge is designed to evaluate candidates for various roles including Backend, Frontend, Full-Stack, and AI/LLM Development positions.

**Time Limit:** 2-4 hours
**Submission:** Git repository with clear README and commit history

---

## Problem Statement

Create a task management system that allows users to create, organize, and manage tasks with intelligent assistance. The system should have a backend API and can optionally include a frontend interface and/or AI-powered features.

---

## Core Requirements (All Candidates)

### 1. Task CRUD Operations
Implement a RESTful API or service layer with the following endpoints:

- **CREATE** - Add a new task
- **READ** - Get task(s) by ID or list all tasks
- **UPDATE** - Modify task details
- **DELETE** - Remove a task

### 2. Task Properties
Each task should have:
- `id` (unique identifier)
- `title` (string, required)
- `description` (string, optional)
- `status` (enum: "pending", "in_progress", "completed")
- `priority` (enum: "low", "medium", "high")
- `created_at` (timestamp)
- `updated_at` (timestamp)
- `tags` (array of strings, optional)

### 3. Data Persistence
Choose appropriate storage:
- **Simple**: JSON file or SQLite
- **Recommended**: MySQL, PostgreSQL, MongoDB, or Redis
- **Advanced**: Combination of database + cache layer

### 4. Code Quality Requirements
- Clean, readable, and well-organized code
- Proper error handling
- Input validation
- At least basic documentation (README)
- Clear commit messages

---

## Role-Specific Features (Choose Based on Your Target Role)

### Option A: Backend Developer Track

Implement these advanced backend features:

1. **Task Filtering & Sorting**
   - Filter by status, priority, tags
   - Sort by creation date, priority, status
   - Pagination support

2. **Task Dependencies**
   - Tasks can depend on other tasks
   - Cannot mark task as completed if dependencies aren't done
   - API to query task dependency tree

3. **Performance Optimization**
   - Implement caching for frequently accessed data
   - Database query optimization
   - API response time < 100ms for basic operations

4. **System Design**
   - Design considerations for scaling to 100k+ tasks
   - Include a brief architecture document

**Bonus Points:**
- Implement search functionality (full-text search)
- Add user authentication/authorization
- Rate limiting for API endpoints
- Containerization (Docker)

---

### Option B: Frontend Developer Track

Build a user interface with these features:

1. **Task Dashboard**
   - Display all tasks in an organized view (list/kanban/calendar)
   - Visual indicators for priority and status
   - Responsive design (mobile-friendly)

2. **Interactive Task Management**
   - Drag-and-drop to change status or reorder
   - Quick actions (mark complete, delete, edit)
   - Real-time search/filter

3. **User Experience**
   - Smooth animations and transitions
   - Loading states and error messages
   - Form validation with helpful feedback

4. **State Management**
   - Proper state management (Context/Redux/Vuex/Pinia)
   - Optimistic UI updates
   - Handle edge cases gracefully

**Tech Stack Options:**
- React + TypeScript + Tailwind/MUI
- Vue 3 + TypeScript + Element Plus
- Vanilla JavaScript (if you want to show fundamentals)

**Bonus Points:**
- Dark mode support
- Keyboard shortcuts
- Offline support (PWA)
- Data visualization (charts/graphs)

---

### Option C: Full-Stack Developer Track

Combine backend and frontend requirements:

1. **Complete Application**
   - Working backend API (choose from Backend Track features)
   - Functional frontend UI (choose from Frontend Track features)
   - Proper integration between frontend and backend

2. **System Architecture**
   - Clear separation of concerns
   - RESTful API design or GraphQL
   - Error handling on both layers

3. **Deployment Consideration**
   - Docker compose setup OR deployment instructions
   - Environment configuration management
   - Basic CI/CD setup (optional but impressive)

**Bonus Points:**
- WebSocket for real-time updates
- File upload for task attachments
- Export tasks (JSON/CSV/PDF)

---

### Option D: AI/LLM Developer Track

Build intelligent features using AI/ML/LLM:

1. **Intelligent Task Generation**
   - Natural language task creation: "Remind me to buy groceries tomorrow at 3pm"
   - Extract: title, description, due date, priority from natural language

2. **Smart Task Organization**
   - Automatic tag suggestion based on task content
   - Priority recommendation using simple ML or LLM
   - Task categorization

3. **AI Assistant Features** (Choose at least 2)
   - Task breakdown: split complex task into subtasks
   - Task summarization: generate summary of daily/weekly tasks
   - Similar task detection: find related tasks
   - Smart search: semantic search instead of keyword matching

4. **Implementation Options**
   - Use OpenAI API / Anthropic API (provide API key handling)
   - Use local models (HuggingFace, LangChain)
   - Use embeddings + vector database (ChromaDB, FAISS)
   - Build simple ML classifier (sklearn, PyTorch)

**Bonus Points:**
- RAG implementation for task knowledge base
- Multi-agent system (planning agent + execution agent)
- Fine-tuned model for task domain
- Prompt optimization and testing

---

## Technical Constraints

### Backend Frameworks (Choose one):
- **Python**: FastAPI, Flask, Django
- **Node.js**: Express, NestJS, Fastify
- **Java**: Spring Boot
- **Go**: Gin, Echo
- **Any other**: Justify your choice

### Database Options:
- SQL: PostgreSQL, MySQL, SQLite
- NoSQL: MongoDB, Redis
- Vector DB (for AI track): ChromaDB, Pinecone, FAISS

### Frontend Frameworks (if applicable):
- React, Vue, Angular, Svelte
- Or vanilla HTML/CSS/JavaScript

---

## Evaluation Criteria

### Code Quality (30%)
- Clean, readable code with consistent style
- Proper project structure and organization
- Meaningful variable/function names
- Comments where necessary (not excessive)
- Error handling and edge cases

### Problem-Solving (30%)
- Correct implementation of requirements
- Algorithmic efficiency
- Handling of edge cases
- Creative solutions to challenges

### System Design (25%)
- Appropriate architecture choices
- Scalability considerations
- Database schema design
- API design (RESTful principles or GraphQL)
- Separation of concerns

### Documentation (15%)
- Clear README with:
  - Project description
  - Setup instructions
  - API documentation
  - Design decisions and trade-offs
  - Known limitations
  - Future improvements
- Code comments where appropriate
- Commit history quality

---

## Submission Requirements

### 1. Git Repository
- Initialize git from the start
- Make meaningful commits (not just one big commit)
- Include a `.gitignore` file
- **Do NOT commit**: API keys, node_modules, venv, IDE configs

### 2. README.md
Must include:
```markdown
# Project Title

## Role Track
[Backend / Frontend / Full-Stack / AI-LLM]

## Tech Stack
- Language:
- Framework:
- Database:
- Other tools:

## Features Implemented
- [ ] Feature 1
- [ ] Feature 2
...

## Setup Instructions
1. Prerequisites
2. Installation steps
3. Configuration
4. Running the application

## API Documentation
[Endpoints, request/response examples]

## Design Decisions
[Why you chose certain technologies or approaches]

## Challenges & Solutions
[Problems you faced and how you solved them]

## Future Improvements
[What you would add with more time]

## Time Spent
Approximately X hours
```

### 3. Code Structure Example
```
project/
├── README.md
├── requirements.txt / package.json
├── .gitignore
├── src/
│   ├── models/
│   ├── controllers/
│   ├── services/
│   ├── routes/
│   └── utils/
├── tests/ (optional but recommended)
└── docs/ (optional)
```

---

## Bonus Points (Optional)

- **Testing**: Unit tests, integration tests
- **CI/CD**: GitHub Actions workflow
- **Logging**: Structured logging implementation
- **Monitoring**: Health check endpoints
- **Security**: SQL injection prevention, XSS protection, CORS setup
- **Performance**: Load testing results, optimization documentation
- **Accessibility**: WCAG compliance (for frontend)


---

## FAQs

**Q: Can I use external libraries/frameworks?**
A: Yes, but justify your choices. Using too many unnecessary libraries may count against you.

**Q: Can I use AI assistants (ChatGPT, Copilot)?**
A: Mention it in your README if you do. We value your understanding and decision-making more than perfect code.

**Q: What if I can't finish everything?**
A: Submit what you have with clear documentation of what's complete and what's pending. Quality > Quantity.

**Q: Can I choose multiple tracks?**
A: Advanced candidates can combine tracks (e.g., Full-Stack + AI features), but ensure quality doesn't suffer.

**Q: Should I deploy the application?**
A: Not required, but providing a live demo is impressive. At minimum, provide clear local setup instructions.


---

Good luck! We're looking forward to seeing your solution. Remember: we value **clean code, good design, and clear thinking** over feature completeness.
