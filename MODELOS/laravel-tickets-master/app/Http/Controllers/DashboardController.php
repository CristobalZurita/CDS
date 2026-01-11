<?php

namespace App\Http\Controllers;

use App\Models\Category;
use App\Models\Team;
use App\Models\Ticket;
use App\Models\User;
use Illuminate\Database\Eloquent\Builder;
use Inertia\Inertia;

class DashboardController extends Controller {
    public function index() {

        $user= auth()->user();
        $stats = [];
        $tickets = Ticket::query()
            ->when($user->isAdmin(), function (Builder $query) {
                $query->withTrashed();
            })->when($user->isManager(), function (Builder $query) use ($user) {
                $query->whereHas('assignedTeams', function (Builder $query) use ($user) {
                    $query->where('teams.manager_id', $user->id);
                });
            })->when($user->isTeamLead() || $user->isTeamMember(), function (Builder $query) use ($user) {
                $query->whereHas('assignedTeams', function (Builder $query) use ($user) {
                    $query->whereHas('users', function (Builder $query) use ($user) {
                        $query->where('users.id', $user->id);
                    });
                });
            })->when($user->isCustomer(), function (Builder $query) use ($user) {
                $query->where('user_id', $user->id);
            })->select(['status'])->get();
        $stats['tickets'] = [
            'total' => $tickets->count(),
            'backlog' => $tickets->where('status', '=', 'backlog')->count(),
            'open' => $tickets->filter(function (Ticket $ticket) {
                return $ticket->status == 'open' || $ticket->status == 'in_progress';
            })->count(),
            'in_progress' => $tickets->where('status', '=', 'in_progress')->count(),
            'resolved' => $tickets->filter(function (Ticket $ticket) {
                return $ticket->status == 'resolved' || $ticket->status == 'closed';
            })->count(),
            'closed' => $tickets->where('status', '=', 'closed')->count(),
        ];

        if ($user->isAdmin()) {
            $users = User::select(['role'])->get();
            $stats['users'] = [
                'total' => $users->count(),
                'managers' => $users->where('role', '=' , 'manager')->count(),
                'customers' => $users->where('role', '=' , 'customer')->count(),
                'team_leads' => $users->where('role', '=' , 'team_lead')->count(),
                'team_members' => $users->where('role', '=' , 'team_member')->count(),
            ];

            $stats['categories'] = Category::select(['id'])->get()->count();
            $stats['teams'] = Team::select(['id'])->get()->count();
        }

//        dd($stats);


        return Inertia::render('Dashboard', [
            'stats' => $stats
        ]);
    }
}
