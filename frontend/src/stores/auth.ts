import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { CognitoUser } from 'amazon-cognito-identity-js'
import { Auth } from 'aws-amplify'
import AppConfig from '@/lib/config'

export const useAuthStore = defineStore('auth', () => {
    const isAuthenticated = ref(false)
    const username = ref('')
    const email = ref('')
    const authJwtToken = ref('')
    const idJwtToken = ref('')
    const linkname = ref('Login')
    const wsUrl = ref('')

    const clearCreds = () => {
        wsUrl.value = ''
        isAuthenticated.value = false
        username.value = ''
        email.value = ''
        authJwtToken.value = ''
        idJwtToken.value = ''
        linkname.value = 'Login'
    }

    const loadCreds = async () => {
        try {
            const user = await Auth.currentAuthenticatedUser()
            setValues(user)
        } catch (err) {
            clearCreds()
        }
    }

    const setValues = (user: CognitoUser) => {
        isAuthenticated.value = true
        username.value = user.getUsername()
        email.value = user.getUsername()
        email.value = user.getUsername()
        linkname.value = 'Profile'
        isAuthenticated.value = true
        const sess = user.getSignInUserSession()
        const idtok = sess?.getIdToken()
        if (idtok) {
            idJwtToken.value = idtok.getJwtToken()
        }
        const authtok = sess?.getAccessToken()
        if (authtok) {
            authJwtToken.value = authtok.getJwtToken()
        }
        email.value = idtok?.payload.email
        wsUrl.value = AppConfig.wsUrl(idJwtToken.value)
    }

    return {
        loadCreds,
        setValues,
        wsUrl,
        clearCreds,
        isAuthenticated,
        username,
        email,
        authJwtToken,
        idJwtToken,
        linkname
    }
})
