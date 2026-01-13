<?php

namespace Database\Seeders;

use App\Models\Team;
use App\Models\User;
use Illuminate\Database\Seeder;

class TeamsTableSeeder extends Seeder {
    public function run(): void {
        $teams = [
            ['name' => 'Hardware Team', 'description' => 'Team handling hardware issues', 'manager_id' => User::where('email', 'manager1@example.com')->first()->id],
            ['name' => 'Software Team', 'description' => 'Team handling software issues', 'manager_id' => User::where('email', 'manager2@example.com')->first()->id],
            ['name' => 'Network Team', 'description' => 'Team handling network issues', 'manager_id' => User::where('email', 'manager3@example.com')->first()->id],
            ['name' => 'Security Team', 'description' => 'Team handling security issues', 'manager_id' => User::where('email', 'manager4@example.com')->first()->id],
        ];

        $teamLeadEmails = ['teamlead1@example.com', 'teamlead2@example.com', 'teamlead3@example.com', 'teamlead4@example.com'];
        $teamMemberEmails = ['teammember1@example.com', 'teammember2@example.com', 'teammember3@example.com', 'teammember4@example.com'];

        foreach ($teams as $index => $team) {
            $createdTeam = Team::create($team);
            $createdTeam->users()->attach(User::where('email', $teamLeadEmails[$index])->first()->id);
            $createdTeam->users()->attach(User::where('email', $teamMemberEmails[$index])->first()->id);
        }
    }
}
