<?php

namespace App\Http\Controllers;

use App\Http\Requests\TicketRequest;
use App\Http\Resources\TeamResource;
use App\Http\Resources\TicketCollection;
use App\Http\Resources\TicketResource;
use App\Http\Resources\UserResource;
use App\Models\Category;
use App\Models\Team;
use App\Models\Ticket;
use App\Models\User;
use App\Services\TicketService;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;
use Illuminate\Validation\Rule;
use Inertia\Inertia;
use Inertia\Response;

class TicketController extends Controller {

    private TicketService $ticketService;

    public function __construct(TicketService $ticketService) {
        $this->ticketService = $ticketService;
    }

    public function index() {
        $this->authorize('viewAny', Ticket::class);
        return Inertia::render('Tickets/Index');
    }

    public function dataTable(Request $request) {
        return $this->ticketService->getAll($request);
    }

    public function create() {
        $this->authorize('create', Ticket::class);
        $categories = Category::all();
        return Inertia::render('Tickets/CreateEdit', ['categories' => $categories]);
    }

    /**
     * @param TicketRequest $request
     * @return RedirectResponse
     */
    public function store(TicketRequest $request): RedirectResponse {
        $ticket = Ticket::create($request->validated());
        $categoryId = $ticket->category_id;

        $team = Team::whereHas('categories', function (Builder $query) use ($categoryId) {
            $query->where('categories.id', $categoryId);
        })->inRandomOrder()->first();

        if ($team) {
            $ticket->assignedTeams()->attach($team->id);
        }

        return redirect()->route('tickets.index')
            ->with('success', 'A new ticket has been created!');
    }

    /**
     * @param Ticket $ticket
     * @return Response
     */
    public function show(Ticket $ticket) {
        $this->authorize('view', $ticket);

        $users = User::where('role', '!=', 'admin')
            ->where('role', '!=', 'manager')
            ->where('role', '!=', 'customer')
            ->get();

        $ticket->load(['user', 'assignedUsers', 'category', 'comments', 'comments.user', 'assignedTeams']);
        return Inertia::render('Tickets/Show', [
            'ticket' => new TicketResource($ticket),
            'users' => UserResource::collection($users)->collection,
            'teams' => TeamResource::collection(Team::all())->collection,
            'ticketStatuses' => Ticket::TICKET_STATUSES
        ]);
    }

    public function update(TicketRequest $request, Ticket $ticket) {
        $ticket->update($request->validated());

        return $ticket;
    }

    public function destroy(Ticket $ticket) {
        $ticket->delete();

        return response()->json();
    }

    /**
     * @param Request $request
     * @param Ticket $ticket
     * @return RedirectResponse
     */
    public function assignUsers(Request $request, Ticket $ticket) {
        $this->authorize('assignUsers', $ticket);
        $request->validate([
            'users' => ['required', 'array'],
            'users.*' => ['exists:users,id']
        ]);

        $ticket->assignedUsers()->sync($request->get('users'));

        $userIds = $request->get('users');
        $teams = Team::whereHas('users', function (Builder $query) use ($userIds) {
            $query->whereIn('users.id', $userIds);
        })->pluck('id')->toArray();

        $ticket->assignedTeams()->sync($teams);

        return redirect()->back();
    }

    /**
     * @param Request $request
     * @param Ticket $ticket
     * @return RedirectResponse
     */
    public function assignTeams(Request $request, Ticket $ticket) {
        $this->authorize('assignTeams', $ticket);
        $request->validate([
            'teams' => ['required', 'array'],
            'teams.*' => ['exists:teams,id']
        ]);

        $ticket->assignedTeams()->sync($request->get('teams'));

        return redirect()->back();
    }

    /**
     * @param Request $request
     * @param Ticket $ticket
     * @return RedirectResponse
     */
    public function updateStatus(Request $request, Ticket $ticket) {
        $this->authorize('updateStatus', $ticket);
        $request->validate([
            'status' => ['required', Rule::in(Ticket::TICKET_STATUSES)]
        ]);

        $ticket->update([
            'status' => $request->get('status')
        ]);

        return redirect()->back();
    }
}
