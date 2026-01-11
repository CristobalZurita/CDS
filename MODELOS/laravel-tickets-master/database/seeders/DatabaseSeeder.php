<?php

namespace Database\Seeders;

// use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use App\Models\Category;
use App\Models\Team;
use App\Models\Ticket;
use App\Models\User;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder {
    /**
     * Seed the application's database.
     */
    public function run(): void {

        // \App\Models\User::factory()->create([
        //     'name' => 'Test User',
        //     'email' => 'test@example.com',
        // ]);

        // \App\Models\User::factory(10)->create();
//
//        User::create([
//            'name' => 'admin',
//            'email' => 'admin@test.com',
//            'password' => 123789,
//            'role' => 'admin',
//            'email_verified_at' => now(),
//        ]);
//
//        User::factory(15)->create();
//
//        Category::factory(10)->create();
//        Team::factory(10)->create();
//        Ticket::factory(50)->create();

        $this->call([
            UsersTableSeeder::class,
            CategoriesTableSeeder::class,
            TeamsTableSeeder::class,
            TicketsTableSeeder::class,
        ]);
    }
}
