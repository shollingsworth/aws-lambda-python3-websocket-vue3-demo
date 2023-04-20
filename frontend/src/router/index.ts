import { createRouter, createWebHistory } from 'vue-router'
import AboutView from '../views/AboutView.vue'
import Login from '../views/Login.vue'
import getUserState from '@/lib/auth'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            component: AboutView
        },
        {
            path: '/login',
            name: 'login',
            component: Login
        },
    ]
})

router.beforeEach(async (to, from) => {
    const auth = await getUserState()
    console.log('to', to.path, 'from', from.path, 'isAuthenticated', auth.isAuthenticated)
    if (to.name !== 'login' && !auth.isAuthenticated) return '/login'
})

export default router
