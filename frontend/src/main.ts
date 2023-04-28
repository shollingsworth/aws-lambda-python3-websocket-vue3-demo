import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { Amplify } from 'aws-amplify'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import ToastPlugin from 'vue-toast-notification'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import AppConfig from '@/lib/config'
import 'vue-toast-notification/dist/theme-bootstrap.css'

const config = new AppConfig()

Amplify.configure({
    Auth: {
        region: import.meta.env.VITE_AWS_REGION,
        userPoolId: import.meta.env.VITE_USER_POOL_ID,
        userPoolWebClientId: import.meta.env.VITE_CLIENT_ID,
        oauth: {
            domain: import.meta.env.VITE_COGNITO_DOMAIN,
            scope: ['email', 'openid'],
            redirectSignIn: config.redirectUrl,
            redirectSignOut: config.redirectUrl,
            responseType: 'code'
        }
    }
})

const vuetify = createVuetify({
    components,
    directives
})

import App from './App.vue'
import router from './router'

import './assets/main.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(vuetify)
app.use(ToastPlugin)
app.mount('#app')
