<!-- SYNC IMPACT REPORT
Version change: N/A -> 1.0.0
Modified principles: N/A (new constitution)
Added sections: All sections (new constitution)
Removed sections: None
Templates requiring updates: TODO
Follow-up TODOs: None
-->
# Physical AI & Humanoid Robotics — AI-Native Textbook Platform Constitution

## Core Principles

### Spec-Driven Development ONLY
All implementation work requires explicit specification approval via `/sp.specify`. No coding, no repositories, no files may be generated until formal approval is granted. This ensures architectural discipline and traceable development.

### Specification-First Validation
All work must be planned and validated through comprehensive Markdown specifications before any coding begins. Each feature, module, and functionality must be detailed with acceptance criteria, interfaces, and test scenarios.

### Frontend Standardization
Frontend development uses Next.js + Docusaurus for content delivery. This ensures consistent user experience, SEO optimization, and scalable content management for the textbook platform.

### Styling Framework
Styling follows TailwindCSS, shadcn/ui, and Skipper-style animated UI implementations. This creates a cohesive visual experience that supports the educational objectives of the platform.

### Backend RAG Architecture
Backend chatbot is Python-based and integrated with Next.js. The RAG system relies on OpenAI Agents/ChatKit SDKs, FastAPI, Neon Serverless Postgres, and Qdrant Cloud (Free Tier) to deliver responsive AI-powered learning assistance.

### Content Modularity
Book content must be modular, versionable, and AI-consumable. This enables adaptive learning paths, personalized content delivery, and seamless updates to educational materials.

### Personalization & Localization
Personalization, Urdu translation, and adaptive learning are first-class design goals. The platform must accommodate diverse learning styles, languages, and proficiency levels.

### Hackathon Traceability
Hackathon bonus objectives must be explicitly planned and traceable. Each objective must have corresponding specifications and implementation tasks that can be tracked through the development lifecycle.

## Additional Constraints

### Non-Goals
- Premature coding without formal specification approval
- UI mockups without underlying architecture plans
- Infrastructure provisioning before specification completion
- Package installation steps without architectural context

### Allowed Technologies
- Next.js + Docusaurus for frontend
- Python with FastAPI for backend services
- TailwindCSS, shadcn/ui for styling
- OpenAI Agents / ChatKit SDKs for AI functionality
- Neon Serverless Postgres for data persistence
- Qdrant Cloud for vector storage
- ROS 2, NVIDIA Isaac, and Vision-Language-Action systems for robotics simulation

### Forbidden Actions
- Starting implementation before specification approval
- Deviating from the chosen technology stack without approval
- Creating repositories or files without proper workflow adherence
- Skipping documentation or testing phases

### Quality Standards
- Code must be maintainable and well-documented
- AI responses must be reliable and pedagogically sound
- Book content must meet academic standards
- System performance must support multi-user educational scenarios

## Development Workflow

### File Generation Rules
- Generate only Markdown files via SpecifyPlus memory during specification phase
- Documentation must precede implementation
- Specifications must include acceptance tests
- All changes must be traceable to requirements

### Approval Process
- Specifications must pass architectural review
- Technical feasibility must be confirmed
- Resource requirements must be validated
- Timeline estimates must be realistic

### Quality Gates
- All features require comprehensive specifications
- Code must pass automated testing
- AI components must undergo validation
- Content must be reviewed by domain experts

## Governance

This constitution supersedes all other development practices and must be followed strictly. Amendments require explicit documentation, approval from project leadership, and a clear migration plan for existing work. All PRs and reviews must verify constitutional compliance. Complexity must be justified with clear benefits to the educational mission. Use this constitution as the primary guidance document for all development decisions.

**Version**: 1.0.0 | **Ratified**: 2025-06-13 | **Last Amended**: 2025-12-14