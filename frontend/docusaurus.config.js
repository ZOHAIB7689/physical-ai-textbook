{
  "presets": [
    [
      "@docusaurus/preset-classic",
      {
        "docs": {
          "sidebarPath": require.resolve("./sidebar.js"),
          "editUrl": "https://github.com/specifyplus/physical-ai-textbook/edit/main/"
        },
        "theme": {
          "customCss": [require.resolve("./src/css/custom.css")]
        }
      }
    ]
  ],
  "plugins": [
    "@docusaurus/plugin-content-docs",
    "@docusaurus/plugin-content-blog",
    "@docusaurus/plugin-sitemap"
  ]
}