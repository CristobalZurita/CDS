import { spawnSync } from 'node:child_process'
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import openapiTS, { COMMENT_HEADER, astToString } from 'openapi-typescript'

const scriptDir = dirname(fileURLToPath(import.meta.url))
const frontendRoot = resolve(scriptDir, '..')
const backendRoot = resolve(frontendRoot, '..', 'backend')
const outputFile = resolve(frontendRoot, 'src/services/generated/openapi.d.ts')

async function loadSpecFromFile(filePath) {
  const raw = await readFile(filePath, 'utf8')
  return JSON.parse(raw)
}

async function loadSpecFromUrl(openapiUrl) {
  const response = await fetch(openapiUrl)
  if (!response.ok) {
    throw new Error(`No se pudo descargar OpenAPI desde ${openapiUrl}: HTTP ${response.status}`)
  }
  return response.json()
}

function loadSpecFromBackendImport() {
  const pythonSource = `
import json
import logging
import sys

logging.disable(logging.CRITICAL)
sys.path.insert(0, ${JSON.stringify(backendRoot)})

from app.main import app

print(json.dumps(app.openapi(), ensure_ascii=False))
`.trim()

  const result = spawnSync('python3', ['-c', pythonSource], {
    cwd: backendRoot,
    encoding: 'utf8',
    env: {
      ...process.env,
      PYTHONIOENCODING: 'utf-8',
    },
  })

  if (result.status !== 0) {
    throw new Error(result.stderr || 'No se pudo importar el backend para generar OpenAPI.')
  }

  return JSON.parse(result.stdout)
}

async function loadSpec() {
  const openapiInput = String(process.env.OPENAPI_INPUT || '').trim()
  if (openapiInput) {
    return loadSpecFromFile(resolve(frontendRoot, openapiInput))
  }

  const openapiUrl = String(process.env.OPENAPI_URL || '').trim()
  if (openapiUrl) {
    return loadSpecFromUrl(openapiUrl)
  }

  return loadSpecFromBackendImport()
}

async function main() {
  const spec = await loadSpec()
  const generatedAst = await openapiTS(spec, {
    alphabetize: true,
  })
  const generated = `${COMMENT_HEADER}${astToString(generatedAst)}`

  await mkdir(dirname(outputFile), { recursive: true })
  await writeFile(
    outputFile,
    ['/* eslint-disable */', generated, ''].join('\n'),
    'utf8'
  )

  console.log(`OpenAPI types generated in ${outputFile}`)
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error))
  process.exit(1)
})
