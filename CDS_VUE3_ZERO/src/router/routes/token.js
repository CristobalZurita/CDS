const SignaturePage = () => import('@new/pages/token/SignaturePage.vue')
const PhotoUploadPage = () => import('@new/pages/token/PhotoUploadPage.vue')

export const tokenRoutes = [
  { path: '/signature/:token', name: 'signature', component: SignaturePage, meta: { requiresAuth: false } },
  { path: '/photo-upload/:token', name: 'photo-upload', component: PhotoUploadPage, meta: { requiresAuth: false } }
]
