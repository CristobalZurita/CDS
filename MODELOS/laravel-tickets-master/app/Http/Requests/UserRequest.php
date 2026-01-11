<?php

namespace App\Http\Requests;

use App\Models\User;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class UserRequest extends FormRequest {
    public function rules(): array {
        return [
            'name' => ['required', 'string', 'max:255'],
            'email' => ['required', 'email', Rule::unique(User::class)->ignore($this->route('user'))],
            'role' => [
                'required', Rule::in(array_values(array_diff(User::ROLES, ['admin'])))
            ],
            'password' => [
                $this->route('user') ? 'nullable' :'required',
                'min:8'
            ]
        ];
    }

    public function authorize(): bool {
        return true;
    }
}
