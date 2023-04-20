import { Auth } from 'aws-amplify'
import type { CognitoUser } from 'amazon-cognito-identity-js'

export interface UserState {
    isAuthenticated: boolean
    username: string | null
    email: string | null
    jwtToken: string | null
}

export const getDefault = (): UserState => {
    return {
        isAuthenticated: false,
        username: null,
        email: null,
        jwtToken: null
    }
}

const getUserState = async (): Promise<UserState> => {
    return await Auth.currentAuthenticatedUser()
        .then((user: CognitoUser) => {
            var us = user.getSignInUserSession()
            var idtoken = us?.getIdToken()
            var atoken = us?.getAccessToken()
            return {
                isAuthenticated: true,
                username: user.getUsername() || null,
                email: idtoken?.payload.email.toString() || null,
                jwtToken: atoken?.getJwtToken() || null
            }
        })
        .catch((err) => {
            console.log(err)
            return {
                isAuthenticated: false,
                username: null,
                email: null,
                jwtToken: null
            }
        })
}

export default getUserState
