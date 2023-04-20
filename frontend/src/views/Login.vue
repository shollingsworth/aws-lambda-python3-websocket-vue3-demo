<script setup lang="ts">
import { Authenticator } from '@aws-amplify/ui-vue'
import '@aws-amplify/ui-vue/styles.css'
import getUserState from '@/lib/auth'
import { getDefault } from '@/lib/auth'
import type { UserState } from '@/lib/auth'
import { ref } from 'vue'

var us = ref<UserState>(getDefault())

getUserState().then((v) => {
    us.value = v
})
</script>
<template>
    <authenticator :social-providers="['google']" :hide-sign-up="true">
        <template v-slot="{ signOut }">
            <h1>Hello {{ us.email }}!</h1>
            <button @click="signOut">Sign Out</button>
        </template>
    </authenticator>
</template>
