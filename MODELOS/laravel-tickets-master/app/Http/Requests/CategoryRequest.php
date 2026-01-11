<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class CategoryRequest extends FormRequest {
    public function rules(): array {
        return [
            'name' => ['required'],
            'description' => ['nullable'],
            'category_id' => ['nullable', 'exists:categories,id'],
        ];
    }

    public function authorize(): bool {
        return true;
    }
}
