<?php

namespace Database\Seeders;

use App\Models\User;
use Illuminate\Database\Seeder;
use Faker\Factory as Faker;

class UsersTableSeeder extends Seeder {
    public function run(): void {

        $faker = Faker::create();

        $users = [
            ['name' => 'Admin User', 'email' => 'admin@example.com', 'password' => '123789', 'role' => 'admin'],
            ['name' => 'Bob Smith', 'email' => 'manager1@example.com', 'password' => 'password', 'role' => 'manager'],
            ['name' => 'Charlie Brown', 'email' => 'manager2@example.com', 'password' => 'password', 'role' => 'manager'],
            ['name' => 'David Wilson', 'email' => 'manager3@example.com', 'password' => 'password', 'role' => 'manager'],
            ['name' => 'Eve Davis', 'email' => 'manager4@example.com', 'password' => 'password', 'role' => 'manager'],
            ['name' => 'Frank Miller', 'email' => 'teamlead1@example.com', 'password' => 'password', 'role' => 'team_lead'],
            ['name' => 'Grace Lee', 'email' => 'teamlead2@example.com', 'password' => 'password', 'role' => 'team_lead'],
            ['name' => 'Hannah White', 'email' => 'teamlead3@example.com', 'password' => 'password', 'role' => 'team_lead'],
            ['name' => 'Isaac Martin', 'email' => 'teamlead4@example.com', 'password' => 'password', 'role' => 'team_lead'],
            ['name' => 'Jack Thompson', 'email' => 'teammember1@example.com', 'password' => 'password', 'role' => 'team_member'],
            ['name' => 'Karen Garcia', 'email' => 'teammember2@example.com', 'password' => 'password', 'role' => 'team_member'],
            ['name' => 'Leo Martinez', 'email' => 'teammember3@example.com', 'password' => 'password', 'role' => 'team_member'],
            ['name' => 'Mona Robinson', 'email' => 'teammember4@example.com', 'password' => 'password', 'role' => 'team_member'],
            ['name' => 'Nancy Clark', 'email' => 'customer1@example.com', 'password' => 'password', 'role' => 'customer'],
            ['name' => 'Oscar Rodriguez', 'email' => 'customer2@example.com', 'password' => 'password', 'role' => 'customer'],
        ];

        foreach ($users as $user) {
            User::create($user);
        }
    }
}
