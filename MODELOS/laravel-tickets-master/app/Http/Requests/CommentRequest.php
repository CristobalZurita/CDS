<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class CommentRequest extends FormRequest {
    public function rules(): array {
        return [
            'message' => ['required'],
            'user_id' => ['required', 'exists:users,id'],
            'ticket_id' => ['required', 'exists:tickets,id'],
        ];
    }

    public function authorize(): bool {
        return true;
    }

    public function messages() {
        return parent::messages();
    }
}
