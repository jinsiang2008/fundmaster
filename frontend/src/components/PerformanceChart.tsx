/**
 * Fund performance line chart using ECharts
 */

import { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import { Card, Segmented, Spin } from 'antd';
import type { FundNAVHistory } from '../types/fund';

interface PerformanceChartProps {
  data?: FundNAVHistory;
  loading?: boolean;
  period: string;
  onPeriodChange: (period: string) => void;
}

const PERIOD_OPTIONS = [
  { label: '1月', value: '1m' },
  { label: '3月', value: '3m' },
  { label: '6月', value: '6m' },
  { label: '1年', value: '1y' },
  { label: '3年', value: '3y' },
  { label: '全部', value: 'max' },
];

export function PerformanceChart({
  data,
  loading = false,
  period,
  onPeriodChange,
}: PerformanceChartProps) {
  const chartOption = useMemo(() => {
    if (!data?.data?.length) {
      return {};
    }

    const dates = data.data.map((d) => d.date);
    const navValues = data.data.map((d) => d.nav);

    // Calculate cumulative returns for better visualization
    const baseNav = navValues[0];
    const returns = navValues.map((nav) => ((nav / baseNav - 1) * 100).toFixed(2));

    return {
      title: {
        text: `${data.name} 累计收益走势`,
        left: 'center',
        textStyle: {
          fontSize: 16,
        },
      },
      tooltip: {
        trigger: 'axis',
        formatter: (params: { name: string; value: string; dataIndex: number }[]) => {
          const point = params[0];
          const originalNav = navValues[point.dataIndex];
          return `
            ${point.name}<br/>
            累计收益: <b>${point.value}%</b><br/>
            单位净值: ${originalNav.toFixed(4)}
          `;
        },
      },
      xAxis: {
        type: 'category',
        data: dates,
        axisLabel: {
          formatter: (value: string) => {
            const date = new Date(value);
            return `${date.getMonth() + 1}/${date.getDate()}`;
          },
          interval: 'auto',
        },
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          formatter: '{value}%',
        },
      },
      series: [
        {
          name: '累计收益',
          type: 'line',
          data: returns,
          smooth: true,
          showSymbol: false,
          lineStyle: {
            width: 2,
          },
          areaStyle: {
            opacity: 0.1,
          },
          itemStyle: {
            color: '#1890ff',
          },
        },
      ],
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true,
      },
    };
  }, [data]);

  return (
    <Card
      title="净值走势"
      extra={
        <Segmented
          options={PERIOD_OPTIONS}
          value={period}
          onChange={(value) => onPeriodChange(value as string)}
        />
      }
    >
      {loading ? (
        <div style={{ textAlign: 'center', padding: 60 }}>
          <Spin size="large" />
        </div>
      ) : data?.data?.length ? (
        <ReactECharts option={chartOption} style={{ height: 400 }} />
      ) : (
        <div style={{ textAlign: 'center', padding: 60, color: '#999' }}>
          暂无数据
        </div>
      )}
    </Card>
  );
}

export default PerformanceChart;
