import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import Profile from '../views/Profile.vue'
import PageNotFound from '../views/PageNotFound.vue'
import AuthState from '@/lib/auth'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            component: HomePage
        },
        {
            path: '/profile',
            name: 'profile',
            component: Profile
        },
        {
            path: '/:pathMatch(.*)*',
            name: '404',
            component: PageNotFound
        }
    ]
})

router.beforeEach(async (to, from) => {
    const auth = await AuthState.getState()
    console.log('to', to.path, 'from', from.path, 'isAuthenticated', auth.isAuthenticated)
    if (to.name !== 'profile' && !auth.isAuthenticated) return '/profile'
})

export default router
