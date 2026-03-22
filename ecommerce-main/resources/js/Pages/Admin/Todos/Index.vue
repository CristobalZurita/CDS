<template>
  <div>
    <CrudComponent :form="form">
      <template #columns>
        <Column field="title" header="Title"></Column>
        <Column field="is_completed" header="Is Completed">
            <template #body="{data}">
                <span :class="{'text-green-400 font-bold' : data.is_completed}">{{ data.is_completed ? 'Yes' : 'No' }}</span>
            </template>
        </Column>
        <!-- <Column field="created_at" header="Created At" sortable></Column> -->
      </template>

      <template #form="{ submitted, handlePhotoUpload, photoPreview, resolveImagePath }">
        <Form :form="form" />
      </template>
    </CrudComponent>
  </div>
</template>
<script setup>
import CrudComponent from '@/Components/CrudComponent.vue';
import Form from './Form.vue';
import { useForm } from '@inertiajs/vue3';

const form = useForm({
    title: '',
    is_completed: '',
});

</script>
