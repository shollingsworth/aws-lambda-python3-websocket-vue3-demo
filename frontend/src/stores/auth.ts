import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { Auth, Hub } from 'aws-amplify'

export const useCounterStore = defineStore('auth', () => {
    Hub.listen('auth', ({ payload: { event, data } }) => {
        console.log('data', data)
        if (event === 'signIn') {
            Auth.currentAuthenticatedUser()
                .then((user) => {
                    console.log(user)
                })
                .catch((e) => {
                    console.log(e)
                })
        }
    })
    const count = ref(0)
    const doubleCount = computed(() => count.value * 2)
    function increment() {
        count.value++
    }

    return { count, doubleCount, increment }
})
