import httpx
import json
import asyncio
from datetime import datetime

BASE_FRONT = 'http://localhost:5173'
BASE_API = 'http://localhost:8000'


async def main():
    results = []

    async with httpx.AsyncClient(timeout=10) as client:

        # 1. FRONTEND CARGA
        try:
            r = await client.get(BASE_FRONT)
            results.append(('FRONTEND', '/', r.status_code,
                'OK' if r.status_code == 200 else 'FAIL'))
        except Exception as e:
            results.append(('FRONTEND', '/', 0, f'ERROR: {e}'))

        # 2. API HEALTH
        for path in ['/health', '/health', '/docs']:
            try:
                r = await client.get(BASE_API + path)
                results.append(('API_PUBLIC', path, r.status_code,
                    'OK' if r.status_code < 400 else 'FAIL'))
            except Exception as e:
                results.append(('API_PUBLIC', path, 0, f'ERROR: {e}'))

        # 3. LOGIN Y TOKEN
        token = None
        try:
            r = await client.post(BASE_API + '/api/v1/auth/login',
                json={'email': 'admin@example.com', 'password': 'admin12'})
            if r.status_code == 200:
                token = r.json().get('access_token')
                results.append(('AUTH', 'login', r.status_code, 'OK — token obtained'))
            else:
                results.append(('AUTH', 'login', r.status_code, f'FAIL — {r.text[:100]}'))
        except Exception as e:
            results.append(('AUTH', 'login', 0, f'ERROR: {e}'))

        # 4. TODOS LOS ENDPOINTS DEL OPENAPI
        try:
            r = await client.get(BASE_API + '/openapi.json')
            spec = r.json()
            headers = {'Authorization': f'Bearer {token}'} if token else {}

            for path, methods in spec['paths'].items():
                for method in methods:
                    if method not in ['get', 'post', 'put', 'patch', 'delete']:
                        continue
                    if 'stream' in path or 'websocket' in path or 'ws' in path:
                        results.append((f'API_{method.upper()}', path, 0, 'SKIP — streaming endpoint'))
                        continue
                    url = BASE_API + path
                    # reemplaza params de path con valor de prueba
                    url = url.replace('{id}', '1').replace('{token}', 'test')
                    try:
                        if method == 'get':
                            res = await client.get(url, headers=headers)
                        else:
                            res = await client.request(method.upper(), url,
                                headers=headers, json={})
                        status = 'OK' if res.status_code < 500 else 'BROKEN_500'
                        results.append((f'API_{method.upper()}', path,
                            res.status_code, status))
                    except Exception as e:
                        results.append((f'API_{method.upper()}', path,
                            0, f'ERROR: {e}'))
        except Exception as e:
            results.append(('API_SCAN', 'openapi', 0, f'ERROR: {e}'))

    # REPORTE
    broken = [r for r in results if 'FAIL' in r[3] or 'BROKEN' in r[3] or 'ERROR' in r[3]]
    ok = [r for r in results if r not in broken]

    report = f"""# CDS AUDIT REPORT — {datetime.now().strftime('%Y-%m-%d %H:%M')}

## RESUMEN
Total checks: {len(results)}
Pasaron: {len(ok)}
Fallaron: {len(broken)}

## CRÍTICOS — ROTO
"""
    for b in broken:
        report += f"  {b[0]} | {b[1]} | HTTP {b[2]} | {b[3]}\n"

    report += "\n## OK\n"
    for o in ok:
        report += f"  {o[0]} | {o[1]} | HTTP {o[2]} | {o[3]}\n"

    with open('reports/AUDIT_HEADLESS.md', 'w') as f:
        f.write(report)
    print(report)


asyncio.run(main())
