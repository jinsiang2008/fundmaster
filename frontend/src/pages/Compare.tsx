/**
 * Fund comparison page
 */

import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Layout,
  Row,
  Col,
  Card,
  Button,
  Typography,
  Table,
  Tag,
  Space,
  Breadcrumb,
  Alert,
  Spin,
  Empty,
} from 'antd';
import {
  HomeOutlined,
  DeleteOutlined,
  PlusOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import { FundSearch, CompareRadar } from '../components';
import { useCompareFunds } from '../hooks/useFund';
import type { FundSearchResult, FundMetrics } from '../types/fund';

const { Content } = Layout;
const { Title, Paragraph } = Typography;

export function Compare() {
  const navigate = useNavigate();
  const [selectedFunds, setSelectedFunds] = useState<FundSearchResult[]>([]);
  const compareMutation = useCompareFunds();

  const handleSelectFund = useCallback((fund: FundSearchResult) => {
    if (selectedFunds.length >= 5) {
      return;
    }
    if (selectedFunds.find((f) => f.code === fund.code)) {
      return;
    }
    setSelectedFunds((prev) => [...prev, fund]);
  }, [selectedFunds]);

  const handleRemoveFund = useCallback((code: string) => {
    setSelectedFunds((prev) => prev.filter((f) => f.code !== code));
  }, []);

  const handleCompare = useCallback(() => {
    if (selectedFunds.length < 2) return;
    compareMutation.mutate({
      fund_codes: selectedFunds.map((f) => f.code),
    });
  }, [selectedFunds, compareMutation]);

  const metricsColumns = [
    {
      title: '指标',
      dataIndex: 'label',
      key: 'label',
      fixed: 'left' as const,
      width: 120,
    },
    ...selectedFunds.map((fund) => ({
      title: fund.name,
      dataIndex: fund.code,
      key: fund.code,
      width: 150,
    })),
  ];

  const getMetricsData = (funds: FundMetrics[]) => {
    const metrics = [
      { key: 'return_1m', label: '近1月收益', suffix: '%' },
      { key: 'return_3m', label: '近3月收益', suffix: '%' },
      { key: 'return_6m', label: '近6月收益', suffix: '%' },
      { key: 'return_1y', label: '近1年收益', suffix: '%' },
      { key: 'return_3y', label: '近3年收益', suffix: '%' },
      { key: 'max_drawdown', label: '最大回撤', suffix: '%' },
      { key: 'volatility', label: '年化波动率', suffix: '%' },
      { key: 'sharpe_ratio', label: '夏普比率', suffix: '' },
    ];

    return metrics.map((m) => {
      const row: Record<string, string | number | null> = {
        key: m.key,
        label: m.label,
      };
      funds.forEach((fund) => {
        const value = fund[m.key as keyof FundMetrics];
        row[fund.code] = value !== null && value !== undefined
          ? `${value}${m.suffix}`
          : '-';
      });
      return row;
    });
  };

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
            { title: '基金对比' },
          ]}
        />

        <Row gutter={[24, 24]}>
          {/* Left: Fund Selection */}
          <Col xs={24} lg={8}>
            <Card title="选择基金 (2-5只)" style={{ marginBottom: 16 }}>
              <FundSearch
                onSelect={handleSelectFund}
                placeholder="搜索添加基金..."
              />

              <div style={{ marginTop: 16 }}>
                {selectedFunds.length === 0 ? (
                  <Empty description="请添加至少2只基金进行对比" />
                ) : (
                  <Space direction="vertical" style={{ width: '100%' }}>
                    {selectedFunds.map((fund, index) => (
                      <Tag
                        key={fund.code}
                        closable
                        onClose={() => handleRemoveFund(fund.code)}
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          padding: '4px 8px',
                          width: '100%',
                        }}
                      >
                        <span>
                          {index + 1}. {fund.name}
                        </span>
                        <span style={{ color: '#999' }}>{fund.code}</span>
                      </Tag>
                    ))}
                  </Space>
                )}
              </div>

              {selectedFunds.length > 0 && selectedFunds.length < 5 && (
                <Paragraph type="secondary" style={{ marginTop: 8, marginBottom: 0 }}>
                  还可添加 {5 - selectedFunds.length} 只基金
                </Paragraph>
              )}

              <Button
                type="primary"
                icon={<ThunderboltOutlined />}
                onClick={handleCompare}
                loading={compareMutation.isPending}
                disabled={selectedFunds.length < 2}
                block
                style={{ marginTop: 16 }}
              >
                开始对比分析
              </Button>
            </Card>
          </Col>

          {/* Right: Comparison Results */}
          <Col xs={24} lg={16}>
            {compareMutation.isPending && (
              <Card>
                <div style={{ textAlign: 'center', padding: 60 }}>
                  <Spin size="large" />
                  <Paragraph style={{ marginTop: 16 }}>
                    AI 正在分析对比数据...
                  </Paragraph>
                </div>
              </Card>
            )}

            {compareMutation.isError && (
              <Alert
                type="error"
                message="对比失败"
                description={compareMutation.error?.message || '请稍后重试'}
                style={{ marginBottom: 16 }}
              />
            )}

            {compareMutation.data && (
              <>
                {/* Radar Chart */}
                <CompareRadar data={compareMutation.data} />

                {/* Metrics Table */}
                <Card title="指标对比" style={{ marginTop: 16 }}>
                  <Table
                    columns={metricsColumns}
                    dataSource={getMetricsData(compareMutation.data.funds)}
                    pagination={false}
                    scroll={{ x: 'max-content' }}
                    size="small"
                  />
                </Card>

                {/* AI Analysis */}
                {compareMutation.data.analysis && (
                  <Card title="AI 对比分析" style={{ marginTop: 16 }}>
                    <div className="markdown-content">
                      <ReactMarkdown
                        components={{
                          h1: ({ children }) => <h1 style={{ fontSize: 24, fontWeight: 600, marginTop: 24, marginBottom: 16, color: '#1890ff' }}>{children}</h1>,
                          h2: ({ children }) => <h2 style={{ fontSize: 20, fontWeight: 600, marginTop: 20, marginBottom: 12 }}>{children}</h2>,
                          h3: ({ children }) => <h3 style={{ fontSize: 16, fontWeight: 600, marginTop: 16, marginBottom: 10 }}>{children}</h3>,
                          p: ({ children }) => <p style={{ marginBottom: 16, lineHeight: 1.8 }}>{children}</p>,
                          ul: ({ children }) => <ul style={{ paddingLeft: 24, marginBottom: 16 }}>{children}</ul>,
                          li: ({ children }) => <li style={{ marginBottom: 8 }}>{children}</li>,
                          strong: ({ children }) => <strong style={{ fontWeight: 600, color: '#1890ff' }}>{children}</strong>,
                          table: ({ children }) => <table style={{ width: '100%', borderCollapse: 'collapse', margin: '16px 0' }}>{children}</table>,
                          th: ({ children }) => <th style={{ border: '1px solid #e8e8e8', padding: '10px 12px', background: '#fafafa' }}>{children}</th>,
                          td: ({ children }) => <td style={{ border: '1px solid #e8e8e8', padding: '10px 12px' }}>{children}</td>,
                        }}
                      >
                        {compareMutation.data.analysis}
                      </ReactMarkdown>
                    </div>
                    {compareMutation.data.recommendation && (
                      <div style={{ marginTop: 16 }}>
                        <Tag color="success" style={{ padding: '4px 8px' }}>
                          推荐: {compareMutation.data.recommendation}
                        </Tag>
                      </div>
                    )}
                  </Card>
                )}
              </>
            )}

            {!compareMutation.data && !compareMutation.isPending && (
              <Card>
                <Empty
                  description="选择2-5只基金后点击开始对比"
                  image={Empty.PRESENTED_IMAGE_SIMPLE}
                />
              </Card>
            )}
          </Col>
        </Row>
      </Content>
    </Layout>
  );
}

export default Compare;
