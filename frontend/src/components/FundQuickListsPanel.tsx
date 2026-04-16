/**
 * 自选与最近浏览快捷列表，用于对比页、定投页等快速选基。
 * 数据存于 localStorage，多标签页会通过 storage 事件同步。
 */

import { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, List, Button, Typography, Empty, Tooltip } from 'antd';
import { StarOutlined, HistoryOutlined, RightOutlined } from '@ant-design/icons';
import type { FundSearchResult } from '../types/fund';
import { useWatchlist, useRecentFunds } from '../hooks/useLocalFundLists';

const { Text } = Typography;

export interface FundQuickListsPanelProps {
  /** 主操作：加入对比、填入测算表单等 */
  onApply: (fund: FundSearchResult) => void;
  applyLabel: string;
  /** 某只基金是否不可点主按钮（如已达对比上限） */
  isApplyDisabled?: (fund: FundSearchResult) => boolean;
  getApplyDisabledReason?: (fund: FundSearchResult) => string | undefined;
}

export function FundQuickListsPanel({
  onApply,
  applyLabel,
  isApplyDisabled,
  getApplyDisabledReason,
}: FundQuickListsPanelProps) {
  const navigate = useNavigate();
  const { watchlist } = useWatchlist();
  const { recentFunds } = useRecentFunds();

  const watchCodes = useMemo(() => new Set(watchlist.map((f) => f.code)), [watchlist]);
  const recentOnly = useMemo(
    () => recentFunds.filter((f) => !watchCodes.has(f.code)),
    [recentFunds, watchCodes]
  );

  const renderRow = (fund: FundSearchResult) => {
    const disabled = isApplyDisabled?.(fund) ?? false;
    const reason = getApplyDisabledReason?.(fund);
    const applyBtn = (
      <Button
        type="primary"
        size="small"
        disabled={disabled}
        onClick={() => onApply(fund)}
      >
        {applyLabel}
      </Button>
    );

    return (
      <List.Item
        style={{ padding: '8px 0', borderBlockEnd: 'none' }}
        actions={[
          disabled && reason ? (
            <Tooltip key="apply" title={reason}>
              <span style={{ display: 'inline-block' }}>{applyBtn}</span>
            </Tooltip>
          ) : (
            <span key="apply">{applyBtn}</span>
          ),
          <Button
            key="detail"
            type="link"
            size="small"
            icon={<RightOutlined />}
            onClick={() => navigate(`/fund/${fund.code}`)}
          >
            详情
          </Button>,
        ]}
      >
        <List.Item.Meta
          title={
            <Text ellipsis style={{ maxWidth: '100%' }}>
              {fund.name}
            </Text>
          }
          description={
            <Text type="secondary" style={{ fontSize: 12 }}>
              {fund.code}
              {fund.type ? ` · ${fund.type}` : ''}
            </Text>
          }
        />
      </List.Item>
    );
  };

  return (
    <div
      style={{
        position: 'sticky',
        top: 80,
        alignSelf: 'flex-start',
      }}
    >
      <Card
        size="small"
        title="自选与最近"
        styles={{ body: { paddingTop: 8 } }}
      >
        <Typography.Title level={5} style={{ marginTop: 0, marginBottom: 8, fontSize: 14 }}>
          <StarOutlined style={{ marginRight: 6, color: '#faad14' }} />
          自选
        </Typography.Title>
        {watchlist.length === 0 ? (
          <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无自选" style={{ marginBottom: 16 }} />
        ) : (
          <List
            size="small"
            dataSource={watchlist}
            renderItem={(fund) => renderRow(fund)}
            style={{ marginBottom: 16 }}
          />
        )}

        <Typography.Title level={5} style={{ marginTop: 0, marginBottom: 8, fontSize: 14 }}>
          <HistoryOutlined style={{ marginRight: 6, color: '#1677ff' }} />
          最近浏览
        </Typography.Title>
        {recentOnly.length === 0 ? (
          <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无记录（在详情页浏览后会出现在此）" />
        ) : (
          <List size="small" dataSource={recentOnly} renderItem={(fund) => renderRow(fund)} />
        )}

        <Text type="secondary" style={{ fontSize: 12, display: 'block', marginTop: 12 }}>
          首页与基金详情可加入自选；打开过详情页会记入「最近浏览」。
        </Text>
      </Card>
    </div>
  );
}

export default FundQuickListsPanel;
