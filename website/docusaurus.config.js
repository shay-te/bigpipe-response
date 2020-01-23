/**
 * Copyright (c) 2017-present, Facebook, Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

module.exports = {
  title: 'Bigpipe Response',
  tagline: 'Fast Web Sites Loading',
  url: 'https://github.com/shacoshe/bigpipe-response',
  baseUrl: '/',
  favicon: 'img/favicon.ico',
  organizationName: 'shacoshe', // Usually your GitHub org/user name.
  projectName: 'bigpipe-response', // Usually your repo name.
  themeConfig: {
    navbar: {
      title: 'Bigpipe Response',
      logo: {
        alt: 'Bigpipe Response Logo',
        src: 'img/logo.svg',
      },
      links: [
        {to: 'docs/main', label: 'Docs', position: 'left'},
//        {to: 'blog', label: 'Blog', position: 'left'},
//        {
//          href: 'https://github.com/facebook/docusaurus',
//          label: 'GitHub',
//          position: 'right',
//        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Docs',
              to: 'docs/main',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'Discord',
              href: 'https://discordapp.com/invite/docusaurus',
            },
          ],
        },
//        {
//          title: 'Social',
//          items: [
//            {
//              label: 'Blog',
//              to: 'blog',
//            },
//          ],
//        },
      ],
      logo: {
        alt: 'Facebook Open Source Logo',
        src: 'https://docusaurus.io/img/oss_logo.png',
      },
      copyright: `Copyright © ${new Date().getFullYear()} Facebook, Inc. Built with Docusaurus.`,
    },
  },
  presets: [
    [
      '@docusaurus/preset-classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
};
