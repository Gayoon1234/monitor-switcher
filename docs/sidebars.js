/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  documentation: [
    'index',
    'technical-implementation',
    'road-map',
    {
      type: 'category',
      label: 'Application',
      items: [
        {
          type: 'category',
          label: 'CLI',
          items: [
            'cli/index',
            'cli/commands/index',
          ],
        },
        {
          type: 'category',
          label: 'Hardware',
          items: [
            {
              type: 'category',
              label: 'Abstract Classes',
              items: [
                'hardware/Abstract Classes/monitor',
                'hardware/Abstract Classes/usb',
              ],
            },
            {
              type: 'category',
              label: 'Implementations',
              items: [
                'hardware/Implementations/windows-monitor',
                'hardware/Implementations/windows-usb',
              ],
            },
          ],
        },
        {
          type: 'category',
          label: 'Models',
          items: [
            {
              type: 'category',
              label: 'Data Models',
              items: [
                'models/Data Models/automation',
                'models/Data Models/usb-device',
                'models/Data Models/display',
              ],
            },
            {
              type: 'category',
              label: 'Event Models',
              items: [
                'models/Event Models/activity-event',
                'models/Event Models/device-event',
              ],
            },
          ],
        },
        {
          type: 'category',
          label: 'Services',
          items: ['services/index'],
        },
        {
          type: 'category',
          label: 'UI',
          items: [
            'ui/index',
            {
              type: 'category',
              label: 'Pages',
              items: ['ui/pages/index'],
            },
            {
              type: 'category',
              label: 'Widgets',
              items: ['ui/widgets/index'],
            },
          ],
        },
      ],
    },
  ],
};

module.exports = sidebars;
