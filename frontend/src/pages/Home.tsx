/**
 * Home page with fund search, filters, watchlist & recent visits
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layout, Typography, Row, Col, Card, Space, Tag, Select, Empty, Button, Spin } from 'antd';
import {
  SearchOutlined,
  RiseOutlined,
  FundOutlined,
  RobotOutlined,
  SwapOutlined,
  StarOutlined,
  HistoryOutlined,
  CalculatorOutlined,
  BulbOutlined,
} from '@ant-design/icons';
import { FundSearch } from '../components';
import type { FundSearchResult } from '../types/fund';
import { useWatchlist, useRecentFunds } from '../hooks/useLocalFundLists';
import { useFeaturedFunds } from '../hooks/useFund';

const { Content } = Layout;
const { Title, Paragraph, Text } = Typography;

const CATEGORY_OPTIONS = [
  { value: 'all', label: '全部类型' },
  { value: 'stock', label: '股票型' },
  { value: 'mixed', label: '混合型' },
  { value: 'bond', label: '债券型' },
  { value: 'index', label: '指数/ETF' },
  { value: 'money', label: '货币型' },
  { value: 'qdii', label: 'QDII' },
];

export function Home() {
  const navigate = useNavigate();
  const [category, setCategory] = useState('all');
  const { watchlist, toggleWatchlist } = useWatchlist();
  const { recentFunds } = useRecentFunds();
  const { data: featuredFunds, isLoading: featuredLoading } = useFeaturedFunds(8);

  const handleSelectFund = (fund: FundSearchResult) => {
    navigate(`/fund/${fund.code}`);
  };

  return (
    <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Content style={{ padding: '40px 24px 56px' }}>
        <Row justify="center">
          <Col xs={24} sm={22} md={18} lg={14} xl={12}>
            <div style={{ textAlign: 'center', marginBottom: 40 }}>
              <Title level={1} style={{ marginBottom: 8 }}>
                <FundOutlined style={{ marginRight: 12, color: '#1890ff' }} />
                FundMaster
              </Title>
              <Paragraph type="secondary" style={{ fontSize: 16, marginBottom: 0 }}>
                AI 驱动的中国公募基金分析助手
              </Paragraph>
            </div>

            <Card style={{ marginBottom: 20 }} styles={{ body: { paddingBottom: 12 } }}>
              <Row gutter={[12, 12]} align="middle">
                <Col xs={24} sm={7} md={6}>
                  <Text type="secondary" style={{ display: 'block', marginBottom: 6 }}>
                    类型筛选
                  </Text>
                  <Select
                    value={category}
                    onChange={setCategory}
                    options={CATEGORY_OPTIONS}
                    style={{ width: '100%' }}
                    popupMatchSelectWidth={false}
                  />
                </Col>
                <Col xs={24} sm={17} md={18}>
                  <Text type="secondary" style={{ display: 'block', marginBottom: 6 }}>
                    搜索基金
                  </Text>
                  <FundSearch onSelect={handleSelectFund} category={category} />
                </Col>
              </Row>
              <Paragraph type="secondary" style={{ marginTop: 12, marginBottom: 0, fontSize: 13 }}>
                筛选在搜索结果上生效；数据来自第三方，类型字段可能不完整。
              </Paragraph>
            </Card>

            <Row gutter={16}>
              <Col span={8}>
                <Card hoverable style={{ textAlign: 'center' }}>
                  <SearchOutlined style={{ fontSize: 32, color: '#1890ff', marginBottom: 12 }} />
                  <Title level={5}>智能搜索</Title>
                  <Text type="secondary">快速找到目标基金</Text>
                </Card>
              </Col>
              <Col span={8}>
                <Card hoverable style={{ textAlign: 'center' }}>
                  <RobotOutlined style={{ fontSize: 32, color: '#52c41a', marginBottom: 12 }} />
                  <Title level={5}>AI 分析</Title>
                  <Text type="secondary">专业深度分析报告</Text>
                </Card>
              </Col>
              <Col span={8}>
                <Card
                  hoverable
                  style={{ textAlign: 'center' }}
                  onClick={() => navigate('/compare')}
                >
                  <SwapOutlined style={{ fontSize: 32, color: '#faad14', marginBottom: 12 }} />
                  <Title level={5}>多基对比</Title>
                  <Text type="secondary">智能对比分析</Text>
                </Card>
              </Col>
            </Row>

            <Card
              title={
                <span>
                  <StarOutlined style={{ marginRight: 8, color: '#faad14' }} />
                  自选
                </span>
              }
              style={{ marginTop: 20 }}
            >
              {watchlist.length === 0 ? (
                <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无自选，在基金详情页点击「加自选」即可添加" />
              ) : (
                <Space wrap size={[8, 8]}>
                  {watchlist.map((fund) => (
                    <Tag key={fund.code} style={{ padding: '4px 10px' }}>
                      <span
                        role="button"
                        tabIndex={0}
                        style={{ cursor: 'pointer' }}
                        onClick={() => handleSelectFund(fund)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' || e.key === ' ') handleSelectFund(fund);
                        }}
                      >
                        {fund.name}
                      </span>
                      <Text
                        type="secondary"
                        aria-label="移除自选"
                        style={{ marginLeft: 8, cursor: 'pointer', userSelect: 'none' }}
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleWatchlist(fund);
                        }}
                      >
                        ×
                      </Text>
                    </Tag>
                  ))}
                </Space>
              )}
            </Card>

            <Card
              title={
                <span>
                  <HistoryOutlined style={{ marginRight: 8, color: '#1677ff' }} />
                  最近浏览
                </span>
              }
              style={{ marginTop: 16 }}
            >
              {recentFunds.length === 0 ? (
                <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="打开过基金详情后将显示在这里" />
              ) : (
                <Space wrap>
                  {recentFunds.map((fund) => (
                    <Tag
                      key={fund.code}
                      style={{ cursor: 'pointer', padding: '4px 10px' }}
                      onClick={() => handleSelectFund(fund)}
                    >
                      {fund.name}
                    </Tag>
                  ))}
                </Space>
              )}
            </Card>

            <Card style={{ marginTop: 16 }}>
              <Space direction="vertical" size="small" style={{ width: '100%' }}>
                <Space align="center" wrap>
                  <BulbOutlined style={{ fontSize: 22, color: '#faad14' }} />
                  <Text>不确定买哪类基金？按风险与期限做个筛选</Text>
                  <Button type="link" onClick={() => navigate('/recommend')} style={{ paddingLeft: 4 }}>
                    智能选基
                  </Button>
                </Space>
                <Space align="center" wrap>
                  <CalculatorOutlined style={{ fontSize: 22, color: '#1677ff' }} />
                  <Text>需要测算定投收益？</Text>
                  <Button type="link" onClick={() => navigate('/calculator')} style={{ paddingLeft: 4 }}>
                    打开定投计算器
                  </Button>
                </Space>
              </Space>
            </Card>

            <Card
              title="今日推荐"
              style={{ marginTop: 16 }}
              extra={<Text type="secondary" style={{ fontSize: 12 }}>每日更新</Text>}
            >
              <Paragraph type="secondary" style={{ marginTop: 0, marginBottom: 12, fontSize: 13 }}>
                从全市场基金库中按日期轮换抽样展示，并非收益排行或官方热销榜；仅作快速入口。
              </Paragraph>
              {featuredLoading ? (
                <div style={{ textAlign: 'center', padding: 16 }}>
                  <Spin />
                </div>
              ) : (
                <Space wrap>
                  {(featuredFunds ?? []).map((fund: FundSearchResult) => (
                    <Tag
                      key={fund.code}
                      color="blue"
                      style={{ cursor: 'pointer', padding: '4px 8px', maxWidth: '100%' }}
                      title={fund.type ? `${fund.name}（${fund.code}）· ${fund.type}` : `${fund.name}（${fund.code}）`}
                      onClick={() => navigate(`/fund/${fund.code}`)}
                    >
                      <RiseOutlined style={{ marginRight: 4 }} />
                      {fund.name}
                    </Tag>
                  ))}
                </Space>
              )}
            </Card>
          </Col>
        </Row>
      </Content>
    </Layout>
  );
}

export default Home;
