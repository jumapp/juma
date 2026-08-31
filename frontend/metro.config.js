module.exports = {
  resolver: {
    assetExts: ['expo-htm', 'htm', 'html'],
    sourceExts: ['ts', 'tsx', 'js', 'jsx', 'cjs', 'json'],
    alias: {
      '^@/lib/config$': './lib/config',
      '^@/providers$': './providers',
      '^@/components$': './components',
      '^@/hooks$': './hooks',
      '^@/constants$': './constants',
      '^@/(.*)$': './$1',
    },
  },
};