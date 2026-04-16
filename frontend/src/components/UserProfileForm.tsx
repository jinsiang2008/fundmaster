/**
 * User investment profile form component
 */

import { Form, Select, Button, Space, Typography } from 'antd';
import type { UserProfile } from '../types/chat';
import { RISK_LEVEL_MAP, PURPOSE_MAP, HORIZON_MAP } from '../types/chat';

const { Text } = Typography;

interface UserProfileFormProps {
  value?: UserProfile;
  onChange: (profile: UserProfile) => void;
  compact?: boolean;
}

const riskOptions = Object.entries(RISK_LEVEL_MAP).map(([value, label]) => ({
  value,
  label,
}));

const purposeOptions = Object.entries(PURPOSE_MAP).map(([value, label]) => ({
  value,
  label,
}));

const horizonOptions = Object.entries(HORIZON_MAP).map(([value, label]) => ({
  value,
  label,
}));

export function UserProfileForm({ value, onChange, compact = false }: UserProfileFormProps) {
  const [form] = Form.useForm();

  const handleSubmit = (values: UserProfile) => {
    onChange(values);
  };

  const initialValues: UserProfile = value || {
    risk_level: 'balanced',
    purpose: 'growth',
    horizon: 'medium',
  };

  if (compact) {
    return (
      <Form
        form={form}
        layout="inline"
        initialValues={initialValues}
        onFinish={handleSubmit}
        size="small"
      >
        <Form.Item name="risk_level" noStyle>
          <Select options={riskOptions} style={{ width: 100 }} />
        </Form.Item>
        <Form.Item name="purpose" noStyle>
          <Select options={purposeOptions} style={{ width: 100 }} />
        </Form.Item>
        <Form.Item name="horizon" noStyle>
          <Select options={horizonOptions} style={{ width: 120 }} />
        </Form.Item>
        <Form.Item noStyle>
          <Button type="primary" htmlType="submit">
            应用
          </Button>
        </Form.Item>
      </Form>
    );
  }

  return (
    <Form
      form={form}
      layout="vertical"
      initialValues={initialValues}
      onFinish={handleSubmit}
    >
      <Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
        设置您的投资偏好，获得更精准的个性化建议
      </Text>

      <Space wrap>
        <Form.Item
          name="risk_level"
          label="风险偏好"
          style={{ marginBottom: 8 }}
        >
          <Select options={riskOptions} style={{ width: 120 }} />
        </Form.Item>

        <Form.Item
          name="purpose"
          label="投资目的"
          style={{ marginBottom: 8 }}
        >
          <Select options={purposeOptions} style={{ width: 120 }} />
        </Form.Item>

        <Form.Item
          name="horizon"
          label="投资期限"
          style={{ marginBottom: 8 }}
        >
          <Select options={horizonOptions} style={{ width: 130 }} />
        </Form.Item>

        <Form.Item label=" " style={{ marginBottom: 8 }}>
          <Button type="primary" htmlType="submit">
            应用设置
          </Button>
        </Form.Item>
      </Space>
    </Form>
  );
}

export default UserProfileForm;
