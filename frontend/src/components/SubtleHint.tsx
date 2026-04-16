/**
 * 与 FundMaster 灰底页配套的轻量提示，避免大块蓝色 info Alert。
 */

import type { ReactNode } from 'react';
import { InfoCircleOutlined } from '@ant-design/icons';

interface SubtleHintProps {
  children: ReactNode;
}

export function SubtleHint({ children }: SubtleHintProps) {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'flex-start',
        gap: 10,
        fontSize: 13,
        color: 'rgba(0, 0, 0, 0.55)',
        lineHeight: 1.6,
        padding: '10px 14px',
        background: '#fafafa',
        border: '1px solid #f0f0f0',
        borderRadius: 8,
        marginBottom: 16,
      }}
    >
      <InfoCircleOutlined
        style={{
          marginTop: 3,
          color: '#8c8c8c',
          fontSize: 14,
          flexShrink: 0,
        }}
      />
      <span>{children}</span>
    </div>
  );
}

export default SubtleHint;
