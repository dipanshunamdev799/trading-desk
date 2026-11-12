/** @type {import('next').NextConfig} */
const nextConfig = {
  distDir: process.env.TRADING_DESK_NEXT_DIST || '.next',
  reactStrictMode: true,
  experimental: { proxyTimeout: 180_000 },
  async redirects() {
    return [
      { source: '/charts', destination: '/nifty', permanent: false },
    ];
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.TRADING_DESK_API_URL || 'http://127.0.0.1:8000'}/:path*`,
      },
    ];
  },
};

export default nextConfig;
