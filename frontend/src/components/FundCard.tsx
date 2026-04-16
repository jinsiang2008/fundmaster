/**
 * Fund summary card component
 */

import type { CSSProperties } from 'react';
import {
  Card,
  Typography,
  Tag,
  Statistic,
  Row,
  Col,
  Tooltip,
  Space,
  Divider,
  Descriptions,
  Alert,
} from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined, InfoCircleOutlined } from '@ant-design/icons';
import type { FundBasicInfo, FundMetrics } from '../types/fund';

const { Title, Text, Paragraph } = Typography;

/** 卡片内数字指标统一字号，避免 Statistic 默认过大、与正文脱节 */
const STAT_VALUE_FONT_SIZE = 20;
const STAT_TITLE_STYLE: CSSProperties = {
  fontSize: 13,
  color: 'rgba(0, 0, 0, 0.45)',
};
const FEE_SECTION_LABEL: CSSProperties = {
  fontSize: 13,
  color: 'rgba(0, 0, 0, 0.45)',
  display: 'block',
  marginBottom: 6,
};
const FEE_PRIMARY_VALUE: CSSProperties = {
  fontSize: 20,
  fontWeight: 600,
  color: '#cf1322',
  lineHeight: 1.3,
};
const BODY_TEXT: CSSProperties = {
  fontSize: 14,
  lineHeight: 1.65,
};
const CAPTION_TEXT: CSSProperties = {
  fontSize: 13,
  lineHeight: 1.6,
  color: 'rgba(0, 0, 0, 0.55)',
};

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
          {metrics?.risk_labels && metrics.risk_labels.length > 0 && (
            <div style={{ marginTop: 10 }}>
              <Space wrap size={[4, 4]}>
                {metrics.risk_labels.map((label) => (
                  <Tag key={label} color="gold" style={{ marginInlineEnd: 0 }}>
                    {label}
                  </Tag>
                ))}
              </Space>
            </div>
          )}
        </Col>

        {fund.nav && (
          <Col>
            <Statistic
              title={<span style={STAT_TITLE_STYLE}>最新净值</span>}
              value={fund.nav}
              precision={4}
              valueStyle={{ fontSize: STAT_VALUE_FONT_SIZE }}
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
              title={<span style={STAT_TITLE_STYLE}>近1年收益</span>}
              value={metrics.return_1y}
              precision={2}
              suffix="%"
              valueStyle={{
                fontSize: STAT_VALUE_FONT_SIZE,
                color: getReturnColor(metrics.return_1y),
              }}
              prefix={getReturnIcon(metrics.return_1y)}
            />
          </Col>
        )}
      </Row>

      {showDetails && (
        <>
          <Row gutter={16} style={{ marginTop: 16 }}>
            {fund.aum && (
              <Col xs={12} sm={6}>
                <Text type="secondary" style={STAT_TITLE_STYLE}>
                  规模
                </Text>
                <br />
                <Text style={BODY_TEXT}>{fund.aum.toFixed(2)}亿</Text>
              </Col>
            )}
            {fund.manager && (
              <Col xs={12} sm={6}>
                <Text type="secondary" style={STAT_TITLE_STYLE}>
                  基金经理
                </Text>
                <br />
                <Text style={BODY_TEXT}>{fund.manager}</Text>
              </Col>
            )}
            {metrics?.max_drawdown !== null && metrics?.max_drawdown !== undefined && (
              <Col xs={12} sm={6}>
                <Statistic
                  title={<span style={STAT_TITLE_STYLE}>最大回撤</span>}
                  value={metrics.max_drawdown}
                  precision={2}
                  suffix="%"
                  valueStyle={{ color: '#ff4d4f', fontSize: STAT_VALUE_FONT_SIZE }}
                />
              </Col>
            )}
          </Row>

          <Divider plain style={{ marginTop: 20, marginBottom: 12 }}>
            <Text type="secondary" style={{ fontSize: 13 }}>
              持有成本与费率
            </Text>
          </Divider>

          {fund.annual_operating_fee_pct != null && (
            <Row style={{ marginBottom: 12 }}>
              <Col span={24}>
                <span style={FEE_SECTION_LABEL}>年度运作费率合计（约）</span>
                <div style={FEE_PRIMARY_VALUE}>
                  {fund.annual_operating_fee_pct}% / 年
                </div>
                <Text type="secondary" style={{ ...CAPTION_TEXT, display: 'block', marginTop: 8 }}>
                  管理费 + 托管费 + 销售服务费（若有），从基金资产每日计提，已反映在净值中。
                </Text>
              </Col>
            </Row>
          )}

          {(fund.management_fee != null ||
            fund.custody_fee != null ||
            fund.sales_service_fee != null ||
            fund.purchase_fee != null ||
            fund.max_subscription_fee_pct != null ||
            fund.redemption_fee != null) && (
            <Descriptions
              size="middle"
              bordered
              column={{ xs: 1, sm: 2 }}
              style={{ marginBottom: 12 }}
              labelStyle={{
                fontSize: 13,
                color: 'rgba(0, 0, 0, 0.55)',
                width: 148,
              }}
              contentStyle={{ fontSize: 14, lineHeight: 1.6 }}
            >
              {fund.management_fee != null && (
                <Descriptions.Item label="管理费率">{fund.management_fee}% / 年</Descriptions.Item>
              )}
              {fund.custody_fee != null && (
                <Descriptions.Item label="托管费率">{fund.custody_fee}% / 年</Descriptions.Item>
              )}
              {fund.sales_service_fee != null && (
                <Descriptions.Item label="销售服务费">{fund.sales_service_fee}% / 年</Descriptions.Item>
              )}
              {fund.max_subscription_fee_pct != null && (
                <Descriptions.Item label="认购费率（上限参考）">
                  {fund.max_subscription_fee_pct}%（募集期）
                </Descriptions.Item>
              )}
              {fund.purchase_fee != null && (
                <Descriptions.Item label="申购费率（参考）">{fund.purchase_fee}%</Descriptions.Item>
              )}
              {fund.redemption_fee != null && (
                <Descriptions.Item label="赎回费率（分档最低档示意）">{fund.redemption_fee}%</Descriptions.Item>
              )}
            </Descriptions>
          )}

          {fund.lockup_note && (
            <Alert
              type="warning"
              showIcon
              style={{ marginBottom: 12 }}
              styles={{ title: { fontSize: 14, lineHeight: 1.65 } }}
              title={fund.lockup_note}
            />
          )}

          {fund.redemption_fee_detail && (
            <div style={{ marginBottom: 12 }}>
              <Text type="secondary" style={STAT_TITLE_STYLE}>
                赎回费分档（摘要）
              </Text>
              <Paragraph style={{ marginTop: 6, marginBottom: 0, ...BODY_TEXT }}>
                {fund.redemption_fee_detail}
              </Paragraph>
            </div>
          )}

          {fund.holding_cost_summary && (
            <Alert
              type="info"
              showIcon
              title={<span style={{ fontSize: 14, fontWeight: 600 }}>综合说明</span>}
              styles={{
                title: { fontSize: 14, fontWeight: 600 },
                description: { fontSize: 14, lineHeight: 1.65 },
              }}
              description={
                <Paragraph style={{ marginBottom: 0, whiteSpace: 'pre-wrap', ...BODY_TEXT }}>
                  {fund.holding_cost_summary}
                </Paragraph>
              }
            />
          )}

          {!fund.annual_operating_fee_pct &&
            !fund.holding_cost_summary &&
            !fund.management_fee &&
            !fund.redemption_fee_detail && (
              <Text type="secondary">暂无费率明细，请至基金公司官网或销售机构查询。</Text>
            )}
        </>
      )}
    </Card>
  );
}

export default FundCard;
