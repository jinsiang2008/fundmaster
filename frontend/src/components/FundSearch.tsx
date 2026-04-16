/**
 * Fund search component with autocomplete
 */

import { useState, useCallback } from 'react';
import { AutoComplete, Input, Typography, Spin } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { useSearchFunds } from '../hooks/useFund';
import type { FundSearchResult } from '../types/fund';

const { Text } = Typography;

interface FundSearchProps {
  onSelect: (fund: FundSearchResult) => void;
  placeholder?: string;
  /** 与后端 category 一致：all / stock / bond / mixed / index / money / qdii */
  category?: string;
}

export function FundSearch({
  onSelect,
  placeholder = '搜索基金名称或代码',
  category = 'all',
}: FundSearchProps) {
  const [searchText, setSearchText] = useState('');
  const { data: results, isLoading } = useSearchFunds(
    searchText,
    searchText.length >= 2,
    category
  );

  const handleSearch = useCallback((value: string) => {
    setSearchText(value);
  }, []);

  const handleSelect = useCallback(
    (_value: string, option: { fund: FundSearchResult }) => {
      onSelect(option.fund);
      setSearchText('');
    },
    [onSelect]
  );

  const options = results?.map((fund) => ({
    value: fund.code,
    label: (
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <span>
          <Text strong>{fund.name}</Text>
          <Text type="secondary" style={{ marginLeft: 8 }}>
            {fund.code}
          </Text>
        </span>
        <Text type="secondary">{fund.type}</Text>
      </div>
    ),
    fund,
  }));

  return (
    <AutoComplete
      style={{ width: '100%' }}
      options={options}
      onSearch={handleSearch}
      onSelect={handleSelect}
      value={searchText}
    >
      <Input
        size="large"
        placeholder={placeholder}
        prefix={<SearchOutlined />}
        suffix={isLoading ? <Spin size="small" /> : undefined}
        allowClear
      />
    </AutoComplete>
  );
}

export default FundSearch;
