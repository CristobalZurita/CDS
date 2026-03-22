<?php

namespace Tests\Feature\Http\Controllers;

use App\Models\Task;
use Illuminate\Foundation\Testing\WithFaker;
use JMac\Testing\Traits\AdditionalAssertions;
use PHPUnit\Framework\Attributes\Test;
use Tests\TestCase;

/**
 * @see \App\Http\Controllers\TaskController
 */
final class TaskControllerTest extends TestCase
{
    use AdditionalAssertions, WithFaker;

    #[Test]
    public function store_uses_form_request_validation(): void
    {
        $this->assertActionUsesFormRequest(
            \App\Http\Controllers\TaskController::class,
            'store',
            \App\Http\Requests\TaskStoreRequest::class
        );
    }

    #[Test]
    public function store_behaves_as_expected(): void
    {
        $title = fake()->sentence(4);

        $response = $this->post(route('tasks.store'), [
            'title' => $title,
        ]);
    }

    #[Test]
    public function update_uses_form_request_validation(): void
    {
        $this->assertActionUsesFormRequest(
            \App\Http\Controllers\TaskController::class,
            'update',
            \App\Http\Requests\TaskUpdateRequest::class
        );
    }

    #[Test]
    public function update_behaves_as_expected(): void
    {
        $task = Task::factory()->create();
        $title = fake()->sentence(4);

        $response = $this->put(route('tasks.update', $task), [
            'title' => $title,
        ]);
    }
}
