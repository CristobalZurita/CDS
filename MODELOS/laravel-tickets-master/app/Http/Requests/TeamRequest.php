<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class TeamRequest extends FormRequest {
    public function rules(): array {
        return [
            'name' => ['required'],
            'description' => ['nullable'],
            'manager_id' => ['required', 'exists:users,id'],
            'users' => ['nullable', 'array'],
            'users.*' => ['exists:users,id'],
            'categories' => ['nullable', 'array'],
            'categories.*' => ['exists:categories,id'],
        ];
    }

    public function authorize(): bool {
        return true;
    }

    public function messages(): array {
        return [
            'name.required' => 'Team name is required.',
            'description.nullable' => 'Team description is required.',
            'manager_id.required' => 'Manager is required.',
            'manager_id.exists' => 'Manager does not exist.',
            'users.*.exists' => 'User does not exist.',
            'categories.*.exists' => 'Category does not exist.',
        ];
    }
}
