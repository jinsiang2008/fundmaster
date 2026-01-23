/**
 * AI analysis report display component
 */

import { Card, Tag, Typography, Spin, Button, Alert, Divider } from 'antd';
import { RobotOutlined, ReloadOutlined } from '@ant-design/icons';
import type { FundAnalysisReport } from '../types/fund';

const { Title, Text, Paragraph } = Typography;

interface AnalysisReportProps {
  report?: FundAnalysisReport;
  loading?: boolean;
  streamingContent?: string;
  isStreaming?: boolean;
  onRefresh?: () => void;
  error?: Error | null;
}

export function AnalysisReport({
  report,
  loading = false,
  streamingContent = '',
  isStreaming = false,
  onRefresh,
  error,
}: AnalysisReportProps) {
  const getRecommendationColor = (rec: string) => {
    if (rec === '买入') return 'success';
    if (rec === '回避') return 'error';
    return 'warning';
  };

  // Show loading state
  if (loading && !isStreaming) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: 60 }}>
          <Spin size="large" />
          <Paragraph style={{ marginTop: 16 }}>
            <RobotOutlined style={{ marginRight: 8 }} />
            AI 正在分析基金数据...
          </Paragraph>
        </div>
      </Card>
    );
  }

  // Show error state
  if (error) {
    return (
      <Card>
        <Alert
          type="error"
          message="分析失败"
          description={error.message || '无法获取分析报告，请稍后重试'}
          action={
            onRefresh && (
              <Button size="small" onClick={onRefresh}>
                重试
              </Button>
            )
          }
        />
      </Card>
    );
  }

  // Show streaming content
  if (isStreaming || streamingContent) {
    const formattedStreaming = (streamingContent || '正在生成...').split('\n').map((line, index) => {
      const trimmed = line.trim();
      if (trimmed.startsWith('### ')) {
        return <h3 key={index} style={{ fontSize: 16, fontWeight: 600, marginTop: 16, marginBottom: 10, color: '#262626' }}>{trimmed.slice(4)}</h3>;
      }
      if (trimmed.startsWith('## ')) {
        return <h2 key={index} style={{ fontSize: 20, fontWeight: 600, marginTop: 20, marginBottom: 12, color: '#262626' }}>{trimmed.slice(3)}</h2>;
      }
      if (trimmed.startsWith('# ')) {
        return <h1 key={index} style={{ fontSize: 24, fontWeight: 600, marginTop: 24, marginBottom: 16, color: '#1890ff' }}>{trimmed.slice(2)}</h1>;
      }
      if (trimmed === '---') {
        return <Divider key={index} style={{ margin: '20px 0' }} />;
      }
      if (trimmed.includes('**')) {
        const parts = trimmed.split('**');
        const formatted = parts.map((part, i) => 
          i % 2 === 1 ? <strong key={i} style={{ fontWeight: 600, color: '#1890ff' }}>{part}</strong> : part
        );
        return <p key={index} style={{ marginBottom: 12, lineHeight: 1.8 }}>{formatted}</p>;
      }
      if (trimmed.match(/^[-*]\s/)) {
        return <li key={index} style={{ marginBottom: 8, marginLeft: 24, lineHeight: 1.6 }}>{trimmed.replace(/^[-*]\s/, '')}</li>;
      }
      if (!trimmed) {
        return <div key={index} style={{ height: 8 }} />;
      }
      return <p key={index} style={{ marginBottom: 12, lineHeight: 1.8 }}>{trimmed}</p>;
    });

    return (
      <Card
        title={
          <span>
            <RobotOutlined style={{ marginRight: 8 }} />
            AI 分析报告
            {isStreaming && <Spin size="small" style={{ marginLeft: 8 }} />}
          </span>
        }
      >
        <div style={{ fontSize: 14 }}>
          {formattedStreaming}
          {isStreaming && <span className="cursor-blink" style={{ fontSize: 18, fontWeight: 'bold', marginLeft: 4 }}>▌</span>}
        </div>
      </Card>
    );
  }

  // Show report
  if (!report) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
          <RobotOutlined style={{ fontSize: 48, marginBottom: 16 }} />
          <Paragraph>点击获取 AI 分析报告</Paragraph>
          {onRefresh && (
            <Button type="primary" onClick={onRefresh}>
              生成分析报告
            </Button>
          )}
        </div>
      </Card>
    );
  }

  // Format analysis content for better readability
  const formattedContent = report.analysis
    .split('\n')
    .map((line, index) => {
      const trimmed = line.trim();
      
      // H1 (# )
      if (trimmed.startsWith('# ')) {
        return <h1 key={index} style={{ fontSize: 24, fontWeight: 600, marginTop: 24, marginBottom: 16, paddingBottom: 8, borderBottom: '2px solid #e8e8e8', color: '#1890ff' }}>{trimmed.slice(2)}</h1>;
      }
      
      // H2 (## )
      if (trimmed.startsWith('## ')) {
        return <h2 key={index} style={{ fontSize: 20, fontWeight: 600, marginTop: 20, marginBottom: 12, color: '#262626' }}>{trimmed.slice(3)}</h2>;
      }
      
      // H3 (### )
      if (trimmed.startsWith('### ')) {
        return <h3 key={index} style={{ fontSize: 16, fontWeight: 600, marginTop: 16, marginBottom: 10, color: '#262626' }}>{trimmed.slice(4)}</h3>;
      }
      
      // H4 (#### )
      if (trimmed.startsWith('#### ')) {
        return <h4 key={index} style={{ fontSize: 14, fontWeight: 600, marginTop: 14, marginBottom: 8, color: '#595959' }}>{trimmed.slice(5)}</h4>;
      }
      
      // HR (---)
      if (trimmed === '---' || trimmed === '___') {
        return <Divider key={index} style={{ margin: '24px 0' }} />;
      }
      
      // Bold text (**text**)
      if (trimmed.includes('**')) {
        const parts = trimmed.split('**');
        const formatted = parts.map((part, i) => 
          i % 2 === 1 ? <strong key={i} style={{ fontWeight: 600, color: '#1890ff' }}>{part}</strong> : part
        );
        return <p key={index} style={{ marginBottom: 12, lineHeight: 1.8, color: '#262626' }}>{formatted}</p>;
      }
      
      // List item (- or 1. )
      if (trimmed.match(/^[-*]\s/) || trimmed.match(/^\d+\.\s/)) {
        const content = trimmed.replace(/^[-*]\s/, '').replace(/^\d+\.\s/, '');
        return <li key={index} style={{ marginBottom: 8, marginLeft: 24, lineHeight: 1.6 }}>{content}</li>;
      }
      
      // Empty line
      if (!trimmed) {
        return <div key={index} style={{ height: 8 }} />;
      }
      
      // Regular paragraph
      return <p key={index} style={{ marginBottom: 12, lineHeight: 1.8, color: '#262626' }}>{trimmed}</p>;
    });

  return (
    <Card
      title={
        <span>
          <RobotOutlined style={{ marginRight: 8 }} />
          AI 分析报告
        </span>
      }
      extra={
        <div>
          <Tag color={getRecommendationColor(report.recommendation)}>
            {report.recommendation}
          </Tag>
          {onRefresh && (
            <Button
              type="text"
              icon={<ReloadOutlined />}
              onClick={onRefresh}
              style={{ marginLeft: 8 }}
            >
              刷新
            </Button>
          )}
        </div>
      }
    >
      <div style={{ fontSize: 14 }}>
        {formattedContent}
      </div>

      <div style={{ marginTop: 24, paddingTop: 16, borderTop: '1px solid #f0f0f0', color: '#999', fontSize: 12 }}>
        报告生成时间: {new Date(report.generated_at).toLocaleString()}
      </div>
    </Card>
  );
}

export default AnalysisReport;
