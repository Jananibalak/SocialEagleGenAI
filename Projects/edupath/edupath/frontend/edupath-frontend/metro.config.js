const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// ❌ Prevent Node.js polyfills
config.resolver.extraNodeModules = {
  crypto: false,
  stream: false,
  buffer: false,
};

module.exports = config;