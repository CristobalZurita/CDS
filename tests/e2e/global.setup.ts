import { execFileSync } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const currentDir = path.dirname(fileURLToPath(import.meta.url))
const repoRoot = path.resolve(currentDir, '../..')

function resolvePythonBinary(): string {
  const venvPython = path.join(repoRoot, 'backend', '.venv', 'bin', 'python')
  return venvPython
}

export default async function globalSetup() {
  execFileSync(resolvePythonBinary(), [path.join(repoRoot, 'scripts', 'e2e', 'seed_users.py')], {
    cwd: repoRoot,
    stdio: 'inherit',
  })
}
