<?php

namespace App\Http\Controllers;

use App\Http\Requests\UserRequest;
use App\Http\Resources\UserCollection;
use App\Models\User;
use App\Services\DataTableService;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;

class UserController extends Controller {
    public function index() {
        $this->authorize('viewAny', User::class);

        return Inertia::render('Users/Index');
    }

    /**
     * @param Request $request
     * @return UserCollection
     */
    public function dataTable(Request $request) {
        $columns = [
            'name',
            'email',
            'role',
        ];

        $query = User::query()
            ->when($request->query('team'), function (Builder $q) use ($request) {
                $teamId = $request->query('team');
                $q->whereHas('teams', function (Builder $q) use ($teamId) {
                    $q->where('teams.id', $teamId);
                });
            });

        $users = DataTableService::data($request, $query, $columns);
        return new UserCollection($users);
    }

    public function create() {
        $roles = User::ROLES;

        $roles = array_diff($roles, ['admin']);
        if (auth()->user()->isManager()) {
            $roles = array_diff($roles, ['manager', 'customer']);
        }


        return Inertia::render('Users/CreateEdit',[
            'roles' => array_values($roles)
        ]);
    }

    /**
     * @param UserRequest $request
     * @return RedirectResponse
     */
    public function store(UserRequest $request) {
        $this->authorize('create', User::class);

        $user = User::create($request->validated());
        return redirect()->route('users.edit', $user->id)
            ->with('success', 'A new user has been created!');
    }

    public function show(User $user) {
        $this->authorize('viewAny', $user);
    }

    /**
     * @param User $user
     * @return Response
     */
    public function edit(User $user) {
        $roles = array_diff(User::ROLES, ['admin']);
        if (auth()->user()->isManager()) {
            $roles = array_diff($roles, ['manager', 'customer']);
        }

        return Inertia::render('Users/CreateEdit', [
            'user' => $user,
            'roles' => array_values($roles)
        ]);
    }

    /**
     * @param UserRequest $request
     * @param User $user
     * @return RedirectResponse
     */
    public function update(UserRequest $request, User $user) {
        $this->authorize('update', $user);

        $fields = $request->validated();
        if (!$request->get('password')) {
            unset($fields['password']);
        }

        $user->update($fields);
        return redirect()->route('users.index')
            ->with('success', 'User information has been updated!');
    }

    public function destroy(User $user) {
        $this->authorize('delete', $user);
        $user->delete();
    }
}
