import path from 'node:path';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov', 'html'],
      exclude: ['src/test/**', '**/*.d.ts', '**/*.config.*', 'src/main.tsx'],
      thresholds: {
        lines: 5,
        functions: 20,
        branches: 40,
      },
    },
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
  },
});
