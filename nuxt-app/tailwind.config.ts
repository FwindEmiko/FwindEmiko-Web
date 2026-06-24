import type { Config } from 'tailwindcss'

export default <Partial<Config>>{
  darkMode: 'class',
  content: [
    './app/components/**/*.{vue,ts,tsx}',
    './app/layouts/**/*.vue',
    './app/pages/**/*.vue',
    './app/composables/**/*.{ts,js}',
    './app/app.vue',
  ],
  theme: {
    extend: {
      colors: {
        glass: 'rgba(255, 255, 255, 0.04)',
        'glass-hover': 'rgba(255, 255, 255, 0.08)',
        'glass-border': 'rgba(255, 255, 255, 0.06)',
        'glass-light': 'rgba(255, 255, 255, 0.65)',
        'glass-light-hover': 'rgba(255, 255, 255, 0.8)',
        'glass-light-border': 'rgba(255, 255, 255, 0.4)',
      },
      backdropBlur: {
        glass: '14px',
      },
      borderRadius: {
        glass: '14px',
      },
      boxShadow: {
        glass: '0 8px 32px rgba(0, 0, 0, 0.12)',
        card: '0 4px 16px rgba(0, 0, 0, 0.08)',
      },
      fontFamily: {
        display: ['"Noto Sans SC"', 'system-ui', 'sans-serif'],
        body: ['"Noto Sans SC"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"Fira Code"', 'Consolas', 'monospace'],
        anime: ['"ZCOOL XiaoWei"', '"Noto Serif SC"', 'serif'],
      },
    },
  },
  plugins: [],
}
