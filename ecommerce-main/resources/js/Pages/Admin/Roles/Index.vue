<template>
    <div>
        <CrudComponent :form="form" @editing-item="handleEditingItem">
            <template #columns>
                <Column field="name" header="Name"></Column>
                <Column field="created_at" header="Created At" sortable></Column>
            </template>
            <template #form="{ submitted }">
                <Form :form="form" v-bind="{ submitted, permissions }" />
            </template>
        </CrudComponent>
    </div>
</template>
<script setup>
import CrudComponent from '@/Components/CrudComponent.vue';
import Form from './Form.vue';
import { useForm } from '@inertiajs/vue3';
const { permissions, items } = defineProps(['permissions', 'items'])

const form = useForm({
    name: '',
    ids: []
});

const handleEditingItem = (editingItem) => {
    const idsArray = items.data.filter(role => role.id === editingItem.id)
        .map(role => role.permissions)

    form.ids = idsArray[0];
}


</script>
