import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { Amplify } from 'aws-amplify'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

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

const vuetify = createVuetify({
  components,
  directives,
})

import App from './App.vue'
import router from './router'

import './assets/main.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(vuetify)
app.mount('#app')
