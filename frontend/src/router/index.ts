import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import Profile from '../views/Profile.vue'
import PageNotFound from '../views/PageNotFound.vue'
import { useAuthStore } from '@/stores/auth'

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


router.beforeEach(async (to) => {
    // make sure creds are loaded before each route
    const auth = useAuthStore()
    await auth.loadCreds()
    // console.log('to', to.path, 'from', from.path, 'isAuthenticated', auth.isAuthenticated)
    if (to.name !== 'profile' && !auth.isAuthenticated) return '/profile'
})

export default router
