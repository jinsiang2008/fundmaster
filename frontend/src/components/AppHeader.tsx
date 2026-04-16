/**
 * Global navigation — sticky top bar for main routes.
 */

import { Layout, Menu } from 'antd';
import { Link, useLocation } from 'react-router-dom';

const { Header } = Layout;

export function AppHeader() {
  const { pathname } = useLocation();
  const selectedKey =
    pathname.startsWith('/compare')
      ? '/compare'
      : pathname.startsWith('/calculator')
        ? '/calculator'
        : pathname.startsWith('/recommend')
          ? '/recommend'
          : '/';

  const items = [
    { key: '/', label: <Link to="/">首页</Link> },
    { key: '/recommend', label: <Link to="/recommend">智能选基</Link> },
    { key: '/calculator', label: <Link to="/calculator">定投计算器</Link> },
    { key: '/compare', label: <Link to="/compare">基金对比</Link> },
  ];

  return (
    <Header
      style={{
        display: 'flex',
        alignItems: 'center',
        background: '#fff',
        paddingInline: 24,
        borderBottom: '1px solid #f0f0f0',
        position: 'sticky',
        top: 0,
        zIndex: 100,
        width: '100%',
      }}
    >
      <Link to="/" style={{ marginRight: 28, fontWeight: 600, fontSize: 17, color: '#1677ff' }}>
        FundMaster
      </Link>
      <Menu
        mode="horizontal"
        selectedKeys={[selectedKey]}
        items={items}
        style={{ flex: 1, minWidth: 0, borderBottom: 'none' }}
      />
    </Header>
  );
}
