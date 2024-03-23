/** @type {import('next').NextConfig} */
const nextConfig = {
    env: {
        API_PATH: process.env.API_PATH,
        API_TOKEN: process.env.API_TOKEN,
    }
};

export default nextConfig;
