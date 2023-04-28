import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { CognitoUser } from 'amazon-cognito-identity-js'
import { Auth } from 'aws-amplify'
import AppConfig from '@/lib/config'

const config = new AppConfig()

export const useAuthStore = defineStore('auth', () => {
    const isAuthenticated = ref(false)
    const username = ref('not logged in')
    const email = ref('not logged in')
    const authJwtToken = ref('')
    const idJwtToken = ref('')
    const linkname = ref('Login')
    const wsUrl = ref('')

    const clearCreds = () => {
        wsUrl.value = ''
        isAuthenticated.value = false
        username.value = 'not logged in'
        email.value = 'not logged in'
        authJwtToken.value = ''
        idJwtToken.value = ''
        linkname.value = 'Login'
    }

    const signOut = async () => {
        try {
            await Auth.signOut()
            clearCreds()
        } catch (err) {
            console.log(err)
        }
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
        wsUrl.value = config.wsUrl(idJwtToken.value)
    }

    return {
        signOut,
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
