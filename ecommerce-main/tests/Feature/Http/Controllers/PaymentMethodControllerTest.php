<?php

namespace Tests\Feature\Http\Controllers;

use App\Models\PaymentMethod;
use Illuminate\Foundation\Testing\WithFaker;
use JMac\Testing\Traits\AdditionalAssertions;
use PHPUnit\Framework\Attributes\Test;
use Tests\TestCase;

/**
 * @see \App\Http\Controllers\PaymentMethodController
 */
final class PaymentMethodControllerTest extends TestCase
{
    use AdditionalAssertions, WithFaker;

    #[Test]
    public function store_uses_form_request_validation(): void
    {
        $this->assertActionUsesFormRequest(
            \App\Http\Controllers\PaymentMethodController::class,
            'store',
            \App\Http\Requests\PaymentMethodStoreRequest::class
        );
    }

    #[Test]
    public function store_behaves_as_expected(): void
    {
        $name = fake()->name();
        $is_active = fake()->boolean();
        $softDelete = fake()->word();

        $response = $this->post(route('payment-methods.store'), [
            'name' => $name,
            'is_active' => $is_active,
        ]);
    }

    #[Test]
    public function update_uses_form_request_validation(): void
    {
        $this->assertActionUsesFormRequest(
            \App\Http\Controllers\PaymentMethodController::class,
            'update',
            \App\Http\Requests\PaymentMethodUpdateRequest::class
        );
    }

    #[Test]
    public function update_behaves_as_expected(): void
    {
        $paymentMethod = PaymentMethod::factory()->create();
        $name = fake()->name();
        $is_active = fake()->boolean();
        $softDelete = fake()->word();

        $response = $this->put(route('payment-methods.update', $paymentMethod), [
            'name' => $name,
            'is_active' => $is_active,
        ]);
    }
}
