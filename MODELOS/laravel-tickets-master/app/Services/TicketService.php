<?php

namespace App\Services;

use App\Http\Resources\TicketCollection;
use App\Models\Ticket;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Http\Request;

class TicketService {
    public function __construct() {
    }

    /**
     * @param Request $request
     * @return TicketCollection
     */
    public function getAll(Request $request): TicketCollection {

        $columns = [
            'title',
            'description',
            'user_id',
            'category_id',
            'status',
        ];

        $query = Ticket::query()
            ->when($request->user()->isCustomer(), function (Builder $query) use ($request) {
                $query->where('user_id', $request->user()->id);
            })->when($request->user()->isManager(), function (Builder $query) use ($request) {
                $query->whereHas('assignedTeams', function (Builder $query) use ($request) {
                    $query->where('teams.manager_id', $request->user()->id);
                });
            })->when($request->user()->isTeamLead() || $request->user()->isTeamMember(), function (Builder $query) use ($request) {
                $query->whereHas('assignedUsers', function (Builder $query) use ($request) {
                    $query->where('users.id', $request->user()->id);
                });
            });

        $tickets = DataTableService::data($request, $query, $columns);

        return new TicketCollection($tickets);
    }
}
