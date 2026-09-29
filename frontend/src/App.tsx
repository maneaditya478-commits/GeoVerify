import { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Navbar } from './components/Navbar';
import { VerifyPage } from './pages/VerifyPage';
import { DocumentVerifyPage } from './pages/DocumentVerifyPage';
import { MapExplorerPage } from './pages/MapExplorerPage';
import { HistoryPage } from './pages/HistoryPage';
import { DocsPage } from './pages/DocsPage';
import { AboutPage } from './pages/AboutPage';
import { VerificationRequest, VerificationResponse } from './types';
import { api } from './services/api';

const queryClient = new QueryClient();

function MainApp() {
  const [activeTab, setActiveTab] = useState<string>('verify');
  const [currentResult, setCurrentResult] = useState<VerificationResponse | null>(null);
  const [history, setHistory] = useState<VerificationResponse[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [backendHealthy, setBackendHealthy] = useState<boolean>(true);

  // Check health on mount
  useEffect(() => {
    api
      .getHealth()
      .then(() => setBackendHealthy(true))
      .catch(() => setBackendHealthy(false));
  }, []);

  // Run initial default verification on load
  useEffect(() => {
    handleVerify({
      address: 'Kharadi, Pune, Maharashtra 411014',
      radius_km: 5.0,
      include_geojson: true,
    });
  }, []);

  const handleVerify = async (req: VerificationRequest) => {
    setIsLoading(true);
    try {
      const res = await api.verifyAddress(req);
      setCurrentResult(res);
      setHistory((prev) => [res, ...prev.filter((p) => p.verification_id !== res.verification_id)]);
      setBackendHealthy(true);
    } catch (err: any) {
      console.error('Verification error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectHistoryResult = (item: VerificationResponse) => {
    setCurrentResult(item);
    setActiveTab('verify');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        backendHealthy={backendHealthy}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        {activeTab === 'verify' && (
          <VerifyPage
            result={currentResult}
            onVerify={handleVerify}
            isLoading={isLoading}
          />
        )}
        {activeTab === 'document' && <DocumentVerifyPage />}
        {activeTab === 'map' && <MapExplorerPage />}
        {activeTab === 'history' && (
          <HistoryPage
            history={history}
            onSelectResult={handleSelectHistoryResult}
          />
        )}
        {activeTab === 'docs' && <DocsPage />}
        {activeTab === 'about' && <AboutPage />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/60 py-6 text-center text-xs font-mono text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>GeoVerify India • Production-Quality Geospatial Verification System</span>
          <span>Open Source under MIT License</span>
        </div>
      </footer>
    </div>
  );
}

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <MainApp />
    </QueryClientProvider>
  );
}

export default App;
