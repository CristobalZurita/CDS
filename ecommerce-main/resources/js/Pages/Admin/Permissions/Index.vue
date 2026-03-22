<template>
    <div>
        <CrudComponent :form="form" :can-delete="false" :can-edit="false">
            <template #messages>
                <small class="text-red-500">
                    *Permissions deletion disabled intentionally
                </small>
            </template>
            <template #columns>
                <Column field="name" header="Action Name"></Column>
                <!-- <Column field="isItCompleted" header="Is Completed"></Column> -->
                <!-- <Column field="created_at" header="Created At" sortable></Column> -->
            </template>
            <template #form="{ submitted }">
                <Form :form="form" v-bind="{ submitted }" />
            </template>
        </CrudComponent>
    </div>
</template>
<script setup>
import CrudComponent from '@/Components/CrudComponent.vue';
import Form from './Form.vue';
import { useForm } from '@inertiajs/vue3';

const form = useForm({
    name: '',
});


</script>
