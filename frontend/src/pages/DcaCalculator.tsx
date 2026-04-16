/**
 * 定投模拟：基于历史净值的按月买入测算。
 */

import { useCallback, useMemo, useState } from 'react';
import {
  Layout,
  Typography,
  Card,
  Form,
  Input,
  InputNumber,
  DatePicker,
  Button,
  Table,
  Row,
  Col,
  Statistic,
  Alert,
  AutoComplete,
  Space,
  Tag,
} from 'antd';
import { FundQuickListsPanel, SubtleHint } from '../components';
import type { Dayjs } from 'dayjs';
import dayjs from 'dayjs';
import {
  CalculatorOutlined,
  InfoCircleOutlined,
  RiseOutlined,
  FallOutlined,
} from '@ant-design/icons';
import axios from 'axios';
import { useSearchFunds, useDCASimulate } from '../hooks/useFund';
import type { ColumnsType } from 'antd/es/table';
import type { DCAPeriodRow, FundSearchResult } from '../types/fund';

const { Content } = Layout;
const { Title, Paragraph, Text } = Typography;

export function DcaCalculator() {
  const [form] = Form.useForm();
  const [fundQuery, setFundQuery] = useState('');
  const [picked, setPicked] = useState<FundSearchResult | null>(null);
  const { data: searchHits, isFetching } = useSearchFunds(fundQuery, fundQuery.length >= 2);

  const dcaMutation = useDCASimulate();

  const options = useMemo(
    () =>
      (searchHits ?? []).map((f) => ({
        value: `${f.code} ${f.name}`,
        label: (
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
            <span>
              <Text strong>{f.name}</Text>
              <Text type="secondary" style={{ marginLeft: 8 }}>
                {f.code}
              </Text>
            </span>
            <Text type="secondary" ellipsis>
              {f.type || ' '}
            </Text>
          </div>
        ),
        fund: f,
      })),
    [searchHits]
  );

  const onSelectFund = useCallback(
    (_: string, option: { fund: FundSearchResult }) => {
      setPicked(option.fund);
      form.setFieldsValue({ fund_code: option.fund.code });
      setFundQuery('');
    },
    [form]
  );

  const onQuickPickFund = useCallback(
    (fund: FundSearchResult) => {
      setPicked(fund);
      form.setFieldsValue({ fund_code: fund.code });
      setFundQuery('');
    },
    [form]
  );

  const onFinish = useCallback(
    (values: {
      fund_code: string;
      monthly_amount: number;
      range: [Dayjs, Dayjs];
    }) => {
      const code = (values.fund_code || '').trim();
      const [start, end] = values.range;
      if (!code || code.length < 6) return;
      dcaMutation.mutate({
        fund_code: code,
        monthly_amount: values.monthly_amount,
        start_date: start.format('YYYY-MM-DD'),
        end_date: end.format('YYYY-MM-DD'),
      });
    },
    [dcaMutation]
  );

  const columns: ColumnsType<DCAPeriodRow> = [
    {
      title: '扣款日',
      dataIndex: 'invest_date',
      width: 120,
    },
    {
      title: '单位净值',
      dataIndex: 'nav',
      render: (v: number) => v.toFixed(4),
    },
    {
      title: '当期金额',
      dataIndex: 'amount',
      render: (v: number) => `${v.toFixed(2)} 元`,
    },
    {
      title: '份额',
      dataIndex: 'shares',
    },
  ];

  const summary = dcaMutation.data?.summary;
  const profit = summary?.profit_loss ?? 0;

  return (
    <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Content style={{ padding: '32px 24px 48px' }}>
        <Row gutter={[24, 24]}>
          <Col xs={24} xl={16}>
        <div style={{ marginBottom: 28 }}>
          <Title level={2} style={{ marginBottom: 8 }}>
            <CalculatorOutlined style={{ marginRight: 10, color: '#1677ff' }} />
            定投计算器
          </Title>
          <Paragraph type="secondary">
            按自然月模拟：每月在当月中取<span style={{ fontWeight: 500 }}>第一个可用净值日</span>
            买入固定金额。未计入申赎费用与分红再投，结果仅供参考。
          </Paragraph>
        </div>

        <SubtleHint>
          除搜索外，可从下方「自选 / 最近浏览」一键填入基金代码（宽屏在页面右侧），数据与首页、详情页同步。
        </SubtleHint>

        <Card bordered={false} style={{ marginBottom: 24 }}>
          <Form
            form={form}
            layout="vertical"
            onFinish={onFinish}
            initialValues={{
              monthly_amount: 1000,
              range: [dayjs().subtract(3, 'year'), dayjs()],
            }}
          >
            <Form.Item
              label="基金代码或搜索"
              extra={
                picked ? (
                  <Text type="success">
                    已选：{picked.name}（{picked.code}）
                  </Text>
                ) : null
              }
            >
              <Space.Compact style={{ width: '100%' }}>
                <AutoComplete
                  style={{ flex: 1 }}
                  options={options}
                  onSearch={setFundQuery}
                  onSelect={onSelectFund}
                  notFoundContent={fundQuery.length >= 2 && !isFetching ? '无匹配基金' : null}
                >
                  <Input placeholder="输入名称或代码搜索，或手动输入 6 位代码" allowClear />
                </AutoComplete>
              </Space.Compact>
            </Form.Item>

            <Form.Item
              name="fund_code"
              label="基金代码"
              rules={[
                { required: true, message: '请输入基金代码' },
                { pattern: /^\d{6}$/, message: '请输入 6 位数字基金代码' },
              ]}
            >
              <Input maxLength={6} placeholder="例如 110011" />
            </Form.Item>

            <Row gutter={16}>
              <Col xs={24} sm={12}>
                <Form.Item
                  name="monthly_amount"
                  label="每期投入（元）"
                  rules={[{ required: true, type: 'number', min: 1, max: 1e9 }]}
                >
                  <InputNumber style={{ width: '100%' }} min={1} step={100} />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item
                  name="range"
                  label="回测区间"
                  rules={[{ required: true, message: '请选择开始与结束日期' }]}
                >
                  <DatePicker.RangePicker
                    style={{ width: '100%' }}
                    allowClear={false}
                    disabledDate={(d) => d.isAfter(dayjs(), 'day')}
                  />
                </Form.Item>
              </Col>
            </Row>

            <Space wrap>
              <Button type="primary" htmlType="submit" loading={dcaMutation.isPending}>
                开始测算
              </Button>
              <Button
                onClick={() =>
                  form.setFieldsValue({
                    range: [dayjs().subtract(1, 'year'), dayjs()],
                  })
                }
              >
                近1年
              </Button>
              <Button
                onClick={() =>
                  form.setFieldsValue({
                    range: [dayjs().subtract(3, 'year'), dayjs()],
                  })
                }
              >
                近3年
              </Button>
              <Button
                onClick={() =>
                  form.setFieldsValue({
                    range: [dayjs().subtract(5, 'year'), dayjs()],
                  })
                }
              >
                近5年
              </Button>
            </Space>
          </Form>
        </Card>

        {dcaMutation.isError && (
          <Alert
            type="error"
            showIcon
            style={{ marginBottom: 16 }}
            message={(() => {
              const err = dcaMutation.error;
              if (axios.isAxiosError(err)) {
                const d = err.response?.data as { detail?: string };
                if (typeof d?.detail === 'string') return d.detail;
              }
              if (err instanceof Error) return err.message;
              return '测算失败，请检查基金代码与日期区间是否覆盖净值数据';
            })()}
          />
        )}

        {dcaMutation.isSuccess && dcaMutation.data && (
          <>
            <Alert
              type="info"
              showIcon
              icon={<InfoCircleOutlined />}
              message={dcaMutation.data.disclaimer}
              style={{ marginBottom: 16 }}
            />
            <Card title={`${dcaMutation.data.fund_name}（${dcaMutation.data.fund_code}）`} style={{ marginBottom: 24 }}>
              <Row gutter={[16, 16]}>
                <Col xs={12} sm={8}>
                  <Statistic title="累计投入" value={summary?.total_invested} suffix="元" />
                </Col>
                <Col xs={12} sm={8}>
                  <Statistic title="持仓估值（按最新净值）" value={summary?.market_value} suffix="元" />
                </Col>
                <Col xs={12} sm={8}>
                  <Statistic
                    title="累计盈亏"
                    value={summary?.profit_loss}
                    suffix="元"
                    prefix={profit >= 0 ? <RiseOutlined /> : <FallOutlined />}
                    valueStyle={{ color: profit >= 0 ? '#52c41a' : '#ff4d4f' }}
                  />
                </Col>
                <Col xs={12} sm={8}>
                  <Statistic
                    title="收益率"
                    value={summary?.profit_loss_pct}
                    suffix="%"
                    valueStyle={{ color: profit >= 0 ? '#52c41a' : '#ff4d4f' }}
                  />
                </Col>
                <Col xs={12} sm={8}>
                  <Statistic title="定投期数" value={summary?.periods_count} suffix="期" />
                </Col>
                <Col xs={12} sm={8}>
                  <Text type="secondary" style={{ display: 'block', marginBottom: 4 }}>
                    最新净值
                  </Text>
                  <Text strong>{summary?.latest_nav_date}</Text>
                  <Tag style={{ marginLeft: 8 }}>净值 {summary?.latest_nav?.toFixed(4)}</Tag>
                </Col>
              </Row>
            </Card>

            <Card title="各期扣款明细">
              <Table<DCAPeriodRow>
                size="small"
                rowKey={(r) => r.invest_date}
                columns={columns}
                dataSource={dcaMutation.data.periods}
                pagination={{ pageSize: 12, showSizeChanger: true }}
                scroll={{ x: true }}
              />
            </Card>
          </>
        )}
          </Col>

          <Col xs={24} xl={8}>
            <FundQuickListsPanel
              onApply={onQuickPickFund}
              applyLabel="填入测算"
            />
          </Col>
        </Row>
      </Content>
    </Layout>
  );
}

export default DcaCalculator;
