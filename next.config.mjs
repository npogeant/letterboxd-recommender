/** @type {import('next').NextConfig} */
const nextConfig = {
    env: {
      API_PATH: process.env.API_PATH,
      API_TOKEN: process.env.API_TOKEN,
    },
    async rewrites() {
      return [
        {
          source: '/api/:path*',
          destination: `${process.env.API_PATH}/:path*`, // Proxy to Backend
        },
      ];
    },
  };
  
  export default nextConfig;
  