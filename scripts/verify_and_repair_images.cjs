#!/usr/bin/env node
/**
 * Script de verificación y reparación de imágenes
 * 
 * Este script:
 * 1. Escanea todas las imágenes locales en CDS_VUE3_ZERO/public/images/
 * 2. Verifica si están disponibles en Cloudinary usando el contrato canónico
 * 3. Genera un reporte simple de qué imágenes necesitan atención
 * 
 * Uso: node scripts/verify_and_repair_images.js
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

function readEnvValue(filePath, key) {
  if (!fs.existsSync(filePath)) return '';
  const content = fs.readFileSync(filePath, 'utf8');
  const match = content.match(new RegExp(`^${key}=(.*)$`, 'm'));
  if (!match) return '';
  return String(match[1] || '').trim().replace(/^['"]|['"]$/g, '');
}

function resolveCloudName() {
  const projectRoot = path.join(__dirname, '..');
  const frontendDir = path.join(projectRoot, 'CDS_VUE3_ZERO');
  const candidates = [
    process.env.VITE_CLOUDINARY_CLOUD_NAME,
    process.env.CLOUDINARY_CLOUD_NAME,
    readEnvValue(path.join(frontendDir, '.env'), 'VITE_CLOUDINARY_CLOUD_NAME'),
    readEnvValue(path.join(frontendDir, '.env.local'), 'VITE_CLOUDINARY_CLOUD_NAME'),
    readEnvValue(path.join(frontendDir, '.env.example'), 'VITE_CLOUDINARY_CLOUD_NAME'),
  ];

  return candidates.find(Boolean) || '';
}

const CLOUD_NAME = resolveCloudName();
if (!CLOUD_NAME) {
  console.error('❌ No se encontró VITE_CLOUDINARY_CLOUD_NAME para verificar imágenes.');
  process.exit(1);
}

const BASE_URL = `https://res.cloudinary.com/${CLOUD_NAME}/image/upload`;
const IMAGES_DIR = path.join(__dirname, '..', 'CDS_VUE3_ZERO', 'public', 'images');

function localPathToPublicId(localPath) {
  return String(localPath || '')
    .replace(/^\/images\//, '')
    .replace(/\.[^.]+$/, '');
}

function publicIdToCloudinaryUrl(publicId) {
  return `${BASE_URL}/${publicId.split('/').map(encodeURIComponent).join('/')}`;
}

// Encontrar todas las imágenes
function findImages(dir, basePath = '') {
  const images = [];
  const items = fs.readdirSync(dir, { withFileTypes: true });
  
  for (const item of items) {
    const fullPath = path.join(dir, item.name);
    const relativePath = basePath ? `${basePath}/${item.name}` : item.name;
    
    if (item.isDirectory()) {
      images.push(...findImages(fullPath, relativePath));
    } else if (/\.(webp|png|jpg|jpeg|gif)$/i.test(item.name)) {
        images.push({
          local: `/images/${relativePath}`,
          cloudinary: publicIdToCloudinaryUrl(localPathToPublicId(`/images/${relativePath}`)),
        filename: item.name,
        folder: basePath
      });
    }
  }
  
  return images;
}

// Verificar si URL existe
function checkUrl(url) {
  return new Promise((resolve) => {
    const req = https.get(url, { method: 'HEAD', timeout: 5000 }, (res) => {
      resolve(res.statusCode === 200);
    });
    req.on('error', () => resolve(false));
    req.on('timeout', () => { req.destroy(); resolve(false); });
  });
}

// Función principal
async function main() {
  console.log('🔍 Escaneando imágenes locales...\n');
  
  if (!fs.existsSync(IMAGES_DIR)) {
    console.error('❌ No se encontró la carpeta:', IMAGES_DIR);
    process.exit(1);
  }
  
  const images = findImages(IMAGES_DIR);
  console.log(`📸 Encontradas ${images.length} imágenes locales\n`);
  
  // Verificar algunas imágenes de muestra
  const sampleSize = 10;
  const sample = images.slice(0, sampleSize);
  
  console.log(`🌐 Verificando ${sampleSize} imágenes de muestra en Cloudinary...\n`);
  
  let working = 0;
  let failed = 0;
  
  for (const img of sample) {
    process.stdout.write(`   Probando: ${img.local} ... `);
    const exists = await checkUrl(img.cloudinary);
    
    if (exists) {
      console.log('✅ OK');
      working++;
    } else {
      console.log('❌ No encontrada');
      console.log(`      URL: ${img.cloudinary}`);
      failed++;
    }
  }
  
  console.log(`\n📊 RESULTADO MUESTRA: ${working} OK, ${failed} fallidas`);
  
  // Instrucciones
  console.log(`
═══════════════════════════════════════════════════════════════
                    INSTRUCCIONES
═══════════════════════════════════════════════════════════════

1. Si las imágenes fallan, verifica en Cloudinary Console:
   https://cloudinary.com/console

2. Asegúrate de que las imágenes estén en la carpeta correcta:
   - personales/
   - instrumentos/
   - INVENTARIO/
   - calculadoras/
   - logo/

3. La URL canónica es:
   ${BASE_URL}/personales/foto

4. El runtime deriva public_id desde /images/... y no depende de image-mapping.json.

5. Para subir imágenes faltantes, arrastra el contenido dentro de images/
   y no la carpeta raíz images/.

═══════════════════════════════════════════════════════════════
`);
}

main().catch(console.error);
