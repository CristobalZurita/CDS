/**
 * Mapa de ciudades/comunas de Chile → nombre de región.
 * Clave: nombre en minúsculas sin tilde.
 * Se usa para autocompletar el campo región al ingresar ciudad.
 */
const CITY_TO_REGION = {
  // Arica y Parinacota
  'arica': 'Arica y Parinacota',
  'putre': 'Arica y Parinacota',

  // Tarapacá
  'iquique': 'Tarapacá',
  'alto hospicio': 'Tarapacá',

  // Antofagasta
  'antofagasta': 'Antofagasta',
  'calama': 'Antofagasta',
  'tocopilla': 'Antofagasta',
  'mejillones': 'Antofagasta',
  'taltal': 'Antofagasta',

  // Atacama
  'copiapo': 'Atacama',
  'copiapó': 'Atacama',
  'vallenar': 'Atacama',
  'chanaral': 'Atacama',
  'chañaral': 'Atacama',
  'caldera': 'Atacama',

  // Coquimbo
  'la serena': 'Coquimbo',
  'coquimbo': 'Coquimbo',
  'ovalle': 'Coquimbo',
  'illapel': 'Coquimbo',
  'los vilos': 'Coquimbo',
  'vicuna': 'Coquimbo',
  'vicuña': 'Coquimbo',

  // Valparaíso
  'valparaiso': 'Valparaíso',
  'valparaíso': 'Valparaíso',
  'vina del mar': 'Valparaíso',
  'viña del mar': 'Valparaíso',
  'quilpue': 'Valparaíso',
  'quilpué': 'Valparaíso',
  'villa alemana': 'Valparaíso',
  'san antonio': 'Valparaíso',
  'los andes': 'Valparaíso',
  'la ligua': 'Valparaíso',
  'quillota': 'Valparaíso',
  'san felipe': 'Valparaíso',
  'limache': 'Valparaíso',
  'olmue': 'Valparaíso',
  'olmué': 'Valparaíso',
  'casablanca': 'Valparaíso',
  'cartagena': 'Valparaíso',
  'el quisco': 'Valparaíso',
  'algarrobo': 'Valparaíso',

  // Metropolitana
  'santiago': 'Metropolitana',
  'providencia': 'Metropolitana',
  'maipu': 'Metropolitana',
  'maipú': 'Metropolitana',
  'la florida': 'Metropolitana',
  'las condes': 'Metropolitana',
  'nunoa': 'Metropolitana',
  'ñuñoa': 'Metropolitana',
  'pudahuel': 'Metropolitana',
  'puente alto': 'Metropolitana',
  'la pintana': 'Metropolitana',
  'penalolen': 'Metropolitana',
  'peñalolén': 'Metropolitana',
  'el bosque': 'Metropolitana',
  'san bernardo': 'Metropolitana',
  'talagante': 'Metropolitana',
  'melipilla': 'Metropolitana',
  'buin': 'Metropolitana',
  'colina': 'Metropolitana',
  'lampa': 'Metropolitana',
  'paine': 'Metropolitana',
  'vitacura': 'Metropolitana',
  'lo barnechea': 'Metropolitana',
  'huechuraba': 'Metropolitana',
  'independencia': 'Metropolitana',
  'recoleta': 'Metropolitana',
  'quilicura': 'Metropolitana',
  'cerrillos': 'Metropolitana',
  'cerro navia': 'Metropolitana',
  'conchali': 'Metropolitana',
  'conchalí': 'Metropolitana',
  'estacion central': 'Metropolitana',
  'estación central': 'Metropolitana',
  'la cisterna': 'Metropolitana',
  'la granja': 'Metropolitana',
  'la reina': 'Metropolitana',
  'lo espejo': 'Metropolitana',
  'lo prado': 'Metropolitana',
  'macul': 'Metropolitana',
  'mipuco': 'Metropolitana',
  'padre hurtado': 'Metropolitana',
  'pedro aguirre cerda': 'Metropolitana',
  'peñaflor': 'Metropolitana',
  'penaflor': 'Metropolitana',
  'renca': 'Metropolitana',
  'san joaquin': 'Metropolitana',
  'san miguel': 'Metropolitana',
  'san ramon': 'Metropolitana',
  'san ramón': 'Metropolitana',

  // O'Higgins
  'rancagua': "O'Higgins",
  'san fernando': "O'Higgins",
  'pichilemu': "O'Higgins",
  'rengo': "O'Higgins",
  'santa cruz': "O'Higgins",

  // Maule
  'talca': 'Maule',
  'curico': 'Maule',
  'curicó': 'Maule',
  'linares': 'Maule',
  'constitucion': 'Maule',
  'constitución': 'Maule',
  'cauquenes': 'Maule',
  'molina': 'Maule',

  // Ñuble
  'chillan': 'Ñuble',
  'chillán': 'Ñuble',
  'chillan viejo': 'Ñuble',
  'chillán viejo': 'Ñuble',
  'san carlos': 'Ñuble',
  'bulnes': 'Ñuble',

  // Biobío
  'concepcion': 'Biobío',
  'concepción': 'Biobío',
  'talcahuano': 'Biobío',
  'los angeles': 'Biobío',
  'los ángeles': 'Biobío',
  'coronel': 'Biobío',
  'lota': 'Biobío',
  'tome': 'Biobío',
  'tomé': 'Biobío',
  'hualpen': 'Biobío',
  'hualpén': 'Biobío',
  'chiguayante': 'Biobío',
  'san pedro de la paz': 'Biobío',

  // Araucanía
  'temuco': 'La Araucanía',
  'padre las casas': 'La Araucanía',
  'villarrica': 'La Araucanía',
  'pucon': 'La Araucanía',
  'pucón': 'La Araucanía',
  'angol': 'La Araucanía',
  'nueva imperial': 'La Araucanía',

  // Los Ríos
  'valdivia': 'Los Ríos',
  'la union': 'Los Ríos',
  'la unión': 'Los Ríos',

  // Los Lagos
  'puerto montt': 'Los Lagos',
  'osorno': 'Los Lagos',
  'castro': 'Los Lagos',
  'puerto varas': 'Los Lagos',
  'ancud': 'Los Lagos',
  'calbuco': 'Los Lagos',

  // Aysén
  'coyhaique': 'Aysén',
  'chile chico': 'Aysén',
  'cochrane': 'Aysén',

  // Magallanes
  'punta arenas': 'Magallanes',
  'puerto natales': 'Magallanes',
  'puerto williams': 'Magallanes',
}

/**
 * Dado un nombre de ciudad, retorna la región de Chile correspondiente.
 * Retorna null si no hay match.
 * @param {string} city
 * @returns {string|null}
 */
export function getRegionForCity(city) {
  if (!city) return null
  const key = city.trim().toLowerCase()
  return CITY_TO_REGION[key] ?? null
}
