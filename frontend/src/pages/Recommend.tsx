/**
 * 智能选基：风险偏好 + 期限 + 流动性 + 可选主题（规则引擎，非业绩排名）
 */

import { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Layout,
  Typography,
  Card,
  Form,
  Radio,
  Checkbox,
  Button,
  Space,
  Slider,
  Alert,
  List,
  Tag,
  Divider,
  Row,
  Col,
} from 'antd';
import {
  BulbOutlined,
  InfoCircleOutlined,
  RightCircleOutlined,
} from '@ant-design/icons';
import axios from 'axios';
import { useRecommendFunds } from '../hooks/useFund';
import { RISK_LEVEL_MAP, HORIZON_MAP } from '../types/chat';
import type { FundRecommendRequest, RecommendLiquidity } from '../types/fund';

const { Content } = Layout;
const { Title, Paragraph, Text } = Typography;

const LIQUIDITY_OPTIONS: { value: RecommendLiquidity; label: string }[] = [
  { value: 'high', label: '高 — 随时可能取用（偏活钱、短久期）' },
  { value: 'medium', label: '中 — 常见理财周期' },
  { value: 'low', label: '低 — 可长期持有，接受更高波动' },
];

const THEME_OPTIONS = [
  { value: 'broad_index', label: '宽基 / 指数联接' },
  { value: 'dividend', label: '红利 / 低波' },
  { value: 'tech', label: '科技 / 半导体 / 互联网' },
  { value: 'medical', label: '医药 / 医疗' },
  { value: 'consumption', label: '消费 / 白酒' },
  { value: 'new_energy', label: '新能源 / 光伏' },
  { value: 'hk', label: '港股 / 恒生' },
  { value: 'gold', label: '黄金 / 贵金属' },
  { value: 'us', label: '美股 / 纳指 QDII' },
  { value: 'bond', label: '纯债 / 短债' },
];

const PREFS_KEY = 'fundmaster.v1.recommendPrefs';

function loadSavedPrefs(): Partial<FundRecommendRequest> | null {
  try {
    const raw = localStorage.getItem(PREFS_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as Partial<FundRecommendRequest>;
  } catch {
    return null;
  }
}

function savePrefs(v: FundRecommendRequest) {
  try {
    localStorage.setItem(PREFS_KEY, JSON.stringify(v));
  } catch {
    /* ignore */
  }
}

export function Recommend() {
  const navigate = useNavigate();
  const [formDefaults] = useState<FundRecommendRequest>(() => {
    const s = loadSavedPrefs();
    return {
      risk_level: s?.risk_level ?? 'balanced',
      horizon: s?.horizon ?? 'medium',
      liquidity: s?.liquidity ?? 'medium',
      themes: s?.themes ?? [],
      limit: s?.limit ?? 10,
    };
  });
  const [form] = Form.useForm<FundRecommendRequest>();
  const resultsRef = useRef<HTMLDivElement>(null);
  const mutation = useRecommendFunds();

  const onFinish = (values: FundRecommendRequest) => {
    const body: FundRecommendRequest = {
      risk_level: values.risk_level,
      horizon: values.horizon,
      liquidity: values.liquidity,
      themes: values.themes ?? [],
      limit: values.limit ?? 10,
    };
    savePrefs(body);
    mutation.mutate(body, {
      onSuccess: () => {
        setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
      },
    });
  };

  const data = mutation.data;

  return (
    <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Content style={{ maxWidth: 920, margin: '0 auto', padding: '28px 24px 48px' }}>
        <div style={{ marginBottom: 24 }}>
          <Title level={2} style={{ marginBottom: 8 }}>
            <BulbOutlined style={{ marginRight: 10, color: '#faad14' }} />
            智能选基
          </Title>
          <Paragraph type="secondary" style={{ marginBottom: 0 }}>
            根据你的<strong>风险偏好</strong>、<strong>投资期限</strong>与<strong>流动性</strong>，在全市场基金中做规则筛选；可选<strong>行业/主题</strong>进一步缩小范围。
            结果附简要理由，便于理解「为何入选」——并非业绩排行榜，也不构成投资建议。
          </Paragraph>
        </div>

        <Card>
          <Form<FundRecommendRequest>
            form={form}
            layout="vertical"
            onFinish={onFinish}
            initialValues={formDefaults}
          >
            <Form.Item
              name="risk_level"
              label="风险偏好"
              rules={[{ required: true }]}
            >
              <Radio.Group>
                {(Object.keys(RISK_LEVEL_MAP) as (keyof typeof RISK_LEVEL_MAP)[]).map((k) => (
                  <Radio.Button key={k} value={k} style={{ marginBottom: 8 }}>
                    {RISK_LEVEL_MAP[k]}
                  </Radio.Button>
                ))}
              </Radio.Group>
            </Form.Item>

            <Form.Item name="horizon" label="投资期限" rules={[{ required: true }]}>
              <Radio.Group>
                {(Object.keys(HORIZON_MAP) as (keyof typeof HORIZON_MAP)[]).map((k) => (
                  <Radio.Button key={k} value={k} style={{ marginBottom: 8 }}>
                    {HORIZON_MAP[k]}
                  </Radio.Button>
                ))}
              </Radio.Group>
            </Form.Item>

            <Form.Item name="liquidity" label="流动性偏好" rules={[{ required: true }]}>
              <Radio.Group>
                {LIQUIDITY_OPTIONS.map((o) => (
                  <Radio key={o.value} value={o.value} style={{ display: 'block', marginBottom: 6 }}>
                    {o.label}
                  </Radio>
                ))}
              </Radio.Group>
            </Form.Item>

            <Form.Item name="themes" label="关注主题（可选，多选；不选则不限定行业）">
              <Checkbox.Group style={{ width: '100%' }}>
                <Row gutter={[8, 8]}>
                  {THEME_OPTIONS.map((t) => (
                    <Col xs={12} sm={8} key={t.value}>
                      <Checkbox value={t.value}>{t.label}</Checkbox>
                    </Col>
                  ))}
                </Row>
              </Checkbox.Group>
            </Form.Item>

            <Form.Item
              name="limit"
              label="返回数量"
              tooltip="从符合条件的基金中抽样展示，同一画像在当天结果相对稳定"
            >
              <Slider min={5} max={20} marks={{ 5: '5', 10: '10', 15: '15', 20: '20' }} />
            </Form.Item>

            <Form.Item>
              <Button type="primary" htmlType="submit" size="large" loading={mutation.isPending} block>
                生成推荐
              </Button>
            </Form.Item>
          </Form>
        </Card>

        {mutation.isError && (
          <Alert
            type="error"
            showIcon
            style={{ marginTop: 16 }}
            message={(() => {
              const err = mutation.error;
              if (axios.isAxiosError(err)) {
                const d = err.response?.data as { detail?: unknown };
                if (typeof d?.detail === 'string') return d.detail;
              }
              return err instanceof Error ? err.message : '推荐失败，请检查网络或稍后重试';
            })()}
          />
        )}

        {data && (
          <div ref={resultsRef}>
            <Card style={{ marginTop: 20 }} title="推荐结果">
              <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                <Paragraph style={{ marginBottom: 0 }}>
                  <InfoCircleOutlined style={{ marginRight: 8, color: '#1677ff' }} />
                  {data.profile_summary}
                </Paragraph>
                <Alert type="warning" showIcon message={data.disclaimer} />
                <Divider style={{ margin: '8px 0' }} />
                {data.funds.length === 0 ? (
                  <Text type="secondary">没有符合条件的基金，请放宽选项后重试。</Text>
                ) : (
                  <List
                    itemLayout="vertical"
                    dataSource={data.funds}
                    renderItem={(item) => (
                      <List.Item
                        key={item.code}
                        extra={
                          <Button
                            type="link"
                            icon={<RightCircleOutlined />}
                            onClick={() => navigate(`/fund/${item.code}`)}
                          >
                            查看详情
                          </Button>
                        }
                      >
                        <List.Item.Meta
                          title={
                            <Space wrap>
                              <Text strong>{item.name}</Text>
                              <Tag>{item.code}</Tag>
                              {item.type ? <Tag color="blue">{item.type}</Tag> : null}
                            </Space>
                          }
                          description={
                            <ul style={{ margin: '8px 0 0', paddingLeft: 20 }}>
                              {item.reasons.map((r) => (
                                <li key={r}>{r}</li>
                              ))}
                            </ul>
                          }
                        />
                      </List.Item>
                    )}
                  />
                )}
              </Space>
            </Card>
          </div>
        )}
      </Content>
    </Layout>
  );
}

export default Recommend;
