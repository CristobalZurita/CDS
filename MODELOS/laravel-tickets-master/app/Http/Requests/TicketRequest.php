<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class TicketRequest extends FormRequest {
    public function rules(): array {
        return [
            'title' => ['required'],
            'description' => ['required'],
            'user_id' => ['required', 'exists:users,id'],
            'category_id' => ['required', 'exists:categories,id'],
            'status' => ['nullable', 'in:open,in_progress,resolved,closed,other'],
        ];
    }

    public function authorize(): bool {
        return true;
    }
}
