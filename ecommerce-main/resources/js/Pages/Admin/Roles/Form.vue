<template>
    <div>
        <div class="mb-3">
            <label for="name" class="block font-bold mb-2">Name</label>
            <InputText id="name" v-model.trim="form.name" required="true" autofocus :invalid="submitted && !form.name"
                fluid />
            <small v-if="submitted && !form.name" class="text-red-500">Name is required.</small>
        </div>
        <div class="mb-3">
            <DataTable :value="permissions" v-model:selection="form.ids" dataKey="id">
                <Column selectionMode="multiple" style="width: 3rem" :exportable="false" header=""></Column>
                <Column field="name" header="Permission Name"></Column>
            </DataTable>
        </div>
    </div>
</template>

<script setup>

defineProps({
    form: {
        type: Object,
        required: true
    },
    submitted: Boolean,
    permissions: Object,
});
</script>
