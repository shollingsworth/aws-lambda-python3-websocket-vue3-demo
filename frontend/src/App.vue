<script setup lang="ts">
import { RouterView } from 'vue-router'
import AppConfig from '@/lib/config'
import { ref, onUnmounted } from 'vue'
import { Hub } from 'aws-amplify'
import { useAuthStore } from '@/stores/auth'
import { useGeneralStore } from '@/stores/general'
import type { CognitoUser } from 'amazon-cognito-identity-js'

const auth = useAuthStore()
const general = useGeneralStore()

const hubListener = Hub.listen('auth', (data) => {
    switch (data.payload.event) {
        case 'tokenRefresh':
            auth.loadCreds()
            break
        case 'signIn':
            const user = data.payload.data as CognitoUser
            auth.setValues(user)
            break
        case 'oAuthSignOut':
            console.log('oAuthSignOut')
            auth.clearCreds()
            break
        case 'signOut':
            console.log('user signed out')
            auth.clearCreds()
            break
        case 'signIn_failure':
            console.log('user sign in failed')
            auth.clearCreds()
            break
    }
})

onUnmounted(() => {
    hubListener()
})

const config = ref(AppConfig)
</script>
<template>
    <v-app>
        <v-main>
            <v-app-bar app>
                <v-toolbar-title>
                    Griddle
                    <v-chip>{{ config.stage }}</v-chip>
                </v-toolbar-title>
                <v-chip :color="general.color">{{ general.connectionId }}</v-chip>
                <v-btn :to="{ name: 'home' }">Home</v-btn>
                <v-btn :to="{ name: 'profile' }">{{ auth.linkname }}</v-btn>
            </v-app-bar>
            <RouterView />
        </v-main>
    </v-app>
</template>
