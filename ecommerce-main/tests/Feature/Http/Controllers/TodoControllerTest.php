<?php

namespace Tests\Feature\Http\Controllers;

use App\Models\Todo;
use Illuminate\Foundation\Testing\WithFaker;
use JMac\Testing\Traits\AdditionalAssertions;
use PHPUnit\Framework\Attributes\Test;
use Tests\TestCase;

/**
 * @see \App\Http\Controllers\TodoController
 */
final class TodoControllerTest extends TestCase
{
    use AdditionalAssertions, WithFaker;

    #[Test]
    public function store_uses_form_request_validation(): void
    {
        $this->assertActionUsesFormRequest(
            \App\Http\Controllers\TodoController::class,
            'store',
            \App\Http\Requests\TodoStoreRequest::class
        );
    }

    #[Test]
    public function store_behaves_as_expected(): void
    {
        $title = fake()->sentence(4);

        $response = $this->post(route('todos.store'), [
            'title' => $title,
        ]);
    }

    #[Test]
    public function update_uses_form_request_validation(): void
    {
        $this->assertActionUsesFormRequest(
            \App\Http\Controllers\TodoController::class,
            'update',
            \App\Http\Requests\TodoUpdateRequest::class
        );
    }

    #[Test]
    public function update_behaves_as_expected(): void
    {
        $todo = Todo::factory()->create();
        $title = fake()->sentence(4);

        $response = $this->put(route('todos.update', $todo), [
            'title' => $title,
        ]);
    }
}
