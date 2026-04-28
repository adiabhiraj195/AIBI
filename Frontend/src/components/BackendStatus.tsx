import { useEffect, useState } from 'react';
import { Wifi, WifiOff, AlertCircle } from 'lucide-react';
import { checkAPIHealth } from '../services/api';
import { Badge } from './ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from './ui/tooltip';

export function BackendStatus() {
  const [isConnected, setIsConnected] = useState<boolean | null>(null);
  const [lastCheck, setLastCheck] = useState<Date | null>(null);

  const checkConnection = async () => {
    try {
      const healthy = await checkAPIHealth();
      setIsConnected(healthy);
      setLastCheck(new Date());
    } catch (error) {
      setIsConnected(false);
      setLastCheck(new Date());
    }
  };

  useEffect(() => {
    // Check immediately
    checkConnection();

    // Check every 30 seconds
    const interval = setInterval(checkConnection, 30000);

    return () => clearInterval(interval);
  }, []);

  if (isConnected === null) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <div>
              <Badge variant="outline" className="gap-2 border-yellow-500/30 bg-yellow-500/10 text-yellow-400">
                <AlertCircle className="h-3 w-3" />
                Checking...
              </Badge>
            </div>
          </TooltipTrigger>
          <TooltipContent>
            <p>Connecting to backend...</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div>
            {isConnected ? (
              <Badge variant="outline" className="gap-2 border-green-500/30 bg-green-500/10 text-green-400">
                <Wifi className="h-3 w-3" />
                Connected
              </Badge>
            ) : (
              <Badge variant="outline" className="gap-2 border-orange-500/30 bg-orange-500/10 text-orange-400">
                <WifiOff className="h-3 w-3" />
                Offline Mode
              </Badge>
            )}
          </div>
        </TooltipTrigger>
        <TooltipContent>
          {isConnected ? (
            <div className="space-y-1">
              <p className="text-green-400">Backend connected</p>
              <p className="text-xs text-gray-400">
                http://localhost:8000
              </p>
              {lastCheck && (
                <p className="text-xs text-gray-500">
                  Last checked: {lastCheck.toLocaleTimeString()}
                </p>
              )}
            </div>
          ) : (
            <div className="space-y-1">
              <p className="text-orange-400">Backend unavailable</p>
              <p className="text-xs text-gray-400">
                Backend service is not reachable
              </p>
              {lastCheck && (
                <p className="text-xs text-gray-500">
                  Last attempt: {lastCheck.toLocaleTimeString()}
                </p>
              )}
            </div>
          )}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
