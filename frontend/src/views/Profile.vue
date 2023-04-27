<script setup lang="ts">
import { Authenticator } from '@aws-amplify/ui-vue'
import '@aws-amplify/ui-vue/styles.css'
import { useAuthStore } from '@/stores/auth'

const us = useAuthStore()
</script>
<template>
    <authenticator :social-providers="['google']" :hide-sign-up="true">
        <template v-slot="{ signOut }">
            <h1>Hello {{ us.email }}!</h1>
            <v-btn color="red" @click="signOut">Sign Out</v-btn>
            <!-- 
            <code>{{ JSON.stringify(us, null, 2) }}</code>
            -->
        </template>
    </authenticator>
</template>
