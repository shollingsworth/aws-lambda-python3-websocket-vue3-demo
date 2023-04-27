<script setup lang="ts">
import { ref, onMounted, onUnmounted, reactive } from 'vue'
import { CanvasGrid } from '@/lib/grid'

const gridelement = ref()
const grid = reactive(new CanvasGrid())

/**
const x = ref(0)
const y = ref(0)
const rando = () => {
    grid.randomActiveCell()
}

const setactive = () => {
    grid.addActiveCell(x.value, y.value)
}
*/

onMounted(() => {
    grid.setup(gridelement.value)
})

onUnmounted(() => {
    grid.close()
})

</script>

<template>
    <v-container>
        <v-row>
            <v-col>
                <v-btn color="orange" @click="grid.clearAlertBoxes()">Clear Alert Boxes</v-btn>
                <v-btn color="red" @click="grid.clearBackendState()">Clear BackendState</v-btn>
            </v-col>
            <v-col>
                x: {{ grid.hovercell?.x || 'n/a' }} y: {{ grid.hovercell?.y || 'n/a' }} state:
                {{ grid.mousestate }}
            </v-col>
        </v-row>
        <!-- 
                <v-btn color="blue" @click="grid.testToast()">Test Toast</v-btn>
        <v-row>
            <v-col>
                <v-text-field v-model="x" label="X" />
            </v-col>
            <v-col>
                <v-text-field v-model="y" label="Y" />
            </v-col>
            <v-col>
                <v-btn @click="setactive" color="green">Active</v-btn>
                <v-btn @click="rando" color="red">Random</v-btn>
            </v-col>
        </v-row>
            <v-col>
                <v-card>
                    <v-card-title>Active Cells</v-card-title>
                    <v-card-text>
                        <v-list>
                            <v-list-item>
                                <v-list-item-title>Title</v-list-item-title>
                                <v-list-item-subtitle>Subtitle</v-list-item-subtitle>
                                hello
                            </v-list-item>
                        </v-list>
                    </v-card-text>
                </v-card>
            </v-col>
        -->
        <v-row>
            <v-col>
                <canvas ref="gridelement" />
            </v-col>
        </v-row>
    </v-container>
</template>
