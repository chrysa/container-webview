import { describe, expect, it, vi, beforeEach } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { DemoBanner } from './DemoBanner';
import type { ConfigStatus } from '@/domain/config/types';

const useConfigStatusMock = vi.fn();

vi.mock('@/domain/config/queries', () => ({
  useConfigStatus: () => useConfigStatusMock() as { data?: ConfigStatus },
}));

describe('DemoBanner', () => {
  beforeEach(() => {
    useConfigStatusMock.mockReset();
  });

  it('renders nothing when demo mode is off', () => {
    useConfigStatusMock.mockReturnValue({ data: { demo_mode: false, ldap_enabled: false } });
    expect(renderToStaticMarkup(<DemoBanner />)).toBe('');
  });

  it('renders nothing while the config status is still loading', () => {
    useConfigStatusMock.mockReturnValue({ data: undefined });
    expect(renderToStaticMarkup(<DemoBanner />)).toBe('');
  });

  it('renders an amber status banner when demo mode is on', () => {
    useConfigStatusMock.mockReturnValue({ data: { demo_mode: true, ldap_enabled: false } });
    const html = renderToStaticMarkup(<DemoBanner />);
    expect(html).toContain('data-testid="demo-banner"');
    expect(html).toContain('role="status"');
    expect(html).toMatch(/DEMO/);
    expect(html).toMatch(/fixture data/i);
  });
});
