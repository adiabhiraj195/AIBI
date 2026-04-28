import { useEffect, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ChatMessage } from '../components/ChatMessage';
import { ChatInput } from '../components/ChatInput';
import { BackendStatus } from '../components/BackendStatus';
import { ScrollArea } from '../components/ui/scroll-area';
import { Brain, Settings, BarChart3, TrendingUp, Users } from 'lucide-react';
import { processQuery, checkAPIHealth, getDatabaseStatus, getSystemStatus, getUserSessions, getConversationHistory, getAuthUser } from '../services/api';
import { Message, ChatSession, AgentType, SystemStatus, QueryResponse } from '../types';
import AppLayout from '../components/AppLayout';


export default function ChatPage() {
    const [userId, setUserId] = useState<string>('');
    const [sessionId, setSessionId] = useState<string>('session_' + Date.now());
    const [messages, setMessages] = useState<Message[]>([]);
    const [sessions, setSessions] = useState<ChatSession[]>([]);
    const [isProcessing, setIsProcessing] = useState(false);
    const [systemStatus, setSystemStatus] = useState<SystemStatus>({
        apiHealth: true,
        dbConnected: true,
        ragSystemActive: true,
        modelsLoaded: true,
        activeAgents: [AgentType.ORCHESTRATOR, AgentType.VISUALIZATION, AgentType.INSIGHTS, AgentType.FORECASTING, AgentType.FOLLOWUP]
    });
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const navigate = useNavigate();
    const location = useLocation() as any;

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        const user = getAuthUser();
        if (user) {
            setUserId(String(user.id));
        } else {
            navigate('/login');
        }
    }, [navigate]);

    useEffect(() => {
        if (userId) {
            checkSystemStatus();
            loadUserSessions(userId);
            restoreCurrentSession(userId);
        }
    }, [userId]);

    // Handle prefill query from navigation state (e.g., from Dashboard)
    useEffect(() => {
        const prefill = location?.state?.prefillQuery as string | undefined;
        if (prefill) {
            handleQuerySubmit(prefill);
            navigate('.', { replace: true, state: {} });
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const restoreCurrentSession = async (currentUserId: string) => {
        try {
            const storedSessionId = localStorage.getItem('currentSessionId');
            if (!storedSessionId) return;

            const conversation = await getConversationHistory(storedSessionId, 50);
            if (!conversation || !conversation.turns || conversation.turns.length === 0) return;

            // Verify session belongs to current user
            if (String(conversation.user_id) !== currentUserId && conversation.user_id !== 'demo_user') return;

            const restoredMessages: Message[] = [];
            for (const turn of conversation.turns) {
                restoredMessages.push({
                    id: `${turn.turn_id}_user`,
                    type: 'user',
                    content: turn.user_query,
                    timestamp: new Date(turn.timestamp)
                });

                const queryResponse: QueryResponse = {
                    query_intent: { intent_type: 'general' as any, confidence: 0.8, entities: [] },
                    agent_responses: [
                        {
                            agent_name: AgentType.INSIGHTS,
                            content: turn.agent_response || 'Response generated',
                            visualizations: turn.visualizations || [],
                            confidence: 0.8,
                            execution_time: 0,
                            follow_up_questions: []
                        }
                    ],
                    conversation_context: {
                        session_id: conversation.session_id,
                        user_id: conversation.user_id,
                        previous_queries: [],
                        previous_responses: []
                    },
                    processing_stages: [
                        { agent_name: AgentType.ORCHESTRATOR, status: 'completed' },
                        { agent_name: AgentType.INSIGHTS, status: 'completed' },
                        { agent_name: AgentType.VISUALIZATION, status: 'completed' }
                    ],
                    total_execution_time: 0,
                    timestamp: turn.timestamp
                };

                restoredMessages.push({
                    id: `${turn.turn_id}_assistant`,
                    type: 'assistant',
                    content: turn.agent_response || 'Response generated',
                    timestamp: new Date(turn.timestamp),
                    queryResponse,
                    isProcessing: false,
                    userQuery: turn.user_query
                });
            }

            setSessionId(storedSessionId);
            setMessages(restoredMessages);
        } catch (error) {
            console.error('[ChatPage] Failed to restore session:', error);
        }
    };

    useEffect(() => {
        if (messages.length > 0) {
            saveCurrentSession();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [messages, sessionId]);

    const checkSystemStatus = async () => {
        try {
            const [apiHealth, dbStatus, sysStatus] = await Promise.all([
                checkAPIHealth(),
                getDatabaseStatus(),
                getSystemStatus()
            ]);

            setSystemStatus({
                apiHealth,
                dbConnected: dbStatus.connected,
                ragSystemActive: sysStatus.ragSystemActive,
                modelsLoaded: sysStatus.modelsLoaded,
                activeAgents: sysStatus.activeAgents
            });
        } catch (error) {
            console.error('System status check failed:', error);
            setSystemStatus({ apiHealth: false, dbConnected: false, ragSystemActive: false, modelsLoaded: false, activeAgents: [] });
        }
    };

    const loadUserSessions = async (currentUserId: string) => {
        try {
            const sessionIds = await getUserSessions(currentUserId);
            if (sessionIds.length > 0) {
                const sessionsData = await Promise.all(
                    sessionIds.map(async (sid) => {
                        try {
                            const conversation = await getConversationHistory(sid, 50);
                            if (!conversation) return null;

                            const msgs: Message[] = [];
                            if (conversation?.turns && Array.isArray(conversation.turns) && conversation.turns.length > 0) {
                                for (const turn of conversation.turns) {
                                    msgs.push({ id: `${turn.turn_id}_user`, type: 'user', content: turn.user_query, timestamp: new Date(turn.timestamp) });
                                    const queryResponse: QueryResponse = {
                                        query_intent: { intent_type: 'general' as any, confidence: 0.8, entities: [] },
                                        agent_responses: [
                                            { agent_name: AgentType.INSIGHTS, content: turn.agent_response || 'Response generated', visualizations: turn.visualizations || [], confidence: 0.8, execution_time: 0, follow_up_questions: [] }
                                        ],
                                        conversation_context: { session_id: conversation.session_id, user_id: conversation.user_id, previous_queries: [], previous_responses: [] },
                                        processing_stages: [
                                            { agent_name: AgentType.ORCHESTRATOR, status: 'completed' },
                                            { agent_name: AgentType.INSIGHTS, status: 'completed' },
                                            { agent_name: AgentType.VISUALIZATION, status: 'completed' }
                                        ],
                                        total_execution_time: 0,
                                        timestamp: turn.timestamp
                                    };
                                    msgs.push({ id: `${turn.turn_id}_assistant`, type: 'assistant', content: turn.agent_response || 'Response generated', timestamp: new Date(turn.timestamp), queryResponse, isProcessing: false, userQuery: turn.user_query });
                                }
                            }

                            const title = conversation?.current_topic || (msgs[0]?.content ? msgs[0].content.slice(0, 50) + (msgs[0].content.length > 50 ? '...' : '') : '') || 'New Conversation';

                            return {
                                id: conversation?.session_id || sid,
                                userId: conversation?.user_id || currentUserId,
                                messages: msgs,
                                timestamp: new Date(conversation?.turns?.[0]?.timestamp || Date.now()),
                                lastActivity: new Date(conversation?.last_activity || Date.now()),
                                title
                            } as ChatSession;
                        } catch (error) {
                            console.error(`[ChatPage] Failed to load session ${sid}:`, error);
                            return null;
                        }
                    })
                );

                const validSessions = sessionsData.filter((s): s is ChatSession => s !== null).sort((a, b) => (b.lastActivity?.getTime() || 0) - (a.lastActivity?.getTime() || 0));
                setSessions(validSessions);
            } else {
                setSessions([]);
            }
        } catch (error) {
            console.error('[ChatPage] Failed to load sessions from backend:', error);
            try {
                const storedSessions = localStorage.getItem(`sessions_${currentUserId}`);
                if (storedSessions) {
                    const parsedSessions = JSON.parse(storedSessions);
                    const sessions = parsedSessions.map((s: any) => ({
                        ...s,
                        timestamp: new Date(s.timestamp),
                        lastActivity: s.lastActivity ? new Date(s.lastActivity) : undefined,
                        messages: s.messages.map((m: any) => ({ ...m, timestamp: new Date(m.timestamp) }))
                    }));
                    setSessions(sessions);
                } else {
                    setSessions([]);
                }
            } catch (localStorageError) {
                console.error('[ChatPage] Failed to load from localStorage:', localStorageError);
                setSessions([]);
            }
        }
    };

    const saveCurrentSession = () => {
        if (!userId) return;
        const firstUserMessage = messages.find(m => m.type === 'user');
        const title = firstUserMessage ? firstUserMessage.content.slice(0, 50) + (firstUserMessage.content.length > 50 ? '...' : '') : 'New Conversation';

        const currentSession: ChatSession = { id: sessionId, messages, timestamp: new Date(), title, userId: userId, lastActivity: new Date() };

        setSessions(prevSessions => {
            const filtered = prevSessions.filter(s => s.id !== sessionId);
            const updated = [currentSession, ...filtered];
            try { localStorage.setItem(`sessions_${userId}`, JSON.stringify(updated)); } catch (error) { console.error('Failed to save session:', error); }
            return updated;
        });
    };

    const handleQuerySubmit = async (query: string) => {
        localStorage.setItem('currentSessionId', sessionId);

        const userMessage: Message = { id: Date.now().toString(), type: 'user', content: query, timestamp: new Date() };
        setMessages(prev => [...prev, userMessage]);
        setIsProcessing(true);

        const assistantMessageId = (Date.now() + 1).toString();
        const assistantMessage: Message = {
            id: assistantMessageId,
            type: 'assistant',
            content: 'Analyzing your query...',
            timestamp: new Date(),
            isProcessing: true,
            userQuery: query,
            queryResponse: {
                query_intent: { intent_type: 'general' as any, confidence: 0, entities: [] },
                agent_responses: [],
                conversation_context: { session_id: sessionId, user_id: userId, previous_queries: [], previous_responses: [] },
                processing_stages: [
                    { agent_name: AgentType.ORCHESTRATOR, status: 'pending' },
                    { agent_name: AgentType.VISUALIZATION, status: 'pending' },
                    { agent_name: AgentType.INSIGHTS, status: 'pending' },
                    { agent_name: AgentType.FORECASTING, status: 'pending' },
                    { agent_name: AgentType.FOLLOWUP, status: 'pending' }
                ],
                total_execution_time: 0,
                timestamp: new Date().toISOString()
            }
        };
        setMessages(prev => [...prev, assistantMessage]);

        try {
            const queryStream = processQuery(
                { query, session_id: sessionId, user_id: userId },
                (stage) => {
                    setMessages(prev => prev.map(m => {
                        if (m.id === assistantMessageId && m.queryResponse) {
                            const updatedStages = m.queryResponse.processing_stages?.map(s => s.agent_name === stage.agent_name ? stage : s) || [];
                            return { ...m, queryResponse: { ...m.queryResponse, processing_stages: updatedStages } };
                        }
                        return m;
                    }));
                }
            );

            for await (const response of queryStream) {
                setMessages(prev => prev.map(m => {
                    if (m.id === assistantMessageId) {
                        const insightsAgent = response.agent_responses?.find(r => r.agent_name === AgentType.INSIGHTS);
                        let content = 'Processing...';
                        if (insightsAgent) {
                            if (insightsAgent.content) content = insightsAgent.content;
                            else if ((insightsAgent as any).cfo_response?.summary) content = (insightsAgent as any).cfo_response.summary;
                            else content = 'Response generated successfully';
                        } else if (response.agent_responses && response.agent_responses.length > 0) {
                            const firstAgent = response.agent_responses[0];
                            content = firstAgent.content || 'Response generated successfully';
                        }

                        const allCompleted = response.processing_stages?.every(s => s.status === 'completed' || s.status === 'error');
                        if (allCompleted && content === 'Processing...') content = 'Analysis completed. Please check the detailed response below.';
                        const isProcessing = response.processing_stages?.some(s => s.status === 'processing') || false;
                        return { ...m, content, queryResponse: response, isProcessing };
                    }
                    return m;
                }));
            }

            setMessages(prev => prev.map(m => (m.id === assistantMessageId ? { ...m, isProcessing: false } : m)));
        } catch (error) {
            console.error('Query processing failed:', error);
            setMessages(prev => prev.map(m => {
                if (m.id === assistantMessageId) {
                    return {
                        ...m,
                        content: 'I apologize, but I cannot process your query right now. The backend service appears to be unavailable. Please ensure the backend server is running and try again.',
                        isProcessing: false,
                        queryResponse: m.queryResponse ? { ...m.queryResponse, processing_stages: m.queryResponse.processing_stages?.map(s => ({ ...s, status: 'error' as const })) || [] } : undefined
                    };
                }
                return m;
            }));
        }

        setIsProcessing(false);
    };

    const handleNewChat = () => {
        if (messages.length > 0) saveCurrentSession();
        const newSessionId = 'session_' + Date.now();
        setSessionId(newSessionId);
        setMessages([]);
        localStorage.setItem('currentSessionId', newSessionId);
        navigate('/chat');
    };

    const handleSessionSelect = async (selectedSessionId: string) => {
        if (selectedSessionId === sessionId) return;
        if (messages.length > 0) saveCurrentSession();
        const selectedSession = sessions.find(s => s.id === selectedSessionId);
        if (selectedSession) {
            setSessionId(selectedSession.id);
            setMessages(selectedSession.messages);
            localStorage.setItem('currentSessionId', selectedSession.id);
            navigate('/chat');
        } else {
            console.error('Session not found:', selectedSessionId);
        }
    };

    const hasUserMessages = messages.some(m => m.type === 'user');

    return (
        <AppLayout
            sessions={sessions}
            currentSessionId={sessionId}
            onNewChat={handleNewChat}
            onSessionSelect={handleSessionSelect}
        >
            <div className="flex flex-col h-screen bg-[#0a0f1e]">
                <div className="bg-[#0f1629] border-b border-gray-800/50 px-6 py-3">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div>
                                <h2 className="text-white text-sm">CFO AI Assistant</h2>
                                <p className="text-gray-500 text-xs">Powered by multi-agent AI system</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            <BackendStatus />
                            <button className="w-9 h-9 flex items-center justify-center rounded-lg hover:bg-gray-800/50 text-gray-400 hover:text-white transition-colors">
                                <Settings className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                </div>

                <ScrollArea className="flex-1 bg-[#0a0f1e]">
                    {!hasUserMessages ? (
                        <div className="flex flex-col items-center justify-center min-h-[calc(100vh-140px)] px-6">
                            <div className="max-w-4xl w-full flex flex-col items-center">
                                {/* Hero Icon */}
                                <div className="mb-8">
                                    <div className="w-20 h-20 bg-[#0f1629] border border-gray-800 rounded-2xl flex items-center justify-center">
                                        <Brain className="w-10 h-10 text-emerald-500" />
                                    </div>
                                </div>

                                {/* Hero Text */}
                                <h1 className="text-4xl md:text-5xl font-bold text-center text-white mb-6 tracking-tight">
                                    AI Assistant
                                </h1>
                                <p className="text-center text-gray-400 mb-16 text-lg max-w-2xl leading-relaxed">
                                    Your intelligent financial companion for Green.co Wind Energy.
                                    <br className="hidden md:block" />
                                    Leveraging <span className="text-emerald-500 font-medium">multi-agent architecture</span> for precision in revenue analysis, forecasting, and risk assessment.
                                </p>

                                {/* Capabilities Visuals */}
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-3xl mb-12">
                                    {[
                                        { icon: BarChart3, label: "Revenue Analytics", desc: "Deep dive into financial performance" },
                                        { icon: TrendingUp, label: "Smart Forecasting", desc: "Predictive modeling and trends" },
                                        { icon: Users, label: "Market Intelligence", desc: "Customer & competitor insights" }
                                    ].map((item, i) => (
                                        <div key={i} className="p-5 rounded-xl border border-gray-800/50 bg-[#0f1629] flex flex-col items-center text-center">
                                            <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center mb-4">
                                                <item.icon className="w-5 h-5 text-emerald-500" />
                                            </div>
                                            <h3 className="text-sm font-medium text-white mb-1.5">{item.label}</h3>
                                            <p className="text-xs text-gray-500">{item.desc}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="px-6 py-6">
                            <div className="max-w-3xl mx-auto space-y-6">
                                {messages.map((message) => (
                                    <ChatMessage key={message.id} message={message} onFollowupClick={handleQuerySubmit} userQuery={message.userQuery} />
                                ))}
                                <div ref={messagesEndRef} />
                            </div>
                        </div>
                    )}
                </ScrollArea>

                <div className="border-t border-gray-800/50 bg-[#0f1629] px-6 py-4">
                    <div className="max-w-3xl mx-auto">
                        <ChatInput onSubmit={handleQuerySubmit} isProcessing={isProcessing} />
                        {!hasUserMessages && (
                            <p className="text-center text-xs text-gray-600 mt-3">Ask anything about financial data, operations, forecasts, or market analysis</p>
                        )}
                    </div>
                </div>
            </div>
        </AppLayout>
    );
}
