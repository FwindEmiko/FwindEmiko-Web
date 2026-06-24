// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  runtimeConfig: {
    public: {
      // 空 = 同源请求，通过 Nuxt server middleware 代理到后端
      apiBase: process.env.NUXT_PUBLIC_API_BASE || '',
      uploadBase: process.env.NUXT_PUBLIC_UPLOAD_BASE || '',
    },
    // 服务端专用：后端地址，用于 server/api 代理
    // 生产: http://backend:8000 (Docker 内部网络) | 开发: http://localhost:8000
    backendUrl: process.env.NUXT_BACKEND_URL || process.env.BACKEND_URL || 'http://localhost:8000',
  },

  app: {
    baseURL: '/',
    head: {
      charset: 'utf-8',
      viewport: 'width=device-width, initial-scale=1',
      titleTemplate: '%s - 狐风轩汐の小屋',
      title: '狐风轩汐の小屋',
      meta: [
        { name: 'description', content: '狐风轩汐の小屋 - 代码 | 游戏 | 创作' },
        { name: 'theme-color', content: '#0f172a' },
        { property: 'og:site_name', content: '狐风轩汐の小屋' },
      ],
      link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&family=JetBrains+Mono:wght@400;500;700&family=ZCOOL+XiaoWei&display=swap' },
      ],
      script: [
        { src: '/live2d/live2dcubismcore.min.js', defer: false },
        // SSR theme injection to prevent FOUC (P2)
        // 移动端兼容：读取 cookie 并在 HTML 渲染前应用主题 class
        {
          innerHTML: `(function(){try{var c=document.cookie.match(/theme=([^;]+)/);var t=c?decodeURIComponent(c[1]):'dark';var cl=document.documentElement.classList;cl.remove('dark','light');if(t==='light'){cl.add('light');}else{cl.add('dark');}}catch(e){document.documentElement.classList.add('dark');}})()`,
          type: 'text/javascript',
          tagPosition: 'head',
        },
      ],
    },
  },

  css: ['~/assets/css/main.css'],

  components: [
    { path: '~/components', pathPrefix: false },
    { path: '../../packages/ui/src/glass', pathPrefix: false },
  ],

  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
    '@element-plus/nuxt',
    '@nuxtjs/sitemap',
    '@nuxtjs/robots',
  ],

  tailwindcss: {
    configPath: '~/tailwind.config.ts',
    cssPath: '~/assets/css/main.css',
    exposeConfig: false,
  },

  site: {
    url: process.env.NUXT_PUBLIC_SITE_URL || 'http://localhost:3000',
  },

  sitemap: {
    defaults: {
      changefreq: 'daily',
      priority: 0.8,
      lastmod: new Date().toISOString(),
    },
    urls: async () => {
      const dynamicUrls: Array<{ loc: string; lastmod?: string; changefreq: string; priority: number }> = []
      const apiBase = `${process.env.BACKEND_URL || 'http://localhost:8000'}/api`
      try {
        const [postsRes, resourcesRes] = await Promise.all([
          fetch(`${apiBase}/posts?size=1000`).then(r => r.json()).catch(() => null),
          fetch(`${apiBase}/resources?size=1000`).then(r => r.json()).catch(() => null),
        ])
        if (postsRes?.code === 0 && Array.isArray(postsRes.data?.items)) {
          for (const post of postsRes.data.items) {
            dynamicUrls.push({
              loc: `/blog/${post.slug}`,
              lastmod: post.updated_at || post.published_at || post.created_at,
              changefreq: 'weekly',
              priority: 0.7,
            })
          }
        }
        if (resourcesRes?.code === 0 && Array.isArray(resourcesRes.data?.items)) {
          for (const resource of resourcesRes.data.items) {
            dynamicUrls.push({
              loc: `/resources/${resource.slug}`,
              lastmod: resource.updated_at || resource.created_at,
              changefreq: 'weekly',
              priority: 0.7,
            })
          }
        }
      } catch (err) {
        // eslint-disable-next-line no-console
        console.error('[sitemap] 动态 URL 生成失败:', err)
      }
      return dynamicUrls
    },
  },

  robots: {
    rules: [
      { UserAgent: '*', Allow: '/' },
      { UserAgent: '*', Disallow: '/admin' },
      { UserAgent: '*', Disallow: '/api' },
      { UserAgent: '*', Disallow: '/login' },
      { UserAgent: '*', Disallow: '/register' },
      { UserAgent: '*', Disallow: '/profile' },
    ],
    sitemap: `${process.env.NUXT_PUBLIC_SITE_URL || 'http://localhost:3000'}/sitemap.xml`,
  },

  nitro: {
    routeRules: {
      '/': { prerender: true },
      '/blog/**': { isr: 3600 },
      '/resources/**': { isr: 86400 },
      '/download/**': { ssr: true },
      '/login': { ssr: false },
      '/register': { ssr: false },
      '/profile': { ssr: false },
    },
  },

  ssr: true,
})
