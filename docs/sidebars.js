/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  documentation: [
    'index',
    {
      type: 'category',
      label: 'Technical implementation',
      link: {
        type: 'doc',
        id: 'technical-implementation',
      },
      items: ['technical-implementation/performance-testing'],
    },
    'road-map',
  ],
};

module.exports = sidebars;
