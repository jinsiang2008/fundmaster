/**
 * Fund summary card component
 */

import { Card, Typography, Tag, Statistic, Row, Col, Tooltip } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined, InfoCircleOutlined } from '@ant-design/icons';
import type { FundBasicInfo, FundMetrics } from '../types/fund';

const { Title, Text } = Typography;

interface FundCardProps {
  fund: FundBasicInfo;
  metrics?: FundMetrics;
  onClick?: () => void;
  showDetails?: boolean;
}

export function FundCard({ fund, metrics, onClick, showDetails = true }: FundCardProps) {
  const getReturnColor = (value: number | null) => {
    if (value === null) return undefined;
    return value >= 0 ? '#52c41a' : '#ff4d4f';
  };

  const getReturnIcon = (value: number | null) => {
    if (value === null) return null;
    return value >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />;
  };

  return (
    <Card
      hoverable={!!onClick}
      onClick={onClick}
      style={{ marginBottom: 16 }}
    >
      <Row gutter={16} align="middle">
        <Col flex="auto">
          <Title level={4} style={{ marginBottom: 4 }}>
            {fund.name}
          </Title>
          <Text type="secondary">{fund.code}</Text>
          <Tag color="blue" style={{ marginLeft: 8 }}>
            {fund.type || '未知类型'}
          </Tag>
        </Col>

        {fund.nav && (
          <Col>
            <Statistic
              title="最新净值"
              value={fund.nav}
              precision={4}
              suffix={
                <Tooltip title={`净值日期: ${fund.nav_date || '-'}`}>
                  <InfoCircleOutlined style={{ fontSize: 12, marginLeft: 4 }} />
                </Tooltip>
              }
            />
          </Col>
        )}

        {metrics?.return_1y !== null && metrics?.return_1y !== undefined && (
          <Col>
            <Statistic
              title="近1年收益"
              value={metrics.return_1y}
              precision={2}
              suffix="%"
              valueStyle={{ color: getReturnColor(metrics.return_1y) }}
              prefix={getReturnIcon(metrics.return_1y)}
            />
          </Col>
        )}
      </Row>

      {showDetails && (
        <Row gutter={16} style={{ marginTop: 16 }}>
          {fund.aum && (
            <Col span={6}>
              <Text type="secondary">规模</Text>
              <br />
              <Text>{fund.aum.toFixed(2)}亿</Text>
            </Col>
          )}
          {fund.manager && (
            <Col span={6}>
              <Text type="secondary">基金经理</Text>
              <br />
              <Text>{fund.manager}</Text>
            </Col>
          )}
          {fund.management_fee && (
            <Col span={6}>
              <Text type="secondary">管理费</Text>
              <br />
              <Text>{fund.management_fee}%</Text>
            </Col>
          )}
          {metrics?.max_drawdown !== null && metrics?.max_drawdown !== undefined && (
            <Col span={6}>
              <Text type="secondary">最大回撤</Text>
              <br />
              <Text style={{ color: '#ff4d4f' }}>{metrics.max_drawdown}%</Text>
            </Col>
          )}
        </Row>
      )}
    </Card>
  );
}

export default FundCard;
