/**
 * Radar chart for fund comparison
 */

import { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import { Card, Empty } from 'antd';
import type { FundCompareResult } from '../types/fund';

interface CompareRadarProps {
  data?: FundCompareResult;
  loading?: boolean;
}

const COLORS = ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1'];

export function CompareRadar({ data, loading = false }: CompareRadarProps) {
  const chartOption = useMemo(() => {
    if (!data?.radar_data?.dimensions?.length) {
      return {};
    }

    const { dimensions, series } = data.radar_data;

    return {
      title: {
        text: '基金综合评分对比',
        left: 'center',
      },
      tooltip: {
        trigger: 'item',
      },
      legend: {
        data: series.map((s) => s.name),
        bottom: 0,
      },
      radar: {
        indicator: dimensions.map((name) => ({
          name,
          max: 100,
        })),
        center: ['50%', '55%'],
        radius: '65%',
      },
      series: [
        {
          type: 'radar',
          data: series.map((s, index) => ({
            name: s.name,
            value: s.values,
            itemStyle: {
              color: COLORS[index % COLORS.length],
            },
            areaStyle: {
              opacity: 0.1,
            },
          })),
        },
      ],
    };
  }, [data]);

  if (!data?.radar_data?.dimensions?.length) {
    return (
      <Card title="对比雷达图" loading={loading}>
        <Empty description="暂无对比数据" />
      </Card>
    );
  }

  return (
    <Card title="对比雷达图" loading={loading}>
      <ReactECharts option={chartOption} style={{ height: 400 }} />
    </Card>
  );
}

export default CompareRadar;
