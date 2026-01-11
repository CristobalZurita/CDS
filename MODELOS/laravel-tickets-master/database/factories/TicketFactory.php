<?php

namespace Database\Factories;

use App\Models\Category;
use App\Models\Ticket;
use App\Models\User;
use Illuminate\Database\Eloquent\Factories\Factory;
use Illuminate\Support\Carbon;

class TicketFactory extends Factory {
    protected $model = Ticket::class;

    public function definition(): array {
        return [
            'title' => $this->faker->realText('20'),
            'description' => $this->faker->realText('50'),
            'status' => $this->faker->randomElement(['backlog', 'open', 'in_progress', 'resolved', 'closed']),
            'created_at' => Carbon::now(),
            'updated_at' => Carbon::now(),

            'user_id' => $this->faker->randomElement(User::where('role', '!=', 'admin')->get()->pluck('id')->toArray()),
            'category_id' =>$this->faker->randomElement(Category::all()->pluck('id')->toArray()),
        ];
    }
}
