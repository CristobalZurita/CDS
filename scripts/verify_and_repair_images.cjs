#!/usr/bin/env node
/**
 * Script de verificación y reparación de imágenes
 * 
 * Este script:
 * 1. Escanea todas las imágenes locales en public/images/
 * 2. Verifica si están disponibles en Cloudinary
 * 3. Genera un reporte de qué imágenes necesitan atención
 * 
 * Uso: node scripts/verify_and_repair_images.js
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

const CLOUD_NAME = 'dgwwi77ic';
const BASE_URL = `https://res.cloudinary.com/${CLOUD_NAME}/image/upload`;
const IMAGES_DIR = path.join(__dirname, '..', 'CDS_VUE3_ZERO', 'public', 'images');

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
        cloudinary: `${BASE_URL}/images/${relativePath}`,
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
  
  // Generar archivo de mapeo
  console.log('\n📝 Generando archivo de mapeo...');
  
  const mapping = images.map(img => ({
    local: img.local,
    cloudinary: img.cloudinary,
    // URL alternativa sin versión (funciona si la imagen existe)
    altUrl: img.cloudinary
  }));
  
  const outputFile = path.join(__dirname, '..', 'image-mapping.json');
  fs.writeFileSync(outputFile, JSON.stringify(mapping, null, 2));
  
  console.log(`   📄 Guardado en: ${outputFile}`);
  
  // Instrucciones
  console.log(`
═══════════════════════════════════════════════════════════════
                    INSTRUCCIONES
═══════════════════════════════════════════════════════════════

1. Si las imágenes fallan, verifica en Cloudinary Console:
   https://cloudinary.com/console

2. Asegúrate de que las imágenes estén en la carpeta correcta:
   - images/personales/
   - images/instrumentos/
   - images/INVENTARIO/
   - images/calculadoras/
   - images/logo/

3. Si las URLs tienen versión (v1234567890), usa este formato:
   ${BASE_URL}/vVERSION/images/personales/foto.webp

4. El código ya tiene fallback automático a local si Cloudinary falla.

5. Para subir imágenes faltantes, arrastra la carpeta completa
   a Cloudinary Media Library.

═══════════════════════════════════════════════════════════════
`);
}

main().catch(console.error);
