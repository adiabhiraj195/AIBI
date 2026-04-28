import { useNavigate } from 'react-router-dom';
import { WelcomePage } from '../components/WelcomePage';

export default function WelcomeRoutePage() {
    const navigate = useNavigate();
    return <WelcomePage onGetStarted={() => navigate('/dashboard')} />;
}
