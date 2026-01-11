<?php

namespace Database\Factories;

use App\Models\Category;
use Illuminate\Database\Eloquent\Factories\Factory;
use Illuminate\Support\Carbon;

class CategoryFactory extends Factory {
    protected $model = Category::class;

    public function definition(): array {
        return [
            'name' => $this->faker->realText(20),
            'description' => $this->faker->realText(100),
            'created_at' => Carbon::now(),
            'updated_at' => Carbon::now(),

            'category_id' => null,
        ];
    }
}
