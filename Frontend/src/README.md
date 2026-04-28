# CFO Multi-Agent Chatbot - Frontend

> Intelligent financial analysis chatbot for AIBI Wind Energy using LangGraph multi-agent AI system

![Status](https://img.shields.io/badge/Status-Ready%20for%20Testing-green)
![Backend](https://img.shields.io/badge/Backend-Integrated-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue)
![React](https://img.shields.io/badge/React-18.x-blue)

---

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ installed
- Your FastAPI backend running at `http://localhost:8000`

### Installation & Run

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open browser at http://localhost:5173
```

**That's it!** The app will connect to your backend automatically.

---

## 📊 What This Does

This is a conversational AI assistant for CFO-level financial analysis of AIBI Wind Energy's turbine operations:

- **Natural Language Queries:** Ask questions in plain English
- **Multi-Agent Processing:** 5 specialized AI agents (Orchestrator, Visualization, Insights, Forecasting, Follow-up)
- **Real-Time Visualization:** Embedded charts and graphs in chat
- **CFO-Grade Insights:** Executive summaries and detailed analysis
- **Session Persistence:** Continue conversations across sessions
- **Smart Follow-ups:** AI-generated contextual next questions

---

## 🎯 Key Features

### 1. Conversational Interface
- ChatGPT-like messaging experience
- Real-time agent pipeline visualization
- Embedded charts and insights
- Clickable follow-up questions

### 2. Dashboard
- 7 key financial metrics
- Click cards to query specific data
- System status monitoring
- Database connection status

### 3. Session Management
- Multiple conversation sessions
- Persistent across page refreshes
- Automatic title generation
- Session switching in sidebar

### 4. Backend Integration
- ✅ Connected to FastAPI backend
- ✅ Real-time data from PostgreSQL
- ✅ Session persistence in Redis
- ✅ Real-time backend integration

---

## 📖 Documentation

| Guide | Description |
|-------|-------------|
| **[QUICKSTART.md](./QUICKSTART.md)** | 5-minute setup and testing guide |
| **[INTEGRATION_COMPLETE.md](./INTEGRATION_COMPLETE.md)** | Backend integration summary |
| **[BACKEND_TESTING.md](./BACKEND_TESTING.md)** | Comprehensive testing documentation |
| **[ARCHITECTURE.md](./ARCHITECTURE.md)** | System architecture and design |
| **[PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md)** | Project background and requirements |

**Start here:** [QUICKSTART.md](./QUICKSTART.md)

---

## 🔌 Backend Connection

### Status Indicator

Look for the connection badge in the top-right corner:

- 🟢 **Connected** - Backend reachable, using real data
- 🟠 **Offline Mode** - Backend unavailable

### Configuration

Create a `.env` file (or use the existing one):

```env
VITE_API_URL=http://localhost:8000
VITE_DEFAULT_USER_ID=demo_user
VITE_DEBUG_MODE=true
```

### Endpoints Connected

- `POST /api/query` - Query processing
- `GET /api/user/{user_id}/sessions` - Session list
- `GET /api/conversation/{session_id}` - Conversation history
- `DELETE /api/conversation/{session_id}` - Clear session
- `GET /health` - Health check
- `GET /api/system/status` - System status
- `GET /api/system/database` - Database status

---

## 🧪 Testing

### With Backend Running

```bash
# Terminal 1: Start backend
cd /path/to/backend
python main.py

# Terminal 2: Start frontend
npm run dev

# Browser: http://localhost:5173
```

### Without Backend (Offline Mode)

```bash
# Just start frontend
npm run dev

# App works with mock data
```

### Test Scenarios

1. **Send a query:** "What was the revenue for Q3 2024?"
2. **View agent pipeline:** See all 5 agents process in real-time
3. **Check visualizations:** Charts embedded in chat messages
4. **Click follow-ups:** Contextual questions auto-generated
5. **Create sessions:** Multiple conversations in sidebar
6. **Refresh page:** Sessions persist

---

## 🏗️ Tech Stack

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS v4** - Styling
- **Shadcn/ui** - Component library
- **Vite** - Build tool
- **Lucide React** - Icons

### Backend Integration
- **FastAPI** - REST API
- **PostgreSQL** - Database (AIBI E3/E4 turbine data)
- **Redis** - Session storage
- **LangGraph** - Multi-agent orchestration
- **LangChain** - Agent framework
- **LlamaIndex** - RAG system

---

## 📁 Project Structure

```
├── /components          # React components
│   ├── /ui             # Shadcn UI components
│   ├── ChatMessage.tsx # Message display
│   ├── ChatInput.tsx   # Input component
│   ├── AgentPipeline.tsx # Agent visualization
│   ├── DashboardPage.tsx # Dashboard
│   └── ...
├── /services           # API integration
│   ├── api.ts         # Backend API calls
│   └── database.ts    # Database utilities
├── /types              # TypeScript types
│   └── index.ts       # Type definitions
├── /styles             # Global styles
│   └── globals.css    # Tailwind config
├── App.tsx            # Main application
├── .env               # Environment config
└── Documentation files
```

---

## 🎨 Design System

### Color Palette
- **Background:** Dark blue (#0a0f1e, #0f1629)
- **Primary:** Emerald green (#10b981)
- **Text:** White/Gray scale
- **Accents:** Green gradients

### Typography
- **Font:** General Sans
- **Headings:** Dynamic sizing
- **Body:** Optimized for readability

### Components
- 40+ Shadcn/ui components
- Custom chat components
- Agent pipeline visualization
- Chart rendering (Plotly)

---

## 🚀 Deployment

### Build for Production

```bash
npm run build
```

Output: `dist/` directory

### Preview Production Build

```bash
npm run preview
```

### Deploy To

- **Vercel** - Recommended (zero config)
- **Netlify** - Easy deploy
- **AWS S3 + CloudFront** - Scalable
- **Any static host**

### Environment Variables

Set in deployment platform:
```
VITE_API_URL=https://your-production-api.com
VITE_DEFAULT_USER_ID=production_user
VITE_DEBUG_MODE=false
```

---

## 🔧 Development

### Install Dependencies

```bash
npm install
```

### Development Server

```bash
npm run dev
```

Hot reload enabled - changes appear instantly.

### Build

```bash
npm run build
```

### Type Check

```bash
npm run type-check
```

### Lint

```bash
npm run lint
```

---

## 📊 Features in Detail

### Multi-Agent System

**5 Specialized Agents:**

1. **Orchestrator** - Routes queries to appropriate agents
2. **Visualization** - Generates Plotly charts
3. **Insights** - Provides CFO-grade analysis
4. **Forecasting** - Prophet/XGBoost predictions
5. **Follow-up** - Generates contextual questions

**Real-time Pipeline:**
- Visual progress bars
- Status indicators (pending → processing → completed)
- Execution time tracking

### Visualizations

Supported chart types:
- Bar charts (stacked, grouped)
- Line charts (time series)
- Pie/Donut charts
- Heatmaps
- Choropleth maps (geographic)
- Scatter plots
- Box plots
- And more...

All charts are:
- Interactive (zoom, pan, hover)
- Responsive
- Dark mode themed
- Embedded in chat messages

### CFO Response Format

Every insight includes:
- **Summary:** 4-5 line executive overview
- **Key Metrics:** 4-6 critical numbers with trends
- **Recommendations:** Actionable next steps
- **Risk Flags:** Potential concerns

---

## 🎯 Use Cases

### Revenue Analysis
"What was the revenue for Q3 2024?"
- Revenue trends
- YoY growth
- Profit margins
- Geographic breakdown

### Project Pipeline
"Show me the operational pipeline breakdown"
- Projects by phase
- Capacity analysis
- Completion rates
- Resource allocation

### Forecasting
"Forecast Q4 2024 revenue"
- Prophet time-series predictions
- Confidence intervals
- Scenario analysis
- Growth projections

### Performance Metrics
"How do E4 turbines compare to E3?"
- Model comparison
- Efficiency metrics
- Market share
- Profitability

---

## 📈 Performance

### Load Times (with backend)
- Initial load: < 2s
- Session load: < 500ms
- Query processing: 2-5s
- Chart rendering: < 1s

### Optimizations
- Code splitting
- Lazy loading
- Efficient re-renders
- Memoization
- Virtual scrolling for long chats

---

## 🔐 Security

### Current Implementation
- Client-side only (no auth yet)
- Demo user ID hardcoded
- CORS configured for localhost

### Production TODO
- [ ] Add authentication (JWT/OAuth)
- [ ] User management
- [ ] Role-based access control
- [ ] API key management
- [ ] Rate limiting
- [ ] Input sanitization

---

## 🐛 Troubleshooting

### Common Issues

**Issue:** "Offline Mode" badge shows
- **Solution:** Check if backend is running on port 8000

**Issue:** CORS errors
- **Solution:** Verify CORS middleware in backend

**Issue:** Sessions not persisting
- **Solution:** Check Redis connection in backend

**Issue:** TypeScript errors
- **Solution:** Run `npm run build` to see details

**See:** [BACKEND_TESTING.md](./BACKEND_TESTING.md) for detailed troubleshooting

---

## 📝 Environment Variables

```env
# Required
VITE_API_URL=http://localhost:8000

# Optional
VITE_DEFAULT_USER_ID=demo_user
VITE_DEBUG_MODE=true
```

Copy `.env.example` to `.env` and customize.

---

## 🤝 Contributing

### Development Workflow

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Build successfully
5. Submit for review

### Code Style

- TypeScript strict mode
- ESLint configured
- Prettier for formatting
- Conventional commits

---

## 📄 License

Proprietary - AIBI Wind Energy

---

## 🎉 Getting Started

**Ready to test?**

```bash
npm install && npm run dev
```

**Then open:** http://localhost:5173

**Need help?** Start with [QUICKSTART.md](./QUICKSTART.md)

---

## 📞 Support

For questions or issues:
1. Check documentation files
2. Review console logs
3. Test endpoints with curl
4. Verify backend connection

---

**Built with ❤️ for AIBI Wind Energy**

*Empowering CFO-level insights through conversational AI*
