// next.config.js
const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export', // Export as static files
  trailingSlash: true, // Ensure trailing slashes for compatibility with Docusaurus
  images: {
    unoptimized: true // Required for export
  },
  experimental: {
    // Configuration for integrating with Docusaurus
    transpilePackages: [
      // Add packages that may need transpilation
    ],
  },
  webpack: (config, { isServer }) => {
    // Add configuration for handling Docusaurus-specific files
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false, // Docusaurus uses fs which isn't available in browser
      };
    }

    // Add rule for handling .mdx files if needed
    config.module.rules.push({
      test: /\.mdx?$/,
      use: [
        {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env', '@babel/preset-react'],
          },
        },
        {
          loader: '@mdx-js/loader',
          options: {},
        },
      ],
    });

    return config;
  },
  async redirects() {
    return [
      // Redirect for handling Docusaurus-style routes
      {
        source: '/docs',
        destination: '/docs/',
        permanent: true,
      },
      {
        source: '/docs/:path*',
        destination: '/docs/:path*/',
        permanent: true,
      },
    ];
  },
};

module.exports = nextConfig;