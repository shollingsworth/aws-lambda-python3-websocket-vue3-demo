import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { Amplify } from 'aws-amplify'
Amplify.configure({
    Auth: {
        region: 'us-east-2',
        userPoolId: 'us-east-2_y3Mq2SZ54',
        userPoolWebClientId: '1tpl86djh4g2uslurljii62sgd',
        oauth: {
            domain: 'sh-ws-demo.auth.us-east-2.amazoncognito.com',
            scope: ['email', 'openid'],
            redirectSignIn: 'http://localhost:8080',
            redirectSignOut: 'http://localhost:8080',
            responseType: 'code'
        }
    }
})

import App from './App.vue'
import router from './router'

import './assets/main.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
