import { defineConfig } from '@farmfe/core';
import postcss from '@farmfe/js-plugin-postcss';
import path from 'path';

export default defineConfig({
  // Options related to the compilation
  compilation: {
    input: {
      // can be a relative path or an absolute path
      index: './index.html',
      // sourcemap: "all",
    },
    output: {
      path: './build',
      publicPath: '/',
      assetsFilename: 'assets/[resourceName]_[hash].[ext]',
      targetEnv: 'browser-es2017',
      format: 'esm',
    },
    resolve: {
      alias: {
        '@': path.join(process.cwd(), 'src'),
      },
    },
    assets: {
      include: ['png', 'jpg', 'jpeg', 'gif', 'svg', 'glb', 'gltf', 'geojson'],
    },
  },
  // Options related to the dev server
  server: {
    port: 9000,
    // open: true,
    // hmr: {
    //   port: 9801,
    //   host: "localhost",
    // },
  },
  // Additional plugins
  plugins: ['@farmfe/plugin-react', postcss()],
});
