<?php

namespace App\Http\Controllers;

use App\Http\Requests\TeamRequest;
use App\Http\Resources\TeamCollection;
use App\Models\Category;
use App\Models\Team;
use App\Models\User;
use App\Services\DataTableService;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;

class TeamController extends Controller {

    /**
     * @return Response
     */
    public function index() {
        $this->authorize('viewAny', Team::class);
        return Inertia::render('Teams/Index');
    }

    /**
     * @param Request $request
     * @return TeamCollection
     */
    public function dataTable(Request $request) {
        $columns = [
            'name',
            'description',
            'manager_id',
        ];
        $teams = DataTableService::data($request, Team::query(), $columns, ['manager']);
        return new TeamCollection($teams);
    }

    /**
     * @return Response
     */
    public function create() {
        $managers = User::whereRole('manager')->get()->toArray();
        $users = User::whereRole('team_member')->orWhere('role', 'team_lead')->get()->toArray();
        $categories = Category::all()->toArray();

        return Inertia::render('Teams/CreateEdit',[
            'managers' => $managers,
            'users' => $users,
            'categories' => $categories
        ]);
    }

    /**
     * @param TeamRequest $request
     * @return RedirectResponse
     */
    public function store(TeamRequest $request) {
        $this->authorize('create', Team::class);

        $team = Team::create($request->validated());
        $team->users()->attach($request->users);
        $team->categories()->attach($request->categories);

        return redirect()->route('teams.edit', ['team' => $team])
            ->with('success', 'Team was created.');
    }

    /**
     * @param Team $team
     * @return Response
     */
    public function edit(Team $team) {
        $this->authorize('update', $team);

        $managers = User::whereRole('manager')->get()->toArray();
        $users = User::whereRole('team_member')->orWhere('role', 'team_lead')->get()->toArray();
        $categories = Category::all()->toArray();

        $team->load(['users', 'categories']);

        return Inertia::render('Teams/CreateEdit',[
            'managers' => $managers,
            'users' => $users,
            'team' => $team,
            'categories' => $categories
        ]);
    }

    public function show(Team $team) {
        $this->authorize('view', $team);
        $team->load(['manager', 'categories']);

        return Inertia::render('Teams/Show', [
            'team' => $team
        ]);
    }

    /**
     * @return RedirectResponse
     */
    public function myTeam() {
        $this->authorize('myTeam', Team::class);
        $team = Team::whereManagerId(auth()->id())->firstOrFail();

        return redirect()->route('teams.show', $team->id);
    }

    /**
     * @param TeamRequest $request
     * @param Team $team
     * @return RedirectResponse
     */
    public function update(TeamRequest $request, Team $team) {
        $this->authorize('update', $team);

        $team->update($request->validated());
        $team->users()->sync($request->users);
        $team->categories()->sync($request->categories);

        return redirect()->route('teams.index')
            ->with('success', 'Team was updated.');
    }

    public function destroy(Team $team) {
        $this->authorize('delete', $team);

        $team->delete();

        return response()->json();
    }
}
