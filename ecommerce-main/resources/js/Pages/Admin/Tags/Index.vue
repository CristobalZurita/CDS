<template>
    <div>
        <CrudComponent :form>
            <template #columns>
                <Column field="name" header="Name"></Column>
                <Column field="is_active" header="Status">
                    <template #body="{ data }">
                        <Badge :severity="data.is_active ? 'success' : 'danger'">
                            {{ data.is_active ? 'Active' : 'Inactive' }}
                        </Badge>
                    </template>
                </Column>

                <Column field="created_at" header="Created At" sortable></Column>
                <Column field="updated_at" header="Updated At" sortable></Column>
            </template>

            <template #form="{ submitted, statuses }">
                <div class="flex flex-col gap-6">
                    <div>
                        <label for="name" class="block font-bold mb-2">Name</label>
                        <InputText id="name" v-model.trim="form.name" required="true" autofocus
                            :invalid="submitted && !form.name" fluid />
                        <small v-if="submitted && !form.name" class="text-red-500">Name is required.</small>
                    </div>
                </div>
                <div class="flex flex-col gap-6 mt-3">
                    <div>
                        <label for="is_active" class="block font-bold mb-2">Status</label>
                        <Select v-model="form.is_active" :options="statuses" optionLabel="label" optionValue="value"
                            placeholder="Select a status" class="w-full" :required="true" />
                        <small v-if="submitted && (form.is_active == null)" class="text-red-500">
                            Status is required.
                        </small>
                    </div>
                </div>
            </template>
        </CrudComponent>
    </div>
</template>
<script setup>
import CrudComponent from '@/Components/CrudComponent.vue';
import { useForm } from '@inertiajs/vue3';

const form = useForm({
    name: '',
    is_active: 1,
});
</script>