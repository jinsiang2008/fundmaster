/**
 * Home page with fund search
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layout, Typography, Row, Col, Card, Space, Tag } from 'antd';
import {
  SearchOutlined,
  RiseOutlined,
  FundOutlined,
  RobotOutlined,
  SwapOutlined,
} from '@ant-design/icons';
import { FundSearch } from '../components';
import type { FundSearchResult } from '../types/fund';

const { Content } = Layout;
const { Title, Paragraph, Text } = Typography;

export function Home() {
  const navigate = useNavigate();
  const [recentSearches] = useState<FundSearchResult[]>([]);

  const handleSelectFund = (fund: FundSearchResult) => {
    navigate(`/fund/${fund.code}`);
  };

  return (
    <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Content style={{ padding: '60px 24px' }}>
        <Row justify="center">
          <Col xs={24} sm={20} md={16} lg={12} xl={10}>
            {/* Header */}
            <div style={{ textAlign: 'center', marginBottom: 48 }}>
              <Title level={1} style={{ marginBottom: 8 }}>
                <FundOutlined style={{ marginRight: 12, color: '#1890ff' }} />
                FundMaster
              </Title>
              <Paragraph type="secondary" style={{ fontSize: 16 }}>
                AI 驱动的中国公募基金分析助手
              </Paragraph>
            </div>

            {/* Search Box */}
            <Card style={{ marginBottom: 24 }}>
              <FundSearch onSelect={handleSelectFund} />
            </Card>

            {/* Features */}
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

            {/* Recent Searches */}
            {recentSearches.length > 0 && (
              <Card title="最近搜索" style={{ marginTop: 24 }}>
                <Space wrap>
                  {recentSearches.map((fund) => (
                    <Tag
                      key={fund.code}
                      style={{ cursor: 'pointer' }}
                      onClick={() => handleSelectFund(fund)}
                    >
                      {fund.name}
                    </Tag>
                  ))}
                </Space>
              </Card>
            )}

            {/* Popular Funds */}
            <Card title="热门基金" style={{ marginTop: 24 }}>
              <Space wrap>
                {[
                  { code: '110011', name: '易方达中小盘混合' },
                  { code: '000961', name: '天弘沪深300ETF联接A' },
                  { code: '005827', name: '易方达蓝筹精选混合' },
                  { code: '161725', name: '招商中证白酒指数' },
                  { code: '007119', name: '景顺长城绩优成长混合' },
                ].map((fund) => (
                  <Tag
                    key={fund.code}
                    color="blue"
                    style={{ cursor: 'pointer', padding: '4px 8px' }}
                    onClick={() => navigate(`/fund/${fund.code}`)}
                  >
                    <RiseOutlined style={{ marginRight: 4 }} />
                    {fund.name}
                  </Tag>
                ))}
              </Space>
            </Card>
          </Col>
        </Row>
      </Content>
    </Layout>
  );
}

export default Home;
