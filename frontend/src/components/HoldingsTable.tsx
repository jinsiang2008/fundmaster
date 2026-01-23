/**
 * Fund holdings table component
 */

import { Card, Table, Progress, Empty } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import type { FundHoldings, FundHolding } from '../types/fund';

interface HoldingsTableProps {
  data?: FundHoldings;
  loading?: boolean;
}

const columns: ColumnsType<FundHolding> = [
  {
    title: '排名',
    key: 'rank',
    width: 60,
    render: (_, __, index) => index + 1,
  },
  {
    title: '证券名称',
    dataIndex: 'name',
    key: 'name',
  },
  {
    title: '证券代码',
    dataIndex: 'code',
    key: 'code',
    render: (code) => code || '-',
  },
  {
    title: '持仓占比',
    dataIndex: 'ratio',
    key: 'ratio',
    width: 200,
    render: (ratio: number) => (
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <Progress
          percent={ratio}
          size="small"
          showInfo={false}
          style={{ flex: 1, maxWidth: 100 }}
        />
        <span>{ratio.toFixed(2)}%</span>
      </div>
    ),
  },
  {
    title: '持仓市值(万)',
    dataIndex: 'market_value',
    key: 'market_value',
    render: (value) => (value ? value.toFixed(2) : '-'),
  },
];

export function HoldingsTable({ data, loading = false }: HoldingsTableProps) {
  const hasStockHoldings = data?.stock_holdings && data.stock_holdings.length > 0;
  const hasBondHoldings = data?.bond_holdings && data.bond_holdings.length > 0;

  return (
    <Card title="前十大持仓" extra={data?.report_date ? `报告期: ${data.report_date}` : null}>
      {hasStockHoldings ? (
        <>
          <div style={{ marginBottom: 8, fontWeight: 600 }}>股票持仓</div>
          <Table
            columns={columns}
            dataSource={data.stock_holdings}
            rowKey="name"
            loading={loading}
            pagination={false}
            size="small"
          />
        </>
      ) : hasBondHoldings ? (
        <>
          <div style={{ marginBottom: 8, fontWeight: 600 }}>债券持仓</div>
          <Table
            columns={columns}
            dataSource={data.bond_holdings}
            rowKey="name"
            loading={loading}
            pagination={false}
            size="small"
          />
        </>
      ) : (
        <Empty 
          description={
            <span>
              暂无持仓数据
              <br />
              <small style={{ color: '#999' }}>
                注：部分债券基金的持仓数据可能未公开或更新延迟
              </small>
            </span>
          } 
        />
      )}
    </Card>
  );
}

export default HoldingsTable;
