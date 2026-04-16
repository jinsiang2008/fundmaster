/**
 * Main application component
 */

import { BrowserRouter, Routes, Route, Outlet } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { Home, FundDetail, Compare, DcaCalculator, Recommend } from './pages';
import { AppHeader } from './components';

import './App.css';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function AppShell() {
  return (
    <>
      <AppHeader />
      <Outlet />
    </>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider locale={zhCN}>
        <BrowserRouter>
          <Routes>
            {/* 无 path 的布局路由：首页必须用 index，勿嵌套 path="/"，否则子路由可能无法匹配导致白屏 */}
            <Route element={<AppShell />}>
              <Route index element={<Home />} />
              <Route path="fund/:fundCode" element={<FundDetail />} />
              <Route path="compare" element={<Compare />} />
              <Route path="calculator" element={<DcaCalculator />} />
              <Route path="recommend" element={<Recommend />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </ConfigProvider>
    </QueryClientProvider>
  );
}

export default App;
