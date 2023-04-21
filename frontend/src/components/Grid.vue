<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { CanvasGrid } from '@/lib/grid'

const gridelement = ref()
const x = ref(0)
const y = ref(0)
// const showname = ref(false)

const grid = reactive(new CanvasGrid())

const setactive = () => {
    grid.addActiveCell(x.value, y.value)
}

onMounted(() => {
    grid.setup(gridelement.value, 50, 50)
})
</script>

<template>
    <!-- 
    <div>
        <button @click="grid.clearAll">Clear Board</button>
        <span v-if="grid.hovercell">x: {{ grid.hovercell.x }} y: {{ grid.hovercell.y }} state: {{ grid.mousestate }}</span>
    </div>
    <hr />
    -->
    <div>
        <span>
            <label>X: <input v-model="x" type="input" /></label>
            <label>Y: <input v-model="y" type="input" /></label>
            <button @click="setactive" color="green">Active</button>
        </span>
    </div>
    <div>
        <canvas ref="gridelement"></canvas>
    </div>
</template>
