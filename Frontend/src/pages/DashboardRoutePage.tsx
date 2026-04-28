import { useNavigate } from 'react-router-dom';
import { DashboardPage } from '../components/DashboardPage';

export default function DashboardRoutePage() {
    const navigate = useNavigate();
    return (
        <DashboardPage
            onCardQuery={(q) => navigate('/chat', { state: { prefillQuery: q } })}
            onNavigateToChat={() => navigate('/chat')}
            onBack={() => navigate(-1)} // Added
        />
    );
}
