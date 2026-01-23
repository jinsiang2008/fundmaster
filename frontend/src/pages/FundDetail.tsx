/**
 * Fund detail page with analysis and chat
 */

import { useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Layout,
  Row,
  Col,
  Breadcrumb,
  Tabs,
  Button,
  Spin,
  Alert,
  message,
} from 'antd';
import { HomeOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import {
  FundCard,
  PerformanceChart,
  HoldingsTable,
  AnalysisReport,
  ChatPanel,
} from '../components';
import {
  useFundInfo,
  useFundNAVHistory,
  useFundHoldings,
  useFundMetrics,
} from '../hooks/useFund';
import { useChat } from '../hooks/useChat';
import { apiClient } from '../api/client';
import type { UserProfile } from '../types/chat';

const { Content } = Layout;

export function FundDetail() {
  const { fundCode } = useParams<{ fundCode: string }>();
  const navigate = useNavigate();
  const [navPeriod, setNavPeriod] = useState('1y');
  const [activeTab, setActiveTab] = useState('overview');
  const [analysisContent, setAnalysisContent] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState<Error | null>(null);
  const [userProfile, setUserProfile] = useState<UserProfile | undefined>();

  // Data fetching
  const { data: fundInfo, isLoading: infoLoading, error: infoError } = useFundInfo(fundCode || '');
  const { data: navHistory, isLoading: navLoading } = useFundNAVHistory(fundCode || '', navPeriod);
  const { data: holdings, isLoading: holdingsLoading } = useFundHoldings(fundCode || '');
  const { data: metrics } = useFundMetrics(fundCode || '');

  // Chat hook
  const {
    messages,
    streamingContent,
    isStreaming,
    sendMessageStream,
  } = useChat(fundCode || '');

  // Generate AI analysis with streaming
  const handleGenerateAnalysis = useCallback(async () => {
    if (!fundCode) return;

    setIsAnalyzing(true);
    setAnalysisContent('');
    setAnalysisError(null);

    try {
      await apiClient.getFundAnalysisStream(fundCode, (chunk) => {
        setAnalysisContent((prev) => prev + chunk);
      });
    } catch (error) {
      console.error('Analysis error:', error);
      setAnalysisError(error as Error);
      message.error('分析失败，请稍后重试');
    } finally {
      setIsAnalyzing(false);
    }
  }, [fundCode]);

  // Handle chat message
  const handleSendMessage = useCallback(
    (msg: string, profile?: UserProfile) => {
      sendMessageStream(msg, profile);
    },
    [sendMessageStream]
  );

  // Loading state
  if (infoLoading) {
    return (
      <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
        <Content style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <Spin size="large" tip="加载中..." />
        </Content>
      </Layout>
    );
  }

  // Error state
  if (infoError || !fundInfo) {
    return (
      <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
        <Content style={{ padding: 24 }}>
          <Alert
            type="error"
            message="加载失败"
            description={`无法加载基金信息: ${fundCode}`}
            action={
              <Button onClick={() => navigate('/')}>返回首页</Button>
            }
          />
        </Content>
      </Layout>
    );
  }

  const tabItems = [
    {
      key: 'overview',
      label: '概览',
      children: (
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <PerformanceChart
              data={navHistory}
              loading={navLoading}
              period={navPeriod}
              onPeriodChange={setNavPeriod}
            />
          </Col>
          <Col span={24}>
            <HoldingsTable data={holdings} loading={holdingsLoading} />
          </Col>
        </Row>
      ),
    },
    {
      key: 'analysis',
      label: 'AI 分析',
      children: (
        <AnalysisReport
          streamingContent={analysisContent}
          isStreaming={isAnalyzing}
          onRefresh={handleGenerateAnalysis}
          error={analysisError}
        />
      ),
    },
    {
      key: 'chat',
      label: '智能问答',
      children: (
        <ChatPanel
          messages={messages}
          streamingContent={streamingContent}
          isStreaming={isStreaming}
          onSendMessage={handleSendMessage}
          userProfile={userProfile}
          onProfileChange={setUserProfile}
        />
      ),
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Content style={{ padding: 24 }}>
        {/* Breadcrumb */}
        <Breadcrumb
          style={{ marginBottom: 16 }}
          items={[
            {
              title: (
                <span onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
                  <HomeOutlined /> 首页
                </span>
              ),
            },
            { title: fundInfo.name },
          ]}
        />

        {/* Back button */}
        <Button
          type="text"
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate(-1)}
          style={{ marginBottom: 16 }}
        >
          返回
        </Button>

        <Row gutter={[24, 24]}>
          {/* Left: Fund Info & Tabs */}
          <Col xs={24} lg={16}>
            <FundCard fund={fundInfo} metrics={metrics} showDetails />

            <Tabs
              activeKey={activeTab}
              onChange={setActiveTab}
              items={tabItems}
              style={{ marginTop: 16 }}
            />
          </Col>

          {/* Right: Quick Chat */}
          <Col xs={24} lg={8}>
            {activeTab !== 'chat' && (
              <ChatPanel
                messages={messages}
                streamingContent={streamingContent}
                isStreaming={isStreaming}
                onSendMessage={handleSendMessage}
                userProfile={userProfile}
                onProfileChange={setUserProfile}
              />
            )}
          </Col>
        </Row>
      </Content>
    </Layout>
  );
}

export default FundDetail;
