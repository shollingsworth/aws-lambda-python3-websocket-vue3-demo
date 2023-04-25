<script setup lang="ts">
import { Authenticator } from '@aws-amplify/ui-vue'
import '@aws-amplify/ui-vue/styles.css'
import AuthState, { type UserState } from '@/lib/auth'
import { ref } from 'vue'

var us = ref<UserState>(AuthState.getDefault())
AuthState.getState().then((v) => {
    us.value = v
})
</script>
<template>
    <authenticator :social-providers="['google']" :hide-sign-up="true">
        <template v-slot="{ signOut }">
            <h1>Hello {{ us.email }}!</h1>
            <v-btn color="red" @click="signOut">Sign Out</v-btn>
            <!-- 
            <pre>{{ JSON.stringify(us, null, 2) }}</pre>
            -->
        </template>
    </authenticator>
</template>
