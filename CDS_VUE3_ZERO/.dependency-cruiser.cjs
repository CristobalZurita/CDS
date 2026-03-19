/** @type {import('dependency-cruiser').IConfiguration} */
module.exports = {
  forbidden: [
    {
      name: 'no-circular',
      severity: 'error',
      from: {},
      to: { circular: true },
    },
    {
      name: 'services-no-ui-deps',
      severity: 'error',
      comment: 'Los services solo deben encargarse de transporte y contratos.',
      from: { path: '^src/services' },
      to: { path: '^src/(pages|components|layouts|composables|stores)' },
    },
    {
      name: 'stores-no-ui-deps',
      severity: 'error',
      comment: 'Los stores no deben depender de capas de UI.',
      from: { path: '^src/stores' },
      to: { path: '^src/(pages|components|layouts)' },
    },
    {
      name: 'composables-no-page-deps',
      severity: 'error',
      comment: 'Los composables no deben importar pages ni layouts.',
      from: { path: '^src/composables' },
      to: { path: '^src/(pages|layouts)' },
    },
    {
      name: 'components-no-page-deps',
      severity: 'error',
      comment: 'Los componentes no deben importar pages ni layouts.',
      from: { path: '^src/components' },
      to: { path: '^src/(pages|layouts)' },
    },
    {
      name: 'ui-should-not-consume-generated-types-directly',
      severity: 'warn',
      comment: 'La UI debe usar services/composables; no depender directo del cliente generado.',
      from: { path: '^src/(pages|components|layouts)' },
      to: { path: '^src/services/generated' },
    },
  ],
  options: {
    doNotFollow: {
      path: 'node_modules',
    },
    exclude: {
      path: '^(dist|coverage|playwright-report|test-results)',
    },
    tsPreCompilationDeps: true,
    combinedDependencies: true,
    reporterOptions: {
      dot: {
        collapsePattern: 'node_modules/[^/]+',
      },
    },
  },
}
