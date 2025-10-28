# TargetScriptAI
> Multi-Agent AI Content Generation System with Persona-Driven Targeting and LangGraph Orchestration

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg)](https://streamlit.io)
[![LangGraph](https://img.shields.io/badge/LangGraph-latest-purple.svg)](https://github.com/langchain-ai/langgraph)
[![Groq](https://img.shields.io/badge/Groq-Cloud-orange.svg)](https://groq.com)

## 🚀 Overview

TargetScriptAI is a sophisticated content generation platform that leverages specialized AI agents working collaboratively to create highly targeted, persona-specific content. Built with modern Python frameworks and enterprise-grade architecture patterns, it combines advanced persona analysis with strategic content planning and quality assurance workflows.

### ✨ Key Features

- **🤖 Multi-Agent Architecture**: Four specialized AI agents in orchestrated workflow
- **👥 Persona-Driven Targeting**: 11 pre-built personas with custom persona creation
- **📝 Versatile Content Types**: 8+ content formats from blog posts to whitepapers
- **⚡ High Performance**: Optimized workflows with ultra-fast Groq inference
- **🔧 Production Ready**: FastAPI backend with comprehensive API documentation
- **📊 Real-Time Analytics**: Content generation tracking and quality metrics
- **🎯 Strategic Planning**: AI-powered content strategy and positioning

### 🏗️ Architecture

┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Streamlit │ │ FastAPI │ │ Groq Cloud │
│ Frontend │◄──►│ Backend │◄──►│ LLM API │
└─────────────────┘ └─────────────────┘ └─────────────────┘
│ │ │
▼ ▼ ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ LangGraph │ │ Persona │ │ Content │
│ Workflow │◄──►│ Service │◄──►│ Orchestrator │
└─────────────────┘ └─────────────────┘ └─────────────────┘

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Groq API Key
- Git

### 1. Clone Repository
git clone https://github.com/Kushan82/TargetScriptAI.git
cd TargetScriptAI

### 2. Environment Setup
Create virtual environment
python -m venv .venv

Activate virtual environment
Windows
.venv\Scripts\activate

Install dependencies
pip install -r requirements.txt

### 3. Configuration
Create a `.env` file in the root directory:
LLM Configuration
LLM__GROQ_API_KEY=your_groq_api_key_here
LLM__GROQ_MODEL_SMART=llama-3.3-70b-versatile
LLM__GROQ_MODEL_FAST=llama-3.1-8b-instant
LLM__GROQ_MODEL_CREATIVE=llama-3.1-8b-instant

API Configuration
API__HOST=0.0.0.0
API__PORT=8000

Security
SECURITY__SECRET_KEY=your_secret_key_here

Environment
ENVIRONMENT=development
DEBUG=True

### 4. Run Development Server

#### Start Backend + Frontend
Terminal 1: Start FastAPI backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

Terminal 2: Start Streamlit frontend
cd frontend
streamlit run app.py --server.port 8501

### 5. Access Application
- **Streamlit Dashboard**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/api/v1/health/

## 🤖 Agent System
### Specialized Agents

| Agent | Role | Capabilities |
|-------|------|-------------|
| **Persona Agent** | Audience Analysis & Insight Generation | Demographics analysis, pain point identification, preference mapping |
| **Strategy Agent** | Content Planning & Positioning | Funnel stage determination, key messaging, CTA recommendations |
| **Creative Agent** | Content Generation & Optimization | Targeted content creation, tone adaptation, keyword integration |
| **QA Agent** | Quality Assurance & Improvement | Content review, alignment scoring, improvement suggestions |

### Workflow Patterns
- **Sequential Processing**: Step-by-step agent execution with cumulative insights
- **Persona-Driven**: All content decisions based on target audience analysis
- **Quality Focused**: Built-in QA agent ensures content excellence
- **Analytics Tracking**: Comprehensive workflow and performance metrics

## 📝 Content Configuration
### Content Types & Specifications

| Content Type | Typical Length | Best For | Required Elements |
|--------------|----------------|----------|-------------------|
| **Blog Post** | 800-2000 words | SEO, Thought Leadership | Title, Introduction, Body, CTA |
| **Social Media** | 50-280 characters | Engagement, Brand Awareness | Hook, Value Prop, Hashtags |
| **Email Campaign** | 150-500 words | Lead Nurturing, Sales | Subject, Preview, Body, CTA |
| **Ad Copy** | 25-150 words | Lead Gen, Conversions | Headline, Description, CTA |
| **Landing Page** | 300-800 words | Lead Capture, Sales | Hero, Benefits, Social Proof |
| **Case Study** | 800-1500 words | Social Proof, Credibility | Challenge, Solution, Results |
| **Newsletter** | 300-800 words | Retention, Education | Header, Content, Updates |
| **Whitepaper** | 2000-5000 words | Lead Gen, Authority | Executive Summary, Research |

### Tone Options
tone_styles:
professional: "Formal business communication"
casual: "Relaxed and approachable"
friendly: "Warm and personal"
authoritative: "Expert and commanding"
conversational: "Natural dialogue style"
formal: "Official and structured"
innovative: "Forward-thinking and creative"   
empathetic: "Understanding and supportive"

### Platform Optimization
website: "SEO-optimized, comprehensive"
linkedin: "Professional, B2B focused"
twitter: "Concise, engaging, hashtag-optimized"
facebook: "Community-oriented, visual"
instagram: "Visual-first, caption-focused"
email: "Direct, personalized, CTA-driven"
blog: "Long-form, educational"
medium: "Story-driven, thought leadership"


## 👥 Persona Library
### Pre-Built Personas
| Persona | Industry | Experience | Primary Goals |
|---------|----------|------------|---------------|
| **Tech Startup Founder** | Technology | Intermediate | Customer acquisition, Fundraising |
| **SaaS Marketing Manager** | Technology | Advanced | Lead generation, ROI improvement |
| **Digital Content Creator** | Media | Intermediate | Audience growth, Monetization |
| **Small Business Owner** | Retail | Beginner | Local visibility, Customer loyalty |
| **Enterprise CEO** | Technology | Expert | Thought leadership, Transformation |
| **Independent Freelancer** | Professional Services | Intermediate | Client pipeline, Reputation |
| **Management Consultant** | Professional Services | Expert | Client trust, Market expansion |
| **Creative Agency Owner** | Marketing | Advanced | High-value clients, Reputation |
| **University Professor** | Education | Expert | Knowledge sharing, Research impact |
| **Healthcare Professional** | Healthcare | Expert | Patient education, Practice reputation |
| **Financial Advisor** | Finance | Advanced | Client trust, Thought leadership |

### Custom Persona Creation
required:
- name: "Persona display name"
- type: "Persona category"
- industry: "Target industry"
- primary_goals: ["List of goals"]
- pain_points: ["List of challenges"]
- preferred_channels: ["Communication channels"]
optional:
- demographics: "Detailed demographics"
- content_preferences: ["Content preferences"]
- tone_preference: "Preferred tone"
- additional_context: "Extra insights"

## 📁 Project Structure
TargetScriptAI/
├── app/ # FastAPI Backend
│ ├── agents/ # AI Agent implementations
│ │ ├── init.py
│ │ ├── persona_agent.py # Persona analysis agent
│ │ ├── strategy_agent.py # Strategy planning agent
│ │ ├── creative_agent.py # Content generation agent
│ │ └── qa_agent.py # Quality assurance agent
│ ├── api/ # API endpoints
│ │ ├── init.py
│ │ └── v1/
│ │ ├── init.py
│ │ ├── endpoints/
│ │ │ ├── health.py # Health check endpoints
│ │ │ ├── personas.py # Persona management
│ │ │ └── generate.py # Content generation
│ │ └── router.py
│ ├── config/ # Configuration management
│ │ ├── init.py
│ │ ├── logger.py # Logging configuration
│ │ └── settings.py # Application settings
│ ├── models/ # Pydantic models
│ │ ├── init.py
│ │ ├── personas.py # Persona data models
│ │ ├── content.py # Content models
│ │ └── responses.py # API response models
│ ├── services/ # Business logic layer
│ │ ├── init.py
│ │ ├── llm_service.py # LLM integration service
│ │ ├── persona_service.py # Persona management
│ │ └── orchestrator.py # Workflow orchestration
│ ├── utils/ # Utility functions
│ │ ├── init.py
│ │ └── helpers.py
│ └── main.py # FastAPI application entry
├── frontend/ # Streamlit Frontend
│ ├── pages/ # Application pages
│ │ ├── Persona_Selection.py # Persona selection UI
│ │ ├── Content_Config.py # Content configuration
│ │ ├── Generation.py # Content generation UI
│ │ └── Analytics.py # Analytics dashboard
│ ├── components/ # Reusable UI components
│ │ └── sidebar.py # Navigation sidebar
│ ├── utils/ # Frontend utilities
│ │ ├── init.py
│ │ └── api_client.py # API client wrapper
│ └── app.py # Main Streamlit application
├── data/ # Data storage
│ ├── personas/ # Persona definitions
│ │ └── default_personas.json
│ └── workflows/ # Workflow logs (generated)
├── tests/ # Test suite
│ ├── init.py
│ ├── test_agents.py # Agent tests
│ ├── test_api.py # API endpoint tests
│ ├── test_services.py # Service layer tests
│ └── test_workflow.py # Workflow tests
├── .env # Environment variables (not in repo)
├── .env.example # Environment template
├── .gitignore # Git ignore rules
├── docker-compose.yml # Docker configuration
├── Dockerfile # Docker image definition
├── requirements.txt # Python dependencies
├── README.md # This file
└── LICENSE # MIT License

## 🚀 Deployment

### Local Development

1. Clone repository
2. Set up virtual environment
3. Configure API keys in `.env`
4. Run backend: `uvicorn app.main:app --reload`
5. Run frontend: `streamlit run frontend/app.py`
