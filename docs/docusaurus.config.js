const {themes} = require('prism-react-renderer');
const lightCodeTheme = themes.github;
const darkCodeTheme = themes.dracula;

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Monitor Switcher',
  tagline: 'Automate monitor inputs from USB device events',
  url: 'https://gayoon1234.github.io',
  baseUrl: '/monitor-switcher/',
  organizationName: 'Gayoon1234',
  projectName: 'monitor-switcher',
  onBrokenLinks: 'throw',
  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },
  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          path: '.',
          exclude: ['node_modules/**', 'build/**', '.docusaurus/**'],
          routeBasePath: '/',
          sidebarPath: './sidebars.js',
          editUrl: 'https://github.com/Gayoon1234/monitor-switcher/edit/main/docs/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],
  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      navbar: {
        title: 'Monitor Switcher',
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'documentation',
            position: 'left',
            label: 'Documentation',
          },
          {
            href: 'https://github.com/Gayoon1234/monitor-switcher',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        copyright: `Copyright ${new Date().getFullYear()} Monitor Switcher contributors.`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
        additionalLanguages: ['python', 'powershell'],
      },
    }),
};

module.exports = config;
