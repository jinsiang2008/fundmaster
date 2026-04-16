/**
 * Chat panel component for personalized conversation
 */

import { useState, useRef, useLayoutEffect } from 'react';
import { Card, Input, Button, Typography, Space, Avatar, Spin } from 'antd';
import { SendOutlined, UserOutlined, RobotOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import type { ChatMessage, UserProfile } from '../types/chat';
import { UserProfileForm } from './UserProfileForm';

const { TextArea } = Input;
const { Text } = Typography;

interface ChatPanelProps {
  messages: ChatMessage[];
  streamingContent?: string;
  isStreaming?: boolean;
  onSendMessage: (message: string, profile?: UserProfile) => void;
  userProfile?: UserProfile;
  onProfileChange?: (profile: UserProfile) => void;
}

export function ChatPanel({
  messages,
  streamingContent = '',
  isStreaming = false,
  onSendMessage,
  userProfile,
  onProfileChange,
}: ChatPanelProps) {
  const [inputValue, setInputValue] = useState('');
  const [showProfileForm, setShowProfileForm] = useState(false);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  /** 用户是否停留在聊天区底部（流式输出时仅在此为 true 时自动下滚，避免与框内回看冲突） */
  const stickToBottomRef = useRef(true);

  const updateStickFromScroll = () => {
    const el = messagesContainerRef.current;
    if (!el) return;
    const gap = el.scrollHeight - el.scrollTop - el.clientHeight;
    stickToBottomRef.current = gap < 80;
  };

  /**
   * 只设置消息区容器的 scrollTop，禁止使用 scrollIntoView：
   * scrollIntoView 会滚动所有可滚动祖先（含整页 Layout），流式时每帧都会把页面拉回底部，
   * 导致左侧主内容无法用滚轮向上查看。
   */
  useLayoutEffect(() => {
    const el = messagesContainerRef.current;
    if (!el || !stickToBottomRef.current) return;
    el.scrollTop = el.scrollHeight;
  }, [messages, streamingContent]);

  const handleSend = () => {
    if (!inputValue.trim() || isStreaming) return;
    stickToBottomRef.current = true;
    onSendMessage(inputValue.trim(), userProfile);
    setInputValue('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Card
      title="💬 智能投资顾问"
      extra={
        <Button
          type="text"
          onClick={() => setShowProfileForm(!showProfileForm)}
        >
          {showProfileForm ? '收起' : '设置投资偏好'}
        </Button>
      }
      bodyStyle={{ padding: 0, display: 'flex', flexDirection: 'column', height: 500 }}
    >
      {/* Profile Form */}
      {showProfileForm && (
        <div style={{ padding: 16, borderBottom: '1px solid #f0f0f0' }}>
          <UserProfileForm
            value={userProfile}
            onChange={(profile) => {
              onProfileChange?.(profile);
              setShowProfileForm(false);
            }}
          />
        </div>
      )}

      {/* Messages Area */}
      <div
        ref={messagesContainerRef}
        onScroll={updateStickFromScroll}
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: 16,
          overscrollBehavior: 'contain',
        }}
      >
        {messages.length === 0 && !streamingContent && (
          <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
            <RobotOutlined style={{ fontSize: 48, marginBottom: 16 }} />
            <Text type="secondary" style={{ display: 'block' }}>
              你好！我是你的智能投资顾问。
            </Text>
            <Text type="secondary" style={{ display: 'block' }}>
              可以问我关于这只基金的任何问题。
            </Text>
            <div style={{ marginTop: 16 }}>
              <Space wrap>
                <Button
                  size="small"
                  onClick={() => setInputValue('这只基金适合稳健型投资者吗？')}
                >
                  这只基金适合稳健型投资者吗？
                </Button>
                <Button
                  size="small"
                  onClick={() => setInputValue('帮我分析一下风险')}
                >
                  帮我分析一下风险
                </Button>
                <Button
                  size="small"
                  onClick={() => setInputValue('有没有类似但更稳健的基金？')}
                >
                  推荐更稳健的基金
                </Button>
              </Space>
            </div>
          </div>
        )}

        {messages.map((msg, index) => (
          <div
            key={index}
            style={{
              display: 'flex',
              marginBottom: 16,
              flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
            }}
          >
            <Avatar
              icon={msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
              style={{
                backgroundColor: msg.role === 'user' ? '#1890ff' : '#52c41a',
                flexShrink: 0,
              }}
            />
            <div
              style={{
                maxWidth: '70%',
                margin: msg.role === 'user' ? '0 8px 0 0' : '0 0 0 8px',
                padding: '8px 12px',
                borderRadius: 8,
                backgroundColor: msg.role === 'user' ? '#e6f7ff' : '#f6ffed',
              }}
            >
              <div className="markdown-content">
                <ReactMarkdown
                  components={{
                    p: ({ children }) => <p style={{ marginBottom: 8, lineHeight: 1.6 }}>{children}</p>,
                    ul: ({ children }) => <ul style={{ paddingLeft: 20, marginBottom: 8 }}>{children}</ul>,
                    ol: ({ children }) => <ol style={{ paddingLeft: 20, marginBottom: 8 }}>{children}</ol>,
                    li: ({ children }) => <li style={{ marginBottom: 4 }}>{children}</li>,
                    strong: ({ children }) => <strong style={{ fontWeight: 600, color: '#1890ff' }}>{children}</strong>,
                  }}
                >
                  {msg.content}
                </ReactMarkdown>
              </div>
            </div>
          </div>
        ))}

        {/* Streaming message */}
        {(isStreaming || streamingContent) && (
          <div style={{ display: 'flex', marginBottom: 16 }}>
            <Avatar
              icon={<RobotOutlined />}
              style={{ backgroundColor: '#52c41a', flexShrink: 0 }}
            />
            <div
              style={{
                maxWidth: '70%',
                marginLeft: 8,
                padding: '8px 12px',
                borderRadius: 8,
                backgroundColor: '#f6ffed',
              }}
            >
              <div className="markdown-content">
                <ReactMarkdown
                  components={{
                    p: ({ children }) => <p style={{ marginBottom: 8, lineHeight: 1.6 }}>{children}</p>,
                    ul: ({ children }) => <ul style={{ paddingLeft: 20, marginBottom: 8 }}>{children}</ul>,
                    strong: ({ children }) => <strong style={{ fontWeight: 600, color: '#1890ff' }}>{children}</strong>,
                  }}
                >
                  {streamingContent || '正在思考...'}
                </ReactMarkdown>
                {isStreaming && <Spin size="small" style={{ marginLeft: 8 }} />}
              </div>
            </div>
          </div>
        )}

      </div>

      {/* Input Area */}
      <div style={{ padding: 16, borderTop: '1px solid #f0f0f0' }}>
        <Space.Compact style={{ width: '100%' }}>
          <TextArea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入你的问题..."
            autoSize={{ minRows: 1, maxRows: 4 }}
            disabled={isStreaming}
            style={{ flex: 1 }}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSend}
            loading={isStreaming}
            disabled={!inputValue.trim()}
          >
            发送
          </Button>
        </Space.Compact>
      </div>
    </Card>
  );
}

export default ChatPanel;
